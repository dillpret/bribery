import authService from '@/services/auth'

describe('Auth Service', () => {
  beforeEach(() => {
    // Clear localStorage before each test
    localStorage.clear()
  })
  
  it('saves auth state to localStorage', () => {
    const gameId = 'test-game'
    const authData = {
      playerId: 'player123',
      username: 'TestUser',
      isHost: true,
      gameId: gameId
    }
    
    authService.saveAuthState(gameId, authData)
    
    // Get the stored data directly from localStorage
    const storageKey = authService.getStorageKey(gameId)
    const storedDataJson = localStorage.getItem(storageKey)
    const storedData = JSON.parse(storedDataJson)
    
    expect(storedData).toBeTruthy()
    expect(storedData.playerId).toBe(authData.playerId)
    expect(storedData.username).toBe(authData.username)
    expect(storedData.isHost).toBe(authData.isHost)
  })
  
  it('loads auth state from localStorage', () => {
    const gameId = 'test-game'
    const authData = {
      playerId: 'player123',
      username: 'TestUser',
      isHost: true,
      gameId: gameId
    }
    
    // Manually store data in localStorage
    const storageKey = authService.getStorageKey(gameId)
    localStorage.setItem(storageKey, JSON.stringify(authData))
    
    // Load the data using the service
    const loadedData = authService.loadAuthState(gameId)
    
    expect(loadedData).toBeTruthy()
    expect(loadedData.playerId).toBe(authData.playerId)
    expect(loadedData.username).toBe(authData.username)
    expect(loadedData.isHost).toBe(authData.isHost)
  })
  
  it('returns null when no auth state exists', () => {
    const gameId = 'nonexistent-game'
    const loadedData = authService.loadAuthState(gameId)
    expect(loadedData).toBeNull()
  })
  
  it('clears auth state from localStorage', () => {
    const gameId = 'test-game'
    const authData = {
      playerId: 'player123',
      username: 'TestUser',
      isHost: true,
      gameId: gameId
    }
    
    // Set up data in localStorage
    const storageKey = authService.getStorageKey(gameId)
    localStorage.setItem(storageKey, JSON.stringify(authData))
    
    // Clear the data
    authService.clearAuthState(gameId)
    
    // Verify it's gone
    const storedDataJson = localStorage.getItem(storageKey)
    expect(storedDataJson).toBeNull()
  })
  
  it('handles null or undefined gameId gracefully', () => {
    expect(authService.loadAuthState(null)).toBeNull()
    expect(authService.loadAuthState(undefined)).toBeNull()
    
    // These should not throw errors
    authService.saveAuthState(null, { playerId: 'test' })
    authService.clearAuthState(undefined)
  })
})
