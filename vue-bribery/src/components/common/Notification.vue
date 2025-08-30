<template>
  <transition name="notification-fade">
    <div 
      v-if="isVisible" 
      class="notification" 
      :class="typeClass"
      role="alert"
    >
      <div class="notification-content">
        <div class="notification-icon" v-if="showIcon">
          <svg v-if="type === 'success'" xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24">
            <path d="M9 16.17L4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41z"/>
          </svg>
          <svg v-else-if="type === 'error'" xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24">
            <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 15h-2v-2h2v2zm0-4h-2V7h2v6z"/>
          </svg>
          <svg v-else-if="type === 'warning'" xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24">
            <path d="M1 21h22L12 2 1 21zm12-3h-2v-2h2v2zm0-4h-2v-4h2v4z"/>
          </svg>
          <svg v-else xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24">
            <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 15h-2v-6h2v6zm0-8h-2V7h2v2z"/>
          </svg>
        </div>
        <div class="notification-text">
          <div class="notification-title" v-if="title">{{ title }}</div>
          <div class="notification-message">{{ message }}</div>
        </div>
      </div>
      <button 
        v-if="dismissible" 
        class="notification-close" 
        @click="dismiss"
        aria-label="Close notification"
      >
        <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24">
          <path d="M19 6.41L17.59 5 12 10.59 6.41 5 5 6.41 10.59 12 5 17.59 6.41 19 12 13.41 17.59 19 19 17.59 13.41 12z"/>
        </svg>
      </button>
    </div>
  </transition>
</template>

<script>
import { ref, computed, onMounted, onBeforeUnmount } from 'vue';

export default {
  name: 'Notification',
  
  props: {
    type: {
      type: String,
      default: 'info',
      validator: (value) => ['info', 'success', 'warning', 'error'].includes(value)
    },
    message: {
      type: String,
      required: true
    },
    title: {
      type: String,
      default: ''
    },
    duration: {
      type: Number,
      default: 5000 // 5 seconds
    },
    dismissible: {
      type: Boolean,
      default: true
    },
    showIcon: {
      type: Boolean,
      default: true
    }
  },
  
  emits: ['close'],
  
  setup(props, { emit }) {
    const isVisible = ref(true);
    const timerId = ref(null);
    
    const typeClass = computed(() => `notification-${props.type}`);
    
    const dismiss = () => {
      isVisible.value = false;
      emit('close');
    };
    
    onMounted(() => {
      if (props.duration > 0) {
        timerId.value = setTimeout(() => {
          dismiss();
        }, props.duration);
      }
    });
    
    onBeforeUnmount(() => {
      if (timerId.value) {
        clearTimeout(timerId.value);
      }
    });
    
    return {
      isVisible,
      typeClass,
      dismiss
    };
  }
}
</script>

<style scoped>
.notification {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  width: 100%;
  max-width: 500px;
  padding: 0.75rem 1rem;
  border-radius: 4px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  margin-bottom: 1rem;
  background-color: #fff;
  border-left: 4px solid #ccc;
}

.notification-content {
  display: flex;
  align-items: flex-start;
  flex: 1;
}

.notification-icon {
  margin-right: 0.75rem;
  margin-top: 0.125rem;
}

.notification-icon svg {
  width: 20px;
  height: 20px;
}

.notification-text {
  flex: 1;
}

.notification-title {
  font-weight: 600;
  margin-bottom: 0.25rem;
}

.notification-message {
  font-size: 0.875rem;
  line-height: 1.4;
}

.notification-close {
  background: transparent;
  border: none;
  padding: 0;
  margin-left: 0.5rem;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  opacity: 0.5;
  transition: opacity 0.2s ease;
}

.notification-close:hover {
  opacity: 1;
}

.notification-close svg {
  width: 16px;
  height: 16px;
}

/* Type-specific styles */
.notification-success {
  border-left-color: #4caf50;
}
.notification-success .notification-icon svg {
  fill: #4caf50;
}

.notification-error {
  border-left-color: #f44336;
}
.notification-error .notification-icon svg {
  fill: #f44336;
}

.notification-warning {
  border-left-color: #ff9800;
}
.notification-warning .notification-icon svg {
  fill: #ff9800;
}

.notification-info {
  border-left-color: #2196f3;
}
.notification-info .notification-icon svg {
  fill: #2196f3;
}

/* Animation */
.notification-fade-enter-active,
.notification-fade-leave-active {
  transition: opacity 0.3s, transform 0.3s;
}

.notification-fade-enter-from,
.notification-fade-leave-to {
  opacity: 0;
  transform: translateY(-10px);
}
</style>
