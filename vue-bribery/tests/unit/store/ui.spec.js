import { createStore } from 'vuex'
import uiModule from '@/store/modules/ui'

describe('UI Store Module', () => {
  let store
  
  beforeEach(() => {
    // Create a new store for each test
    store = createStore({
      modules: {
        ui: {
          ...uiModule,
          state: { ...uiModule.state } // Create a fresh copy of the state
        }
      }
    })
    
    // Mock timers
    jest.useFakeTimers()
  })
  
  afterEach(() => {
    jest.useRealTimers()
    
    // Clean up any event listeners
    window.removeEventListener = jest.fn()
  })
  
  it('sets status message', () => {
    store.commit('ui/SET_STATUS', 'Test message')
    expect(store.state.ui.statusMessage).toBe('Test message')
  })
  
  it('sets connection state', () => {
    store.commit('ui/SET_CONNECTION', true)
    expect(store.state.ui.isConnected).toBe(true)
  })
  
  it('sets timer value', () => {
    store.commit('ui/SET_TIMER', 30)
    expect(store.state.ui.timerValue).toBe(30)
  })
  
  it('sets timer active state', () => {
    store.commit('ui/SET_TIMER_ACTIVE', true)
    expect(store.state.ui.timerActive).toBe(true)
  })
  
  it('sets active dialog', () => {
    store.commit('ui/SET_ACTIVE_DIALOG', 'settings')
    expect(store.state.ui.activeDialog).toBe('settings')
  })
  
  it('sets loading state', () => {
    store.commit('ui/SET_LOADING', { isLoading: true, message: 'Loading...' })
    expect(store.state.ui.isLoading).toBe(true)
    expect(store.state.ui.loadingMessage).toBe('Loading...')
  })
  
  it('sets named loading state', () => {
    store.commit('ui/SET_LOADING_STATE', { name: 'submissions', isLoading: true })
    expect(store.state.ui.loadingStates.submissions).toBe(true)
  })
  
  it('clears all loading states', () => {
    // Set up some loading states
    store.commit('ui/SET_LOADING', { isLoading: true, message: 'Loading...' })
    store.commit('ui/SET_LOADING_STATE', { name: 'submissions', isLoading: true })
    
    // Clear them
    store.commit('ui/CLEAR_ALL_LOADING_STATES')
    
    // Verify they're cleared
    expect(store.state.ui.isLoading).toBe(false)
    expect(store.state.ui.loadingMessage).toBe('')
    expect(store.state.ui.loadingStates).toEqual({})
  })
  
  it('shows loading state with action', async () => {
    await store.dispatch('ui/showLoading', 'Loading...')
    
    expect(store.state.ui.isLoading).toBe(true)
    expect(store.state.ui.loadingMessage).toBe('Loading...')
  })
  
  it('hides loading state with action', async () => {
    // Set loading state
    store.commit('ui/SET_LOADING', { isLoading: true, message: 'Loading...' })
    
    // Hide it
    await store.dispatch('ui/hideLoading')
    
    expect(store.state.ui.isLoading).toBe(false)
    expect(store.state.ui.loadingMessage).toBe('')
  })
  
  it('updates connection status', async () => {
    await store.dispatch('ui/updateConnectionStatus', { connected: true, message: 'Connected' })
    
    expect(store.state.ui.isConnected).toBe(true)
    expect(store.state.ui.statusMessage).toBe('Connected')
  })
  
  it('checks if a specific loading state is active', () => {
    // Set a loading state
    store.commit('ui/SET_LOADING_STATE', { name: 'submissions', isLoading: true })
    
    // Check via getter
    const isSubmissionsLoading = store.getters['ui/isLoadingState']('submissions')
    const isVotingLoading = store.getters['ui/isLoadingState']('voting')
    
    expect(isSubmissionsLoading).toBe(true)
    expect(isVotingLoading).toBe(false)
  })
  
  it('gets all active loading states', () => {
    // Set multiple loading states
    store.commit('ui/SET_LOADING_STATE', { name: 'submissions', isLoading: true })
    store.commit('ui/SET_LOADING_STATE', { name: 'voting', isLoading: false })
    store.commit('ui/SET_LOADING_STATE', { name: 'results', isLoading: true })
    
    // Get active states
    const activeStates = store.getters['ui/activeLoadingStates']
    
    expect(activeStates).toContain('submissions')
    expect(activeStates).toContain('results')
    expect(activeStates).not.toContain('voting')
    expect(activeStates.length).toBe(2)
  })
  
  it('checks if any loading state is active', () => {
    // Initially no loading
    expect(store.getters['ui/isAnyLoading']).toBe(false)
    
    // Set global loading
    store.commit('ui/SET_LOADING', { isLoading: true })
    expect(store.getters['ui/isAnyLoading']).toBe(true)
    
    // Clear global, set named loading
    store.commit('ui/SET_LOADING', { isLoading: false })
    store.commit('ui/SET_LOADING_STATE', { name: 'submissions', isLoading: true })
    expect(store.getters['ui/isAnyLoading']).toBe(true)
    
    // Clear all loading
    store.commit('ui/CLEAR_ALL_LOADING_STATES')
    expect(store.getters['ui/isAnyLoading']).toBe(false)
  })
})
