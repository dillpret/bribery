<template>
  <div class="waiting-screen phase-container">
    <div class="waiting-content">
      <div class="waiting-spinner"></div>
      <h2>{{ title }}</h2>
      <p>{{ message || defaultMessage }}</p>
      
      <div class="game-info" v-if="showGameInfo">
        <p>Round {{ currentRound }} of {{ totalRounds }}</p>
        <p>Current phase: {{ formatGamePhase(phase) }}</p>
      </div>
    </div>
  </div>
</template>

<script>
import { mapState } from 'vuex'

export default {
  name: 'WaitingScreen',
  
  props: {
    title: {
      type: String,
      default: 'Please Wait'
    },
    message: {
      type: String,
      default: ''
    },
    showGameInfo: {
      type: Boolean,
      default: true
    }
  },
  
  computed: {
    ...mapState('game', ['currentRound', 'totalRounds', 'phase']),
    
    defaultMessage() {
      return 'Loading game data...'
    }
  },
  
  methods: {
    formatGamePhase(phase) {
      const phaseMap = {
        'lobby': 'Game Lobby',
        'prompt_selection': 'Prompt Selection',
        'submission': 'Submission',
        'voting': 'Voting',
        'results': 'Round Results',
        'game_over': 'Game Over',
        'waiting': 'Waiting',
        'connecting': 'Connecting'
      }
      
      return phaseMap[phase] || 'Unknown'
    }
  }
}
</script>

<style scoped>
.waiting-screen {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: calc(100vh - var(--header-height) - var(--status-bar-height));
}

.waiting-content {
  text-align: center;
  background-color: white;
  padding: 32px;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  max-width: 500px;
}

.waiting-spinner {
  width: 50px;
  height: 50px;
  border: 5px solid #f3f3f3;
  border-top: 5px solid var(--primary-color);
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin: 0 auto 24px auto;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

h2 {
  margin-bottom: 16px;
}

p {
  color: var(--text-secondary);
  margin-bottom: 8px;
}

.game-info {
  margin-top: 24px;
  padding-top: 16px;
  border-top: 1px solid #eee;
}
</style>
