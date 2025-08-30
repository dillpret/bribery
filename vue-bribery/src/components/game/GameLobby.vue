<template>
  <div class="game-lobby phase-container">
    <h2>Game Lobby</h2>
    <div class="lobby-content">
      <div class="game-info-panel">
        <div class="game-id-display">
          <h3>Game ID</h3>
          <div class="id-container">
            <span class="game-id">{{ gameId }}</span>
            <button @click="copyGameId" class="copy-btn">Copy</button>
          </div>
          <p class="help-text">Share this ID with your friends so they can join your game</p>
        </div>

        <div class="game-settings" v-if="isHost">
          <h3>Game Settings</h3>
          <div class="setting-item">
            <label for="rounds-setting">Rounds:</label>
            <input type="number" id="rounds-setting" v-model.number="settings.rounds" min="1" max="10">
          </div>
          <button @click="updateSettings" class="btn-primary">Update Settings</button>
        </div>
      </div>

      <div class="player-status-panel">
        <h3>Players ({{ players.length }})</h3>
        <ul class="lobby-player-list">
          <li v-for="player in players" :key="player.player_id" class="lobby-player-item">
            {{ player.username }}
            <span v-if="player.is_host" class="host-indicator">(Host)</span>
          </li>
        </ul>
      </div>
    </div>

    <div class="lobby-actions">
      <button v-if="isHost" @click="startGame" class="start-game-btn" :disabled="players.length < 2">
        Start Game
      </button>
      <p v-if="isHost && players.length < 2" class="help-text">
        You need at least 2 players to start the game
      </p>
      <p v-if="!isHost" class="help-text">
        Waiting for the host to start the game...
      </p>
    </div>
  </div>
</template>

<script>
import { mapState } from 'vuex'
import socketService from '@/services/socket'
import { copyToClipboard } from '@/utils/helpers'

export default {
  name: 'GameLobby',

  data() {
    return {
      settings: {
        rounds: 3
      }
    }
  },

  computed: {
    ...mapState('auth', ['gameId', 'isHost']),
    ...mapState('game', ['players'])
  },

  methods: {
    copyGameId() {
      copyToClipboard(this.gameId)
        .then(() => {
          // Show a notification or toast
          this.$store.commit('ui/SET_STATUS', 'Game ID copied to clipboard')
        })
        .catch(() => {
          this.$store.commit('ui/SET_STATUS', 'Failed to copy Game ID')
        })
    },

    updateSettings() {
      socketService.socket.emit('update_settings', {
        rounds: this.settings.rounds
      })
    },

    startGame() {
      if (this.players.length < 2) return
      socketService.socket.emit('start_game')
    }
  }
}
</script>

<style scoped>
.game-lobby {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}

.lobby-content {
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  gap: 32px;
  width: 100%;
  max-width: 900px;
}

.game-info-panel, .player-status-panel {
  background-color: white;
  padding: 24px;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  min-width: 300px;
  margin-bottom: 32px;
}

.game-id-display {
  margin-bottom: 24px;
}

.id-container {
  display: flex;
  align-items: center;
  margin: 8px 0;
}

.game-id {
  font-size: 1.5rem;
  font-weight: bold;
  font-family: monospace;
  margin-right: 8px;
  padding: 4px 8px;
  background-color: #f5f5f5;
  border-radius: 4px;
}

.copy-btn {
  padding: 4px 8px;
  font-size: 0.9rem;
}

.setting-item {
  margin-bottom: 16px;
}

.lobby-player-list {
  list-style: none;
}

.lobby-player-item {
  padding: 8px 0;
  border-bottom: 1px solid #eee;
}

.host-indicator {
  font-size: 0.8rem;
  color: var(--primary-color);
  margin-left: 8px;
  font-weight: bold;
}

.lobby-actions {
  margin-top: 32px;
  text-align: center;
}

.start-game-btn {
  padding: 12px 32px;
  font-size: 1.2rem;
}

.help-text {
  font-size: 0.9rem;
  color: var(--text-secondary);
  margin-top: 8px;
}
</style>
