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
      if (this.seconds <= 0) return '0:00'
      
      const mins = Math.floor(this.seconds / 60)
      const secs = this.seconds % 60
      return `${mins}:${secs.toString().padStart(2, '0')}`
    }
  }
}
</script>

<style scoped>
.timer-component {
  font-family: monospace;
  font-weight: bold;
  padding: 0.5rem 1rem;
  border-radius: 4px;
  background-color: rgba(0, 0, 0, 0.1);
  visibility: hidden;
  opacity: 0;
  transition: opacity 0.3s ease;
}

.timer-component.active {
  visibility: visible;
  opacity: 1;
}

/* Timer colors based on time remaining */
@media (prefers-reduced-motion: no-preference) {
  .timer-component.active {
    animation: pulse 1s infinite alternate;
  }
  
  @keyframes pulse {
    from {
      background-color: rgba(0, 0, 0, 0.1);
    }
    to {
      background-color: rgba(255, 64, 129, 0.2);
    }
  }
}
</style>
