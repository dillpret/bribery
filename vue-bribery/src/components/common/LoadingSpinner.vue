<template>
  <div class="spinner-container" :class="{ overlay: overlay, fixed: fixed }">
    <div class="spinner" :class="sizeClass">
      <div class="spinner-inner"></div>
    </div>
    <div v-if="message" class="spinner-message">{{ message }}</div>
  </div>
</template>

<script>
export default {
  name: 'LoadingSpinner',
  
  props: {
    size: {
      type: String,
      default: 'medium',
      validator: (value) => ['small', 'medium', 'large'].includes(value)
    },
    overlay: {
      type: Boolean,
      default: false
    },
    fixed: {
      type: Boolean,
      default: false
    },
    message: {
      type: String,
      default: ''
    }
  },
  
  computed: {
    sizeClass() {
      return `spinner-${this.size}`;
    }
  }
}
</script>

<style scoped>
.spinner-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 1rem;
}

.spinner-container.overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(255, 255, 255, 0.8);
  z-index: 100;
}

.spinner-container.fixed {
  position: fixed;
  z-index: 9000;
}

.spinner {
  position: relative;
}

.spinner-inner {
  border-radius: 50%;
  border: 3px solid transparent;
  border-top-color: var(--primary-color, #0080ff);
  border-right-color: var(--primary-color, #0080ff);
  animation: spinner-rotation 1s linear infinite;
}

.spinner-small .spinner-inner {
  width: 20px;
  height: 20px;
  border-width: 2px;
}

.spinner-medium .spinner-inner {
  width: 40px;
  height: 40px;
  border-width: 3px;
}

.spinner-large .spinner-inner {
  width: 60px;
  height: 60px;
  border-width: 4px;
}

.spinner-message {
  margin-top: 1rem;
  font-size: 0.9rem;
  color: #666;
  text-align: center;
}

@keyframes spinner-rotation {
  0% {
    transform: rotate(0deg);
  }
  100% {
    transform: rotate(360deg);
  }
}
</style>
