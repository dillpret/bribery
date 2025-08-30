import { shallowMount } from '@vue/test-utils';
import CompatibilityWarning from '@/components/common/CompatibilityWarning.vue';
import { isBrowserCompatible, getMissingFeatures } from '@/services/browser-compatibility';

// Mock the browser compatibility service
jest.mock('@/services/browser-compatibility', () => ({
  isBrowserCompatible: jest.fn(),
  getMissingFeatures: jest.fn()
}));

describe('CompatibilityWarning.vue', () => {
  beforeEach(() => {
    // Reset mocks before each test
    isBrowserCompatible.mockReset();
    getMissingFeatures.mockReset();
  });
  
  it('should not display warning when browser is compatible', () => {
    // Mock browser as compatible
    isBrowserCompatible.mockReturnValue(true);
    
    const wrapper = shallowMount(CompatibilityWarning);
    
    // Warning should not be visible
    expect(wrapper.find('.compatibility-warning').exists()).toBe(false);
  });
  
  it('should display warning when browser is not compatible', () => {
    // Mock browser as incompatible
    isBrowserCompatible.mockReturnValue(false);
    getMissingFeatures.mockReturnValue(['localStorage', 'webSockets']);
    
    const wrapper = shallowMount(CompatibilityWarning);
    
    // Warning should be visible
    expect(wrapper.find('.compatibility-warning').exists()).toBe(true);
    
    // Should list missing features
    const listItems = wrapper.findAll('.missing-features li');
    expect(listItems.length).toBe(2);
  });
  
  it('should emit event when compatibility issues are detected', async () => {
    // Mock browser as incompatible
    isBrowserCompatible.mockReturnValue(false);
    getMissingFeatures.mockReturnValue(['localStorage']);
    
    const wrapper = shallowMount(CompatibilityWarning);
    
    // Check if event was emitted with correct payload
    expect(wrapper.emitted('compatibility-issue')).toBeTruthy();
    expect(wrapper.emitted('compatibility-issue')[0][0]).toEqual(['localStorage']);
  });
  
  it('should dismiss warning when button is clicked', async () => {
    // Mock browser as incompatible
    isBrowserCompatible.mockReturnValue(false);
    getMissingFeatures.mockReturnValue(['localStorage']);
    
    const wrapper = shallowMount(CompatibilityWarning);
    
    // Warning should be visible initially
    expect(wrapper.find('.compatibility-warning').exists()).toBe(true);
    
    // Click dismiss button
    await wrapper.find('.dismiss-button').trigger('click');
    
    // Warning should be hidden
    expect(wrapper.find('.compatibility-warning').exists()).toBe(false);
    
    // Should emit dismiss event
    expect(wrapper.emitted('dismiss')).toBeTruthy();
  });
  
  it('should not show dismiss button when isDismissable is false', () => {
    // Mock browser as incompatible
    isBrowserCompatible.mockReturnValue(false);
    getMissingFeatures.mockReturnValue(['localStorage']);
    
    const wrapper = shallowMount(CompatibilityWarning, {
      props: {
        isDismissable: false
      }
    });
    
    // Warning should be visible
    expect(wrapper.find('.compatibility-warning').exists()).toBe(true);
    
    // Dismiss button should not be visible
    expect(wrapper.find('.dismiss-button').exists()).toBe(false);
  });
  
  it('should not check compatibility on mount when checkOnMount is false', () => {
    // Mock browser-compatibility functions
    isBrowserCompatible.mockReturnValue(true);
    
    const wrapper = shallowMount(CompatibilityWarning, {
      props: {
        checkOnMount: false
      }
    });
    
    // isBrowserCompatible should not have been called
    expect(isBrowserCompatible).not.toHaveBeenCalled();
  });
  
  it('should display user-friendly labels for features', () => {
    // Mock browser as incompatible
    isBrowserCompatible.mockReturnValue(false);
    getMissingFeatures.mockReturnValue(['localStorage', 'webSockets']);
    
    const wrapper = shallowMount(CompatibilityWarning);
    
    // Get the text content of the list items
    const listItems = wrapper.findAll('.missing-features li');
    const textContents = listItems.map(item => item.text());
    
    // Check if user-friendly labels are used
    expect(textContents).toContain('Local storage for saving game progress');
    expect(textContents).toContain('WebSockets for real-time communication');
  });
});
