import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import store from './store'
import notificationService from './services/notification'
import socketService from './services/socket'
import authService from './services/auth'

// Create app instance
const app = createApp(App)

// Register global properties
app.config.globalProperties.$notify = notificationService
app.config.globalProperties.$socket = socketService
app.config.globalProperties.$auth = authService

// Analytics and monitoring setup
const isProd = process.env.NODE_ENV === 'production'

// Track page views
router.afterEach((to) => {
  if (isProd) {
    // Send page view to analytics
    console.log('Page view:', to.fullPath)
    
    // In a real implementation, you would send to a real analytics service
    // Example: 
    // fetch('/api/analytics', {
    //   method: 'POST',
    //   headers: { 'Content-Type': 'application/json' },
    //   body: JSON.stringify({
    //     type: 'pageview',
    //     page: to.fullPath,
    //     timestamp: Date.now()
    //   })
    // })
  }
})

// Register global error handler
app.config.errorHandler = (err, vm, info) => {
  console.error('Global error:', err)
  console.error('Info:', info)
  
  // Send to notification service
  notificationService.error('An unexpected error occurred. Please try again.', {
    title: 'Error',
    duration: 8000
  })
  
  if (isProd) {
    // Log error to server in production
    // Example:
    // fetch('/api/log', {
    //   method: 'POST',
    //   headers: { 'Content-Type': 'application/json' },
    //   body: JSON.stringify({
    //     type: 'error',
    //     message: err.message,
    //     stack: err.stack,
    //     info: info,
    //     location: window.location.href,
    //     timestamp: Date.now()
    //   })
    // })
  }
}

// Unhandled promise rejection tracker
window.addEventListener('unhandledrejection', (event) => {
  console.error('Unhandled rejection:', event.reason)
  
  if (isProd) {
    // Log to server
    // Similar implementation to error handler above
  }
})

// Performance monitoring
if (isProd && window.PerformanceObserver) {
  // Monitor Largest Contentful Paint
  const lcpObserver = new PerformanceObserver((entryList) => {
    const entries = entryList.getEntries();
    const lastEntry = entries[entries.length - 1];
    console.log('LCP:', lastEntry.startTime, 'Element:', lastEntry.element);
    
    // Send to analytics
  });
  lcpObserver.observe({ type: 'largest-contentful-paint', buffered: true });
  
  // Monitor First Input Delay
  const fidObserver = new PerformanceObserver((entryList) => {
    const entries = entryList.getEntries();
    const firstEntry = entries[0];
    console.log('FID:', firstEntry.processingStart - firstEntry.startTime);
    
    // Send to analytics
  });
  fidObserver.observe({ type: 'first-input', buffered: true });
}

// Use plugins and mount app
app
  .use(store)
  .use(router)
  .mount('#app')
