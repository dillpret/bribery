#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Browser automation helper functions for UI tests

If you see import errors with Selenium or webdriver_manager:
Run: py -m pip install -r requirements-dev.txt
"""

import os
import time

# Selenium imports are optional
try:
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.chrome.options import Options
    from webdriver_manager.chrome import ChromeDriverManager
    from selenium.webdriver.chrome.service import Service
    SELENIUM_AVAILABLE = True
except ImportError:
    SELENIUM_AVAILABLE = False
    print("Selenium imports failed - UI tests will be skipped")
    print("To run UI tests: py -m pip install -r requirements-dev.txt")

class BrowserHelper:
    """Helper class for browser automation in tests"""
    
    @staticmethod
    def create_chrome_driver():
        """Create Chrome driver with optimised settings"""
        if not SELENIUM_AVAILABLE:
            return None
            
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--window-size=1920,1080')
        # Suppress Google service errors
        chrome_options.add_argument('--disable-background-networking')
        chrome_options.add_argument('--disable-background-timer-throttling')
        chrome_options.add_argument('--disable-backgrounding-occluded-windows')
    
    @staticmethod
    def create_chrome_driver(headless=True):
        """Create Chrome driver with optimised settings
        
        Args:
            headless (bool): Whether to run Chrome in headless mode
            
        Returns:
            WebDriver or None: Chrome WebDriver instance or None if not available
            
        Raises:
            RuntimeError: If dependencies are missing with clear installation instructions
        """
        if not SELENIUM_AVAILABLE:
            raise RuntimeError(
                "Selenium is required for UI tests but not installed.\n"
                "Install it with: py -m pip install -r requirements-dev.txt"
            )
            
        # Create Chrome options
        chrome_options = Options()
        if headless:
            chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--window-size=1920,1080')
        # Suppress Google service errors
        chrome_options.add_argument('--disable-background-networking')
        chrome_options.add_argument('--disable-background-timer-throttling')
        chrome_options.add_argument('--disable-backgrounding-occluded-windows')
        chrome_options.add_argument('--disable-renderer-backgrounding')
        chrome_options.add_argument('--disable-features=TranslateUI')
        chrome_options.add_argument('--disable-extensions')
        chrome_options.add_argument('--disable-ipc-flooding-protection')
        chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_argument('--log-level=3')  # Suppress INFO, WARNING, ERROR
        
        try:
            # Try different approaches to get ChromeDriver - system PATH first for offline reliability
            service = None
            
            # Method 1: Try system PATH chromedriver first (works offline)
            try:
                driver = webdriver.Chrome(options=chrome_options)
                print("✅ Using system PATH chromedriver")
                return driver
            except Exception as e1:
                print(f"System PATH chromedriver failed: {e1}")
                
                # Method 2: Try ChromeDriverManager with caching
                try:
                    service = Service(ChromeDriverManager().install())
                    driver = webdriver.Chrome(service=service, options=chrome_options)
                    print("✅ Using ChromeDriverManager")
                    return driver
                except Exception as e2:
                    print(f"ChromeDriverManager failed: {e2}")
                    
                    # Method 3: Try common installation paths
                    common_paths = [
                        r".\chromedriver.exe",
                        r"chromedriver.exe",
                        r"C:\chromedriver\chromedriver.exe",
                        r"C:\Program Files\chromedriver\chromedriver.exe",
                        r"C:\Program Files (x86)\chromedriver\chromedriver.exe",
                        r"C:\Tools\chromedriver.exe",
                        r"C:\WebDrivers\chromedriver.exe",
                        os.path.join(os.path.dirname(__file__), "chromedriver.exe"),
                    ]
                    
                    for path in common_paths:
                        if os.path.exists(path):
                            try:
                                service = Service(path)
                                driver = webdriver.Chrome(service=service, options=chrome_options)
                                print(f"✅ Using chromedriver from: {path}")
                                return driver
                            except Exception as e3:
                                print(f"Path {path} failed: {e3}")
                                continue
                    
                    print("❌ All ChromeDriver methods failed")
                    return None
                    
        except Exception as e:
            print("Chrome driver not available:", str(e))
            return None
    
    @staticmethod
    def create_game_as_host(driver, test_server, username="TestHost"):
        """Helper method to create a game and return game ID"""
        try:
            # Navigate to the page and wait for it to load
            driver.get(test_server['base_url'])
            
            # Wait for the page to fully load by checking for the main content
            WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            # Additional wait for any JavaScript to initialize
            time.sleep(1)
            
            # Find and click the host button
            host_button = WebDriverWait(driver, 15).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Host New Game')]"))
            )
            host_button.click()

            # Wait for the host game form to appear
            WebDriverWait(driver, 15).until(
                EC.visibility_of_element_located((By.ID, "host-game"))
            )
            
            # Fill in username
            username_input = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.ID, "host-username"))
            )
            username_input.clear()
            username_input.send_keys(username)
            
            # Click create game button
            create_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Create Game')]"))
            )
            create_button.click()

            # Wait for game creation confirmation
            WebDriverWait(driver, 20).until(
                EC.visibility_of_element_located((By.ID, "game-created"))
            )
            
            # Get the game ID
            game_id_element = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, "created-game-id"))
            )
            
            return game_id_element.text
            
        except Exception as e:
            print(f"❌ Error in create_game_as_host: {e}")
            print(f"Current URL: {driver.current_url}")
            print(f"Page title: {driver.title}")
            # Take a screenshot for debugging
            try:
                driver.save_screenshot("create_game_error.png")
                print("Screenshot saved as create_game_error.png")
            except:
                pass
            raise
    
    @staticmethod
    def join_game_as_player(driver, test_server, game_id, username):
        """Helper method to join a game in a new window"""
        try:
            # Open new window
            driver.execute_script("window.open('');")
            player_window = driver.window_handles[-1]
            driver.switch_to.window(player_window)
            driver.get(test_server['base_url'])
            
            # Wait for page to load
            WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            time.sleep(1)  # Allow JS to initialize

            # Find and click join button
            join_button = WebDriverWait(driver, 15).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Join Game')]"))
            )
            join_button.click()

            # Wait for join form to appear
            WebDriverWait(driver, 15).until(
                EC.visibility_of_element_located((By.ID, "join-game"))
            )
            
            # Fill in username
            username_input = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.ID, "join-username"))
            )
            username_input.clear()
            username_input.send_keys(username)
            
            # Fill in game ID
            game_id_input = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.ID, "game-id"))
            )
            game_id_input.clear()
            game_id_input.send_keys(game_id)
            
            # Submit join request
            join_submit_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//div[@id='join-game']//button[contains(text(), 'Join Game')]"))
            )
            join_submit_button.click()

            # Handle potential alert
            try:
                WebDriverWait(driver, 3).until(EC.alert_is_present())
                alert = driver.switch_to.alert
                alert.send_keys(username)
                alert.accept()
            except:
                pass

            # Wait for game page to load
            WebDriverWait(driver, 20).until(
                EC.any_of(
                    EC.visibility_of_element_located((By.ID, "game-screen")),
                    EC.visibility_of_element_located((By.CLASS_NAME, "game-content")),
                    EC.visibility_of_element_located((By.ID, "player-list"))
                )
            )
            
            return player_window
            
        except Exception as e:
            print(f"❌ Error in join_game_as_player: {e}")
            print(f"Current URL: {driver.current_url}")
            print(f"Page title: {driver.title}")
            try:
                driver.save_screenshot("join_game_error.png")
                print("Screenshot saved as join_game_error.png")
            except:
                pass
            raise
        WebDriverWait(driver, 10).until(
            lambda driver: "/game/" in driver.current_url
        )
        
        return player_window
    
    @staticmethod
    def submit_bribe(driver, bribe_text="Test bribe"):
        """Helper method to submit bribes for all targets"""
        try:
            # Wait for submission phase to be visible
            WebDriverWait(driver, 10).until(
                EC.visibility_of_element_located((By.ID, "submission-phase"))
            )
            
            # Find all submission textareas (one for each target)
            submission_areas = driver.find_elements(By.CSS_SELECTOR, "textarea.submission-input")
            if not submission_areas:
                print("      → No submission textareas found")
                return False
            
            print(f"      → Found {len(submission_areas)} targets to submit to")
            
            # Submit to ALL targets (each player typically has 2 targets)
            for i, submission_area in enumerate(submission_areas):
                try:
                    submission_area.clear()
                    submission_area.send_keys(f"{bribe_text} (target {i+1})")
                    
                    # Find the corresponding submit button
                    submit_buttons = driver.find_elements(By.CSS_SELECTOR, "button.submit-btn")
                    if i < len(submit_buttons):
                        submit_buttons[i].click()
                        print(f"      → Submitted bribe for target {i+1}")
                    else:
                        print(f"      → No submit button found for target {i+1}")
                        return False
                        
                except Exception as e:
                    print(f"      → Failed to submit for target {i+1}: {str(e)}")
                    return False
                    
            return True
                
        except Exception as e:
            print(f"      → Failed to submit bribes: {str(e)}")
            return False
    
    @staticmethod
    def vote_for_first_option(driver):
        """Helper method to vote for the first available option"""
        try:
            # First, wait for voting phase to be visible with a reasonable timeout
            try:
                WebDriverWait(driver, 5).until(
                    EC.visibility_of_element_located((By.ID, "voting-phase"))
                )
                print(f"      → Voting phase is visible")
            except:
                # If voting phase isn't visible, check what phase we're in
                current_phase = BrowserHelper.get_current_game_phase(driver)
                print(f"      → Current phase: {current_phase}")
                if current_phase != "voting-phase":
                    print(f"      → Not in voting phase, skipping vote")
                    return False
            
            # Look for bribe options with a quick timeout
            bribe_options = driver.find_elements(By.CSS_SELECTOR, ".bribe-option")
            print(f"      → Found {len(bribe_options)} bribe options")
            
            if bribe_options:
                print(f"      → Clicking first bribe option")
                bribe_options[0].click()  # This selects the vote
                
                # Quick check for submit button
                try:
                    submit_vote_btn = WebDriverWait(driver, 2).until(
                        EC.element_to_be_clickable((By.ID, "submit-vote-btn"))
                    )
                    submit_vote_btn.click()
                    print(f"      → Vote submitted successfully")
                    return True
                except:
                    print("      → Submit vote button not clickable")
                    return False
            else:
                print("      → No bribe options found")
                return False
                
        except Exception as e:
            print(f"      → Voting failed: {str(e)}")
            return False
    
    @staticmethod
    def get_current_game_phase(driver):
        """Helper method to determine current game phase"""
        phases = ["lobby", "submission-phase", "voting-phase", "scoreboard-phase", "final-results"]
        for phase in phases:
            try:
                element = driver.find_element(By.ID, phase)
                if element and "hidden" not in element.get_attribute("class"):
                    return phase
            except:
                continue
        return "unknown"
