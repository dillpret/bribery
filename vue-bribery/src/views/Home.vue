<template>
  <div class="home">
    <div class="container">
      <!-- Logo and Title -->
      <div class="logo-container">
        <img src="/img/logo/logo-full.png" alt="Bribery Game" class="game-logo" @error="logoLoadError = true">
        
        <div class="title-container" v-if="logoLoadError">
          <span class="emoji-logo">😉</span>
          <span class="title-text">Bribery</span>
        </div>
        
        <p class="subtitle">A casual web game</p>
      </div>
      
      <!-- Main Menu -->
      <div id="main-menu" v-if="currentView === 'main'">
        <div class="card">
          <div class="button-container">
            <button class="host-button" @click="showHostGame">
              <span class="button-icon">🎮</span> Host New Game
            </button>
            <button class="join-button" @click="showJoinGame">
              <span class="button-icon">🔍</span> Join Existing Game
            </button>
          </div>
        </div>
        <button class="how-to-play-button" @click="showInstructions">
          <span class="button-icon">❓</span> How To Play
        </button>
      </div>

      <!-- Host Game Form -->
      <div id="host-game" v-if="currentView === 'host'" class="card">
        <h2>Host New Game</h2>
        <div class="form-container">
          <div class="form-group">
            <label for="host-username">Your Name:</label>
            <input type="text" id="host-username" v-model="hostForm.username" required>
          </div>
          <div class="form-group">
            <label for="rounds">Rounds:</label>
            <input type="number" id="rounds" v-model.number="hostForm.rounds" min="1" max="10" required>
          </div>
          <div class="form-actions">
            <button class="back-button" @click="showMainMenu">
              <span class="button-icon">⬅️</span> Back
            </button>
            <button class="create-button" @click="createGame">
              <span class="button-icon">✅</span> Create Game
            </button>
          </div>
        </div>
      </div>

      <!-- Join Game Form -->
      <div id="join-game" v-if="currentView === 'join'" class="card">
        <h2>Join Game</h2>
        <div class="form-container">
          <div class="form-group">
            <label for="join-username">Your Name:</label>
            <input type="text" id="join-username" v-model="joinForm.username" required>
          </div>
          <div class="form-group">
            <label for="game-id">Game ID:</label>
            <input type="text" id="game-id" v-model="joinForm.gameId" required style="text-transform: uppercase;">
          </div>
          <div class="form-actions">
            <button class="back-button" @click="showMainMenu">
              <span class="button-icon">⬅️</span> Back
            </button>
            <button class="join-button-submit" @click="joinGame">
              <span class="button-icon">➡️</span> Join Game
            </button>
          </div>
        </div>
      </div>
      
      <!-- Instructions Panel -->
      <div id="instructions" v-if="currentView === 'instructions'" class="card">
        <h2>How To Play</h2>
        <div class="instructions-content">
          <p>Bribery is a casual party game where players create creative bribes and vote on the best ones.</p>
          <ol>
            <li>Each round, players receive a target to bribe.</li>
            <li>Create a creative, funny, or persuasive bribe for your target.</li>
            <li>Vote for your favorite bribes (not your own).</li>
            <li>Earn points when others vote for your bribes.</li>
            <li>The player with the most points at the end wins!</li>
          </ol>
        </div>
        <button class="got-it-button" @click="showMainMenu">
          <span class="button-icon">👍</span> Got It!
        </button>
      </div>
    </div>
  </div>
</template>

<script>
import socketService from '@/services/socket'
import { mapActions } from 'vuex'

