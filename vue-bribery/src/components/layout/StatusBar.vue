<template>
  <div class="status-bar" :class="{ 'has-timer': timerActive }">
    <div class="game-status">{{ message }}</div>
    <Timer v-if="timerActive" :seconds="timer" class="status-timer" />
  </div>
</template>

<script>
import { Timer } from '@/components/common'

export default {
  name: 'StatusBar',
  
  components: {
    Timer
  },
  
  props: {
    message: {
      type: String,
      default: ''
    },
    timer: {
      type: Number,
      default: 0
    },
    timerActive: {
      type: Boolean,
      default: false
    }
  }
}
</script>

<style scoped>
.status-bar {
  height: var(--status-bar-height, 40px);
  background-color: #f0f0f0;
  border-bottom: 1px solid #ddd;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 16px;
  font-size: 0.9rem;
  transition: all 0.3s ease;
}

.status-bar.has-timer {
  background-color: #e9f5ff;
}

.status-timer {
  font-weight: bold;
  font-family: monospace;
}

/* Dark mode support */
:global(.dark-mode) .status-bar {
  background-color: #222;
  border-bottom-color: #444;
  color: #e0e0e0;
}

:global(.dark-mode) .status-bar.has-timer {
  background-color: #1a3045;
}

/* Responsive adjustments */
@media (max-width: 768px) {
  .status-bar {
    font-size: 0.8rem;
    padding: 0 10px;
    height: var(--status-bar-height-mobile, 36px);
  }
}
</style>
