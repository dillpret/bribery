/**
 * Common components index file
 * Export all common components for easier imports
 */

import Button from './Button.vue'
import ImageUploader from './ImageUploader.vue'
import LoadingSpinner from './LoadingSpinner.vue'
import Notification from './Notification.vue'
import NotificationManager from './NotificationManager.vue'
import Timer from './Timer.vue'

// Export individual components
export {
  Button,
  ImageUploader,
  LoadingSpinner,
  Notification,
  NotificationManager,
  Timer
}

// Default export for plugin-style usage
export default {
  install(app) {
    // Register all components globally
    app.component('Button', Button)
    app.component('ImageUploader', ImageUploader)
    app.component('LoadingSpinner', LoadingSpinner)
    app.component('Notification', Notification)
    app.component('NotificationManager', NotificationManager)
    app.component('Timer', Timer)
  }
}