export default {
  name: 'Home',
  
  data() {
    return {
      currentView: 'main', // main, host, join, instructions
      logoLoadError: false,
      joinForm: {
        username: '',
        gameId: ''
      },
      hostForm: {
        username: '',
        rounds: 3
      }
    }
  },

  mounted() {
    // Check if the logo can be loaded, if not, show fallback
    const img = new Image();
    img.onerror = () => {
      this.logoLoadError = true;
    };
    img.src = '/images/logo/logo-full.png';
  },
  
  created() {
    // Initialize socket connection
    socketService.init()
    
    // Set up socket event handlers for home page
    socketService.socket.on('game_created', this.handleGameCreated)
    socketService.socket.on('joined_game', this.handleJoinedGame)
    
    // Check for stored credentials and attempt reconnection if needed
    this.checkForStoredCredentials()
  },
  
  beforeUnmount() {
    // Remove event listeners when component is destroyed
    socketService.socket.off('game_created', this.handleGameCreated)
    socketService.socket.off('joined_game', this.handleJoinedGame)
  },
  
  methods: {
    ...mapActions('auth', ['saveAuth']),
    
    // Navigation methods
    showMainMenu() {
      this.currentView = 'main'
    },
    
    showHostGame() {
      this.currentView = 'host'
    },
    
    showJoinGame() {
      this.currentView = 'join'
    },
    
    showInstructions() {
      this.currentView = 'instructions'
    },
    
    // Game methods
    joinGame() {
      if (!this.joinForm.username.trim() || !this.joinForm.gameId.trim()) {
        return // Form validation
      }
      
      socketService.joinGame(
        this.joinForm.gameId, 
        this.joinForm.username
      )
    },
    
    createGame() {
      if (!this.hostForm.username.trim()) {
        return // Form validation
      }
      
      socketService.createGame(
        this.hostForm.username, 
        { rounds: this.hostForm.rounds }
      )
    },
    
    // Socket handlers
    handleGameCreated(data) {
      // Update auth store with host information
      this.$store.commit('auth/SET_USERNAME', this.hostForm.username)
      this.$store.commit('auth/SET_HOST', true)
      this.$store.commit('auth/SET_GAME_ID', data.game_id)
      this.$store.commit('auth/SET_PLAYER_ID', data.player_id)
      this.$store.commit('auth/SET_AUTHENTICATED', true)
      
      // Save auth state
      this.saveAuth()
      
      // Navigate to game page
      this.$router.push(`/game/${data.game_id}`)
    },
    
    handleJoinedGame(data) {
      // Update auth store with player information
      this.$store.commit('auth/SET_USERNAME', this.joinForm.username)
      this.$store.commit('auth/SET_GAME_ID', data.game_id)
      this.$store.commit('auth/SET_PLAYER_ID', data.player_id)
      this.$store.commit('auth/SET_HOST', data.is_host || false)
      this.$store.commit('auth/SET_AUTHENTICATED', true)
      
      // Save auth state
      this.saveAuth()
      
      // Navigate to game page
      this.$router.push(`/game/${data.game_id}`)
    },
    
    // Check for stored credentials (reconnection logic)
    checkForStoredCredentials() {
      // Look for existing games in localStorage
      const storedGames = Object.keys(localStorage)
        .filter(key => key.startsWith('bribery_game_'))
      
      if (storedGames.length > 0) {
        try {
          // Take the most recent game
          const gameKey = storedGames[storedGames.length - 1]
          const gameData = JSON.parse(localStorage.getItem(gameKey))
          
          if (gameData && gameData.gameId && gameData.playerId && gameData.username) {
            // Pre-fill the join form with the stored username and game ID
            this.joinForm.username = gameData.username
            this.joinForm.gameId = gameData.gameId
            
            // If auto-reconnect is implemented, could handle it here
            // For now, just show the join form with pre-filled data
            this.showJoinGame()
          }
        } catch (err) {
          console.error('Error checking for stored credentials:', err)
        }
      }
    }
  }
}
</script>

<style scoped>
.home {
  display: flex;
  flex-direction: column;
  align-items: center;
  min-height: 100vh;
  padding: 2rem 1rem;
  background-color: #f5f5f5;
}

.container {
  width: 100%;
  max-width: 600px;
  margin: 0 auto;
  display: flex;
  flex-direction: column;
  align-items: center;
}

/* Logo and Title Section */
.logo-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  margin-bottom: 2rem;
  text-align: center;
}

.game-logo {
  max-width: 320px;
  height: auto;
  margin-bottom: 0.5rem;
}

.title-container {
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 0.5rem;
}

.emoji-logo {
  font-size: 2.5rem;
  margin-right: 0.5rem;
}

.title-text {
  color: #0080ff;
  font-size: 2.5rem;
  font-weight: bold;
}

.subtitle {
  font-size: 1.2rem;
  color: #666;
  margin: 0.5rem 0 1.5rem;
}

/* Card styles */
.card {
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  padding: 1.5rem;
  width: 100%;
  margin-bottom: 1rem;
}

/* Button container */
.button-container {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  margin-bottom: 0.5rem;
}

/* Button styles */
button {
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-weight: 600;
  padding: 0.75rem;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 100%;
  font-size: 1rem;
  transition: background-color 0.2s;
}

.host-button {
  background-color: #0080ff;
  color: white;
}

.join-button {
  background-color: #ff4081;
  color: white;
}

.how-to-play-button {
  background-color: transparent;
  border: 1px solid #ddd;
  color: #666;
  margin-top: 0.5rem;
}

.button-icon {
  margin-right: 0.5rem;
}

.form-actions {
  display: flex;
  justify-content: space-between;
  gap: 1rem;
  margin-top: 1.5rem;
}

.back-button {
  background-color: #f5f5f5;
  color: #333;
}

.create-button {
  background-color: #0080ff;
  color: white;
}

.join-button-submit {
  background-color: #ff4081;
  color: white;
}

.got-it-button {
  background-color: #0080ff;
  color: white;
  margin-top: 1rem;
}

/* Form styles */
h2 {
  text-align: center;
  margin-bottom: 1.5rem;
  color: #333;
  font-size: 1.5rem;
}

.form-container {
  width: 100%;
}

.form-group {
  margin-bottom: 1rem;
}

label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 500;
}

input {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 1rem;
}

input:focus {
  outline: none;
  border-color: #0080ff;
}

/* Instructions panel */
.instructions-content {
  margin-bottom: 1.5rem;
}

.instructions-content p {
  margin-bottom: 1rem;
}

.instructions-content ol {
  padding-left: 1.5rem;
}

.instructions-content li {
  margin-bottom: 0.5rem;
}

/* Responsive adjustments */
@media (max-width: 480px) {
  .form-actions {
    flex-direction: column;
    gap: 0.5rem;
  }
  
  .card {
    padding: 1rem;
  }
}
</style>
