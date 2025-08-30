<template>
  <div id="app">
    <CompatibilityWarning 
      @compatibility-issue="handleCompatibilityIssue"
      @dismiss="compatibilityDismissed" />
    <router-view />
    <NotificationManager ref="notificationManager" position="top-right" />
  </div>
</template>

<script>
import { onMounted, ref } from 'vue';
import NotificationManager from '@/components/common/NotificationManager.vue';
import CompatibilityWarning from '@/components/common/CompatibilityWarning.vue';
import notificationService from '@/services/notification';
import { applyCompatibilityFixes } from '@/services/browser-compatibility';

export default {
  name: 'App',
  
  components: {
    NotificationManager,
    CompatibilityWarning
  },
  
  setup() {
    const notificationManager = ref(null);
    
    // Handle compatibility issues
    const handleCompatibilityIssue = (missingFeatures) => {
      console.warn('Browser compatibility issues detected:', missingFeatures);
      
      // Apply any available compatibility fixes/polyfills
      applyCompatibilityFixes((message) => {
        notificationService.showWarning(message);
      });
    };
    
    // Handle compatibility warning dismissal
    const compatibilityDismissed = () => {
      notificationService.showInfo('You may experience issues with this browser. Consider upgrading for the best experience.');
    };
    
    onMounted(() => {
      // Register the notification manager with the notification service
      notificationService.setNotificationManager(notificationManager.value);
    });
    
    return {
      notificationManager,
      handleCompatibilityIssue,
      compatibilityDismissed
    };
  }
}
</script>

<style>
/* Import base styles */
@import './assets/styles/base.css';

/* Global styles */
:root {
  --primary-color: #0080ff;
  --secondary-color: #ff4081;
  --success-color: #4caf50;
  --error-color: #f44336;
  --warning-color: #ff9800;
  --info-color: #2196f3;
  --background-color: #f5f5f5;
  --text-color: #333;
  --border-color: #e0e0e0;
}

body {
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
  background-color: var(--background-color);
  color: var(--text-color);
  margin: 0;
  padding: 0;
  line-height: 1.6;
}

#app {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
}

.container {
  width: 100%;
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 1rem;
}

/* Accessibility improvements */
.visually-hidden {
  position: absolute;
  width: 1px;
  height: 1px;
  padding: 0;
  margin: -1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  white-space: nowrap;
  border-width: 0;
}

/* Add focus styles for keyboard navigation */
:focus-visible {
  outline: 3px solid var(--primary-color);
  outline-offset: 2px;
}

/* Responsive adjustments */
@media (max-width: 768px) {
  .container {
    padding: 0 0.5rem;
  }
  
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
  
  .vote-card {
    width: 100%;
    margin: 0.5rem 0;
  }
  
  .header {
    padding: 0.5rem 1rem;
  }
  
  .footer {
    padding: 0.5rem;
  }
  
  /* Adjust font sizes */
  h1 {
    font-size: 1.5rem;
  }
  
  h2 {
    font-size: 1.25rem;
  }
  
  .btn {
    padding: 0.5rem 1rem;
    font-size: 0.9rem;
  }
}
</style>
