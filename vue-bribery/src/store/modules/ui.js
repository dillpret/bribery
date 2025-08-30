/**
 * UI state module
 * Manages UI-related state such as loading indicators, status messages, and timers
 */

export default {
  namespaced: true,
  
  state: {
    // Connection state
    statusMessage: 'Connecting...',
    isConnected: false,
    
    // Timer state
    timerValue: 0,
    timerActive: false,
    
    // Loading states
    isLoading: false,
    loadingMessage: '',
    loadingStates: {}, // Allows multiple named loading states
    
    // UI controls
    activeDialog: null,
    sidebarOpen: false,
    isMobileView: false,
    darkMode: false,
    
    // Notification state
    notifications: []
  },
  
  getters: {
    /**
     * Check if a specific loading state is active
     */
    isLoadingState: (state) => (stateName) => {
      return state.loadingStates[stateName] === true
    },
    
    /**
     * Get all active loading states
     */
    activeLoadingStates(state) {
      return Object.keys(state.loadingStates).filter(key => state.loadingStates[key])
    },
    
    /**
     * Check if any loading state is active
     */
    isAnyLoading(state, getters) {
      return state.isLoading || getters.activeLoadingStates.length > 0
    }
  },
  
  mutations: {
    SET_STATUS(state, message) {
      state.statusMessage = message
    },
    
    SET_CONNECTION(state, isConnected) {
      state.isConnected = isConnected
    },
    
    SET_TIMER(state, value) {
      state.timerValue = value
    },
    
    SET_TIMER_ACTIVE(state, active) {
      state.timerActive = active
    },
    
    SET_ACTIVE_DIALOG(state, dialog) {
      state.activeDialog = dialog
    },
    
    SET_LOADING(state, { isLoading, message = '' }) {
      state.isLoading = isLoading
      state.loadingMessage = message
    },
    
    SET_LOADING_STATE(state, { name, isLoading }) {
      state.loadingStates = {
        ...state.loadingStates,
        [name]: isLoading
      }
    },
    
    CLEAR_ALL_LOADING_STATES(state) {
      state.loadingStates = {}
      state.isLoading = false
      state.loadingMessage = ''
    },
    
    SET_SIDEBAR_OPEN(state, isOpen) {
      state.sidebarOpen = isOpen
    },
    
    SET_MOBILE_VIEW(state, isMobile) {
      state.isMobileView = isMobile
    },
    
    SET_DARK_MODE(state, isDark) {
      state.darkMode = isDark
    },
    
    ADD_NOTIFICATION(state, notification) {
      state.notifications.push({
        id: Date.now(),
        ...notification
      })
    },
    
    REMOVE_NOTIFICATION(state, id) {
      state.notifications = state.notifications.filter(note => note.id !== id)
    },
    
    CLEAR_NOTIFICATIONS(state) {
      state.notifications = []
    }
  },
  
  actions: {
    /**
     * Set a named loading state
     */
    setLoadingState({ commit }, { name, isLoading }) {
      commit('SET_LOADING_STATE', { name, isLoading })
    },
    
    /**
     * Show global loading state with message
     */
    showLoading({ commit }, message = '') {
      commit('SET_LOADING', { isLoading: true, message })
    },
    
    /**
     * Hide global loading state
     */
    hideLoading({ commit }) {
      commit('SET_LOADING', { isLoading: false, message: '' })
    },
    
    /**
     * Set status message and connection state
     */
    updateConnectionStatus({ commit }, { connected, message }) {
      commit('SET_CONNECTION', connected)
      if (message) {
        commit('SET_STATUS', message)
      }
    },
    
    /**
     * Start a countdown timer
     */
    startTimer({ commit, state, dispatch }, duration) {
      // Clear any existing timer
      if (state.timerActive) {
        dispatch('stopTimer')
      }
      
      commit('SET_TIMER', duration)
      commit('SET_TIMER_ACTIVE', true)
      
      // Create a timer that counts down
      const timerInterval = setInterval(() => {
        if (state.timerValue <= 0) {
          clearInterval(timerInterval)
          commit('SET_TIMER_ACTIVE', false)
          return
        }
        
        commit('SET_TIMER', state.timerValue - 1)
      }, 1000)
      
      // Store the interval ID in state for cleanup
      return timerInterval
    },
    
    /**
     * Stop the active timer
     */
    stopTimer({ commit }) {
      commit('SET_TIMER_ACTIVE', false)
      commit('SET_TIMER', 0)
    },
    
    /**
     * Toggle the sidebar open/closed state
     */
    toggleSidebar({ commit, state }) {
      commit('SET_SIDEBAR_OPEN', !state.sidebarOpen)
    },
    
    /**
     * Update mobile view state based on screen size
     */
    checkMobileView({ commit }) {
      const isMobile = window.innerWidth < 768
      commit('SET_MOBILE_VIEW', isMobile)
    },
    
    /**
     * Toggle dark mode
     */
    toggleDarkMode({ commit, state }) {
      const newMode = !state.darkMode
      commit('SET_DARK_MODE', newMode)
      
      // Apply dark mode class to body
      if (newMode) {
        document.body.classList.add('dark-mode')
      } else {
        document.body.classList.remove('dark-mode')
      }
      
      // Store preference
      localStorage.setItem('darkMode', newMode ? 'true' : 'false')
    },
    
    /**
     * Initialize UI state (call on app startup)
     */
    initializeUI({ dispatch }) {
      // Check for saved preferences
      const savedDarkMode = localStorage.getItem('darkMode') === 'true'
      if (savedDarkMode) {
        dispatch('toggleDarkMode')
      }
      
      // Set up responsive handling
      dispatch('checkMobileView')
      window.addEventListener('resize', () => {
        dispatch('checkMobileView')
      })
    }
  }
}
