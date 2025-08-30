<template>
  <div :class="['player-list-panel', { visible: isVisible }]">
    <button class="player-list-toggle" @click="togglePanel">
      <span v-if="isVisible">Hide Players</span>
      <span v-else>Show Players</span>
    </button>
    
    <div class="player-list-content">
      <h3>Players ({{ players.length }})</h3>
      <ul class="player-score-list">
        <li v-for="player in sortedPlayers" :key="player.player_id" class="player-score-item">
          <div class="player-info">
            <span :class="['player-status', player.connected ? 'online' : 'offline']"></span>
            <span class="player-name">{{ player.username }}</span>
            <span v-if="player.is_host" class="host-badge">HOST</span>
            <span 
              v-if="showSubmissionStatus && player.hasOwnProperty('submitted')" 
              :class="['submission-status', player.submitted ? 'submitted' : 'pending']"
              :title="player.submitted ? 'Submitted' : 'Waiting for submission'">
              {{ player.submitted ? '✓' : '⋯' }}
            </span>
          </div>
          
          <div class="player-score">{{ player.score }}</div>
          
          <button 
            v-if="isHost && !player.is_host" 
            class="kick-button" 
            @click="showKickConfirmation(player)">
            Kick
          </button>
        </li>
      </ul>
    </div>
    
    <!-- Kick confirmation modal -->
    <div v-if="kickTargetPlayer" class="modal-overlay">
      <div class="modal-content">
        <h3>Kick Player</h3>
        <p>Are you sure you want to kick <strong>{{ kickTargetPlayer.username }}</strong>?</p>
        <div class="modal-actions">
          <button @click="kickPlayer" class="btn-danger">Kick Player</button>
          <button @click="kickTargetPlayer = null" class="btn-secondary">Cancel</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { mapState } from 'vuex'
import socketService from '@/services/socket'

export default {
  name: 'PlayerListPanel',
  
  data() {
    return {
      isVisible: false,
      kickTargetPlayer: null
    }
  },
  
  computed: {
    ...mapState('auth', ['playerId', 'isHost']),
    ...mapState('game', ['players', 'phase']),
    
    sortedPlayers() {
      return [...this.players].sort((a, b) => {
        // Host first
        if (a.is_host !== b.is_host) return a.is_host ? -1 : 1
        
        // Then by score (descending)
        if (a.score !== b.score) return b.score - a.score
        
        // Then by name
        return a.username.localeCompare(b.username)
      })
    },
    
    showSubmissionStatus() {
      return ['submission', 'voting'].includes(this.phase)
    }
  },
  
  methods: {
    togglePanel() {
      this.isVisible = !this.isVisible
    },
    
    showKickConfirmation(player) {
      this.kickTargetPlayer = player
    },
    
    kickPlayer() {
      if (!this.kickTargetPlayer) return
      
      socketService.socket.emit('kick_player', {
        player_id: this.kickTargetPlayer.player_id
      })
      
      this.kickTargetPlayer = null
    }
  }
}
</script>

<style scoped>
.player-list-panel {
  position: fixed;
  right: 0;
  top: var(--header-height);
  height: calc(100vh - var(--header-height));
  width: 250px;
  background-color: white;
  box-shadow: -2px 0 5px rgba(0, 0, 0, 0.1);
  transform: translateX(100%);
  transition: transform 0.3s ease;
  z-index: 100;
}

.player-list-panel.visible {
  transform: translateX(0);
}

.player-list-toggle {
  position: absolute;
  left: -80px;
  top: 20px;
  width: 80px;
  border-radius: 4px 0 0 4px;
}

.player-list-content {
  padding: 16px;
  overflow-y: auto;
  height: 100%;
}

.player-score-list {
  list-style: none;
  margin-top: 16px;
}

.player-score-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 0;
  border-bottom: 1px solid #eee;
}

.player-info {
  display: flex;
  align-items: center;
  flex: 1;
}

.player-status {
  display: inline-block;
  width: 8px;
  height: 8px;
  border-radius: 50%;
  margin-right: 8px;
}

.player-status.online {
  background-color: var(--success-color);
}

.player-status.offline {
  background-color: var(--error-color);
}

.player-name {
  font-weight: 500;
  max-width: 120px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.host-badge {
  font-size: 0.7rem;
  background-color: var(--primary-color);
  color: white;
  padding: 2px 4px;
  border-radius: 2px;
  margin-left: 4px;
}

.player-score {
  font-weight: bold;
  margin: 0 8px;
}

.kick-button {
  font-size: 0.8rem;
  padding: 2px 8px;
  background-color: var(--error-color);
}

.submission-status {
  margin-left: 8px;
  font-size: 1.2rem;
}

.submission-status.submitted {
  color: var(--success-color);
}

.submission-status.pending {
  color: var(--text-secondary);
}

.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 200;
}

.modal-content {
  background-color: white;
  padding: 24px;
  border-radius: 8px;
  width: 300px;
}

.modal-actions {
  display: flex;
  justify-content: space-between;
  margin-top: 24px;
}

.btn-danger {
  background-color: var(--error-color);
}

.btn-secondary {
  background-color: #ccc;
}
</style>
