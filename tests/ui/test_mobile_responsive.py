#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Mobile responsive UI tests
"""

import pytest
import sys
import os
import requests
import time

# Add the app directory to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'src'))
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from helpers.browser_helpers import BrowserHelper
# -*- coding: utf-8 -*-
"""
Mobile responsiveness tests for the Bribery game UI
"""

import pytest
import sys
import os

# Add the app directory to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'src'))
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from helpers.browser_helpers import BrowserHelper

# Selenium imports are optional
try:
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.chrome.options import Options
    SELENIUM_AVAILABLE = True
except ImportError:
    SELENIUM_AVAILABLE = False

class MobileBrowserHelper(BrowserHelper):
    """Extended browser helper for mobile testing"""
    
    @staticmethod
    def create_mobile_chrome_driver(device_name="iPhone 12"):
        """Create Chrome driver with mobile device emulation"""
        if not SELENIUM_AVAILABLE:
            return None
        
        # Mobile device configurations
        mobile_devices = {
            "iPhone 12": {"width": 390, "height": 844, "pixelRatio": 3, "userAgent": "Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1"},
            "iPhone SE": {"width": 375, "height": 667, "pixelRatio": 2, "userAgent": "Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1"},
            "Samsung Galaxy S21": {"width": 384, "height": 854, "pixelRatio": 2.75, "userAgent": "Mozilla/5.0 (Linux; Android 11; SM-G991B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.82 Mobile Safari/537.36"},
            "iPad": {"width": 768, "height": 1024, "pixelRatio": 2, "userAgent": "Mozilla/5.0 (iPad; CPU OS 14_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1"}
        }
        
        device_config = mobile_devices.get(device_name, mobile_devices["iPhone 12"])
        
        chrome_options = Options()
        # Add mobile emulation
        chrome_options.add_experimental_option("mobileEmulation", {
            "deviceMetrics": {
                "width": device_config["width"],
                "height": device_config["height"],
                "pixelRatio": device_config["pixelRatio"]
            },
            "userAgent": device_config["userAgent"]
        })
        
        # Standard optimizations
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--disable-background-networking')
        chrome_options.add_argument('--disable-background-timer-throttling')
        chrome_options.add_argument('--disable-backgrounding-occluded-windows')
        chrome_options.add_argument('--disable-renderer-backgrounding')
        chrome_options.add_argument('--disable-features=TranslateUI')
        chrome_options.add_argument('--disable-extensions')
        chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        chrome_options.add_argument('--log-level=3')
        
        try:
            return webdriver.Chrome(options=chrome_options)
        except Exception as e:
            print(f"Chrome driver not available for mobile testing: {str(e)}")
            return None
    
    @staticmethod
    def check_mobile_responsiveness(driver, test_server):
        """Check that the mobile layout is working properly"""
        driver.get(test_server['base_url'])
        
        # Check viewport meta tag exists
        viewport_tag = driver.find_element(By.XPATH, "//meta[@name='viewport']")
        viewport_content = viewport_tag.get_attribute('content')
        assert 'width=device-width' in viewport_content
        assert 'user-scalable=no' in viewport_content
        
        # Check that main elements are visible and properly sized
        container = driver.find_element(By.CLASS_NAME, "container")
        container_width = container.size['width']
        window_width = driver.get_window_size()['width']
        
        # Container should take most of the screen width on mobile
        # Note: Mobile devices may report different window vs container widths due to viewport scaling
        container_ratio = container_width / window_width
        assert container_ratio >= 0.4, f"Container width {container_width} should be at least 40% of window width {window_width} (ratio: {container_ratio:.2f})"
        
        # Check button sizes are touch-friendly (minimum 44px height)
        buttons = driver.find_elements(By.TAG_NAME, "button")
        for button in buttons:
            if button.is_displayed():  # Only check visible buttons
                button_height = button.size['height']
                assert button_height >= 44, f"Button height {button_height} should be at least 44px for touch accessibility"
        
        return True
    
    @staticmethod
    def test_mobile_game_flow(driver, test_server):
        """Test a basic game flow on mobile"""
        # Create game
        game_id = MobileBrowserHelper.create_game_as_host(driver, test_server, "MobileHost")
        
        # Check that game ID is displayed properly on mobile
        game_id_element = driver.find_element(By.ID, "created-game-id")
        assert game_id_element.is_displayed()
        
        # Check that text is readable (not too small)
        font_size = driver.execute_script(
            "return window.getComputedStyle(arguments[0]).fontSize", 
            game_id_element
        )
        font_size_px = float(font_size.replace('px', ''))
        assert font_size_px >= 16, f"Font size {font_size_px}px should be at least 16px for mobile readability"
        
        return True

class TestMobileUI:
    """Mobile UI responsiveness tests"""
    
    @classmethod
    def setup_class(cls):
        """Set up mobile test environment"""
        cls.mobile_devices = ["iPhone 12", "iPhone SE", "Samsung Galaxy S21", "iPad"]
        cls.drivers = {}
        
        if not SELENIUM_AVAILABLE:
            pytest.skip("Selenium not available for mobile testing")
        
        # Create drivers for different devices
        for device in cls.mobile_devices:
            driver = MobileBrowserHelper.create_mobile_chrome_driver(device)
            if driver:
                cls.drivers[device] = driver
        
        if not cls.drivers:
            pytest.skip("No mobile drivers available")
    
    @classmethod
    def teardown_class(cls):
        """Clean up mobile drivers"""
        for driver in cls.drivers.values():
            if driver:
                driver.quit()
    
    def _verify_server_health(self, test_server):
        """Verify the test server is responding properly"""
        try:
            response = requests.get(test_server['base_url'], timeout=5)
            if response.status_code != 200:
                pytest.skip(f"Test server not responding properly (status: {response.status_code})")
        except requests.exceptions.RequestException as e:
            pytest.skip(f"Test server not accessible: {e}")
    
    def test_mobile_viewport_configuration(self, test_server):
        """Test that viewport is properly configured for mobile"""
        if not self.drivers:
            pytest.skip("No mobile drivers available")
        
        self._verify_server_health(test_server)
        
        # Test on iPhone 12
        driver = self.drivers.get("iPhone 12")
        if not driver:
            pytest.skip("iPhone 12 driver not available")
        
        assert MobileBrowserHelper.check_mobile_responsiveness(driver, test_server)
    
    def test_mobile_touch_targets(self, test_server):
        """Test that all interactive elements are touch-friendly"""
        if not self.drivers:
            pytest.skip("No mobile drivers available")
        
        for device_name, driver in self.drivers.items():
            print(f"\n📱 Testing touch targets on {device_name}")
            
            driver.get(test_server['base_url'])
            
            # Check all buttons are touch-friendly
            buttons = driver.find_elements(By.TAG_NAME, "button")
            for i, button in enumerate(buttons):
                if button.is_displayed():
                    height = button.size['height']
                    width = button.size['width']
                    print(f"   Button {i+1}: {width}x{height}px")
                    assert height >= 44, f"Button {i+1} height {height}px too small for {device_name}"
                    assert width >= 44, f"Button {i+1} width {width}px too small for {device_name}"
    
    def test_mobile_text_readability(self, test_server):
        """Test that text is readable on mobile devices"""
        if not self.drivers:
            pytest.skip("No mobile drivers available")
        
        driver = self.drivers.get("iPhone 12")
        if not driver:
            pytest.skip("iPhone 12 driver not available")
        
        driver.get(test_server['base_url'])
        
        # Check main heading font size
        h1 = driver.find_element(By.TAG_NAME, "h1")
        font_size = driver.execute_script(
            "return window.getComputedStyle(arguments[0]).fontSize", h1
        )
        font_size_px = float(font_size.replace('px', ''))
        assert font_size_px >= 24, f"H1 font size {font_size_px}px too small for mobile"
        
        # Check subtitle readability
        subtitle = driver.find_element(By.CLASS_NAME, "subtitle")
        font_size = driver.execute_script(
            "return window.getComputedStyle(arguments[0]).fontSize", subtitle
        )
        font_size_px = float(font_size.replace('px', ''))
        assert font_size_px >= 14, f"Subtitle font size {font_size_px}px too small for mobile"
    
    def test_mobile_form_usability(self, test_server):
        """Test that forms are usable on mobile"""
        if not self.drivers:
            pytest.skip("No mobile drivers available")
        
        driver = self.drivers.get("iPhone 12")
        if not driver:
            pytest.skip("iPhone 12 driver not available")
        
        driver.get(test_server['base_url'])
        
        # Click Host New Game
        host_button = driver.find_element(By.XPATH, "//button[contains(text(), 'Host New Game')]")
        host_button.click()
        
        WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.ID, "host-game"))
        )
        
        # Check input field size and accessibility
        username_input = driver.find_element(By.ID, "host-username")
        input_height = username_input.size['height']
        assert input_height >= 44, f"Input height {input_height}px too small for mobile"
        
        # Test that input doesn't zoom on focus (font-size >= 16px)
        font_size = driver.execute_script(
            "return window.getComputedStyle(arguments[0]).fontSize", username_input
        )
        font_size_px = float(font_size.replace('px', ''))
        assert font_size_px >= 16, f"Input font size {font_size_px}px will cause zoom on iOS"
    
    def test_mobile_game_creation_flow(self, test_server):
        """Test the complete mobile game creation flow"""
        if not self.drivers:
            pytest.skip("No mobile drivers available")

        driver = self.drivers.get("iPhone 12")
        if not driver:
            pytest.skip("iPhone 12 driver not available")
        
        self._verify_server_health(test_server)

        # Test mobile game flow with better error handling
        try:
            result = MobileBrowserHelper.test_mobile_game_flow(driver, test_server)
            assert result, "Mobile game flow test failed"
        except Exception as e:
            print(f"❌ Mobile game flow failed: {e}")
            try:
                driver.save_screenshot("mobile_game_flow_error.png")
                print("Screenshot saved as mobile_game_flow_error.png")
            except:
                pass
            raise

    def test_cross_device_consistency(self, test_server):
        """Test that the UI is consistent across different mobile devices"""
        if len(self.drivers) < 2:
            pytest.skip("Need at least 2 mobile drivers for consistency testing")
        
        results = {}
        
        for device_name, driver in self.drivers.items():
            driver.get(test_server['base_url'])
            
            # Check that main elements exist and are visible
            container = driver.find_element(By.CLASS_NAME, "container")
            h1 = driver.find_element(By.TAG_NAME, "h1")
            buttons = driver.find_elements(By.TAG_NAME, "button")
            
            results[device_name] = {
                'container_visible': container.is_displayed(),
                'h1_visible': h1.is_displayed(),
                'button_count': len([b for b in buttons if b.is_displayed()]),
                'viewport_width': driver.get_window_size()['width']
            }
            
            print(f"\n{device_name}: {results[device_name]}")
        
        # All devices should show the same basic elements
        button_counts = [r['button_count'] for r in results.values()]
        assert len(set(button_counts)) <= 1, f"Inconsistent button counts across devices: {button_counts}"
        
        # All devices should show main elements
        for device_name, result in results.items():
            assert result['container_visible'], f"Container not visible on {device_name}"
            assert result['h1_visible'], f"H1 not visible on {device_name}"
