<template>
  <div class="notification-container" :class="positionClass">
    <Notification
      v-for="notification in notifications"
      :key="notification.id"
      :type="notification.type"
      :message="notification.message"
      :title="notification.title"
      :duration="notification.duration"
      :dismissible="notification.dismissible"
      :show-icon="notification.showIcon"
      @close="removeNotification(notification.id)"
    />
  </div>
</template>

<script>
import { ref, computed } from 'vue';
import Notification from './Notification.vue';

export default {
  name: 'NotificationManager',
  
  components: {
    Notification
  },
  
  props: {
    position: {
      type: String,
      default: 'top-right',
      validator: (value) => ['top-left', 'top-right', 'bottom-left', 'bottom-right', 'top-center', 'bottom-center'].includes(value)
    },
    maxNotifications: {
      type: Number,
      default: 5
    }
  },
  
  setup(props) {
    const notifications = ref([]);
    const idCounter = ref(0);
    
    const positionClass = computed(() => `position-${props.position}`);
    
    const addNotification = (notification) => {
      const id = idCounter.value++;
      const newNotification = {
        id,
        type: notification.type || 'info',
        message: notification.message,
        title: notification.title || '',
        duration: notification.duration !== undefined ? notification.duration : 5000,
        dismissible: notification.dismissible !== undefined ? notification.dismissible : true,
        showIcon: notification.showIcon !== undefined ? notification.showIcon : true
      };
      
      // Limit number of notifications
      if (notifications.value.length >= props.maxNotifications) {
        notifications.value.shift();
      }
      
      notifications.value.push(newNotification);
      return id;
    };
    
    const removeNotification = (id) => {
      const index = notifications.value.findIndex(notification => notification.id === id);
      if (index !== -1) {
        notifications.value.splice(index, 1);
      }
    };
    
    const clearAllNotifications = () => {
      notifications.value = [];
    };
    
    return {
      notifications,
      positionClass,
      addNotification,
      removeNotification,
      clearAllNotifications
    };
  }
}
</script>

<style scoped>
.notification-container {
  position: fixed;
  z-index: 9999;
  padding: 1rem;
  display: flex;
  flex-direction: column;
  pointer-events: none;
}

.notification-container :deep(.notification) {
  pointer-events: auto;
}

/* Position variants */
.position-top-right {
  top: 0;
  right: 0;
  align-items: flex-end;
}

.position-top-left {
  top: 0;
  left: 0;
  align-items: flex-start;
}

.position-bottom-right {
  bottom: 0;
  right: 0;
  align-items: flex-end;
}

.position-bottom-left {
  bottom: 0;
  left: 0;
  align-items: flex-start;
}

.position-top-center {
  top: 0;
  left: 50%;
  transform: translateX(-50%);
  align-items: center;
}

.position-bottom-center {
  bottom: 0;
  left: 50%;
  transform: translateX(-50%);
  align-items: center;
}
</style>
