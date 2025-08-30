<template>
  <div class="connection-error phase-container">
    <div class="error-content">
      <div class="error-icon">
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="64" height="64">
          <path fill="none" d="M0 0h24v24H0z"/>
          <path d="M12 22C6.477 22 2 17.523 2 12S6.477 2 12 2s10 4.477 10 10-4.477 10-10 10zm0-2a8 8 0 1 0 0-16 8 8 0 0 0 0 16zm-1-5h2v2h-2v-2zm0-8h2v6h-2V7z" fill="currentColor"/>
        </svg>
      </div>
      
      <h2>{{ title }}</h2>
      <p>{{ message }}</p>
      
      <div class="reconnection-status" v-if="reconnectAttempt > 0">
        <p>Reconnection attempt {{ reconnectAttempt }} of {{ maxReconnectAttempts }}</p>
        <div class="progress-bar">
          <div 
            class="progress-fill" 
            :style="{width: `${(reconnectAttempt / maxReconnectAttempts) * 100}%`}">
          </div>
        </div>
      </div>
      
      <div class="error-actions">
        <button @click="manualReconnect" class="reconnect-btn">
          Reconnect
        </button>
        <button @click="goToHome" class="home-btn">
          Return to Home
        </button>
      </div>
    </div>
  </div>
</template>

<script>
import socketService from '@/services/socket'

export default {
  name: 'ConnectionError',
  
  props: {
    title: {
      type: String,
      default: 'Connection Error'
    },
    message: {
      type: String,
      default: 'Unable to connect to the game server. Please check your internet connection and try again.'
    }
  },
  
  data() {
    return {
      reconnectAttempt: 0,
      maxReconnectAttempts: 5
    }
  },
  
  created() {
    // Listen for reconnection attempts
    socketService.socket.on('reconnect_attempt', this.handleReconnectAttempt)
  },
  
  beforeUnmount() {
    socketService.socket.off('reconnect_attempt', this.handleReconnectAttempt)
  },
  
  methods: {
    handleReconnectAttempt(attemptNumber) {
      this.reconnectAttempt = attemptNumber
    },
    
    manualReconnect() {
      // Reset reconnection attempt counter
      this.reconnectAttempt = 0
      
      // Attempt to reconnect socket
      if (socketService.socket.disconnected) {
        socketService.socket.connect()
      }
    },
    
    goToHome() {
      // Navigate back to home page
      this.$router.push('/')
    }
  }
}
</script>

<style scoped>
.connection-error {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: calc(100vh - var(--header-height) - var(--status-bar-height));
}

.error-content {
  text-align: center;
  background-color: white;
  padding: 32px;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  max-width: 500px;
}

.error-icon {
  color: var(--error-color);
  margin-bottom: 24px;
}

h2 {
  margin-bottom: 16px;
}

p {
  color: var(--text-secondary);
  margin-bottom: 16px;
}

.reconnection-status {
  margin: 24px 0;
}

.progress-bar {
  height: 8px;
  background-color: #eee;
  border-radius: 4px;
  overflow: hidden;
  margin-top: 8px;
}

.progress-fill {
  height: 100%;
  background-color: var(--primary-color);
  transition: width 0.3s ease;
}

.error-actions {
  display: flex;
  justify-content: center;
  gap: 16px;
  margin-top: 24px;
}

.reconnect-btn {
  background-color: var(--primary-color);
  color: white;
  border: none;
  border-radius: 4px;
  padding: 10px 24px;
  cursor: pointer;
}

.home-btn {
  background-color: #f5f5f5;
  color: var(--text-primary);
  border: 1px solid #ddd;
  border-radius: 4px;
  padding: 10px 24px;
  cursor: pointer;
}
</style>
