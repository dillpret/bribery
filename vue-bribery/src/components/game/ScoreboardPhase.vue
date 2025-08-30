<template>
  <div class="scoreboard-phase phase-container">
    <h2>Round Results</h2>
    <p class="phase-description">
      Round {{ currentRound }} of {{ totalRounds }} completed
    </p>
    
    <div class="round-results">
      <div class="round-prompt">
        <h3>Prompt:</h3>
        <div class="prompt-text">{{ roundData.prompt }}</div>
      </div>
      
      <div class="winning-submission" v-if="winningSubmission">
        <h3>Winning Bribe:</h3>
        <div class="winner-card">
          <div class="winner-header">
            <div class="winner-name">{{ winningSubmission.username }}</div>
            <div class="winner-points">+{{ winningSubmission.points }} points</div>
          </div>
          
          <div class="winner-content">
            <div v-if="winningSubmission.type === 'text'" class="text-submission">
              <p>{{ winningSubmission.content }}</p>
            </div>
            
            <div v-if="winningSubmission.type === 'image'" class="image-submission">
              <img :src="winningSubmission.content" alt="Winning submission">
            </div>
          </div>
          
          <div class="vote-count">
            {{ winningSubmission.votes }} {{ winningSubmission.votes === 1 ? 'vote' : 'votes' }}
          </div>
        </div>
      </div>
      
      <div class="other-submissions" v-if="otherSubmissions.length > 0">
        <h3>Other Submissions:</h3>
        <div class="submissions-grid">
          <div 
            v-for="submission in otherSubmissions" 
            :key="submission.id" 
            class="submission-card">
            
            <div class="submission-header">
              <div class="submission-name">{{ submission.username }}</div>
              <div 
                v-if="submission.points > 0" 
                class="submission-points">+{{ submission.points }} points</div>
            </div>
            
            <div class="submission-content">
              <div v-if="submission.type === 'text'" class="text-submission">
                <p>{{ submission.content }}</p>
              </div>
              
              <div v-if="submission.type === 'image'" class="image-submission">
                <img :src="submission.content" alt="Submission">
              </div>
            </div>
            
            <div class="vote-count">
              {{ submission.votes }} {{ submission.votes === 1 ? 'vote' : 'votes' }}
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <div class="scoreboard">
      <h3>Current Standings</h3>
      <table class="score-table">
        <thead>
          <tr>
            <th>Rank</th>
            <th>Player</th>
            <th>Score</th>
          </tr>
        </thead>
        <tbody>
          <tr 
            v-for="(player, index) in sortedPlayers" 
            :key="player.player_id"
            :class="{ 'current-player': player.player_id === playerId }">
            <td class="rank">{{ index + 1 }}</td>
            <td class="player-name">
              {{ player.username }}
              <span v-if="player.is_host" class="host-badge">HOST</span>
            </td>
            <td class="player-score">{{ player.score }}</td>
          </tr>
        </tbody>
      </table>
    </div>
    
    <div class="round-actions" v-if="isHost && !isLastRound">
      <button @click="startNextRound" class="next-round-btn">
        Start Next Round
      </button>
    </div>
    
    <div class="round-actions" v-if="isHost && isLastRound">
      <button @click="endGame" class="end-game-btn">
        End Game
      </button>
    </div>
    
    <div class="round-actions" v-if="!isHost">
      <p class="waiting-message">
        {{ isLastRound ? 'Waiting for host to end the game...' : 'Waiting for host to start the next round...' }}
      </p>
    </div>
  </div>
</template>

<script>
import { mapState } from 'vuex'
import socketService from '@/services/socket'

