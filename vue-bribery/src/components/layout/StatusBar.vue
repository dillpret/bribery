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
.status-bar {
  height: var(--status-bar-height);
  background-color: #f0f0f0;
  border-bottom: 1px solid #ddd;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 16px;
  font-size: 0.9rem;
}

.timer {
  font-weight: bold;
  font-family: monospace;
}
</style>
