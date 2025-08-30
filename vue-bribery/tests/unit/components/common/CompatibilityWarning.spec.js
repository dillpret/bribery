import { mount } from '@vue/test-utils';
import CompatibilityWarning from '@/components/common/CompatibilityWarning.vue';
import * as browserCompat from '@/services/browser-compatibility';

// Mock the browser compatibility service
jest.mock('@/services/browser-compatibility', () => {
  return {
    isBrowserCompatible: jest.fn(),
    getMissingFeatures: jest.fn(),
    detectBrowserCapabilities: jest.fn()
  };
});

describe('CompatibilityWarning.vue', () => {
  beforeEach(() => {
    // Reset mocks before each test
    jest.clearAllMocks();
    
    // Default mock implementations
    browserCompat.isBrowserCompatible.mockImplementation(() => true);
    browserCompat.getMissingFeatures.mockImplementation(() => []);
  });
  
  it('should not display warning when browser is compatible', async () => {
    // Mock browser as compatible
    browserCompat.isBrowserCompatible.mockReturnValue(true);
    
    const wrapper = mount(CompatibilityWarning);
    await wrapper.vm.$nextTick();
    
    // Warning should not be visible
    expect(wrapper.find('.compatibility-warning').exists()).toBe(false);
  });
  
  it('should display warning when browser is not compatible', async () => {
    // Mock browser as incompatible
    browserCompat.isBrowserCompatible.mockReturnValue(false);
    browserCompat.getMissingFeatures.mockReturnValue(['localStorage', 'webSockets']);
    
    const wrapper = mount(CompatibilityWarning);
    await wrapper.vm.$nextTick();
    
    // Warning should be visible
    expect(wrapper.find('.compatibility-warning').exists()).toBe(true);
    
    // Should list missing features
    const listItems = wrapper.findAll('.missing-features li');
    expect(listItems.length).toBe(2);
  });
  
  it('should emit event when compatibility issues are detected', async () => {
    // Mock browser as incompatible
    browserCompat.isBrowserCompatible.mockReturnValue(false);
    browserCompat.getMissingFeatures.mockReturnValue(['localStorage']);
    
    const wrapper = mount(CompatibilityWarning);
    await wrapper.vm.$nextTick();
    
    // Check if event was emitted with correct payload
    expect(wrapper.emitted('compatibility-issue')).toBeTruthy();
    expect(wrapper.emitted('compatibility-issue')[0][0]).toEqual(['localStorage']);
  });
  
  it('should dismiss warning when button is clicked', async () => {
    // Mock browser as incompatible
    browserCompat.isBrowserCompatible.mockReturnValue(false);
    browserCompat.getMissingFeatures.mockReturnValue(['localStorage']);
    
    const wrapper = mount(CompatibilityWarning);
    await wrapper.vm.$nextTick();
    
    // Warning should be visible initially
    expect(wrapper.find('.compatibility-warning').exists()).toBe(true);
    
    // Click dismiss button
    await wrapper.find('.dismiss-button').trigger('click');
    await wrapper.vm.$nextTick();
    
    // Warning should be hidden
    expect(wrapper.find('.compatibility-warning').exists()).toBe(false);
    
    // Should emit dismiss event
    expect(wrapper.emitted('dismiss')).toBeTruthy();
  });
  
  it('should not show dismiss button when isDismissable is false', async () => {
    // Mock browser as incompatible
    browserCompat.isBrowserCompatible.mockReturnValue(false);
    browserCompat.getMissingFeatures.mockReturnValue(['localStorage']);
    
    const wrapper = mount(CompatibilityWarning, {
      props: {
        isDismissable: false
      }
    });
    await wrapper.vm.$nextTick();
    
    // Warning should be visible
    expect(wrapper.find('.compatibility-warning').exists()).toBe(true);
    
    // Dismiss button should not be visible
    expect(wrapper.find('.dismiss-button').exists()).toBe(false);
  });
  
  it('should not check compatibility on mount when checkOnMount is false', async () => {
    // Mock browser-compatibility functions
    browserCompat.isBrowserCompatible.mockReturnValue(true);
    
    const wrapper = mount(CompatibilityWarning, {
      props: {
        checkOnMount: false
      }
    });
    await wrapper.vm.$nextTick();
    
    // isBrowserCompatible should not have been called
    expect(browserCompat.isBrowserCompatible).not.toHaveBeenCalled();
  });
  
  it('should display user-friendly labels for features', async () => {
    // Mock browser as incompatible
    browserCompat.isBrowserCompatible.mockReturnValue(false);
    browserCompat.getMissingFeatures.mockReturnValue(['localStorage', 'webSockets']);
    
    const wrapper = mount(CompatibilityWarning);
    await wrapper.vm.$nextTick();
    
    // Get the text content of the list items
    const listItems = wrapper.findAll('.missing-features li');
    const textContents = Array.from(listItems).map(item => item.text());
    
    // Check if user-friendly labels are used
    expect(textContents).toContain('Local storage for saving game progress');
    expect(textContents).toContain('WebSockets for real-time communication');
  });
});
