#!/usr/bin/env python3
"""
Test cases for auto-submission of bribes when timers expire
"""

import time
import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def test_auto_submission_on_timer_expiry(test_server, chrome_driver, socketio_helper_manager):
    """Test that bribes are auto-submitted when timer expires"""
    # Create test players
    host = socketio_helper_manager.create_host("TestHost")
    player1 = socketio_helper_manager.create_player("Player1")
    player2 = socketio_helper_manager.create_player("Player2")
    
    # Create and start game with very short submission time (5 seconds)
    game_id = host.create_game("TestHost", rounds=1, submission_time=5)
    player1.join_game(game_id, "Player1")
    player2.join_game(game_id, "Player2")
    host.start_game()
    
    # Wait for targets assignment
    targets_data = host.wait_for_event('your_targets')
    assert 'targets' in targets_data
    target_ids = targets_data['targets']
    
    # Open the game in browser
    chrome_driver.get(f"http://localhost:5001/game/{game_id}")
    
    # Handle authentication if needed
    try:
        WebDriverWait(chrome_driver, 5).until(EC.alert_is_present())
        alert = chrome_driver.switch_to.alert
        alert.send_keys("TestHost")
        alert.accept()
    except:
        pass  # No alert, which is fine
    
    # Wait for submission phase to appear
    WebDriverWait(chrome_driver, 10).until(
        EC.visibility_of_element_located((By.ID, "submission-phase"))
    )
    
    # Find the first textarea and enter some text, but don't submit manually
    try:
        first_target_id = target_ids[0]['target_id']
        textarea = chrome_driver.find_element(By.ID, f"submission-{first_target_id}")
        textarea.send_keys("This is an auto-submission test")
        
        # Wait for the timer to expire (slightly longer than the 5s timer)
        time.sleep(6)
        
        # Check if button was automatically updated to show auto-submission
        WebDriverWait(chrome_driver, 5).until(
            lambda driver: "Auto-Submitted" in 
            driver.find_element(By.CSS_SELECTOR, 
                               f"button[onclick*='submitTargetBribe(\"{first_target_id}\")']").text
        )
        
        # Verify that the button is disabled
        submit_button = chrome_driver.find_element(
            By.CSS_SELECTOR, f"button[onclick*='submitTargetBribe(\"{first_target_id}\")']"
        )
        assert submit_button.get_attribute("disabled") == "true"
        
        # Check that the textarea was also disabled
        assert textarea.get_attribute("disabled") == "true"
        
        # We should also see a bribe_submitted event on the socket
        submission_events = host.get_events('bribe_submitted')
        assert len(submission_events) > 0
        
        # We should eventually transition to voting phase
        WebDriverWait(chrome_driver, 10).until(
            EC.visibility_of_element_located((By.ID, "voting-phase"))
        )
        
        print("Auto-submission test passed successfully!")
        
    except Exception as e:
        # Take a screenshot if something fails
        chrome_driver.save_screenshot("auto_submission_test_failure.png")
        raise e
