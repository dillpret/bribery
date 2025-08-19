#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
UI tests using browser automation

Dependencies:
- pytest (from requirements.txt)
- selenium (from requirements-dev.txt)
- webdriver-manager (from requirements-dev.txt)
- Chrome browser (installed on system)

Common Issues:
- If 'selenium' import fails: Run 'py -m pip install -r requirements-dev.txt'
- If browser fails to start: Chrome may be outdated or missing
- For timeout issues: Check test server is running on port 5001
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

class TestUIBasic:
    """Basic UI tests for individual page elements and flows"""
    
    def setup_method(self):
        """Set up test environment for each test method"""
        # Check if selenium is available
        try:
            from selenium import webdriver
            selenium_available = True
        except ImportError:
            selenium_available = False
        
        if not selenium_available:
            pytest.skip("Selenium not available")
        
        self.driver = BrowserHelper.create_chrome_driver()
        if not self.driver:
            pytest.skip("Browser driver not available")
    
    def teardown_method(self):
        """Clean up after each test method"""
        if hasattr(self, 'driver') and self.driver:
            self.driver.quit()
    
    def _verify_server_health(self, test_server):
        """Verify the test server is responding properly"""
        try:
            response = requests.get(test_server['base_url'], timeout=5)
            if response.status_code != 200:
                pytest.skip(f"Test server not responding properly (status: {response.status_code})")
        except requests.exceptions.RequestException as e:
            pytest.skip(f"Test server not accessible: {e}")
    
    def test_home_page_elements(self, test_server):
        """Test that all home page elements are present"""
        if not self.driver:
            pytest.skip("Browser driver not available")
            
        self._verify_server_health(test_server)
        
        self.driver.get(test_server['base_url'])
        time.sleep(2)  # Allow page to fully load
        
        # Check title
        assert "Bribery" in self.driver.title
        
        # Check main elements
        from selenium.webdriver.common.by import By
        assert self.driver.find_element(By.ID, "main-menu")
        assert self.driver.find_element(By.XPATH, "//button[contains(text(), 'Host New Game')]")
        assert self.driver.find_element(By.XPATH, "//button[contains(text(), 'Join Game')]")
    
    def test_host_game_flow(self, test_server):
        """Test the complete host game flow"""
        if not self.driver:
            pytest.skip("Browser driver not available")
            
        self._verify_server_health(test_server)
        
        game_id = BrowserHelper.create_game_as_host(self.driver, test_server, "TestHost")
        
        assert len(game_id) > 0
        assert game_id.isalnum()
        
        # Store game_id for use in other tests
        self.last_created_game_id = game_id
    
    def test_join_game_flow(self, test_server):
        """Test joining a game"""
        if not self.driver:
            pytest.skip("Browser driver not available")
            
        self._verify_server_health(test_server)
        
        # First create a game to join
        self.test_host_game_flow(test_server)
        game_id = self.last_created_game_id
        
        # Join the game
        window = BrowserHelper.join_game_as_player(self.driver, test_server, game_id, "TestPlayer")
        
        assert game_id in self.driver.current_url
        
        # Close the extra window
        self.driver.close()
        self.driver.switch_to.window(self.driver.window_handles[0])
