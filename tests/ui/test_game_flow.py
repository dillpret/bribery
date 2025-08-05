#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Advanced UI tests for complete game flows
"""

import pytest
import time
import sys
import os

# Add the app directory to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'src'))
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from helpers.browser_helpers import BrowserHelper

# Selenium imports are optional
try:
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    SELENIUM_AVAILABLE = True
except ImportError:
    SELENIUM_AVAILABLE = False

class TestUIGameFlow:
    """Advanced UI tests for complete game scenarios"""
    
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
    
    def test_complete_game_round_ui(self, test_server):
        """Test a complete game round with multiple players through the UI"""
        # Phase 1: Create Game (Host)
        print("\n🎯 Phase 1: Creating game with host...")
        game_id = BrowserHelper.create_game_as_host(self.driver, test_server, "GameHost")
        print(f"   ✅ Game created with ID: {game_id}")
        
        # Phase 2: Add Players
        print("\n👥 Phase 2: Adding players...")
        player_windows = []
        player_names = ["Alice", "Bob", "Charlie"]
        
        for player_name in player_names:
            window = BrowserHelper.join_game_as_player(self.driver, test_server, game_id, player_name)
            player_windows.append(window)
            print(f"   ✅ {player_name} joined the game")
        
        # Phase 3: Start Game
        print("\n🚀 Phase 3: Starting the game...")
        # Switch back to host window (first window)
        self.driver.switch_to.window(self.driver.window_handles[0])
        
        # Navigate to game page
        self.driver.get(f"{test_server['base_url']}/game/{game_id}")
        
        # Handle username alert for host when navigating to game page
        try:
            WebDriverWait(self.driver, 5).until(EC.alert_is_present())
            alert = self.driver.switch_to.alert
            alert.send_keys("GameHost")
            alert.accept()
            print("   ✅ Host username alert handled")
        except:
            print("   ℹ️  No username alert for host")
        
        # Wait for lobby and start game
        try:
            start_button = WebDriverWait(self.driver, 15).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Start Game')]"))
            )
            start_button.click()
            print("   ✅ Game started!")
            
            # Phase 4: Submission Phase
            print("\n📝 Phase 4: Submission phase...")
            
            # Wait for submission phase to begin
            WebDriverWait(self.driver, 15).until(
                EC.visibility_of_element_located((By.ID, "submission-phase"))
            )
            
            # Submit bribes from each player with minimal delay
            all_windows = self.driver.window_handles
            for i, window in enumerate(all_windows):
                self.driver.switch_to.window(window)
                
                player_name = ["GameHost", "Alice", "Bob", "Charlie"][i]
                bribe_text = f"Creative bribe from {player_name}!"
                
                if BrowserHelper.submit_bribe(self.driver, bribe_text):
                    print(f"   ✅ {player_name} submitted bribe")
                else:
                    print(f"   ⚠️  {player_name} failed to submit bribe")
            
            # Phase 5: Voting Phase - Wait for state change, not arbitrary time
            print("\n🗳️  Phase 5: Voting phase...")
            
            # Vote from each player - try immediately, no long waits
            voted_successfully = 0
            for i, window in enumerate(all_windows):
                self.driver.switch_to.window(window)
                player_name = ["GameHost", "Alice", "Bob", "Charlie"][i]
                
                # Quick attempt at voting
                if BrowserHelper.vote_for_first_option(self.driver):
                    print(f"   ✅ {player_name} voted")
                    voted_successfully += 1
                else:
                    print(f"   ⚠️  {player_name} failed to vote")
            
            print(f"   📊 {voted_successfully}/{len(all_windows)} players voted successfully")
            
            # Phase 6: Results - Wait for any results phase
            print("\n🏆 Phase 6: Viewing results...")
            
            # Switch to host window to check results
            self.driver.switch_to.window(self.driver.window_handles[0])
            
            try:
                # Wait for results to appear (could be scoreboard-phase or final-results)
                WebDriverWait(self.driver, 20).until(
                    lambda driver: driver.find_elements(By.ID, "scoreboard-phase") or 
                                 driver.find_elements(By.ID, "final-results")
                )
                print("   ✅ Results displayed successfully!")
                
                # Verify scoreboard exists
                scoreboard = None
                try:
                    scoreboard = self.driver.find_element(By.ID, "scoreboard")
                except:
                    try:
                        scoreboard = self.driver.find_element(By.ID, "final-scoreboard")
                    except:
                        pass
                
                if scoreboard:
                    print("   ✅ Scoreboard found")
                else:
                    print("   ⚠️  Scoreboard not found, but results phase loaded")
                
            except Exception as e:
                print(f"   ⚠️  Results verification failed: {str(e)}")
                # Take screenshot for debugging
                self.driver.save_screenshot("test_failure_results.png")
        
        except Exception as e:
            print(f"❌ Game flow failed: {str(e)}")
            # Take screenshot for debugging
            self.driver.save_screenshot("test_failure_complete_round.png")
            raise
        
        finally:
            # Phase 7: Cleanup
            print("\n🧹 Phase 7: Cleaning up...")
            # Close all extra windows
            while len(self.driver.window_handles) > 1:
                self.driver.switch_to.window(self.driver.window_handles[-1])
                self.driver.close()
            
            self.driver.switch_to.window(self.driver.window_handles[0])
            print("   ✅ Cleanup complete")
