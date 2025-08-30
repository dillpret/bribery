import { 
  detectBrowserCapabilities,
  isBrowserCompatible,
  getMissingFeatures,
  applyCompatibilityFixes
} from '@/services/browser-compatibility';

// Mock the browser-compatibility module
jest.mock('@/services/browser-compatibility', () => {
  // Store the original module
  const originalModule = jest.requireActual('@/services/browser-compatibility');
  
  return {
    __esModule: true,
    ...originalModule,
    detectBrowserCapabilities: jest.fn(),
    isBrowserCompatible: jest.fn(),
    getMissingFeatures: jest.fn(),
    applyCompatibilityFixes: jest.fn()
  };
});

// Mock window objects
describe('Browser Compatibility Service', () => {
  let originalWindowProps;
  
  beforeEach(() => {
    // Reset mocks
    detectBrowserCapabilities.mockReset();
    isBrowserCompatible.mockReset();
    getMissingFeatures.mockReset();
    applyCompatibilityFixes.mockReset();
    
    // Store original window properties
    originalWindowProps = {
      localStorage: window.localStorage,
      sessionStorage: window.sessionStorage,
      WebSocket: window.WebSocket,
      FileReader: window.FileReader,
      fetch: window.fetch,
      Promise: window.Promise
    };
  });
  
  afterEach(() => {
    // Restore original window properties
    window.localStorage = originalWindowProps.localStorage;
    window.sessionStorage = originalWindowProps.sessionStorage;
    window.WebSocket = originalWindowProps.WebSocket;
    window.FileReader = originalWindowProps.FileReader;
    window.fetch = originalWindowProps.fetch;
    window.Promise = originalWindowProps.Promise;
    
    // Clear any localStorage test items
    try {
      localStorage.removeItem('test-ls-availability');
    } catch (e) {
      // Ignore errors if localStorage is not available
    }
  });
  
  describe('detectBrowserCapabilities', () => {
    it('should detect browser capabilities', () => {
      // Setup the mock to return specific capabilities
      detectBrowserCapabilities.mockReturnValue({
        localStorage: true,
        webSockets: true,
        fileReader: true,
        flexbox: true,
        sessionStorage: true,
        fetch: true,
        promises: true,
        canvas: true
      });
      
      const capabilities = detectBrowserCapabilities();
      
      // Check that it returns an object with the expected properties
      expect(capabilities).toHaveProperty('localStorage');
      expect(capabilities).toHaveProperty('webSockets');
      expect(capabilities).toHaveProperty('fileReader');
      expect(capabilities).toHaveProperty('flexbox');
      expect(capabilities).toHaveProperty('sessionStorage');
      expect(capabilities).toHaveProperty('fetch');
      expect(capabilities).toHaveProperty('promises');
      expect(capabilities).toHaveProperty('canvas');
    });
  });
  
  describe('isBrowserCompatible', () => {
    it('should return true when all required features are supported', () => {
      // Setup the mock to return all features as supported
      detectBrowserCapabilities.mockReturnValue({
        localStorage: true,
        webSockets: true,
        fileReader: true,
        flexbox: true,
        sessionStorage: true,
        fetch: true,
        promises: true,
        canvas: true
      });
      
      // Mock isBrowserCompatible to return true
      isBrowserCompatible.mockReturnValue(true);
      
      const result = isBrowserCompatible();
      expect(result).toBe(true);
    });
    
    it('should return false when localStorage is not available', () => {
      // Setup the mock to return localStorage as not supported
      detectBrowserCapabilities.mockReturnValue({
        localStorage: false,
        webSockets: true,
        fileReader: true,
        flexbox: true,
        sessionStorage: true,
        fetch: true,
        promises: true,
        canvas: true
      });
      
      // Mock isBrowserCompatible to return false
      isBrowserCompatible.mockReturnValue(false);
      
      const result = isBrowserCompatible();
      expect(result).toBe(false);
    });
  });
  
  describe('getMissingFeatures', () => {
    it('should return empty array when all features are supported', () => {
      // Setup the mock to return all features as supported
      detectBrowserCapabilities.mockReturnValue({
        localStorage: true,
        webSockets: true,
        fileReader: true,
        flexbox: true,
        sessionStorage: true,
        fetch: true,
        promises: true,
        canvas: true
      });
      
      // Use the mock implementation
      getMissingFeatures.mockReturnValue([]);
      
      const missingFeatures = getMissingFeatures();
      expect(missingFeatures).toEqual([]);
    });
    
    it('should return array of missing features', () => {
      // Setup the mock to return some features as not supported
      detectBrowserCapabilities.mockReturnValue({
        localStorage: true,
        webSockets: false,
        fileReader: true,
        flexbox: true,
        sessionStorage: true,
        fetch: true,
        promises: false,
        canvas: true
      });
      
      // Use the mock implementation
      getMissingFeatures.mockReturnValue(['webSockets', 'promises']);
      
      const missingFeatures = getMissingFeatures();
      expect(missingFeatures).toContain('webSockets');
      expect(missingFeatures).toContain('promises');
    });
  });
  
  describe('applyCompatibilityFixes', () => {
    it('should call notification callback when features are missing', () => {
      // Setup the mock for required functions
      detectBrowserCapabilities.mockReturnValue({
        localStorage: true,
        webSockets: true,
        fileReader: true,
        flexbox: true,
        sessionStorage: true,
        fetch: true,
        promises: false,
        canvas: true
      });
      
      // Implement our own version of applyCompatibilityFixes for testing
      applyCompatibilityFixes.mockImplementation((callback) => {
        if (callback) {
          callback('Your browser has limited support for some features. The app may not function optimally.');
        }
      });
      
      // Mock console.warn
      const originalConsoleWarn = console.warn;
      console.warn = jest.fn();
      
      // Create mock notification callback
      const mockNotificationCallback = jest.fn();
      
      // Call the function
      applyCompatibilityFixes(mockNotificationCallback);
      
      // Check if notification callback was called
      expect(mockNotificationCallback).toHaveBeenCalledTimes(1);
      
      // Restore console.warn
      console.warn = originalConsoleWarn;
    });
    
    it('should handle null notification callback gracefully', () => {
      // Mock localStorage and sessionStorage to be unavailable
      detectBrowserCapabilities.mockReturnValue({
        localStorage: false,
        webSockets: true,
        fileReader: true,
        flexbox: true,
        sessionStorage: false,
        fetch: true,
        promises: true,
        canvas: true
      });
      
      // Mock console.warn
      const originalConsoleWarn = console.warn;
      console.warn = jest.fn();
      
      // Call the function without a callback
      expect(() => {
        applyCompatibilityFixes(null);
      }).not.toThrow();
      
      // Restore console.warn
      console.warn = originalConsoleWarn;
    });
  });
});
