<template>
  <div class="voting-phase phase-container">
    <h2>Vote for the Best Bribe</h2>
    <p class="phase-description">Choose your favorite bribe from the submissions</p>
    
    <div class="target-info">
      <h3>Prompt: <span class="prompt-text">{{ currentPrompt }}</span></h3>
    </div>
    
    <div class="submissions-container">
      <div v-if="submissions.length === 0" class="no-submissions-message">
        <p>Waiting for submissions to be loaded...</p>
      </div>
      
      <div v-else class="submissions-grid">
        <div 
          v-for="(submission, index) in submissions" 
          :key="submission.id" 
          :class="['submission-card', { 'selected': selectedSubmission === submission.id }]"
          @click="selectSubmission(submission.id)">
          
          <div class="submission-number">#{{ index + 1 }}</div>
          
          <div class="submission-content">
            <div v-if="submission.type === 'text'" class="text-submission">
              <p>{{ submission.content }}</p>
            </div>
            
            <div v-if="submission.type === 'image'" class="image-submission">
              <img :src="submission.content" alt="Bribe submission">
            </div>
          </div>
          
          <div class="submission-selection">
            <div class="selection-indicator" v-if="selectedSubmission === submission.id">
              Selected
            </div>
            <button 
              v-else
              class="select-btn" 
              @click.stop="selectSubmission(submission.id)"
              :disabled="submitted">
              Select
            </button>
          </div>
        </div>
      </div>
    </div>
    
    <div class="voting-actions">
      <button 
        class="submit-vote-btn" 
        @click="submitVote" 
        :disabled="!selectedSubmission || submitted">
        {{ submitted ? 'Vote Submitted' : 'Submit Vote' }}
      </button>
    </div>
    
    <div class="waiting-message" v-if="submitted">
      <p>Waiting for other players to vote...</p>
      <div class="progress-container">
        <div class="progress-label">
          {{ votedCount }} of {{ totalPlayers }} players have voted
        </div>
        <div class="progress-bar">
          <div 
            class="progress-fill" 
            :style="{width: `${(votedCount / totalPlayers) * 100}%`}">
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
  name: 'VotingPhase',
  
  data() {
    return {
      currentPrompt: '',
      submissions: [],
      selectedSubmission: null,
      submitted: false
    }
  },
  
  computed: {
    ...mapState('auth', ['playerId']),
    ...mapState('game', ['players', 'currentRound', 'totalRounds']),
    
    votedCount() {
      return this.players.filter(player => player.voted).length
    },
    
    totalPlayers() {
      return this.players.length
    }
  },
  
  created() {
    // Listen for voting phase updates
    socketService.socket.on('voting_phase_started', this.handleVotingPhase)
    socketService.socket.on('vote_submitted', this.handleVoteSubmitted)
    socketService.socket.on('all_votes_received', this.handleAllVotesReceived)
    
    // Request voting data when component is created
    socketService.socket.emit('request_voting_data')
  },
  
  beforeUnmount() {
    socketService.socket.off('voting_phase_started', this.handleVotingPhase)
    socketService.socket.off('vote_submitted', this.handleVoteSubmitted)
    socketService.socket.off('all_votes_received', this.handleAllVotesReceived)
  },
  
  methods: {
    handleVotingPhase(data) {
      this.currentPrompt = data.prompt
      this.submissions = data.submissions.map(submission => ({
        ...submission,
        id: submission.submission_id
      }))
      
      // Filter out the player's own submission if it exists
      this.submissions = this.submissions.filter(sub => sub.player_id !== this.playerId)
      
      // Reset vote state
      this.selectedSubmission = null
      this.submitted = false
    },
    
    selectSubmission(submissionId) {
      if (!this.submitted) {
        this.selectedSubmission = submissionId
      }
    },
    
    submitVote() {
      if (!this.selectedSubmission || this.submitted) return
      
      socketService.socket.emit('submit_vote', {
        submission_id: this.selectedSubmission
      })
      
      this.submitted = true
      this.$store.commit('game/SET_SELECTED_VOTE', this.selectedSubmission)
    },
    
    handleVoteSubmitted(data) {
      // Update the player's voted status
      const playerIndex = this.players.findIndex(p => p.player_id === data.player_id)
      if (playerIndex !== -1) {
        const updatedPlayers = [...this.players]
        updatedPlayers[playerIndex] = {
          ...updatedPlayers[playerIndex],
          voted: true
        }
        this.$store.commit('game/SET_PLAYERS', updatedPlayers)
      }
    },
    
    handleAllVotesReceived() {
      // All votes are in, this will trigger a phase change
      // The Game.vue component will handle the phase change
    }
  }
}
</script>

<style scoped>
.voting-phase {
  max-width: 900px;
  margin: 0 auto;
  padding: 24px;
}

.phase-description {
  margin-bottom: 24px;
  color: var(--text-secondary);
}

.target-info {
  background-color: white;
  padding: 16px;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  margin-bottom: 24px;
  text-align: center;
}

.prompt-text {
  font-style: italic;
}

.submissions-container {
  margin-bottom: 24px;
}

.no-submissions-message {
  text-align: center;
  padding: 32px;
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.submissions-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 16px;
}

.submission-card {
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  overflow: hidden;
  transition: all 0.3s ease;
  position: relative;
  cursor: pointer;
}

.submission-card.selected {
  box-shadow: 0 0 0 3px var(--primary-color);
}

.submission-number {
  position: absolute;
  top: 8px;
  left: 8px;
  background-color: var(--primary-color);
  color: white;
  border-radius: 50%;
  width: 24px;
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.8rem;
  font-weight: bold;
}

.submission-content {
  padding: 24px;
  min-height: 150px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.text-submission {
  word-break: break-word;
}

.image-submission img {
  max-width: 100%;
  max-height: 200px;
  object-fit: contain;
}

.submission-selection {
  padding: 12px;
  background-color: #f5f5f5;
  border-top: 1px solid #eee;
  text-align: center;
}

.selection-indicator {
  color: var(--primary-color);
  font-weight: bold;
}

.select-btn {
  background-color: var(--primary-color);
  color: white;
  border: none;
  border-radius: 4px;
  padding: 8px 16px;
  cursor: pointer;
}

.voting-actions {
  display: flex;
  justify-content: center;
}

.submit-vote-btn {
  background-color: var(--primary-color);
  color: white;
  border: none;
  border-radius: 4px;
  padding: 12px 32px;
  font-size: 1.1rem;
  cursor: pointer;
}

.submit-vote-btn:disabled {
  background-color: #ccc;
  cursor: not-allowed;
}

.waiting-message {
  margin-top: 24px;
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

@media (max-width: 768px) {
  .submissions-grid {
    grid-template-columns: 1fr;
  }
}
</style>
