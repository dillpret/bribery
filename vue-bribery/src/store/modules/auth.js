import authService from '@/services/auth'

export default {
  namespaced: true,
  
  state: {
    playerId: null,
    username: null,
    isHost: false,
    gameId: null,
    isAuthenticated: false
  },
  
  mutations: {
    SET_PLAYER_ID(state, id) {
      state.playerId = id
    },
    SET_USERNAME(state, name) {
      state.username = name
    },
    SET_HOST(state, isHost) {
      state.isHost = isHost
    },
    SET_GAME_ID(state, id) {
      state.gameId = id
    },
    SET_AUTHENTICATED(state, value) {
      state.isAuthenticated = value
    },
    CLEAR_AUTH(state) {
      state.playerId = null
      state.username = null
      state.isHost = false
      state.gameId = null
      state.isAuthenticated = false
    }
  },
  
  actions: {
    initAuth({ commit, dispatch }, gameId) {
      const authData = authService.loadAuthState(gameId)
      if (authData) {
        commit('SET_PLAYER_ID', authData.playerId)
        commit('SET_USERNAME', authData.username)
        commit('SET_HOST', authData.isHost)
        commit('SET_GAME_ID', gameId)
        commit('SET_AUTHENTICATED', true)
        return true
      }
      return false
    },
    
    saveAuth({ state }) {
      if (state.gameId) {
        authService.saveAuthState(state.gameId, {
          playerId: state.playerId,
          username: state.username,
          isHost: state.isHost
        })
      }
    }
  }
}
