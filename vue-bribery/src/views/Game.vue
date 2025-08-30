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
import PlayerListPanel from '@/components/common/PlayerListPanel.vue'
import GameLobby from '@/components/game/GameLobby.vue'
import PromptPhase from '@/components/game/PromptPhase.vue'
import SubmissionPhase from '@/components/game/SubmissionPhase.vue'
import VotingPhase from '@/components/game/VotingPhase.vue'
import ScoreboardPhase from '@/components/game/ScoreboardPhase.vue'
import WaitingScreen from '@/components/game/WaitingScreen.vue'
import ConnectionError from '@/components/game/ConnectionError.vue'

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
    ...mapState('game', ['phase']),
    ...mapState('ui', ['statusMessage', 'timerValue']),
    
    currentPhase() {
      return this.phase || 'connecting'
    }
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
.game-container {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
  background-color: var(--background-color);
}
</style>
