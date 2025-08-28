# Bribery Game Migration Plan: Vanilla JS to Vue.js

This document provides a detailed, step-by-step plan for migrating the Bribery game from its current vanilla JavaScript architecture to a modern Vue.js implementation. The plan is broken down into manageable phases, with special attention to potential challenges and compatibility concerns.

## Table of Contents

1. [Project Assessment](#1-project-assessment)
2. [Development Environment Setup](#2-development-environment-setup)
3. [Core Architecture Design](#3-core-architecture-design)
4. [Migration Phase 1: Foundation](#4-migration-phase-1-foundation)
5. [Migration Phase 2: Component Migration](#5-migration-phase-2-component-migration)
6. [Migration Phase 3: State Management](#6-migration-phase-3-state-management)
7. [Migration Phase 4: Testing & Optimization](#7-migration-phase-4-testing--optimization)
8. [Migration Phase 5: Deployment](#8-migration-phase-5-deployment)
9. [Common Pitfalls & Solutions](#9-common-pitfalls--solutions)
10. [Special Considerations for AI Assistants](#10-special-considerations-for-ai-assistants)

## 1. Project Assessment

Before beginning the migration, we need to thoroughly understand the current codebase architecture.

### 1.1 Current Architecture Overview

The Bribery game currently uses:
- Vanilla JavaScript with a mix of ES6 modules and global variables
- Socket.IO for real-time communication
- Flask backend with SocketIO
- Direct DOM manipulation for UI updates
- LocalStorage for state persistence
- Multiple JS files with unclear boundaries

### 1.2 Key Components to Migrate

1. **Authentication System**
   - Currently implemented across multiple files
   - Uses localStorage for persistence
   - Relies on multiple fallback mechanisms

2. **Game State Management**
   - Distributed across game-core.js, game-state.js, and socket-handlers.js
   - Uses a mix of global variables and module patterns

3. **UI Components**
   - Lobby, Prompt Selection, Submission Phase, Voting Phase, Scoreboard
   - Currently managed through direct DOM manipulation
   - Screen visibility controlled by adding/removing CSS classes

4. **Socket Communication**
   - Centralized in socket-manager.js but with handlers in multiple files
   - Event handling in socket-handlers.js (765+ lines)

5. **Image Processing**
   - Image optimization and handling in image-utils.js

### 1.3 Technical Debt & Issues to Address

- Inconsistent module patterns across files
- Tightly coupled components with unclear responsibilities
- Complex initialization sequences with multiple fallbacks
- Imperative UI updates instead of declarative patterns
- No clear separation between UI and business logic
- Lack of a build system for optimization

### 1.4 Migration Goals

1. **Improve Maintainability**: Clear component boundaries and responsibilities
2. **Enhance Testability**: Components that can be tested in isolation
3. **Modernize Development Experience**: Leverage Vue's tooling and ecosystem
4. **Preserve Functionality**: Ensure all existing features work correctly
5. **Enable Future Growth**: Create a foundation for adding new features

---

## 2. Development Environment Setup

Before starting the migration, we need to set up a proper development environment.

### 2.1 Install Node.js and npm

Ensure Node.js (v16+) and npm are installed:

```powershell
# Check current version (if installed)
node -v
npm -v

# Install latest LTS if needed (use an installer from nodejs.org for Windows)
```

### 2.2 Create Vue Project

We'll use Vue CLI to scaffold the new project structure:

```powershell
# Install Vue CLI globally
npm install -g @vue/cli

# Create a new Vue project in a subdirectory
vue create vue-bribery

# Select Vue 3, Babel, Router, Vuex, ESLint+Prettier
# Choose history mode for router
```

### 2.3 Set Up Development Tools

```powershell
# Install additional dependencies
cd vue-bribery
npm install socket.io-client
npm install --save-dev sass sass-loader
```

### 2.4 Configure Project Structure

Create the folder structure for the new Vue project:

```
vue-bribery/
├── public/
│   ├── index.html
│   └── favicon.ico
├── src/
│   ├── assets/
│   │   ├── images/
│   │   └── styles/
│   ├── components/
│   │   ├── common/
│   │   ├── game/
│   │   └── layout/
│   ├── router/
│   │   └── index.js
│   ├── store/
│   │   ├── index.js
│   │   ├── modules/
│   │   │   ├── auth.js
│   │   │   ├── game.js
│   │   │   └── ui.js
│   ├── services/
│   │   ├── socket.js
│   │   ├── auth.js
│   │   └── storage.js
│   ├── utils/
│   │   ├── image-processing.js
│   │   └── helpers.js
│   ├── views/
│   │   ├── Home.vue
│   │   └── Game.vue
│   ├── App.vue
│   └── main.js
├── .gitignore
├── babel.config.js
├── package.json
└── README.md
```

### 2.5 Configure Communication with Backend

1. Create a Vue environment configuration:

Create `.env.development` file:
```
VUE_APP_API_URL=http://localhost:5000
```

2. Add CORS support to your Flask backend:

```python
from flask_cors import CORS

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})
```

3. Add `flask-cors` to your `requirements.txt`:
```
flask-cors==3.0.10
```

### 2.6 Set Up Build Configuration

Create `vue.config.js` in the project root:

```javascript
module.exports = {
  devServer: {
    proxy: {
      '/socket.io': {
        target: 'http://localhost:5000',
        ws: true,
        changeOrigin: true
      }
    }
  },
  // Output to the main Flask static directory
  outputDir: '../static/vue',
  // Adjust public path for Flask integration
  publicPath: process.env.NODE_ENV === 'production' ? '/static/vue/' : '/'
}
```

## 3. Core Architecture Design

Now we'll design the core architecture of our Vue application.

### 3.1 Application Structure

The Vue application will follow a modular architecture:

```
└── src/
    ├── App.vue                 # Root component
    ├── main.js                 # Application entry point
    ├── components/             # Reusable UI components
    │   ├── common/             # General-purpose components
    │   │   ├── Timer.vue
    │   │   ├── PlayerList.vue
    │   │   └── ImageUploader.vue
    │   ├── game/               # Game-specific components
    │   │   ├── GameLobby.vue
    │   │   ├── PromptPhase.vue
    │   │   ├── SubmissionPhase.vue
    │   │   ├── VotingPhase.vue
    │   │   └── ScoreboardPhase.vue
    │   └── layout/             # Page layout components
    │       ├── Header.vue
    │       ├── Footer.vue
    │       └── StatusBar.vue
    ├── views/                  # Page components
    │   ├── Home.vue            # Homepage (join/create game)
    │   └── Game.vue            # Main game container
    ├── store/                  # Vuex state management
    │   ├── index.js            # Root store
    │   └── modules/            # Store modules
    │       ├── auth.js         # Authentication state
    │       ├── game.js         # Game state
    │       └── ui.js           # UI state
    ├── services/               # API and service layer
    │   ├── socket.js           # Socket.IO integration
    │   ├── auth.js             # Authentication logic
    │   └── storage.js          # LocalStorage wrapper
    └── utils/                  # Utility functions
        ├── image-processing.js # Image handling
        └── helpers.js          # Helper functions
```

### 3.2 State Management Design

We'll use Vuex to centralize all state management:

```javascript
// store/index.js
import { createStore } from 'vuex'
import auth from './modules/auth'
import game from './modules/game'
import ui from './modules/ui'

export default createStore({
  modules: {
    auth,
    game,
    ui
  }
})
```

#### Auth Module
```javascript
// store/modules/auth.js
import authService from '@/services/auth'

export default {
  namespaced: true,
  
  state: {
    playerId: null,
    username: null,
    isHost: false,
    gameId: null,
    isAuthenticated: false
  },
  
  mutations: {
    SET_PLAYER_ID(state, id) {
      state.playerId = id
    },
    SET_USERNAME(state, name) {
      state.username = name
    },
    SET_HOST(state, isHost) {
      state.isHost = isHost
    },
    SET_GAME_ID(state, id) {
      state.gameId = id
    },
    SET_AUTHENTICATED(state, value) {
      state.isAuthenticated = value
    },
    CLEAR_AUTH(state) {
      state.playerId = null
      state.username = null
      state.isHost = false
      state.gameId = null
      state.isAuthenticated = false
    }
  },
  
  actions: {
    initAuth({ commit, dispatch }, gameId) {
      const authData = authService.loadAuthState(gameId)
      if (authData) {
        commit('SET_PLAYER_ID', authData.playerId)
        commit('SET_USERNAME', authData.username)
        commit('SET_HOST', authData.isHost)
        commit('SET_GAME_ID', gameId)
        commit('SET_AUTHENTICATED', true)
        return true
      }
      return false
    },
    
    saveAuth({ state }) {
      if (state.gameId) {
        authService.saveAuthState(state.gameId, {
          playerId: state.playerId,
          username: state.username,
          isHost: state.isHost
        })
      }
    }
  }
}
```

#### Game Module
```javascript
// store/modules/game.js
export default {
  namespaced: true,
  
  state: {
    phase: 'connecting',  // connecting, lobby, prompt_selection, submission, voting, results, game_over
    currentRound: 0,
    totalRounds: 0,
    players: [],
    currentTargets: [],
    submissions: {},
    selectedVote: null,
    scoreboard: []
  },
  
  mutations: {
    SET_PHASE(state, phase) {
      state.phase = phase
    },
    SET_ROUND_INFO(state, { current, total }) {
      state.currentRound = current
      state.totalRounds = total
    },
    SET_PLAYERS(state, players) {
      state.players = players
    },
    SET_TARGETS(state, targets) {
      state.currentTargets = targets
    },
    SET_SUBMISSIONS(state, submissions) {
      state.submissions = submissions
    },
    SET_SELECTED_VOTE(state, voteId) {
      state.selectedVote = voteId
    },
    SET_SCOREBOARD(state, scoreboard) {
      state.scoreboard = scoreboard
    }
  },
  
  actions: {
    updateGameState({ commit }, data) {
      if (data.phase) commit('SET_PHASE', data.phase)
      if (data.currentRound !== undefined && data.totalRounds !== undefined) {
        commit('SET_ROUND_INFO', { 
          current: data.currentRound, 
          total: data.totalRounds 
        })
      }
      if (data.players) commit('SET_PLAYERS', data.players)
    }
  }
}
```

#### UI Module
```javascript
// store/modules/ui.js
export default {
  namespaced: true,
  
  state: {
    statusMessage: 'Connecting...',
    isConnected: false,
    timerValue: 0,
    timerActive: false,
    activeDialog: null
  },
  
  mutations: {
    SET_STATUS(state, message) {
      state.statusMessage = message
    },
    SET_CONNECTION(state, isConnected) {
      state.isConnected = isConnected
    },
    SET_TIMER(state, value) {
      state.timerValue = value
    },
    SET_TIMER_ACTIVE(state, active) {
      state.timerActive = active
    },
    SET_ACTIVE_DIALOG(state, dialog) {
      state.activeDialog = dialog
    }
  }
}
```

### 3.3 Socket Service Design

We'll create a dedicated service for socket communication:

```javascript
// services/socket.js
import { io } from 'socket.io-client'
import store from '@/store'

class SocketService {
  constructor() {
    this.socket = null
    this.reconnectAttempts = 0
    this.maxReconnectAttempts = 5
  }

  init() {
    this.socket = io(process.env.VUE_APP_API_URL, {
      transports: ['websocket', 'polling'],
      reconnection: true,
      reconnectionDelay: 1000,
      reconnectionDelayMax: 5000,
      reconnectionAttempts: this.maxReconnectAttempts
    })

    this._setupListeners()
    return this.socket
  }

  _setupListeners() {
    // Connection events
    this.socket.on('connect', () => {
      store.commit('ui/SET_CONNECTION', true)
      store.commit('ui/SET_STATUS', 'Connected')
      this.reconnectAttempts = 0
    })

    this.socket.on('disconnect', () => {
      store.commit('ui/SET_CONNECTION', false)
      store.commit('ui/SET_STATUS', 'Disconnected')
    })

    this.socket.on('reconnect_attempt', (attempt) => {
      this.reconnectAttempts = attempt
      store.commit('ui/SET_STATUS', `Reconnecting (${attempt}/${this.maxReconnectAttempts})...`)
    })

    // Game events
    this.socket.on('joined_game', (data) => {
      store.commit('auth/SET_PLAYER_ID', data.player_id)
      store.commit('auth/SET_USERNAME', data.username)
      store.commit('auth/SET_HOST', data.is_host)
      store.commit('auth/SET_AUTHENTICATED', true)
      store.dispatch('auth/saveAuth')
      
      store.dispatch('game/updateGameState', {
        phase: data.game_state,
        currentRound: data.current_round,
        totalRounds: data.total_rounds
      })
    })

    // More event handlers will be added here
  }

  // Socket API methods
  joinGame(gameId, username, playerId) {
    this.socket.emit('join_game', {
      game_id: gameId,
      username,
      player_id: playerId
    })
  }

  createGame(username, settings) {
    this.socket.emit('create_game', {
      username,
      settings
    })
  }

  // Additional methods for other socket events
}

export default new SocketService()
```

### 3.4 Authentication Service Design

```javascript
// services/auth.js
class AuthService {
  getStorageKey(gameId) {
    return `bribery_game_${gameId}`
  }

  saveAuthState(gameId, authData) {
    if (!gameId) return false

    const storageKey = this.getStorageKey(gameId)
    try {
      const dataToStore = JSON.stringify({
        playerId: authData.playerId,
        username: authData.username,
        isHost: authData.isHost,
        timestamp: Date.now()
      })
      
      localStorage.setItem(storageKey, dataToStore)
      return true
    } catch (error) {
      console.warn('Failed to save auth state:', error)
      return false
    }
  }

  loadAuthState(gameId) {
    if (!gameId) return null
    
    const storageKey = this.getStorageKey(gameId)
    try {
      const storedData = localStorage.getItem(storageKey)
      
      if (!storedData) return null
      
      const parsedData = JSON.parse(storedData)
      return {
        playerId: parsedData.playerId || null,
        username: parsedData.username || null,
        isHost: !!parsedData.isHost
      }
    } catch (error) {
      console.error('Error loading auth state:', error)
      return null
    }
  }

  clearAuthState(gameId) {
    if (!gameId) return
    
    const storageKey = this.getStorageKey(gameId)
    localStorage.removeItem(storageKey)
  }
}

export default new AuthService()
```

### 3.5 Image Processing Service Design

```javascript
// utils/image-processing.js
export default {
  MAX_WIDTH: 1200,
  MAX_HEIGHT: 800,
  MAX_FILE_SIZE: 5 * 1024 * 1024, // 5MB
  
  async validateFile(file) {
    // Check file size
    if (file.size > this.MAX_FILE_SIZE) {
      return {
        valid: false,
        message: `File size exceeds 5MB limit (${Math.round(file.size/1024/1024)}MB)`
      }
    }
    
    // Check file type
    if (!file.type.startsWith('image/')) {
      return {
        valid: false,
        message: 'Only image files are supported'
      }
    }
    
    // Further validation
    return new Promise((resolve) => {
      const img = new Image()
      const objectUrl = URL.createObjectURL(file)
      
      img.onload = () => {
        URL.revokeObjectURL(objectUrl)
        resolve({ valid: true, message: 'Valid image' })
      }
      
      img.onerror = () => {
        URL.revokeObjectURL(objectUrl)
        resolve({ 
          valid: false, 
          message: 'Invalid or corrupted image file'
        })
      }
      
      img.src = objectUrl
    })
  },
  
  async processImage(file) {
    // Implementation will be migrated from the current image-utils.js
    // This is a placeholder for the structure
  }
}
```

---

## 4. Migration Phase 1: Foundation

This phase focuses on setting up the basic Vue application structure and implementing the first components.

### 4.1 Create Basic Vue Components

Start by creating the essential components needed for the application:

#### App.vue (Root Component)
```vue
<template>
  <div id="app">
    <router-view />
  </div>
</template>

<script>
export default {
  name: 'App'
}
</script>

<style>
/* Import base styles */
@import './assets/styles/base.css';
</style>
```

#### Home.vue (Landing Page)
```vue
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
/* Styles will be migrated from current index.css */
</style>
```

#### Game.vue (Main Game Container)
```vue
<template>
  <div class="game-container">
    <header-component :game-id="gameId" />
    <status-bar :message="statusMessage" :timer="timerValue" />
    
    <!-- Game phases -->
    <game-lobby v-if="currentPhase === 'lobby'" />
    <prompt-phase v-else-if="currentPhase === 'prompt_selection'" />
    <submission-phase v-else-if="currentPhase === 'submission'" />
    <voting-phase v-else-if="currentPhase === 'voting'" />
    <scoreboard-phase v-else-if="currentPhase === 'results'" />
    <waiting-screen v-else-if="currentPhase === 'waiting'" />
    <connection-error v-else-if="currentPhase === 'error'" />
    
    <player-list-panel />
  </div>
</template>

<script>
import HeaderComponent from '@/components/layout/Header.vue'
import StatusBar from '@/components/layout/StatusBar.vue'
import GameLobby from '@/components/game/GameLobby.vue'
import PromptPhase from '@/components/game/PromptPhase.vue'
import SubmissionPhase from '@/components/game/SubmissionPhase.vue'
import VotingPhase from '@/components/game/VotingPhase.vue'
import ScoreboardPhase from '@/components/game/ScoreboardPhase.vue'
import WaitingScreen from '@/components/game/WaitingScreen.vue'
import ConnectionError from '@/components/game/ConnectionError.vue'
import PlayerListPanel from '@/components/common/PlayerListPanel.vue'

import socketService from '@/services/socket'
import { mapState, mapActions } from 'vuex'

export default {
  name: 'Game',
  
  components: {
    HeaderComponent,
    StatusBar,
    GameLobby,
    PromptPhase,
    SubmissionPhase,
    VotingPhase,
    ScoreboardPhase,
    WaitingScreen,
    ConnectionError,
    PlayerListPanel
  },
  
  computed: {
    ...mapState('auth', ['gameId', 'playerId', 'username', 'isAuthenticated']),
    ...mapState('game', ['currentPhase']),
    ...mapState('ui', ['statusMessage', 'timerValue'])
  },
  
  created() {
    // Initialize socket connection
    socketService.init()
    
    // Get game ID from route
    const gameId = this.$route.params.id
    
    // Initialize auth from localStorage if available
    this.initAuth(gameId).then(success => {
      if (success) {
        // We have stored credentials, attempt to join with them
        socketService.joinGame(gameId, this.username, this.playerId)
      } else {
        // No stored credentials, redirect to home page
        this.$router.push('/')
      }
    })
  },
  
  methods: {
    ...mapActions('auth', ['initAuth'])
  }
}
</script>

<style scoped>
/* Styles will be migrated from current game.css */
</style>
```

### 4.2 Create Layout Components

#### Header.vue
```vue
<template>
  <div class="header">
    <div class="logo-wrapper">
      <img src="@/assets/images/logo/logo-full.png" alt="Bribery Game" class="hero-logo">
      <h1 class="hero-logo-fallback">🎯 Bribery</h1>
    </div>
    <div class="game-info">
      Game ID: <strong>{{ gameId }}</strong>
      <span 
        :class="['connection-status', isConnected ? 'connected' : 'disconnected']" 
        :title="isConnected ? 'Connected' : 'Disconnected'">
      </span>
    </div>
  </div>
</template>

<script>
import { mapState } from 'vuex'

export default {
  name: 'HeaderComponent',
  
  props: {
    gameId: {
      type: String,
      required: true
    }
  },
  
  computed: {
    ...mapState('ui', ['isConnected'])
  }
}
</script>

<style scoped>
/* Styles will be migrated from current game.css */
</style>
```

#### StatusBar.vue
```vue
<template>
  <div class="status-bar">
    <div class="game-status">{{ message }}</div>
    <div class="timer" v-if="timer > 0">{{ formatTime(timer) }}</div>
  </div>
</template>

<script>
export default {
  name: 'StatusBar',
  
  props: {
    message: {
      type: String,
      default: ''
    },
    timer: {
      type: Number,
      default: 0
    }
  },
  
  methods: {
    formatTime(seconds) {
      const mins = Math.floor(seconds / 60)
      const secs = seconds % 60
      return `${mins}:${secs.toString().padStart(2, '0')}`
    }
  }
}
</script>

<style scoped>
/* Styles will be migrated from current game.css */
</style>
```

### 4.3 Implement Common Components

#### PlayerListPanel.vue
```vue
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
    <div :class="['confirmation-modal-overlay', { visible: showKickModal }]">
      <div class="confirmation-modal">
        <p id="kick-confirmation-message">
          Are you sure you want to kick {{ playerToKick?.username }} from the game?
        </p>
        <div class="confirmation-buttons">
          <button id="confirm-kick" @click="confirmKick">Kick Player</button>
          <button id="cancel-kick" @click="cancelKick">Cancel</button>
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
      isVisible: window.innerWidth >= 769, // Show by default on larger screens
      showKickModal: false,
      playerToKick: null
    }
  },
  
  computed: {
    ...mapState('auth', ['isHost']),
    ...mapState('game', ['players', 'phase']),
    
    sortedPlayers() {
      return [...this.players].sort((a, b) => b.score - a.score)
    },
    
    showSubmissionStatus() {
      return ['prompt_selection', 'submission', 'voting'].includes(this.phase)
    }
  },
  
  mounted() {
    window.addEventListener('resize', this.handleScreenSizeChange)
  },
  
  beforeUnmount() {
    window.removeEventListener('resize', this.handleScreenSizeChange)
  },
  
  methods: {
    togglePanel() {
      this.isVisible = !this.isVisible
    },
    
    handleScreenSizeChange() {
      // Auto show/hide based on screen width
      const wasAlreadyVisible = this.isVisible
      
      if (window.innerWidth >= 769) {
        document.querySelector('.container')?.classList.add('with-player-panel')
        if (!wasAlreadyVisible) {
          this.isVisible = true
        }
      } else {
        document.querySelector('.container')?.classList.remove('with-player-panel')
      }
    },
    
    showKickConfirmation(player) {
      this.playerToKick = player
      this.showKickModal = true
    },
    
    confirmKick() {
      if (this.playerToKick) {
        socketService.socket.emit('kick_player', {
          player_id: this.playerToKick.player_id,
          game_id: this.$store.state.auth.gameId
        })
        this.showKickModal = false
        this.playerToKick = null
      }
    },
    
    cancelKick() {
      this.showKickModal = false
      this.playerToKick = null
    }
  }
}
</script>

<style scoped>
/* Styles will be migrated from current game.css */
</style>
```

#### Timer.vue
```vue
<template>
  <div class="timer-component" :class="{ active: seconds > 0 }">
    {{ formattedTime }}
  </div>
</template>

<script>
export default {
  name: 'Timer',
  
  props: {
    seconds: {
      type: Number,
      required: true
    }
  },
  
  computed: {
    formattedTime() {
      if (this.seconds <= 0) return ''
      
      const minutes = Math.floor(this.seconds / 60)
      const secs = this.seconds % 60
      
      if (minutes > 0) {
        return `${minutes}:${secs.toString().padStart(2, '0')}`
      } else {
        return `${secs}`
      }
    }
  }
}
</script>

<style scoped>
.timer-component {
  font-weight: bold;
  padding: 0.5rem 1rem;
  border-radius: 4px;
  background-color: rgba(0, 0, 0, 0.1);
  visibility: hidden;
}

.timer-component.active {
  visibility: visible;
}
</style>
```

### 4.4 Set Up Vue Router

```javascript
// router/index.js
import { createRouter, createWebHistory } from 'vue-router'
import Home from '@/views/Home.vue'
import Game from '@/views/Game.vue'
import store from '@/store'

const routes = [
  {
    path: '/',
    name: 'Home',
    component: Home
  },
  {
    path: '/game/:id',
    name: 'Game',
    component: Game,
    props: true,
    beforeEnter: (to, from, next) => {
      const gameId = to.params.id
      
      // Check if there's saved auth for this game
      const authService = require('@/services/auth').default
      const savedAuth = authService.loadAuthState(gameId)
      
      if (savedAuth) {
        // We have credentials, allow access
        next()
      } else {
        // No credentials, redirect to home with game ID filled
        next({ 
          path: '/', 
          query: { 
            game: gameId,
            message: 'Please enter your name to join the game' 
          } 
        })
      }
    }
  },
  {
    path: '/:pathMatch(.*)*',
    redirect: '/'
  }
]

const router = createRouter({
  history: createWebHistory(process.env.BASE_URL),
  routes
})

export default router
```

### 4.5 Set Up Main Entry Point

```javascript
// main.js
import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import store from './store'

// Create and mount the Vue application
createApp(App)
  .use(store)
  .use(router)
  .mount('#app')
```

### 4.6 Migrate Base Styles

Copy over the base styles from the current project to the Vue project:

```css
/* src/assets/styles/base.css */
/* Base styles migrated from current CSS files */
```

### 4.7 Update Flask Templates to Load Vue App

For the Vue app to work with the Flask backend, update the Flask templates:

1. Create a new template for Vue integration:

```html
<!-- templates/vue_app.html -->
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=no">
    <title>Bribery Game</title>
    <link rel="icon" type="image/png" href="{{ url_for('static', filename='images/logo/favicon-96x96.png') }}" sizes="96x96" />
    <link rel="icon" type="image/svg+xml" href="{{ url_for('static', filename='images/logo/favicon.svg') }}" />
    <link rel="shortcut icon" href="{{ url_for('static', filename='images/logo/favicon.ico') }}" />
    <link rel="apple-touch-icon" sizes="180x180" href="{{ url_for('static', filename='images/logo/apple-touch-icon.png') }}" />
    <meta name="apple-mobile-web-app-title" content="Bribery" />
</head>
<body>
    <div id="app"></div>
    
    <!-- Production mode - load built Vue app -->
    {% if config.ENV == 'production' %}
    <script src="{{ url_for('static', filename='vue/js/chunk-vendors.js') }}"></script>
    <script src="{{ url_for('static', filename='vue/js/app.js') }}"></script>
    {% endif %}
</body>
</html>
```

2. Update Flask routes to use the Vue template:

```python
@app.route('/')
@app.route('/game/<game_id>')
def vue_app(game_id=None):
    return render_template('vue_app.html')
```

---

## 5. Migration Phase 2: Component Migration

This phase focuses on migrating specific game components to Vue.

### 5.1 Migrate Game Lobby Component

```vue
<!-- components/game/GameLobby.vue -->
<template>
  <div class="lobby">
    <div class="lobby-content">
      <h2>Waiting for Players</h2>
      <div class="player-list" id="player-list"></div>
      <div class="settings-display">
        <div v-if="settings">
          <h3>Game Settings</h3>
          <p>Rounds: {{ settings.rounds }}</p>
          <p>Submission Time: {{ formatTimeSetting(settings.submission_time) }}</p>
          <p>Voting Time: {{ formatTimeSetting(settings.voting_time) }}</p>
          <p>Results Screen Time: {{ formatTimeSetting(settings.results_time) }}</p>
          <p>Custom Prompts: {{ settings.custom_prompts ? 'Enabled' : 'Disabled' }}</p>
        </div>
      </div>
      
      <!-- Host Settings Controls (only visible to host) -->
      <div v-if="isHost" class="host-settings">
        <h3>Game Settings</h3>
        <div class="settings-grid">
          <div class="form-group">
            <label for="rounds">Number of Rounds:</label>
            <input type="number" id="rounds" v-model.number="hostSettings.rounds" min="1" max="100">
          </div>
          
          <div class="form-group">
            <label for="submission-time-mode">Submission Time:</label>
            <div class="time-input-container">
              <select id="submission-time-mode" v-model="hostSettings.submissionTimeMode">
                <option value="off">Off - Wait for all players</option>
                <option value="timed">Timed</option>
              </select>
              <div v-if="hostSettings.submissionTimeMode === 'timed'" class="time-controls">
                <input 
                  type="number" 
                  id="submission-time-value" 
                  v-model.number="hostSettings.submissionTimeValue" 
                  min="1" 
                  max="999">
                <select id="submission-time-unit" v-model="hostSettings.submissionTimeUnit">
                  <option value="minutes">Minutes</option>
                  <option value="seconds">Seconds</option>
                </select>
              </div>
            </div>
          </div>
          
          <!-- Additional settings -->
          <div class="form-group">
            <label for="custom-prompts">Custom Prompts:</label>
            <div class="toggle-container">
              <input type="checkbox" id="custom-prompts" v-model="hostSettings.customPrompts">
              <label for="custom-prompts" class="toggle-label">{{ hostSettings.customPrompts ? 'Enabled' : 'Disabled' }}</label>
            </div>
          </div>
        </div>
        
        <div class="lobby-actions">
          <button 
            @click="updateSettings" 
            class="btn btn-secondary" 
            :disabled="!settingsChanged">
            Update Settings
          </button>
          <button 
            @click="startGame" 
            class="btn btn-primary" 
            :disabled="players.length < 3">
            Start Game
          </button>
          <p v-if="players.length < 3" class="warning-text">
            At least 3 players are needed to start.
          </p>
        </div>
      </div>
      
      <!-- Player View (non-host) -->
      <div v-else class="player-waiting">
        <p>Waiting for the host to start the game...</p>
        <div class="waiting-spinner"></div>
      </div>
    </div>
  </div>
</template>

<script>
import { mapState } from 'vuex'
import socketService from '@/services/socket'

export default {
  name: 'GameLobby',
  
  data() {
    return {
      hostSettings: {
        rounds: 3,
        submissionTimeMode: 'off',
        submissionTimeValue: 2,
        submissionTimeUnit: 'minutes',
        votingTimeMode: 'off',
        votingTimeValue: 60,
        votingTimeUnit: 'seconds',
        resultsTimeMode: 'off',
        resultsTimeValue: 10,
        resultsTimeUnit: 'seconds',
        customPrompts: false
      },
      initialSettings: null
    }
  },
  
  computed: {
    ...mapState('auth', ['isHost']),
    ...mapState('game', ['players', 'settings']),
    
    settingsChanged() {
      if (!this.initialSettings) return false
      
      return JSON.stringify(this.hostSettings) !== JSON.stringify(this.initialSettings)
    }
  },
  
  created() {
    // Initialize socket handlers
    socketService.socket.on('settings_updated', this.handleSettingsUpdated)
    
    // Initialize settings if available
    if (this.settings) {
      this.updateHostSettingsFromServer(this.settings)
    }
  },
  
  beforeUnmount() {
    // Clean up socket handlers
    socketService.socket.off('settings_updated', this.handleSettingsUpdated)
  },
  
  methods: {
    updateSettings() {
      // Convert settings to server format
      const serverSettings = {
        rounds: this.hostSettings.rounds,
        submission_time: this.getTimeInSeconds('submission'),
        voting_time: this.getTimeInSeconds('voting'),
        results_time: this.getTimeInSeconds('results'),
        custom_prompts: this.hostSettings.customPrompts
      }
      
      // Send settings to server
      socketService.socket.emit('update_settings', {
        game_id: this.$store.state.auth.gameId,
        settings: serverSettings
      })
    },
    
    startGame() {
      socketService.socket.emit('start_game', {
        game_id: this.$store.state.auth.gameId
      })
    },
    
    handleSettingsUpdated(data) {
      this.updateHostSettingsFromServer(data.settings)
      this.$store.commit('game/SET_SETTINGS', data.settings)
    },
    
    updateHostSettingsFromServer(settings) {
      if (!settings) return
      
      // Update host settings from server data
      this.hostSettings = {
        rounds: settings.rounds || 3,
        submissionTimeMode: settings.submission_time > 0 ? 'timed' : 'off',
        submissionTimeValue: this.getTimeValue(settings.submission_time),
        submissionTimeUnit: this.getTimeUnit(settings.submission_time),
        votingTimeMode: settings.voting_time > 0 ? 'timed' : 'off',
        votingTimeValue: this.getTimeValue(settings.voting_time),
        votingTimeUnit: this.getTimeUnit(settings.voting_time),
        resultsTimeMode: settings.results_time > 0 ? 'timed' : 'off',
        resultsTimeValue: this.getTimeValue(settings.results_time),
        resultsTimeUnit: this.getTimeUnit(settings.results_time),
        customPrompts: settings.custom_prompts || false
      }
      
      // Save initial settings for comparison
      this.initialSettings = { ...this.hostSettings }
    },
    
    getTimeInSeconds(type) {
      const mode = this.hostSettings[`${type}TimeMode`]
      if (mode === 'off') return 0
      
      const value = this.hostSettings[`${type}TimeValue`]
      const unit = this.hostSettings[`${type}TimeUnit`]
      
      return unit === 'minutes' ? value * 60 : value
    },
    
    getTimeValue(seconds) {
      if (!seconds) return 0
      
      if (seconds >= 60 && seconds % 60 === 0) {
        return seconds / 60
      }
      return seconds
    },
    
    getTimeUnit(seconds) {
      if (!seconds) return 'seconds'
      
      if (seconds >= 60 && seconds % 60 === 0) {
        return 'minutes'
      }
      return 'seconds'
    },
    
    formatTimeSetting(seconds) {
      if (!seconds) return 'Off (Wait for all players)'
      
      if (seconds >= 60 && seconds % 60 === 0) {
        return `${seconds / 60} minute${seconds / 60 !== 1 ? 's' : ''}`
      }
      return `${seconds} second${seconds !== 1 ? 's' : ''}`
    }
  }
}
</script>

<style scoped>
/* Styles will be migrated from current game.css */
</style>
```

### 5.2 Migrate Submission Phase Component

```vue
<!-- components/game/SubmissionPhase.vue -->
<template>
  <div class="submission-phase">
    <h2>Submit Your Bribes</h2>
    <p>Round {{ currentRound }} of {{ totalRounds }}</p>
    
    <div class="targets-container">
      <div 
        v-for="target in currentTargets" 
        :key="target.player_id" 
        class="target-card">
        <h3>{{ target.username }}</h3>
        <p>{{ target.prompt }}</p>
        
        <div 
          v-if="!submissions[target.player_id] || !submissions[target.player_id].submitted" 
          class="submission-form">
          <!-- Text submission area -->
          <textarea 
            :id="`submission-${target.player_id}`" 
            class="submission-textarea" 
            placeholder="Enter your bribe here..." 
            :disabled="submissions[target.player_id]?.submitted"
          ></textarea>
          
          <!-- Image upload area -->
          <div 
            :id="`drop-${target.player_id}`" 
            class="drop-area" 
            @dragenter.prevent="onDragEnter"
            @dragover.prevent="onDragOver"
            @dragleave.prevent="onDragLeave"
            @drop.prevent="onDrop($event, target.player_id)">
            <p>Drag & drop an image here</p>
            <span>or</span>
            <button 
              :id="`upload-btn-${target.player_id}`" 
              class="upload-button" 
              @click="triggerFileInput(target.player_id)">
              Choose File
            </button>
            <input 
              :id="`file-input-${target.player_id}`" 
              type="file" 
              class="file-input" 
              accept="image/*" 
              @change="handleFileChange($event, target.player_id)">
          </div>
          
          <!-- Submit button -->
          <button 
            :id="`submit-btn-${target.player_id}`" 
            class="submit-button" 
            @click="submitBribe(target.player_id)" 
            :disabled="submissions[target.player_id]?.submitted">
            Submit Bribe
          </button>
        </div>
        
        <!-- Submitted indicator -->
        <div 
          v-else 
          class="submission-complete">
          <div class="checkmark">✓</div>
          <p>Bribe submitted!</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { mapState } from 'vuex'
import socketService from '@/services/socket'
import imageProcessing from '@/utils/image-processing'

export default {
  name: 'SubmissionPhase',
  
  data() {
    return {
      submissions: {},
      dragCounter: 0
    }
  },
  
  computed: {
    ...mapState('game', ['currentTargets', 'currentRound', 'totalRounds'])
  },
  
  created() {
    // Initialize socket handlers
    socketService.socket.on('submission_received', this.handleSubmissionReceived)
    socketService.socket.on('all_submissions_received', this.handleAllSubmissionsReceived)
  },
  
  beforeUnmount() {
    // Clean up socket handlers
    socketService.socket.off('submission_received', this.handleSubmissionReceived)
    socketService.socket.off('all_submissions_received', this.handleAllSubmissionsReceived)
    
    // Reset submissions when leaving
    this.submissions = {}
  },
  
  methods: {
    submitBribe(targetId) {
      let content, type = 'text'
      
      if (this.submissions[targetId]?.content) {
        content = this.submissions[targetId].content
        type = this.submissions[targetId].type
      } else {
        const textarea = document.getElementById(`submission-${targetId}`)
        content = textarea ? textarea.value.trim() : ''
      }
      
      if (!content) {
        alert('Please enter a bribe before submitting!')
        return
      }
      
      // Send submission to server
      socketService.socket.emit('submit_bribe', {
        game_id: this.$store.state.auth.gameId,
        player_id: this.$store.state.auth.playerId,
        target_id: targetId,
        content: content,
        type: type
      })
      
      // Update local submission state
      this.$set(this.submissions, targetId, {
        content,
        type,
        submitted: true
      })
    },
    
    // Drag and drop handlers
    onDragEnter(event) {
      this.dragCounter++
      event.currentTarget.classList.add('dragover')
    },
    
    onDragOver(event) {
      event.preventDefault()
    },
    
    onDragLeave(event) {
      this.dragCounter--
      if (this.dragCounter === 0) {
        event.currentTarget.classList.remove('dragover')
      }
    },
    
    onDrop(event, targetId) {
      this.dragCounter = 0
      event.currentTarget.classList.remove('dragover')
      
      const files = event.dataTransfer.files
      if (files.length > 0) {
        this.handleFile(files[0], targetId)
      }
    },
    
    triggerFileInput(targetId) {
      const fileInput = document.getElementById(`file-input-${targetId}`)
      if (fileInput) {
        fileInput.click()
      }
    },
    
    handleFileChange(event, targetId) {
      const files = event.target.files
      if (files.length > 0) {
        this.handleFile(files[0], targetId)
      }
    },
    
    async handleFile(file, targetId) {
      // Show loading state
      const dropArea = document.getElementById(`drop-${targetId}`)
      const submitBtn = document.getElementById(`submit-btn-${targetId}`)
      
      if (submitBtn) submitBtn.disabled = true
      if (dropArea) dropArea.innerHTML = '<div class="upload-loading">Processing image...</div>'
      
      try {
        // Process the image
        const result = await imageProcessing.processImage(file)
        
        if (result.error) {
          if (dropArea) dropArea.innerHTML = `<div class="upload-error">${result.error}</div>`
          if (submitBtn) submitBtn.disabled = false
          return
        }
        
        // Display preview
        const isGif = result.type === 'gif'
        const img = new Image()
        
        img.onload = () => {
          if (dropArea) {
            dropArea.innerHTML = `<img src="${result.content}" class="file-preview${isGif ? ' gif-preview' : ''}" alt="Uploaded ${isGif ? 'GIF' : 'image'}">`
          }
          
          // Store submission data
          this.$set(this.submissions, targetId, {
            content: result.content,
            type: result.type,
            submitted: false
          })
          
          if (submitBtn) submitBtn.disabled = false
        }
        
        img.onerror = () => {
          if (dropArea) dropArea.innerHTML = '<div class="upload-error">Failed to load image. Please try another.</div>'
          if (submitBtn) submitBtn.disabled = false
        }
        
        img.src = result.content
      } catch (error) {
        console.error('Image processing error:', error)
        if (dropArea) dropArea.innerHTML = '<div class="upload-error">Failed to process image. Please try another.</div>'
        if (submitBtn) submitBtn.disabled = false
      }
    },
    
    handleSubmissionReceived(data) {
      // Update submission status for a target
      if (data.player_id === this.$store.state.auth.playerId) {
        this.$set(this.submissions, data.target_id, {
          submitted: true
        })
      }
    },
    
    handleAllSubmissionsReceived() {
      // All submissions received, usually the game will progress automatically
      this.$store.commit('ui/SET_STATUS', 'All bribes submitted, waiting for next phase...')
    }
  }
}
</script>

<style scoped>
/* Styles will be migrated from current game.css */
</style>
```

### 5.3 Migrate Voting Phase Component

```vue
<!-- components/game/VotingPhase.vue -->
<template>
  <div class="voting-phase">
    <h2>Vote for the Best Bribe</h2>
    <p>Round {{ currentRound }} of {{ totalRounds }}</p>
    
    <div class="prompt-display">
      <h3>{{ currentPrompt }}</h3>
      <p v-if="promptTarget">For: {{ promptTarget.username }}</p>
    </div>
    
    <div class="bribes-container">
      <div 
        v-for="(bribe, index) in bribes" 
        :key="index"
        :class="['bribe-option', { selected: selectedVote === bribe.submission_id }]" 
        @click="selectBribe(bribe.submission_id, $event)">
        
        <!-- Text bribe -->
        <div v-if="bribe.type === 'text'" class="bribe-content text-bribe">
          {{ bribe.content }}
        </div>
        
        <!-- Image bribe -->
        <div v-else-if="bribe.type === 'image'" class="bribe-content image-bribe">
          <img :src="bribe.content" alt="Bribe Image">
        </div>
        
        <!-- GIF bribe -->
        <div v-else-if="bribe.type === 'gif'" class="bribe-content gif-bribe">
          <img :src="bribe.content" alt="Bribe GIF" class="gif-content">
        </div>
      </div>
    </div>
    
    <button 
      class="submit-vote-btn" 
      :disabled="!selectedVote" 
      @click="submitVote">
      Submit Vote
    </button>
  </div>
</template>

<script>
import { mapState } from 'vuex'
import socketService from '@/services/socket'

export default {
  name: 'VotingPhase',
  
  data() {
    return {
      bribes: [],
      currentPrompt: '',
      promptTarget: null,
      selectedVote: null,
      hasVoted: false
    }
  },
  
  computed: {
    ...mapState('game', ['currentRound', 'totalRounds'])
  },
  
  created() {
    // Initialize socket handlers
    socketService.socket.on('voting_phase', this.handleVotingPhase)
    socketService.socket.on('vote_registered', this.handleVoteRegistered)
    socketService.socket.on('all_votes_received', this.handleAllVotesReceived)
  },
  
  beforeUnmount() {
    // Clean up socket handlers
    socketService.socket.off('voting_phase', this.handleVotingPhase)
    socketService.socket.off('vote_registered', this.handleVoteRegistered)
    socketService.socket.off('all_votes_received', this.handleAllVotesReceived)
    
    // Reset component state
    this.resetState()
  },
  
  methods: {
    handleVotingPhase(data) {
      this.bribes = data.submissions || []
      this.currentPrompt = data.prompt || ''
      this.promptTarget = data.target || null
      this.hasVoted = false
      this.selectedVote = null
    },
    
    selectBribe(submissionId, event) {
      if (this.hasVoted) return
      
      this.selectedVote = submissionId
      
      // Update UI
      document.querySelectorAll('.bribe-option').forEach(el => {
        el.classList.remove('selected')
      })
      event.currentTarget.classList.add('selected')
    },
    
    submitVote() {
      if (!this.selectedVote || this.hasVoted) return
      
      socketService.socket.emit('submit_vote', {
        game_id: this.$store.state.auth.gameId,
        player_id: this.$store.state.auth.playerId,
        submission_id: this.selectedVote
      })
      
      this.hasVoted = true
      this.$store.commit('ui/SET_STATUS', 'Vote submitted, waiting for others...')
    },
    
    handleVoteRegistered(data) {
      if (data.player_id === this.$store.state.auth.playerId) {
        this.hasVoted = true
      }
    },
    
    handleAllVotesReceived() {
      this.$store.commit('ui/SET_STATUS', 'All votes received, calculating results...')
    },
    
    resetState() {
      this.bribes = []
      this.currentPrompt = ''
      this.promptTarget = null
      this.selectedVote = null
      this.hasVoted = false
    }
  }
}
</script>

<style scoped>
/* Styles will be migrated from current game.css */
</style>
```

### 5.4 Migrate Scoreboard Phase Component

```vue
<!-- components/game/ScoreboardPhase.vue -->
<template>
  <div class="scoreboard-phase">
    <h2>Round Results</h2>
    <p>Round {{ currentRound }} of {{ totalRounds }}</p>
    
    <div class="winner-display" v-if="roundWinner">
      <h3>Winning Bribe</h3>
      <div class="winning-prompt">{{ roundWinner.prompt }}</div>
      
      <div class="winning-submission">
        <!-- Text submission -->
        <div v-if="roundWinner.type === 'text'" class="text-submission">
          {{ roundWinner.content }}
        </div>
        
        <!-- Image submission -->
        <div v-else-if="roundWinner.type === 'image'" class="image-submission">
          <img :src="roundWinner.content" alt="Winning image">
        </div>
        
        <!-- GIF submission -->
        <div v-else-if="roundWinner.type === 'gif'" class="gif-submission">
          <img :src="roundWinner.content" alt="Winning GIF" class="gif-content">
        </div>
      </div>
      
      <div class="winner-info">
        <div class="submitted-by">Submitted by: {{ roundWinner.submitter }}</div>
        <div class="won-for">Won for: {{ roundWinner.target }}</div>
        <div class="vote-count">{{ roundWinner.vote_count }} vote{{ roundWinner.vote_count !== 1 ? 's' : '' }}</div>
      </div>
    </div>
    
    <div class="scoreboard">
      <h3>Scoreboard</h3>
      <div class="score-list">
        <div 
          v-for="player in scoreboard" 
          :key="player.player_id"
          class="score-item">
          <div class="player-name">{{ player.username }}</div>
          <div class="player-score">
            <div class="scores">
              <div v-if="player.round_score > 0" class="round-score">+{{ player.round_score }}</div>
              <div class="total-score">{{ player.total_score }} pts</div>
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <!-- Host controls -->
    <div v-if="isHost && !autoProgress" class="host-controls">
      <button @click="nextRound" class="next-round-btn">
        {{ isLastRound ? 'Show Final Results' : 'Next Round' }}
      </button>
    </div>
    
    <!-- Timer for auto-progress -->
    <div v-if="autoProgress && timerSeconds > 0" class="auto-progress">
      <p>Next round in: {{ timerSeconds }} seconds</p>
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
      roundWinner: null,
      scoreboard: [],
      autoProgress: false,
      timerSeconds: 0,
      timerInterval: null
    }
  },
  
  computed: {
    ...mapState('auth', ['isHost']),
    ...mapState('game', ['currentRound', 'totalRounds']),
    
    isLastRound() {
      return this.currentRound >= this.totalRounds
    }
  },
  
  created() {
    // Initialize socket handlers
    socketService.socket.on('round_results', this.handleRoundResults)
  },
  
  beforeUnmount() {
    // Clean up socket handlers
    socketService.socket.off('round_results', this.handleRoundResults)
    
    // Clear timer if active
    this.clearTimer()
  },
  
  methods: {
    handleRoundResults(data) {
      this.roundWinner = data.winner
      this.scoreboard = data.scoreboard
      this.autoProgress = data.auto_progress || false
      
      // Set up auto-progress timer if enabled
      if (this.autoProgress && data.next_phase_in) {
        this.startTimer(data.next_phase_in)
      }
    },
    
    nextRound() {
      socketService.socket.emit('next_round', {
        game_id: this.$store.state.auth.gameId
      })
    },
    
    startTimer(seconds) {
      this.timerSeconds = seconds
      
      this.clearTimer() // Clear any existing timer
      
      this.timerInterval = setInterval(() => {
        this.timerSeconds--
        
        if (this.timerSeconds <= 0) {
          this.clearTimer()
        }
      }, 1000)
    },
    
    clearTimer() {
      if (this.timerInterval) {
        clearInterval(this.timerInterval)
        this.timerInterval = null
      }
    }
  }
}
</script>

<style scoped>
/* Styles will be migrated from current game.css */
</style>
```

### 5.5 Migrate Final Results Component

```vue
<!-- components/game/FinalResults.vue -->
<template>
  <div class="final-results">
    <h2>Game Over</h2>
    
    <div class="winner-announcement" v-if="gameWinner">
      <div class="confetti-container" ref="confettiContainer"></div>
      <h3>{{ gameWinner.username }} Wins!</h3>
      <div class="winner-score">{{ gameWinner.total_score }} points</div>
    </div>
    
    <div class="final-scoreboard">
      <h3>Final Scores</h3>
      <div class="score-list">
        <div 
          v-for="(player, index) in finalScoreboard" 
          :key="player.player_id"
          :class="['score-item', player.podium_position ? `podium-${player.podium_position}` : '']">
          <div class="player-name">
            <span class="position-indicator">
              {{ getPodiumSymbol(player.podium_position) || `${index + 1}.` }}
            </span>
            {{ player.username }}
          </div>
          <div class="player-score">
            <div class="total-score">{{ player.total_score }} pts</div>
          </div>
        </div>
      </div>
    </div>
    
    <!-- Host controls -->
    <div v-if="isHost" class="host-controls">
      <button @click="playAgain" class="play-again-btn">Play Again</button>
      <button @click="backToLobby" class="back-to-lobby-btn">Back to Lobby</button>
    </div>
  </div>
</template>

<script>
import { mapState } from 'vuex'
import socketService from '@/services/socket'

export default {
  name: 'FinalResults',
  
  data() {
    return {
      finalScoreboard: [],
      gameWinner: null,
      confetti: null
    }
  },
  
  computed: {
    ...mapState('auth', ['isHost'])
  },
  
  created() {
    // Initialize socket handlers
    socketService.socket.on('game_over', this.handleGameOver)
  },
  
  beforeUnmount() {
    // Clean up socket handlers
    socketService.socket.off('game_over', this.handleGameOver)
    
    // Clean up confetti
    if (this.confetti) {
      this.confetti.reset()
    }
  },
  
  methods: {
    handleGameOver(data) {
      this.finalScoreboard = data.final_scoreboard || []
      
      // Find game winner (player with highest score)
      if (this.finalScoreboard.length > 0) {
        this.gameWinner = this.finalScoreboard.find(player => player.podium_position === 1) || 
                          this.finalScoreboard[0]
      }
      
      // Start confetti animation after DOM is updated
      this.$nextTick(() => {
        this.startConfetti()
      })
    },
    
    getPodiumSymbol(position) {
      if (position === 1) return '🥇'
      if (position === 2) return '🥈'
      if (position === 3) return '🥉'
      return null
    },
    
    playAgain() {
      socketService.socket.emit('play_again', {
        game_id: this.$store.state.auth.gameId
      })
    },
    
    backToLobby() {
      socketService.socket.emit('back_to_lobby', {
        game_id: this.$store.state.auth.gameId
      })
    },
    
    startConfetti() {
      // Import and initialize confetti library (optional)
      // This would require installing a confetti library via npm
      // Example: npm install canvas-confetti
      if (window.confetti) {
        this.confetti = window.confetti(this.$refs.confettiContainer, {
          particleCount: 100,
          spread: 70,
          origin: { y: 0.6 }
        })
      }
    }
  }
}
</script>

<style scoped>
/* Styles will be migrated from current game.css */
</style>
```

### 5.6 Migrate Waiting Screen Component

```vue
<!-- components/game/WaitingScreen.vue -->
<template>
  <div class="waiting-screen">
    <div class="waiting-content">
      <div class="waiting-spinner"></div>
      <h2>{{ message }}</h2>
      <p v-if="currentRound > 0">Current Round: {{ currentRound }} / {{ totalRounds }}</p>
      <p v-if="gamePhase">Game Phase: {{ formatGamePhase(gamePhase) }}</p>
    </div>
  </div>
</template>

<script>
import { mapState } from 'vuex'

export default {
  name: 'WaitingScreen',
  
  props: {
    message: {
      type: String,
      default: 'Waiting for the next round to begin...'
    }
  },
  
  computed: {
    ...mapState('game', ['currentRound', 'totalRounds', 'phase']),
    
    gamePhase() {
      return this.phase
    }
  },
  
  methods: {
    formatGamePhase(phase) {
      // Convert snake_case to Title Case with spaces
      if (!phase) return ''
      
      return phase
        .split('_')
        .map(word => word.charAt(0).toUpperCase() + word.slice(1))
        .join(' ')
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
  min-height: 300px;
  text-align: center;
  padding: 2rem;
}

.waiting-spinner {
  width: 50px;
  height: 50px;
  border: 5px solid #f3f3f3;
  border-top: 5px solid #3498db;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 1rem;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}
</style>
```

### 5.7 Migrate Image Uploader Component

```vue
<!-- components/common/ImageUploader.vue -->
<template>
  <div class="image-uploader">
    <div 
      :id="`drop-area-${id}`"
      class="drop-area" 
      :class="{ dragover: isDragging, 'has-image': hasImage }"
      @dragenter.prevent="onDragEnter"
      @dragover.prevent="onDragOver"
      @dragleave.prevent="onDragLeave"
      @drop.prevent="onDrop">
      
      <!-- Loading state -->
      <div v-if="isLoading" class="upload-loading">
        <div class="spinner"></div>
        <span>Processing image...</span>
      </div>
      
      <!-- Error state -->
      <div v-else-if="error" class="upload-error">
        <span>{{ error }}</span>
      </div>
      
      <!-- Preview state -->
      <div v-else-if="imagePreview" class="image-preview">
        <img :src="imagePreview" :class="{ 'gif-preview': isGif }" :alt="`Uploaded ${isGif ? 'GIF' : 'image'}`">
      </div>
      
      <!-- Default state -->
      <div v-else class="upload-prompt">
        <p>Drag & drop an image here</p>
        <span>or</span>
        <button class="upload-button" @click="triggerFileInput">
          Choose File
        </button>
      </div>
    </div>
    
    <!-- Hidden file input -->
    <input 
      :id="`file-input-${id}`" 
      ref="fileInput"
      type="file" 
      class="file-input" 
      accept="image/*" 
      @change="onFileChange">
  </div>
</template>

<script>
import imageProcessing from '@/utils/image-processing'

export default {
  name: 'ImageUploader',
  
  props: {
    id: {
      type: String,
      required: true
    }
  },
  
  data() {
    return {
      isDragging: false,
      isLoading: false,
      error: null,
      imagePreview: null,
      isGif: false,
      dragCounter: 0
    }
  },
  
  computed: {
    hasImage() {
      return !!this.imagePreview
    }
  },
  
  methods: {
    // Drag and drop handlers
    onDragEnter(event) {
      this.dragCounter++
      this.isDragging = true
    },
    
    onDragOver(event) {
      event.preventDefault()
      this.isDragging = true
    },
    
    onDragLeave(event) {
      this.dragCounter--
      if (this.dragCounter === 0) {
        this.isDragging = false
      }
    },
    
    onDrop(event) {
      this.dragCounter = 0
      this.isDragging = false
      
      const files = event.dataTransfer.files
      if (files.length > 0) {
        this.processFile(files[0])
      }
    },
    
    triggerFileInput() {
      this.$refs.fileInput.click()
    },
    
    onFileChange(event) {
      const files = event.target.files
      if (files.length > 0) {
        this.processFile(files[0])
      }
    },
    
    async processFile(file) {
      this.isLoading = true
      this.error = null
      this.imagePreview = null
      
      try {
        const result = await imageProcessing.processImage(file)
        
        if (result.error) {
          this.error = result.error
          this.isLoading = false
          return
        }
        
        this.isGif = result.type === 'gif'
        this.imagePreview = result.content
        
        // Emit the result to parent component
        this.$emit('image-uploaded', {
          content: result.content,
          type: result.type
        })
      } catch (error) {
        console.error('Image processing error:', error)
        this.error = 'Failed to process image. Please try another.'
      } finally {
        this.isLoading = false
      }
    },
    
    reset() {
      this.error = null
      this.imagePreview = null
      this.isLoading = false
      this.isGif = false
      this.dragCounter = 0
      this.isDragging = false
      
      // Reset file input
      if (this.$refs.fileInput) {
        this.$refs.fileInput.value = ''
      }
    }
  }
}
</script>

<style scoped>
.image-uploader {
  width: 100%;
  margin-bottom: 1rem;
}

.drop-area {
  border: 2px dashed #ccc;
  border-radius: 8px;
  padding: 1.5rem;
  text-align: center;
  cursor: pointer;
  transition: all 0.3s ease;
  background-color: #f9f9f9;
  position: relative;
  min-height: 150px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.drop-area.dragover {
  border-color: #3498db;
  background-color: rgba(52, 152, 219, 0.1);
}

.drop-area.has-image {
  border-style: solid;
  border-color: #2ecc71;
}

.file-input {
  display: none;
}

.upload-button {
  background-color: #3498db;
  color: white;
  padding: 0.5rem 1rem;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  margin-top: 0.5rem;
}

.upload-prompt {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.upload-prompt p {
  margin-bottom: 0.5rem;
}

.image-preview {
  width: 100%;
  display: flex;
  justify-content: center;
}

.image-preview img {
  max-width: 100%;
  max-height: 250px;
  object-fit: contain;
}

.gif-preview {
  max-height: 200px;
}

.upload-loading {
  display: flex;
  flex-direction: column;
  align-items: center;
  color: #3498db;
}

.spinner {
  width: 30px;
  height: 30px;
  border: 3px solid #f3f3f3;
  border-top: 3px solid #3498db;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 0.5rem;
}

.upload-error {
  color: #e74c3c;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}
</style>
```

---

## 6. Migration Phase 3: State Management

This phase focuses on ensuring proper state management throughout the application.

### 6.1 Enhance Vuex Store with Socket Events

Update the socket service to better integrate with the Vuex store:

```javascript
// services/socket.js
import { io } from 'socket.io-client'
import store from '@/store'

class SocketService {
  constructor() {
    this.socket = null
    this.reconnectAttempts = 0
    this.maxReconnectAttempts = 5
  }

  init() {
    this.socket = io(process.env.VUE_APP_API_URL, {
      transports: ['websocket', 'polling'],
      reconnection: true,
      reconnectionDelay: 1000,
      reconnectionDelayMax: 5000,
      reconnectionAttempts: this.maxReconnectAttempts
    })

    this._setupListeners()
    return this.socket
  }

  _setupListeners() {
    // Connection events
    this.socket.on('connect', () => {
      store.commit('ui/SET_CONNECTION', true)
      store.commit('ui/SET_STATUS', 'Connected')
      this.reconnectAttempts = 0
    })

    this.socket.on('disconnect', () => {
      store.commit('ui/SET_CONNECTION', false)
      store.commit('ui/SET_STATUS', 'Disconnected')
    })

    this.socket.on('reconnect_attempt', (attempt) => {
      this.reconnectAttempts = attempt
      store.commit('ui/SET_STATUS', `Reconnecting (${attempt}/${this.maxReconnectAttempts})...`)
    })

    // Game events
    this.socket.on('joined_game', (data) => {
      store.dispatch('auth/updateFromServer', data)
      store.dispatch('game/updateGameState', {
        phase: data.game_state,
        currentRound: data.current_round,
        totalRounds: data.total_rounds
      })
    })

    // Lobby events
    this.socket.on('lobby_update', (data) => {
      store.commit('game/SET_PLAYERS', data.players)
      store.commit('game/SET_PHASE', 'lobby')
    })

    // Game phase events
    this.socket.on('game_started', (data) => {
      store.dispatch('game/updateGameState', {
        phase: 'game_started',
        currentRound: data.current_round,
        totalRounds: data.total_rounds
      })
    })

    this.socket.on('prompt_selection', (data) => {
      store.commit('game/SET_PHASE', 'prompt_selection')
      store.commit('ui/SET_STATUS', 'Select a prompt')
    })

    this.socket.on('submission_phase', (data) => {
      store.commit('game/SET_PHASE', 'submission')
      store.commit('game/SET_TARGETS', data.targets)
      store.commit('ui/SET_STATUS', 'Submit your bribes')
      
      // Set timer if provided
      if (data.time_limit) {
        store.commit('ui/SET_TIMER', data.time_limit)
        store.commit('ui/SET_TIMER_ACTIVE', true)
      } else {
        store.commit('ui/SET_TIMER_ACTIVE', false)
      }
    })

    this.socket.on('voting_phase', (data) => {
      store.commit('game/SET_PHASE', 'voting')
      store.commit('ui/SET_STATUS', 'Vote for the best bribe')
      
      // Set timer if provided
      if (data.time_limit) {
        store.commit('ui/SET_TIMER', data.time_limit)
        store.commit('ui/SET_TIMER_ACTIVE', true)
      } else {
        store.commit('ui/SET_TIMER_ACTIVE', false)
      }
    })

    this.socket.on('round_results', (data) => {
      store.commit('game/SET_PHASE', 'results')
      store.commit('game/SET_SCOREBOARD', data.scoreboard)
      store.commit('ui/SET_STATUS', 'Round results')
      
      // Set timer if auto-progress is enabled
      if (data.auto_progress && data.next_phase_in) {
        store.commit('ui/SET_TIMER', data.next_phase_in)
        store.commit('ui/SET_TIMER_ACTIVE', true)
      } else {
        store.commit('ui/SET_TIMER_ACTIVE', false)
      }
    })

    this.socket.on('game_over', (data) => {
      store.commit('game/SET_PHASE', 'game_over')
      store.commit('game/SET_SCOREBOARD', data.final_scoreboard)
      store.commit('ui/SET_STATUS', 'Game over')
      store.commit('ui/SET_TIMER_ACTIVE', false)
    })

    // Midgame joining
    this.socket.on('midgame_waiting', (data) => {
      store.commit('game/SET_PHASE', 'waiting')
      store.commit('ui/SET_STATUS', data.message || 'Waiting for next round')
      store.dispatch('game/updateGameState', {
        currentRound: data.current_round,
        totalRounds: data.total_rounds
      })
    })

    // Error events
    this.socket.on('error', (data) => {
      store.commit('ui/SET_STATUS', data.message || 'An error occurred')
      if (data.error_type === 'auth_error') {
        store.dispatch('auth/clearAuth')
      }
    })
  }

  // Socket API methods
  joinGame(gameId, username, playerId) {
    this.socket.emit('join_game', {
      game_id: gameId,
      username,
      player_id: playerId
    })
  }

  createGame(username, settings) {
    this.socket.emit('create_game', {
      username,
      settings
    })
  }

  startGame(gameId) {
    this.socket.emit('start_game', {
      game_id: gameId
    })
  }

  submitBribe(gameId, playerId, targetId, content, type) {
    this.socket.emit('submit_bribe', {
      game_id: gameId,
      player_id: playerId,
      target_id: targetId,
      content,
      type
    })
  }

  submitVote(gameId, playerId, submissionId) {
    this.socket.emit('submit_vote', {
      game_id: gameId,
      player_id: playerId,
      submission_id: submissionId
    })
  }

  nextRound(gameId) {
    this.socket.emit('next_round', {
      game_id: gameId
    })
  }

  disconnect() {
    if (this.socket) {
      this.socket.disconnect()
    }
  }
}

export default new SocketService()
```

### 6.2 Enhance Auth Module

```javascript
// store/modules/auth.js
import authService from '@/services/auth'

export default {
  namespaced: true,
  
  state: {
    playerId: null,
    username: null,
    isHost: false,
    gameId: null,
    isAuthenticated: false
  },
  
  mutations: {
    SET_PLAYER_ID(state, id) {
      state.playerId = id
    },
    SET_USERNAME(state, name) {
      state.username = name
    },
    SET_HOST(state, isHost) {
      state.isHost = isHost
    },
    SET_GAME_ID(state, id) {
      state.gameId = id
    },
    SET_AUTHENTICATED(state, value) {
      state.isAuthenticated = value
    },
    CLEAR_AUTH(state) {
      state.playerId = null
      state.username = null
      state.isHost = false
      state.gameId = null
      state.isAuthenticated = false
    }
  },
  
  actions: {
    async initAuth({ commit, dispatch }, gameId) {
      const authData = authService.loadAuthState(gameId)
      if (authData) {
        commit('SET_PLAYER_ID', authData.playerId)
        commit('SET_USERNAME', authData.username)
        commit('SET_HOST', authData.isHost)
        commit('SET_GAME_ID', gameId)
        commit('SET_AUTHENTICATED', true)
        return true
      }
      return false
    },
    
    saveAuth({ state }) {
      if (state.gameId) {
        authService.saveAuthState(state.gameId, {
          playerId: state.playerId,
          username: state.username,
          isHost: state.isHost
        })
      }
    },
    
    clearAuth({ commit }) {
      commit('CLEAR_AUTH')
    },
    
    updateFromServer({ commit, dispatch, state }, data) {
      // Update with server-provided values
      if (data.player_id) {
        commit('SET_PLAYER_ID', data.player_id)
      }
      
      if (data.username && (!state.username || state.username === '')) {
        commit('SET_USERNAME', data.username)
      }
      
      if (data.is_host !== undefined) {
        commit('SET_HOST', !!data.is_host)
      }
      
      if (data.game_id) {
        commit('SET_GAME_ID', data.game_id)
      }
      
      commit('SET_AUTHENTICATED', true)
      
      // Save updated auth state
      dispatch('saveAuth')
    }
  }
}
```

### 6.3 Enhance Game Module

```javascript
// store/modules/game.js
export default {
  namespaced: true,
  
  state: {
    phase: 'connecting',  // connecting, lobby, prompt_selection, submission, voting, results, game_over, waiting
    currentRound: 0,
    totalRounds: 0,
    players: [],
    currentTargets: [],
    submissions: {},
    selectedVote: null,
    scoreboard: [],
    settings: null
  },
  
  mutations: {
    SET_PHASE(state, phase) {
      state.phase = phase
    },
    SET_ROUND_INFO(state, { current, total }) {
      state.currentRound = current
      state.totalRounds = total
    },
    SET_PLAYERS(state, players) {
      state.players = players
    },
    SET_TARGETS(state, targets) {
      state.currentTargets = targets
    },
    SET_SUBMISSIONS(state, submissions) {
      state.submissions = submissions
    },
    SET_SELECTED_VOTE(state, voteId) {
      state.selectedVote = voteId
    },
    SET_SCOREBOARD(state, scoreboard) {
      state.scoreboard = scoreboard
    },
    SET_SETTINGS(state, settings) {
      state.settings = settings
    },
    RESET_PHASE_DATA(state) {
      // Reset phase-specific data when changing phases
      state.selectedVote = null
      state.submissions = {}
    }
  },
  
  actions: {
    updateGameState({ commit }, data) {
      if (data.phase) {
        commit('SET_PHASE', data.phase)
        commit('RESET_PHASE_DATA')
      }
      
      if (data.currentRound !== undefined && data.totalRounds !== undefined) {
        commit('SET_ROUND_INFO', { 
          current: data.currentRound, 
          total: data.totalRounds 
        })
      }
      
      if (data.players) {
        commit('SET_PLAYERS', data.players)
      }
      
      if (data.settings) {
        commit('SET_SETTINGS', data.settings)
      }
    },
    
    selectVote({ commit }, submissionId) {
      commit('SET_SELECTED_VOTE', submissionId)
    },
    
    addSubmission({ commit, state }, { targetId, submission }) {
      const submissions = { ...state.submissions }
      submissions[targetId] = submission
      commit('SET_SUBMISSIONS', submissions)
    },
    
    markSubmitted({ commit, state }, targetId) {
      const submissions = { ...state.submissions }
      if (submissions[targetId]) {
        submissions[targetId].submitted = true
        commit('SET_SUBMISSIONS', submissions)
      }
    }
  }
}
```

### 6.4 Enhance UI Module

```javascript
// store/modules/ui.js
export default {
  namespaced: true,
  
  state: {
    statusMessage: 'Connecting...',
    isConnected: false,
    timerValue: 0,
    timerActive: false,
    timerInterval: null,
    timerEndTime: 0,
    activeDialog: null
  },
  
  mutations: {
    SET_STATUS(state, message) {
      state.statusMessage = message
    },
    SET_CONNECTION(state, isConnected) {
      state.isConnected = isConnected
    },
    SET_TIMER(state, value) {
      state.timerValue = value
      state.timerEndTime = Date.now() + (value * 1000)
    },
    SET_TIMER_ACTIVE(state, active) {
      state.timerActive = active
    },
    SET_TIMER_INTERVAL(state, interval) {
      state.timerInterval = interval
    },
    DECREMENT_TIMER(state) {
      if (state.timerValue > 0) {
        state.timerValue--
      }
    },
    SET_ACTIVE_DIALOG(state, dialog) {
      state.activeDialog = dialog
    },
    CLEAR_TIMER(state) {
      if (state.timerInterval) {
        clearInterval(state.timerInterval)
        state.timerInterval = null
      }
      state.timerActive = false
    }
  },
  
  actions: {
    startTimer({ commit, state, dispatch }, seconds) {
      // Clear any existing timer
      dispatch('stopTimer')
      
      // Set initial timer value
      commit('SET_TIMER', seconds)
      commit('SET_TIMER_ACTIVE', true)
      
      // Start interval to update timer
      const interval = setInterval(() => {
        commit('DECREMENT_TIMER')
        
        if (state.timerValue <= 0) {
          dispatch('stopTimer')
        }
      }, 1000)
      
      commit('SET_TIMER_INTERVAL', interval)
    },
    
    stopTimer({ commit }) {
      commit('CLEAR_TIMER')
    },
    
    showDialog({ commit }, dialog) {
      commit('SET_ACTIVE_DIALOG', dialog)
    },
    
    hideDialog({ commit }) {
      commit('SET_ACTIVE_DIALOG', null)
    }
  }
}
```

### 6.5 Finalize Store Configuration

```javascript
// store/index.js
import { createStore } from 'vuex'
import auth from './modules/auth'
import game from './modules/game'
import ui from './modules/ui'

export default createStore({
  modules: {
    auth,
    game,
    ui
  },
  
  // Global actions for cross-module operations
  actions: {
    resetGame({ commit, dispatch }) {
      commit('game/SET_PHASE', 'lobby')
      commit('game/RESET_PHASE_DATA')
      commit('ui/SET_STATUS', 'Back to lobby')
      dispatch('ui/stopTimer')
    }
  }
})
```

---

## 7. Migration Phase 4: Testing & Optimization

This phase focuses on ensuring the migrated application works correctly and optimizing its performance.

### 7.1 Set Up Testing Environment

Install testing libraries:

```powershell
npm install --save-dev @vue/test-utils jest @vue/vue3-jest babel-jest @babel/preset-env jest-environment-jsdom
```

Configure Jest in `jest.config.js`:

```javascript
module.exports = {
  testEnvironment: 'jsdom',
  transform: {
    '^.+\\.vue$': '@vue/vue3-jest',
    '^.+\\.js$': 'babel-jest'
  },
  moduleFileExtensions: ['vue', 'js', 'json', 'jsx'],
  moduleNameMapper: {
    '^@/(.*)$': '<rootDir>/src/$1'
  },
  testMatch: [
    '**/tests/unit/**/*.spec.js'
  ],
  transformIgnorePatterns: ['/node_modules/(?!vue-socket.io)']
}
```

Configure Babel in `babel.config.js`:

```javascript
module.exports = {
  presets: [
    '@vue/cli-plugin-babel/preset',
    '@babel/preset-env'
  ]
}
```

### 7.2 Create Unit Tests

Create tests for key components and services:

```javascript
// tests/unit/services/auth.spec.js
import authService from '@/services/auth'

describe('Auth Service', () => {
  beforeEach(() => {
    // Clear localStorage before each test
    localStorage.clear()
  })
  
  it('saves auth state to localStorage', () => {
    const gameId = 'test-game'
    const authData = {
      playerId: 'player-123',
      username: 'TestUser',
      isHost: true
    }
    
    const result = authService.saveAuthState(gameId, authData)
    
    expect(result).toBe(true)
    
    // Check that data was saved correctly
    const storedData = JSON.parse(localStorage.getItem(`bribery_game_${gameId}`))
    expect(storedData.playerId).toBe(authData.playerId)
    expect(storedData.username).toBe(authData.username)
    expect(storedData.isHost).toBe(authData.isHost)
  })
  
  it('loads auth state from localStorage', () => {
    const gameId = 'test-game'
    const authData = {
      playerId: 'player-123',
      username: 'TestUser',
      isHost: true,
      timestamp: Date.now()
    }
    
    // Manually set localStorage
    localStorage.setItem(`bribery_game_${gameId}`, JSON.stringify(authData))
    
    const loadedData = authService.loadAuthState(gameId)
    
    expect(loadedData).not.toBeNull()
    expect(loadedData.playerId).toBe(authData.playerId)
    expect(loadedData.username).toBe(authData.username)
    expect(loadedData.isHost).toBe(authData.isHost)
  })
  
  it('returns null when no auth state exists', () => {
    const gameId = 'nonexistent-game'
    
    const loadedData = authService.loadAuthState(gameId)
    
    expect(loadedData).toBeNull()
  })
})
```

Add more tests for components, store modules, and other services.

### 7.3 Performance Optimization

#### Lazy Loading Routes

Update router configuration to use lazy loading:

```javascript
// router/index.js
import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/',
    name: 'Home',
    component: () => import(/* webpackChunkName: "home" */ '@/views/Home.vue')
  },
  {
    path: '/game/:id',
    name: 'Game',
    component: () => import(/* webpackChunkName: "game" */ '@/views/Game.vue'),
    props: true,
    // beforeEnter guard remains the same
  }
]

const router = createRouter({
  history: createWebHistory(process.env.BASE_URL),
  routes
})

export default router
```

#### Optimize Asset Loading

Add a Vue config for asset optimization:

```javascript
// vue.config.js
module.exports = {
  // ... existing config ...
  
  chainWebpack: config => {
    // Optimize images
    config.module
      .rule('images')
      .use('image-webpack-loader')
      .loader('image-webpack-loader')
      .options({
        bypassOnDebug: true,
        mozjpeg: {
          progressive: true,
          quality: 65
        },
        optipng: {
          enabled: true
        },
        pngquant: {
          quality: [0.65, 0.90],
          speed: 4
        },
        gifsicle: {
          interlaced: false
        },
        webp: {
          quality: 75
        }
      })
  }
}
```

#### Add Prefetching Directives

Update key components to prefetch likely next screens:

```vue
<!-- Example in GameLobby.vue -->
<script>
export default {
  // ... existing component code ...
  
  mounted() {
    // Prefetch likely next components
    const PromptPhase = () => import(/* webpackPrefetch: true */ '@/components/game/PromptPhase.vue')
    const SubmissionPhase = () => import(/* webpackPrefetch: true */ '@/components/game/SubmissionPhase.vue')
  }
}
</script>
```

### 7.4 Cross-Browser Testing

Test the application in multiple browsers and fix any compatibility issues:

1. Chrome
2. Firefox
3. Safari
4. Edge

Focus on:
- Socket.IO connection stability
- CSS compatibility
- Image upload functionality
- localStorage access

### 7.5 Mobile Optimization

Enhance the application for mobile devices:

```css
/* Add to App.vue global styles */
@media (max-width: 768px) {
  .game-container {
    padding: 0.5rem;
  }
  
  .targets-container {
    flex-direction: column;
  }
  
  .target-card {
    width: 100%;
    margin: 0.5rem 0;
  }
  
  .bribes-container {
    grid-template-columns: 1fr;
  }
}
```

Add touch-specific event handlers:

```javascript
// Example for ImageUploader.vue
mounted() {
  // Add touch events for mobile devices
  if ('ontouchstart' in window) {
    this.$el.addEventListener('touchstart', this.handleTouchStart)
    this.$el.addEventListener('touchend', this.handleTouchEnd)
  }
},

beforeUnmount() {
  if ('ontouchstart' in window) {
    this.$el.removeEventListener('touchstart', this.handleTouchStart)
    this.$el.removeEventListener('touchend', this.handleTouchEnd)
  }
},

methods: {
  handleTouchStart(event) {
    // Touch event handling
  },
  
  handleTouchEnd(event) {
    // Touch event handling
  }
}
```

---

## 8. Migration Phase 5: Deployment

This phase focuses on preparing the migrated application for deployment.

### 8.1 Build Configuration

Create production-specific environment variables:

```
# .env.production
VUE_APP_API_URL=
NODE_ENV=production
```

Update `vue.config.js` for production:

```javascript
module.exports = {
  // Output to Flask static directory
  outputDir: '../static/vue',
  
  // Adjust public path for Flask integration
  publicPath: process.env.NODE_ENV === 'production' ? '/static/vue/' : '/',
  
  // Configure dev server for local development
  devServer: {
    proxy: {
      '/socket.io': {
        target: 'http://localhost:5000',
        ws: true,
        changeOrigin: true
      },
      '/api': {
        target: 'http://localhost:5000',
        changeOrigin: true
      }
    }
  },
  
  // Production optimizations
  productionSourceMap: false,
  
  // Other configurations...
}
```

### 8.2 Flask Integration

Update Flask routes to serve the Vue application:

```python
from flask import Flask, render_template, send_from_directory

app = Flask(__name__)

# Serve Vue app for all routes that should use the SPA
@app.route('/')
@app.route('/game/<game_id>')
def vue_app(game_id=None):
    return render_template('vue_app.html')

# Add API endpoint prefix for any backend API routes
@app.route('/api/status')
def api_status():
    return {'status': 'ok'}

# Handle 404 errors by returning the Vue app
@app.errorhandler(404)
def not_found(e):
    return render_template('vue_app.html')
```

### 8.3 Build and Deploy

Build the Vue application:

```powershell
# Navigate to Vue project directory
cd vue-bribery

# Build for production
npm run build
```

Update Flask deployment scripts:

```python
# wsgi.py
from src.web.app import app

if __name__ == '__main__':
    app.run()
```

### 8.4 Docker Integration (Optional)

If using Docker, update the Dockerfile:

```dockerfile
# Use multi-stage build for frontend
FROM node:16 as frontend-build

WORKDIR /app/frontend
COPY vue-bribery/package*.json ./
RUN npm install
COPY vue-bribery/ ./
RUN npm run build

# Python stage
FROM python:3.9-slim

WORKDIR /app

# Copy Python requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy Python code
COPY src/ ./src/
COPY wsgi.py .

# Copy built frontend from previous stage
COPY --from=frontend-build /app/frontend/dist /app/static/vue

# Set environment variables
ENV FLASK_APP=wsgi.py
ENV FLASK_ENV=production

EXPOSE 5000

CMD ["gunicorn", "--worker-class", "eventlet", "-w", "1", "-b", "0.0.0.0:5000", "wsgi:app"]
```

### 8.5 Monitoring and Analytics

Add basic analytics and monitoring:

```javascript
// main.js
import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import store from './store'

// Simple error tracking
if (process.env.NODE_ENV === 'production') {
  window.addEventListener('error', (event) => {
    // Log error to server or analytics
    console.error('Application error:', event.error)
    
    // Could send to a logging endpoint
    // fetch('/api/log', {
    //   method: 'POST',
    //   body: JSON.stringify({
    //     type: 'error',
    //     message: event.message,
    //     stack: event.error?.stack,
    //     location: window.location.href
    //   })
    // })
  })
  
  // Track page views
  router.afterEach((to) => {
    // Could send to analytics
    console.log('Page view:', to.fullPath)
  })
}

createApp(App)
  .use(store)
  .use(router)
  .mount('#app')
```

---

## 9. Common Pitfalls & Solutions

### 9.1 Socket.IO Connection Issues

**Problem:** Socket.IO connection fails after migrating to Vue.

**Solution:**
1. Ensure CORS is properly configured on the Flask backend
2. Check that the Socket.IO client and server versions are compatible
3. Configure the proxy correctly in `vue.config.js`
4. Use the correct transport options:

```javascript
this.socket = io(process.env.VUE_APP_API_URL, {
  transports: ['websocket', 'polling'],
  reconnection: true
})
```

### 9.2 Authentication Persistence Issues

**Problem:** Authentication state is lost after refreshing the page.

**Solution:**
1. Ensure localStorage keys match between old and new code
2. Verify that auth state is properly hydrated on application startup
3. Check for any race conditions in initialization:

```javascript
// In Game.vue
created() {
  // Initialize socket first
  socketService.init()
  
  // Then load auth from localStorage
  const gameId = this.$route.params.id
  this.initAuth(gameId).then(success => {
    if (success) {
      // Only attempt to join after auth is initialized
      socketService.joinGame(gameId, this.username, this.playerId)
    } else {
      this.$router.push('/')
    }
  })
}
```

### 9.3 Component Lifecycle Issues

**Problem:** Components try to access DOM elements before they're available.

**Solution:**
1. Use Vue lifecycle hooks correctly
2. Use `$nextTick` for DOM manipulations after state changes
3. Leverage Vue's reactivity system instead of direct DOM manipulation:

```javascript
// Instead of:
document.getElementById('element').textContent = 'New value'

// Use:
data() {
  return {
    elementText: 'New value'
  }
}
// In template:
<div>{{ elementText }}</div>
```

### 9.4 Vuex State Management Issues

**Problem:** Components don't update when state changes.

**Solution:**
1. Ensure you're using computed properties with mapState
2. Use proper mutation methods to update state
3. Watch for nested objects that need Vue's reactivity:

```javascript
// When updating nested objects in state:
const submissions = { ...state.submissions }
submissions[targetId] = submission
commit('SET_SUBMISSIONS', submissions)

// Instead of:
state.submissions[targetId] = submission // This won't trigger reactivity
```

### 9.5 Image Processing Issues

**Problem:** Image processing and uploads don't work as expected.

**Solution:**
1. Ensure proper error handling in image processing
2. Check for browser compatibility issues with File API
3. Add multiple fallbacks for image display
4. Verify MIME types and content handling:

```javascript
// Add proper error boundaries
try {
  const result = await imageProcessing.processImage(file)
  // Handle success
} catch (error) {
  console.error('Image processing error:', error)
  // Show user-friendly error
}
```

### 9.6 Mobile Safari Issues

**Problem:** Specific issues with Mobile Safari browsers.

**Solution:**
1. Test specifically with iOS Safari
2. Handle touch events properly
3. Be careful with viewport height calculations
4. Add special CSS for iOS:

```css
/* Fix for iOS 100vh issue */
@supports (-webkit-touch-callout: none) {
  .full-height {
    height: -webkit-fill-available;
  }
}
```

---

## 10. Special Considerations for AI Assistants

This section contains important notes for AI assistants who may be helping with this migration process. These tips will help avoid common errors and misunderstandings.

### 10.1 Understanding the Context Window

When implementing or debugging code, keep in mind that the full codebase context is important:

- **Socket.IO Event Flow**: Always consider both client and server sides of Socket.IO events
- **Authentication Flow**: The authentication mechanism spans multiple files and uses both client-side storage and server verification
- **State Management**: Game state is complex and distributed across both client and server

When working on one component, consider how it interacts with the broader system.

### 10.2 Common Migration Mistakes to Avoid

- **Mixing old and new patterns**: Ensure complete migration of a feature before moving to the next
- **Duplicate event listeners**: Socket event handlers should be properly cleaned up with `beforeUnmount`
- **Premature optimization**: Focus on correct functionality first, then optimize
- **Insufficient error handling**: Add proper error boundaries around all async operations
- **Inconsistent state updates**: All state updates should go through Vuex mutations

### 10.3 Testing Guidelines

When testing the migrated application:

- **Test reconnection scenarios**: Close browser tab and reopen
- **Test mid-game joining**: Join an in-progress game with a new player
- **Test various submission types**: Try text, images, and GIFs
- **Test error scenarios**: Disconnect internet during gameplay
- **Test browser compatibility**: Try multiple browsers
- **Test mobile experience**: Verify touch interactions and layout

### 10.4 Special Attention Areas

Certain areas require special attention during migration:

- **Socket handler mapping**: Ensure all socket events from the original code are properly handled
- **Authentication state persistence**: Maintain the same localStorage format for backward compatibility
- **Game phase transitions**: All game phase transitions must be properly implemented
- **Timer management**: Timer functionality should be consistent with the original application
- **Error recovery**: The application should handle disconnections and errors gracefully

### 10.5 Migration Strategy

When implementing this migration:

1. **Start with the foundation**: Core services, router, and store
2. **Implement one game phase at a time**: Complete each phase before moving to the next
3. **Test extensively**: After each component is migrated
4. **Keep both versions running**: Until migration is complete
5. **Migrate static assets last**: After all functionality is working

### 10.6 Context Retrieval Tips

When you need additional context:

- Check related files on both client and server sides
- Look for event names to trace flows through the application
- Refer to the original implementation for business logic details
- Check commit history if available for recent changes
- Review server-side handlers to understand expected data formats

By following this comprehensive guide, you can successfully migrate the Bribery game from vanilla JavaScript to a modern Vue.js implementation while maintaining all functionality and improving the codebase.
