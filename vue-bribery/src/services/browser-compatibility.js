/**
 * Browser Compatibility Service
 * 
 * Provides browser capability detection and fallbacks for features
 * used in the Bribery Game application.
 */

/**
 * Detects if the browser supports modern features needed by the app
 * @returns {Object} Object with support flags for various features
 */
export function detectBrowserCapabilities() {
  return {
    localStorage: isLocalStorageAvailable(),
    webSockets: isWebSocketSupported(),
    fileReader: isFileReaderSupported(),
    flexbox: isFlexboxSupported(),
    sessionStorage: isSessionStorageAvailable(),
    fetch: isFetchSupported(),
    promises: arePromisesSupported(),
    canvas: isCanvasSupported()
  };
}

/**
 * Checks if browser is compatible with all required features
 * @returns {boolean} True if browser is compatible, false otherwise
 */
export function isBrowserCompatible() {
  const capabilities = detectBrowserCapabilities();
  
  // Required features for the app to function
  const requiredFeatures = [
    'localStorage',
    'webSockets',
    'fileReader',
    'flexbox',
    'promises'
  ];
  
  return requiredFeatures.every(feature => capabilities[feature]);
}

/**
 * Identifies missing browser features
 * @returns {Array} List of missing features 
 */
export function getMissingFeatures() {
  const capabilities = detectBrowserCapabilities();
  
  return Object.entries(capabilities)
    .filter(([_, supported]) => !supported)
    .map(([feature]) => feature);
}

/**
 * Checks if localStorage is available and working
 * @returns {boolean} True if localStorage is available
 */
function isLocalStorageAvailable() {
  try {
    const testKey = 'test-ls-availability';
    localStorage.setItem(testKey, 'test');
    const result = localStorage.getItem(testKey) === 'test';
    localStorage.removeItem(testKey);
    return result;
  } catch (e) {
    return false;
  }
}

/**
 * Checks if sessionStorage is available and working
 * @returns {boolean} True if sessionStorage is available
 */
function isSessionStorageAvailable() {
  try {
    const testKey = 'test-ss-availability';
    sessionStorage.setItem(testKey, 'test');
    const result = sessionStorage.getItem(testKey) === 'test';
    sessionStorage.removeItem(testKey);
    return result;
  } catch (e) {
    return false;
  }
}

/**
 * Checks if WebSockets are supported
 * @returns {boolean} True if WebSockets are supported
 */
function isWebSocketSupported() {
  return 'WebSocket' in window;
}

/**
 * Checks if FileReader is supported
 * @returns {boolean} True if FileReader is supported
 */
function isFileReaderSupported() {
  return 'FileReader' in window;
}

/**
 * Checks if Flexbox is supported
 * @returns {boolean} True if Flexbox is supported
 */
function isFlexboxSupported() {
  const testEl = document.createElement('div');
  try {
    // We test for flex display property
    testEl.style.display = 'flex';
    return testEl.style.display === 'flex';
  } catch (e) {
    return false;
  }
}

/**
 * Checks if Fetch API is supported
 * @returns {boolean} True if Fetch API is supported
 */
function isFetchSupported() {
  return 'fetch' in window;
}

/**
 * Checks if Promises are supported
 * @returns {boolean} True if Promises are supported
 */
function arePromisesSupported() {
  return 'Promise' in window;
}

/**
 * Checks if Canvas is supported
 * @returns {boolean} True if Canvas is supported
 */
function isCanvasSupported() {
  try {
    const canvas = document.createElement('canvas');
    return !!(canvas.getContext && typeof canvas.getContext === 'function');
  } catch (e) {
    return false;
  }
}

/**
 * Polyfills/fallbacks for browser features if needed
 * @param {Function} notificationCallback Function to call with compatibility messages
 * @returns {void}
 */
export function applyCompatibilityFixes(notificationCallback) {
  const capabilities = detectBrowserCapabilities();
  
  // Apply polyfills only for features that need them
  if (!capabilities.promises) {
    console.warn('Browser lacks Promise support. Loading polyfill would be required.');
    notificationCallback?.('Your browser has limited support for some features. The app may not function optimally.');
  }
  
  if (!capabilities.localStorage && !capabilities.sessionStorage) {
    console.warn('Browser lacks storage support. Using memory-based fallback.');
    notificationCallback?.('Your browser does not support local storage. Game progress cannot be saved.');
    // Memory-based storage fallback would be implemented here
  }
}
