import { io } from 'socket.io-client'
import store from '@/store'

class SocketService {
  constructor() {
    this.socket = null
    this.reconnectAttempts = 0
    this.maxReconnectAttempts = 5
  }

  init() {
    this.socket = io(process.env.VUE_APP_API_URL, {
      transports: ['websocket', 'polling'],
      reconnection: true,
      reconnectionDelay: 1000,
      reconnectionDelayMax: 5000,
      reconnectionAttempts: this.maxReconnectAttempts
    })

    this._setupListeners()
    return this.socket
  }

  _setupListeners() {
    // Connection events
    this.socket.on('connect', () => {
      store.commit('ui/SET_CONNECTION', true)
      store.commit('ui/SET_STATUS', 'Connected')
      this.reconnectAttempts = 0
    })

    this.socket.on('disconnect', () => {
      store.commit('ui/SET_CONNECTION', false)
      store.commit('ui/SET_STATUS', 'Disconnected')
    })

    this.socket.on('reconnect_attempt', (attempt) => {
      this.reconnectAttempts = attempt
      store.commit('ui/SET_STATUS', `Reconnecting (${attempt}/${this.maxReconnectAttempts})...`)
    })

    // Game events
    this.socket.on('joined_game', (data) => {
      store.commit('auth/SET_PLAYER_ID', data.player_id)
      store.commit('auth/SET_USERNAME', data.username)
      store.commit('auth/SET_HOST', data.is_host)
      store.commit('auth/SET_AUTHENTICATED', true)
      store.dispatch('auth/saveAuth')
      
      store.dispatch('game/updateGameState', {
        phase: data.game_state,
        currentRound: data.current_round,
        totalRounds: data.total_rounds
      })
    })

    // More event handlers will be added here
  }

  // Socket API methods
  joinGame(gameId, username, playerId) {
    this.socket.emit('join_game', {
      game_id: gameId,
      username,
      player_id: playerId
    })
  }

  createGame(username, settings) {
    this.socket.emit('create_game', {
      username,
      settings
    })
  }

  // Additional methods for other socket events
}

export default new SocketService()
