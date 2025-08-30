<template>
  <div class="home">
    <div class="logo-container">
      <img src="@/assets/images/logo/logo-full.png" alt="Bribery Game" class="hero-logo">
    </div>
    
    <div class="forms-container">
      <div class="join-form">
        <h2>Join a Game</h2>
        <form @submit.prevent="joinGame">
          <div class="form-group">
            <label for="join-username">Your Name:</label>
            <input type="text" id="join-username" v-model="joinForm.username" required>
          </div>
          <div class="form-group">
            <label for="game-id">Game ID:</label>
            <input type="text" id="game-id" v-model="joinForm.gameId" required>
          </div>
          <button type="submit" class="btn btn-primary">Join Game</button>
        </form>
      </div>
      
      <div class="host-form">
        <h2>Host a Game</h2>
        <form @submit.prevent="createGame">
          <div class="form-group">
            <label for="host-username">Your Name:</label>
            <input type="text" id="host-username" v-model="hostForm.username" required>
          </div>
          <div class="form-group">
            <label for="rounds">Rounds:</label>
            <input type="number" id="rounds" v-model.number="hostForm.rounds" min="1" max="10" required>
          </div>
          <button type="submit" class="btn btn-primary">Create Game</button>
        </form>
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
  
  created() {
    // Initialize socket connection
    socketService.init()
    
    // Set up socket event handlers for home page
    socketService.socket.on('game_created', this.handleGameCreated)
    socketService.socket.on('joined_game', this.handleJoinedGame)
  },
  
  beforeUnmount() {
    // Remove event listeners when component is destroyed
    socketService.socket.off('game_created', this.handleGameCreated)
    socketService.socket.off('joined_game', this.handleJoinedGame)
  },
  
  methods: {
    ...mapActions('auth', ['saveAuth']),
    
    joinGame() {
      socketService.joinGame(
        this.joinForm.gameId, 
        this.joinForm.username
      )
    },
    
    createGame() {
      socketService.createGame(
        this.hostForm.username, 
        { rounds: this.hostForm.rounds }
      )
    },
    
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
    }
  }
}
</script>

<style scoped>
.home {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 2rem;
  min-height: 100vh;
}

.logo-container {
  margin-bottom: 2rem;
}

.hero-logo {
  max-width: 300px;
  height: auto;
}

.forms-container {
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  gap: 2rem;
  max-width: 800px;
}

.join-form, .host-form {
  background-color: white;
  padding: 1.5rem;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  min-width: 300px;
}

h2 {
  margin-bottom: 1.5rem;
  color: var(--primary-color);
}

.form-group {
  margin-bottom: 1rem;
}

label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 500;
}

button {
  width: 100%;
  padding: 0.75rem;
  margin-top: 1rem;
}

@media (max-width: 768px) {
  .forms-container {
    flex-direction: column;
  }
  
  .join-form, .host-form {
    width: 100%;
  }
}
</style>
