<template>
  <div class="submission-phase phase-container">
    <h2>Submit Your Bribe</h2>
    <p class="phase-description">Create a bribe for your target player based on their prompt</p>
    
    <div v-if="targetInfo" class="target-info">
      <div class="target-prompt">
        <h3>Your Target: <span class="target-name">{{ targetInfo.username }}</span></h3>
        <div class="prompt-box">
          <p>{{ targetInfo.prompt }}</p>
        </div>
      </div>
      
      <div class="submission-form">
        <div class="submission-type-selector">
          <label>
            <input type="radio" v-model="submissionType" value="text" :disabled="submitted">
            Text
          </label>
          <label>
            <input type="radio" v-model="submissionType" value="image" :disabled="submitted">
            Image
          </label>
        </div>
        
        <div v-if="submissionType === 'text'" class="text-submission">
          <label for="bribe-text">Your Bribe:</label>
          <textarea 
            id="bribe-text" 
            v-model="textSubmission" 
            :disabled="submitted"
            placeholder="Write something creative to bribe your target..."
            rows="5"
            maxlength="500">
          </textarea>
          <div class="character-counter">{{ textSubmission.length }}/500</div>
        </div>
        
        <div v-if="submissionType === 'image'" class="image-submission">
          <ImageUploader 
            v-model:image="imageData" 
            :maxSize="2 * 1024 * 1024" 
            @upload-error="handleUploadError" 
            :disabled="submitted" 
          />
        </div>
        
        <Button 
          @click="submitBribe" 
          :disabled="!isValid || submitted || isProcessing"
          :loading="isProcessing"
          variant="primary"
          block
        >
          {{ submitted ? 'Submitted' : 'Submit Bribe' }}
        </Button>
      </div>
    </div>
    
    <div v-else class="no-target-message">
      <p>Waiting for targets to be assigned...</p>
      <LoadingSpinner size="medium" />
    </div>
    
    <div class="waiting-message" v-if="submitted">
      <p>Waiting for other players to submit their bribes...</p>
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
import notificationService from '@/services/notification'
import { ImageUploader, Button, LoadingSpinner } from '@/components/common'

export default {
  name: 'SubmissionPhase',
  
  components: {
    ImageUploader,
    Button,
    LoadingSpinner
  },
  
  data() {
    return {
      submissionType: 'text',
      textSubmission: '',
      imageData: null,
      isProcessing: false,
      submitted: false
    }
  },
  
  computed: {
    ...mapState('auth', ['playerId']),
    ...mapState('game', ['currentTargets', 'players', 'currentRound', 'totalRounds']),
    
    targetInfo() {
      // Find the target assigned to the current player
      return this.currentTargets.find(target => target.player_id === this.playerId)
    },
    
    hasImage() {
      return !!this.imageData
    },
    
    isValid() {
      if (this.submissionType === 'text') {
        return this.textSubmission.trim().length > 0
      } else if (this.submissionType === 'image') {
        return this.hasImage
      }
      return false
    },
    
    submittedCount() {
      return this.players.filter(player => player.submitted).length
    },
    
    totalPlayers() {
      return this.players.length
    }
  },
  
  created() {
    // Listen for submission updates
    socketService.socket.on('submission_received', this.handleSubmissionReceived)
    socketService.socket.on('all_submissions_received', this.handleAllSubmissionsReceived)
  },
  
  beforeUnmount() {
    socketService.socket.off('submission_received', this.handleSubmissionReceived)
    socketService.socket.off('all_submissions_received', this.handleAllSubmissionsReceived)
  },
  
  methods: {
    handleUploadError(error) {
      notificationService.error(error, {
        title: 'Upload Error'
      });
    },
    
    submitBribe() {
      if (!this.isValid || this.submitted || !this.targetInfo) return
      
      this.isProcessing = true;
      
      let submissionData = {
        type: this.submissionType,
        target_id: this.targetInfo.target_id
      }
      
      if (this.submissionType === 'text') {
        submissionData.content = this.textSubmission.trim()
      } else if (this.submissionType === 'image') {
        submissionData.content = this.imageData
      }
      
      socketService.socket.emit('submit_bribe', submissionData, (response) => {
        this.isProcessing = false;
        
        if (response.success) {
          this.submitted = true;
          notificationService.success('Bribe submitted successfully!', {
            duration: 3000
          });
        } else {
          notificationService.error(response.error || 'Failed to submit bribe', {
            title: 'Submission Error'
          });
        }
      });
    },
    
    handleSubmissionReceived(data) {
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
    },
    
    handleAllSubmissionsReceived() {
      // All submissions are in, this will trigger a phase change
      // The Game.vue component will handle the phase change
      notificationService.info('All bribes received! Moving to voting phase...', {
        duration: 3000
      });
    }
  }
}
</script>

<style scoped>
.submission-phase {
  max-width: 800px;
  margin: 0 auto;
  padding: 24px;
}

.phase-description {
  margin-bottom: 24px;
  color: var(--text-secondary);
}

.target-info {
  background-color: white;
  padding: 24px;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  margin-bottom: 24px;
}

.target-prompt {
  margin-bottom: 24px;
}

.target-name {
  color: var(--primary-color);
}

.prompt-box {
  background-color: #f5f5f5;
  padding: 16px;
  border-radius: 8px;
  margin-top: 8px;
  font-style: italic;
}

.submission-form {
  border-top: 1px solid #eee;
  padding-top: 24px;
}

.submission-type-selector {
  display: flex;
  gap: 24px;
  margin-bottom: 16px;
}

.submission-type-selector label {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
}

label {
  display: block;
  margin-bottom: 8px;
  font-weight: 500;
}

textarea {
  width: 100%;
  padding: 12px;
  border: 1px solid #ccc;
  border-radius: 4px;
  resize: vertical;
  font-family: inherit;
  transition: border-color 0.2s ease;
}

textarea:focus {
  outline: none;
  border-color: var(--primary-color);
  box-shadow: 0 0 0 3px rgba(0, 128, 255, 0.1);
}

.character-counter {
  text-align: right;
  font-size: 0.8rem;
  color: var(--text-secondary);
  margin-top: 4px;
}

.text-submission {
  margin-bottom: 20px;
}

.image-submission {
  margin-bottom: 20px;
}

.no-target-message, .waiting-message {
  text-align: center;
  padding: 24px;
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 16px;
}

.progress-container {
  margin-top: 16px;
  width: 100%;
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

/* Dark mode support */
:global(.dark-mode) .target-info,
:global(.dark-mode) .no-target-message,
:global(.dark-mode) .waiting-message {
  background-color: #2a2a2a;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
}

:global(.dark-mode) .prompt-box {
  background-color: #3a3a3a;
}

:global(.dark-mode) textarea {
  background-color: #333;
  color: #e0e0e0;
  border-color: #555;
}

:global(.dark-mode) .progress-bar {
  background-color: #444;
}

/* Responsive adjustments */
@media (max-width: 768px) {
  .submission-phase {
    padding: 16px;
  }
  
  .target-info {
    padding: 16px;
  }
}
</style>
