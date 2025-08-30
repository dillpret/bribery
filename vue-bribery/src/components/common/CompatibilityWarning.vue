<template>
  <div v-if="!isCompatible" class="compatibility-warning" role="alert">
    <div class="compatibility-content">
      <h2>Browser Compatibility Issue</h2>
      <p>Your browser doesn't support all the features needed for this game.</p>
      <ul class="missing-features">
        <li v-for="(feature, index) in missingFeatures" :key="index">
          {{ getFeatureLabel(feature) }}
        </li>
      </ul>
      <p>Please consider using a modern browser like:</p>
      <ul class="browser-list">
        <li>Google Chrome</li>
        <li>Microsoft Edge</li>
        <li>Mozilla Firefox</li>
        <li>Safari (latest version)</li>
      </ul>
      <button 
        class="dismiss-button" 
        @click="dismissWarning"
        v-if="isDismissable">
        Continue anyway
      </button>
    </div>
  </div>
</template>

<script>
import { ref, onMounted, computed } from 'vue';
import { isBrowserCompatible, getMissingFeatures } from '@/services/browser-compatibility';

export default {
  name: 'CompatibilityWarning',
  props: {
    isDismissable: {
      type: Boolean,
      default: true
    },
    checkOnMount: {
      type: Boolean,
      default: true
    }
  },
  setup(props, { emit }) {
    const isCompatible = ref(true);
    const missingFeatures = ref([]);
    
    // Map technical feature names to user-friendly labels
    const featureLabels = {
      localStorage: 'Local storage for saving game progress',
      webSockets: 'WebSockets for real-time communication',
      fileReader: 'File handling for image uploads',
      flexbox: 'Modern layout features',
      sessionStorage: 'Session storage',
      fetch: 'Network communication',
      promises: 'Modern JavaScript features',
      canvas: 'Graphics capabilities'
    };
    
    // Check browser compatibility
    const checkCompatibility = () => {
      const compatible = isBrowserCompatible();
      isCompatible.value = compatible;
      
      if (!compatible) {
        missingFeatures.value = getMissingFeatures();
        emit('compatibility-issue', missingFeatures.value);
      }
    };
    
    // Get user-friendly label for a feature
    const getFeatureLabel = (feature) => {
      return featureLabels[feature] || feature;
    };
    
    // Dismiss the warning
    const dismissWarning = () => {
      isCompatible.value = true;
      emit('dismiss');
    };
    
    // Calculate if we should show critical warning based on missing features
    const hasCriticalIssues = computed(() => {
      const criticalFeatures = ['localStorage', 'webSockets'];
      return missingFeatures.value.some(feature => criticalFeatures.includes(feature));
    });
    
    onMounted(() => {
      if (props.checkOnMount) {
        checkCompatibility();
      }
    });
    
    return {
      isCompatible,
      missingFeatures,
      getFeatureLabel,
      dismissWarning,
      hasCriticalIssues
    };
  }
};
</script>

<style scoped>
.compatibility-warning {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.85);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 9999;
  color: white;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, 'Open Sans', sans-serif;
}

.compatibility-content {
  background-color: #2c3e50;
  padding: 2rem;
  border-radius: 8px;
  max-width: 500px;
  width: 90%;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.5);
}

h2 {
  margin-top: 0;
  font-size: 1.5rem;
  color: #ff9800;
}

ul {
  text-align: left;
  margin: 1rem 0;
  padding-left: 1.5rem;
}

.missing-features li {
  margin-bottom: 0.5rem;
  color: #ff5252;
}

.browser-list li {
  margin-bottom: 0.5rem;
}

.dismiss-button {
  background-color: #ff9800;
  border: none;
  color: white;
  padding: 0.5rem 1rem;
  font-size: 1rem;
  border-radius: 4px;
  cursor: pointer;
  margin-top: 1rem;
  transition: background-color 0.2s;
}

.dismiss-button:hover {
  background-color: #f57c00;
}

@media (max-width: 600px) {
  .compatibility-content {
    padding: 1.5rem;
    width: 95%;
  }
  
  h2 {
    font-size: 1.2rem;
  }
}
</style>
