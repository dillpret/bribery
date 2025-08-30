export default {
  namespaced: true,
  
  state: {
    statusMessage: 'Connecting...',
    isConnected: false,
    timerValue: 0,
    timerActive: false,
    activeDialog: null
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
    }
  }
}
