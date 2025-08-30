<template>
  <div class="prompt-phase phase-container">
    <h2>Prompt Selection</h2>
    <p class="phase-description">Select a target player and write a prompt for them</p>
    
    <div class="prompt-selection-form">
      <div class="target-selection">
        <label for="target-player">Select a player to target:</label>
        <select id="target-player" v-model="targetPlayerId" :disabled="submitted">
          <option disabled value="">Choose a player</option>
          <option 
            v-for="player in availableTargets" 
            :key="player.player_id" 
            :value="player.player_id">
            {{ player.username }}
          </option>
        </select>
      </div>
      
      <div class="prompt-input">
        <label for="prompt-text">Write a prompt:</label>
        <textarea 
          id="prompt-text" 
          v-model="promptText"
          placeholder="Enter a prompt for your target to draw..."
          :disabled="submitted"
          rows="3"
          maxlength="200">
        </textarea>
        <div class="character-counter">{{ promptText.length }}/200</div>
      </div>
      
      <button 
        @click="submitPrompt" 
        class="submit-btn" 
        :disabled="!isValid || submitted">
        {{ submitted ? 'Submitted' : 'Submit Prompt' }}
      </button>
    </div>
    
    <div class="waiting-message" v-if="submitted">
      <p>Waiting for other players to submit their prompts...</p>
      <div class="progress-container">
        <div class="progress-label">
          {{ submittedCount }} of {{ totalPlayers }} players have submitted
        </div>
        <div class="progress-bar">
          <div 
            class="progress-fill" 
            :style="{width: `${(submittedCount / totalPlayers) * 100}%`}">
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { mapState } from 'vuex'
import socketService from '@/services/socket'

export default {
  name: 'PromptPhase',
  
  data() {
    return {
      targetPlayerId: '',
      promptText: '',
      submitted: false
    }
  },
  
  computed: {
    ...mapState('auth', ['playerId']),
    ...mapState('game', ['players']),
    
    availableTargets() {
      // Filter out the current player
      return this.players.filter(player => player.player_id !== this.playerId)
    },
    
    isValid() {
      return this.targetPlayerId && this.promptText.trim().length > 0
    },
    
    submittedCount() {
      return this.players.filter(player => player.submitted).length
    },
    
    totalPlayers() {
      return this.players.length
    }
  },
  
  created() {
    // Listen for prompt submission updates
    socketService.socket.on('prompt_submitted', this.handlePromptSubmitted)
  },
  
  beforeUnmount() {
    socketService.socket.off('prompt_submitted', this.handlePromptSubmitted)
  },
  
  methods: {
    submitPrompt() {
      if (!this.isValid || this.submitted) return
      
      socketService.socket.emit('submit_prompt', {
        target_player_id: this.targetPlayerId,
        prompt_text: this.promptText.trim()
      })
      
      this.submitted = true
    },
    
    handlePromptSubmitted(data) {
      // Update the player's submitted status
      const playerIndex = this.players.findIndex(p => p.player_id === data.player_id)
      if (playerIndex !== -1) {
        const updatedPlayers = [...this.players]
        updatedPlayers[playerIndex] = {
          ...updatedPlayers[playerIndex],
          submitted: true
        }
        this.$store.commit('game/SET_PLAYERS', updatedPlayers)
      }
    }
  }
}
</script>

<style scoped>
.prompt-phase {
  max-width: 600px;
  margin: 0 auto;
  padding: 24px;
}

.phase-description {
  margin-bottom: 24px;
  color: var(--text-secondary);
}

.prompt-selection-form {
  background-color: white;
  padding: 24px;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  margin-bottom: 24px;
}

.target-selection, .prompt-input {
  margin-bottom: 16px;
}

label {
  display: block;
  margin-bottom: 8px;
  font-weight: 500;
}

select, textarea {
  width: 100%;
  padding: 8px;
  border: 1px solid #ccc;
  border-radius: 4px;
}

textarea {
  resize: vertical;
  min-height: 100px;
}

.character-counter {
  text-align: right;
  font-size: 0.8rem;
  color: var(--text-secondary);
  margin-top: 4px;
}

.submit-btn {
  width: 100%;
  padding: 12px;
  margin-top: 16px;
}

.waiting-message {
  text-align: center;
  padding: 16px;
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.progress-container {
  margin-top: 16px;
}

.progress-label {
  margin-bottom: 8px;
  font-size: 0.9rem;
}

.progress-bar {
  height: 8px;
  background-color: #eee;
  border-radius: 4px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background-color: var(--primary-color);
  transition: width 0.3s ease;
}
</style>