export default {
  name: 'ScoreboardPhase',
  
  data() {
    return {
      roundData: {
        prompt: '',
        submissions: []
      }
    }
  },
  
  computed: {
    ...mapState('auth', ['playerId', 'isHost']),
    ...mapState('game', ['players', 'currentRound', 'totalRounds']),
    
    sortedPlayers() {
      return [...this.players].sort((a, b) => b.score - a.score)
    },
    
    winningSubmission() {
      if (!this.roundData.submissions || this.roundData.submissions.length === 0) return null
      
      // Find the submission with the most votes
      return this.roundData.submissions.reduce((winner, current) => {
        return (current.votes > winner.votes) ? current : winner
      }, this.roundData.submissions[0])
    },
    
    otherSubmissions() {
      if (!this.roundData.submissions || this.roundData.submissions.length <= 1) return []
      
      // Return all submissions except the winning one
      return this.roundData.submissions
        .filter(sub => sub.id !== this.winningSubmission.id)
        .sort((a, b) => b.votes - a.votes)
    },
    
    isLastRound() {
      return this.currentRound >= this.totalRounds
    }
  },
  
  created() {
    // Listen for round results updates
    socketService.socket.on('round_results', this.handleRoundResults)
  },
  
  beforeUnmount() {
    socketService.socket.off('round_results', this.handleRoundResults)
  },
  
  methods: {
    handleRoundResults(data) {
      this.roundData = {
        prompt: data.prompt,
        submissions: data.submissions.map(sub => ({
          ...sub,
          id: sub.submission_id
        }))
      }
    },
    
    startNextRound() {
      if (!this.isHost || this.isLastRound) return
      
      socketService.socket.emit('next_round')
    },
    
    endGame() {
      if (!this.isHost) return
      
      socketService.socket.emit('end_game')
    }
  }
}
</script>

<style scoped>
.scoreboard-phase {
  max-width: 900px;
  margin: 0 auto;
  padding: 24px;
}

.phase-description {
  margin-bottom: 24px;
  color: var(--text-secondary);
  text-align: center;
}

.round-results {
  background-color: white;
  padding: 24px;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  margin-bottom: 32px;
}

.round-prompt {
  margin-bottom: 24px;
}

.prompt-text {
  background-color: #f5f5f5;
  padding: 16px;
  border-radius: 8px;
  font-style: italic;
  margin-top: 8px;
}

.winning-submission {
  margin-bottom: 32px;
}

.winner-card {
  background-color: #fff9e6;
  border: 2px solid #ffd700;
  border-radius: 8px;
  overflow: hidden;
  margin-top: 8px;
}

.winner-header {
  background-color: #ffd700;
  color: #333;
  padding: 12px 16px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.winner-name {
  font-weight: bold;
  font-size: 1.1rem;
}

.winner-points {
  font-weight: bold;
  color: #2ecc71;
}

.winner-content {
  padding: 24px;
}

.text-submission {
  word-break: break-word;
}

.image-submission img {
  max-width: 100%;
  max-height: 300px;
  object-fit: contain;
  display: block;
  margin: 0 auto;
}

.vote-count {
  text-align: center;
  padding: 8px;
  background-color: rgba(0, 0, 0, 0.05);
  font-size: 0.9rem;
}

.other-submissions h3 {
  margin-bottom: 16px;
}

.submissions-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
  gap: 16px;
}

.submission-card {
  background-color: white;
  border: 1px solid #eee;
  border-radius: 8px;
  overflow: hidden;
}

.submission-header {
  background-color: #f5f5f5;
  padding: 8px 12px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.submission-name {
  font-weight: 500;
}

.submission-points {
  color: #2ecc71;
  font-weight: 500;
}

.submission-content {
  padding: 16px;
  min-height: 100px;
}

.scoreboard {
  background-color: white;
  padding: 24px;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  margin-bottom: 32px;
}

.scoreboard h3 {
  margin-bottom: 16px;
  text-align: center;
}

.score-table {
  width: 100%;
  border-collapse: collapse;
}

.score-table th, .score-table td {
  padding: 12px 16px;
  text-align: left;
  border-bottom: 1px solid #eee;
}

.score-table th {
  background-color: #f5f5f5;
  font-weight: 600;
}

.score-table tr.current-player {
  background-color: rgba(255, 64, 129, 0.1);
}

.rank {
  text-align: center;
  font-weight: 600;
}

.player-score {
  font-weight: 600;
  text-align: right;
}

.host-badge {
  font-size: 0.7rem;
  background-color: var(--primary-color);
  color: white;
  padding: 2px 4px;
  border-radius: 2px;
  margin-left: 4px;
}

.round-actions {
  text-align: center;
}

.next-round-btn, .end-game-btn {
  background-color: var(--primary-color);
  color: white;
  border: none;
  border-radius: 4px;
  padding: 12px 32px;
  font-size: 1.1rem;
  cursor: pointer;
}

.end-game-btn {
  background-color: #2ecc71;
}

.waiting-message {
  color: var(--text-secondary);
  font-style: italic;
}

@media (max-width: 768px) {
  .submissions-grid {
    grid-template-columns: 1fr;
  }
  
  .score-table th, .score-table td {
    padding: 8px;
  }
}
</style>
