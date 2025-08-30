/**
 * Notification service for managing application-wide notifications
 * Provides methods for showing success, error, info, and warning notifications
 */

import { ref, markRaw } from 'vue';
import NotificationManager from '@/components/common/NotificationManager.vue';

const notificationManagerRef = ref(null);

const notificationService = {
  /**
   * Set the notification manager component reference
   * This should be called once when the app is initialized
   * @param {Object} managerRef - Reference to the NotificationManager component
   */
  setNotificationManager(managerRef) {
    if (managerRef) {
      notificationManagerRef.value = markRaw(managerRef);
    } else {
      notificationManagerRef.value = null;
      console.warn('NotificationManager is undefined or null');
    }
  },

  /**
   * Show a success notification
   * @param {String} message - The notification message
   * @param {Object} options - Additional options (title, duration, etc.)
   * @returns {Number} The notification ID
   */
  success(message, options = {}) {
    return this._showNotification({
      type: 'success',
      message,
      ...options
    });
  },

  /**
   * Show an error notification
   * @param {String} message - The notification message
   * @param {Object} options - Additional options (title, duration, etc.)
   * @returns {Number} The notification ID
   */
  error(message, options = {}) {
    return this._showNotification({
      type: 'error',
      message,
      ...options
    });
  },

  /**
   * Show a warning notification
   * @param {String} message - The notification message
   * @param {Object} options - Additional options (title, duration, etc.)
   * @returns {Number} The notification ID
   */
  warning(message, options = {}) {
    return this._showNotification({
      type: 'warning',
      message,
      ...options
    });
  },

  /**
   * Show an info notification
   * @param {String} message - The notification message
   * @param {Object} options - Additional options (title, duration, etc.)
   * @returns {Number} The notification ID
   */
  info(message, options = {}) {
    return this._showNotification({
      type: 'info',
      message,
      ...options
    });
  },

  /**
   * Remove a specific notification by ID
   * @param {Number} id - The notification ID to remove
   */
  remove(id) {
    if (notificationManagerRef.value) {
      notificationManagerRef.value.removeNotification(id);
    }
  },

  /**
   * Clear all notifications
   */
  clearAll() {
    if (notificationManagerRef.value) {
      notificationManagerRef.value.clearAllNotifications();
    }
  },

  /**
   * Internal method to show a notification
   * @private
   * @param {Object} notification - The notification configuration
   * @returns {Number|Boolean} The notification ID or false if manager not set
   */
  _showNotification(notification) {
    if (notificationManagerRef.value) {
      return notificationManagerRef.value.addNotification(notification);
    } else {
      console.warn('NotificationManager not set. Call setNotificationManager first.');
      return false;
    }
  }
};

export default notificationService;
