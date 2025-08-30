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
.header {
  height: var(--header-height);
  background-color: white;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 16px;
}

.logo-wrapper {
  display: flex;
  align-items: center;
}

.hero-logo {
  height: 40px;
}

.hero-logo-fallback {
  display: none;
  font-size: 1.2rem;
}

.game-info {
  font-size: 0.9rem;
  display: flex;
  align-items: center;
}

@media (max-width: 768px) {
  .hero-logo {
    display: none;
  }
  
  .hero-logo-fallback {
    display: block;
  }
}
</style>
