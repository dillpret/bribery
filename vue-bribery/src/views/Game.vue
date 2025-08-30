<template>
  <div class="game-container" :class="{ 'dark-mode': darkMode }">
    <header-component :game-id="gameId" />
    <status-bar :message="statusMessage" :timer="timerValue" :timer-active="timerActive" />
    
    <!-- Loading overlay -->
    <loading-spinner 
      v-if="isLoading" 
      :message="loadingMessage" 
      size="large" 
      overlay 
      fixed 
    />
    
    <!-- Game phases -->
    <game-lobby v-if="currentPhase === 'lobby'" />
    <prompt-phase v-else-if="currentPhase === 'prompt_selection'" />
    <submission-phase v-else-if="currentPhase === 'submission'" />
    <voting-phase v-else-if="currentPhase === 'voting'" />
    <scoreboard-phase v-else-if="currentPhase === 'results'" />
    <waiting-screen v-else-if="currentPhase === 'waiting'" />
    <connection-error v-else-if="currentPhase === 'error'" />
    
    <player-list-panel />
    
    <!-- Timer component at the bottom -->
    <Timer v-if="timerActive" :seconds="timerValue" class="game-timer" />
  </div>
</template>

<script>
import HeaderComponent from '@/components/layout/Header.vue'
import StatusBar from '@/components/layout/StatusBar.vue'
import PlayerListPanel from '@/components/common/PlayerListPanel.vue'
import GameLobby from '@/components/game/GameLobby.vue'
import PromptPhase from '@/components/game/PromptPhase.vue'
import SubmissionPhase from '@/components/game/SubmissionPhase.vue'
import VotingPhase from '@/components/game/VotingPhase.vue'
import ScoreboardPhase from '@/components/game/ScoreboardPhase.vue'
import WaitingScreen from '@/components/game/WaitingScreen.vue'
import ConnectionError from '@/components/game/ConnectionError.vue'
import { LoadingSpinner, Timer } from '@/components/common'

import socketService from '@/services/socket'
import notificationService from '@/services/notification'
import { mapState, mapActions, mapGetters } from 'vuex'
import { onBeforeUnmount, onMounted } from 'vue'

export default {
  name: 'Game',
  
  components: {
    HeaderComponent,
    StatusBar,
    GameLobby,
    PromptPhase,
    SubmissionPhase,
    VotingPhase,
    ScoreboardPhase,
    WaitingScreen,
    ConnectionError,
    PlayerListPanel,
    LoadingSpinner,
    Timer
  },
  
  computed: {
    ...mapState('auth', ['gameId', 'playerId', 'username', 'isAuthenticated']),
    ...mapState('game', ['phase']),
    ...mapState('ui', [
      'statusMessage', 
      'timerValue', 
      'timerActive', 
      'isLoading', 
      'loadingMessage',
      'darkMode'
    ]),
    ...mapGetters('ui', ['isAnyLoading']),
    
    currentPhase() {
      return this.phase || 'connecting'
    }
  },
  
  setup() {
    // Reconnection logic
    let reconnectionAttempts = 0
    const maxReconnectionAttempts = 5
    let reconnectionTimer = null
    
    const handleBeforeUnload = (event) => {
      // Notify server before user leaves
      socketService.leaveGame(true)
      
      // Show confirmation dialog in some browsers
      event.preventDefault()
      event.returnValue = ''
    }
    
    onMounted(() => {
      // Add event listener for page unload
      window.addEventListener('beforeunload', handleBeforeUnload)
      
      // Listen for socket disconnect events
      socketService.onDisconnect(() => {
        if (reconnectionAttempts < maxReconnectionAttempts) {
          reconnectionAttempts++
          
          // Exponential backoff for reconnection attempts
          const delay = Math.min(1000 * Math.pow(2, reconnectionAttempts - 1), 10000)
          
          notificationService.warning(`Connection lost. Reconnecting in ${delay/1000} seconds...`, {
            title: 'Connection Lost',
            duration: delay + 1000
          })
          
          reconnectionTimer = setTimeout(() => {
            socketService.reconnect()
          }, delay)
        } else {
          notificationService.error('Could not reconnect to the server. Please refresh the page.', {
            title: 'Connection Failed',
            duration: 0,
            dismissible: true
          })
        }
      })
      
      // Reset reconnection counter on successful connection
      socketService.onConnect(() => {
        reconnectionAttempts = 0
        if (reconnectionTimer) {
          clearTimeout(reconnectionTimer)
          reconnectionTimer = null
        }
        
        notificationService.success('Connected to server', {
          duration: 2000
        })
      })
    })
    
    onBeforeUnmount(() => {
      // Clean up event listeners
      window.removeEventListener('beforeunload', handleBeforeUnload)
      
      // Clear any pending timers
      if (reconnectionTimer) {
        clearTimeout(reconnectionTimer)
      }
      
      // Notify server we're leaving
      socketService.leaveGame()
    })
  },
  
  created() {
    // Initialize UI state
    this.initializeUI()
    
    // Initialize socket connection
    socketService.init()
    
    // Get game ID from route
    const gameId = this.$route.params.id
    
    // Show loading state
    this.showLoading('Connecting to game...')
    
    // Initialize auth from localStorage if available
    this.initAuth(gameId).then(success => {
      if (success) {
        // We have stored credentials, attempt to join with them
        socketService.joinGame(gameId, this.username, this.playerId)
          .then(() => {
            this.hideLoading()
          })
          .catch(error => {
            this.hideLoading()
            notificationService.error(error.message || 'Failed to join game', {
              title: 'Connection Error',
              duration: 8000
            })
            this.$router.push('/')
          })
      } else {
        // No stored credentials, redirect to home page
        this.hideLoading()
        this.$router.push('/')
      }
    })
  },
  
  methods: {
    ...mapActions('auth', ['initAuth']),
    ...mapActions('ui', ['showLoading', 'hideLoading', 'initializeUI'])
  }
}
</script>

<style scoped>
.game-container {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
  background-color: var(--background-color);
  transition: background-color 0.3s ease;
}

.game-container.dark-mode {
  --background-color: #121212;
  --text-color: #e0e0e0;
  --border-color: #333;
  background-color: var(--background-color);
  color: var(--text-color);
}

.game-timer {
  position: fixed;
  bottom: 1rem;
  right: 1rem;
  z-index: 100;
  font-size: 1.25rem;
  background-color: rgba(0, 0, 0, 0.75);
  color: white;
  padding: 0.5rem 1rem;
  border-radius: 2rem;
  box-shadow: 0 3px 6px rgba(0, 0, 0, 0.16);
}

@media (max-width: 768px) {
  .game-timer {
    bottom: 0.5rem;
    right: 0.5rem;
    font-size: 1rem;
    padding: 0.25rem 0.75rem;
  }
}
</style>
