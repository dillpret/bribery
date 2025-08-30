import { createStore } from 'vuex'
import authModule from '@/store/modules/auth'
import authService from '@/services/auth'

// Mock the auth service
jest.mock('@/services/auth', () => ({
  getStorageKey: jest.fn().mockReturnValue('bribery_game_test-game'),
  saveAuthState: jest.fn(),
  loadAuthState: jest.fn(),
  clearAuthState: jest.fn()
}))

describe('Auth Store Module', () => {
  let store
  
  beforeEach(() => {
    // Reset mocks
    jest.clearAllMocks()
    
    // Create a new store for each test
    store = createStore({
      modules: {
        auth: {
          ...authModule,
          state: { ...authModule.state } // Create a fresh copy of the state
        }
      }
    })
  })
  
  it('sets player ID', () => {
    store.commit('auth/SET_PLAYER_ID', 'player123')
    expect(store.state.auth.playerId).toBe('player123')
  })
  
  it('sets username', () => {
    store.commit('auth/SET_USERNAME', 'TestUser')
    expect(store.state.auth.username).toBe('TestUser')
  })
  
  it('sets host status', () => {
    store.commit('auth/SET_HOST', true)
    expect(store.state.auth.isHost).toBe(true)
  })
  
  it('sets game ID', () => {
    store.commit('auth/SET_GAME_ID', 'game123')
    expect(store.state.auth.gameId).toBe('game123')
  })
  
  it('sets authentication status', () => {
    store.commit('auth/SET_AUTHENTICATED', true)
    expect(store.state.auth.isAuthenticated).toBe(true)
  })
  
  it('clears auth state', () => {
    // Set some state
    store.commit('auth/SET_PLAYER_ID', 'player123')
    store.commit('auth/SET_USERNAME', 'TestUser')
    store.commit('auth/SET_HOST', true)
    store.commit('auth/SET_GAME_ID', 'game123')
    store.commit('auth/SET_AUTHENTICATED', true)
    
    // Clear it
    store.commit('auth/CLEAR_AUTH')
    
    // Verify it's cleared
    expect(store.state.auth.playerId).toBeNull()
    expect(store.state.auth.isAuthenticated).toBe(false)
  })
  
  it('initializes auth from localStorage when available', async () => {
    const gameId = 'test-game'
    const authData = {
      playerId: 'player123',
      username: 'TestUser',
      isHost: true,
      gameId
    }
    
    // Mock loadAuthState to return our data
    authService.loadAuthState.mockReturnValue(authData)
    
    // Call the action
    const result = await store.dispatch('auth/initAuth', gameId)
    
    // Verify the result
    expect(result).toBe(true)
    
    // Verify the state is updated
    expect(store.state.auth.playerId).toBe(authData.playerId)
    expect(store.state.auth.username).toBe(authData.username)
    expect(store.state.auth.isHost).toBe(authData.isHost)
    expect(store.state.auth.gameId).toBe(authData.gameId)
    expect(store.state.auth.isAuthenticated).toBe(true)
  })
  
  it('returns false when no auth data is available', async () => {
    const gameId = 'test-game'
    
    // Mock loadAuthState to return null
    authService.loadAuthState.mockReturnValue(null)
    
    // Call the action
    const result = await store.dispatch('auth/initAuth', gameId)
    
    // Verify the result
    expect(result).toBe(false)
    
    // Verify the state is not updated
    expect(store.state.auth.isAuthenticated).toBe(false)
  })
  
  it('saves auth state', async () => {
    const gameId = 'test-game'
    const playerId = 'player123'
    const username = 'TestUser'
    const isHost = true
    
    // Set up the state
    store.commit('auth/SET_PLAYER_ID', playerId)
    store.commit('auth/SET_USERNAME', username)
    store.commit('auth/SET_HOST', isHost)
    store.commit('auth/SET_GAME_ID', gameId)
    
    // Call the action
    await store.dispatch('auth/saveAuth')
    
    // Verify the service was called
    expect(authService.saveAuthState).toHaveBeenCalledWith(gameId, {
      playerId,
      username,
      isHost
    })
  })
  
  it('does not save auth state when gameId is missing', async () => {
    // Set up the state without a gameId
    store.commit('auth/SET_PLAYER_ID', 'player123')
    
    // Call the action
    await store.dispatch('auth/saveAuth')
    
    // Verify the service was not called
    expect(authService.saveAuthState).not.toHaveBeenCalled()
  })
})
