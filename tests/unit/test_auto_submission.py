#!/usr/bin/env python3
"""
Test cases for auto-submission of bribes when timers expire

This test verifies the JavaScript implementation without requiring a running server.
It's preferred over UI/Selenium tests which are more brittle and difficult to maintain.

Test Philosophy:
- We use static analysis to verify JavaScript structure
- This approach is faster and more reliable than UI tests
- No server or browser is required to run these tests
- Run with: py -m pytest tests/unit/test_auto_submission.py -v
"""

import pytest
import os
import re

def test_auto_submission_javascript_implementation():
    """
    Test that the JavaScript code includes auto-submission functionality
    when timers expire.
    """
    # Verify that the autoSubmitPendingBribes function exists in ui-handlers.js
    ui_handlers_path = os.path.join(
        os.path.dirname(__file__), '..', '..', 
        'static', 'js', 'ui-handlers.js'
    )
    
    with open(ui_handlers_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check that autoSubmitPendingBribes function exists
    assert 'function autoSubmitPendingBribes()' in content, \
        "The autoSubmitPendingBribes function should be defined in ui-handlers.js"
    
    # Verify that the function collects and submits non-empty bribes
    # Extract the function content from where it's defined until the next function
    match_index = content.find('function autoSubmitPendingBribes()')
    if match_index >= 0:
        end_index = content.find('function setupDragDrop', match_index)
        if end_index >= 0:
            auto_submit_code = content[match_index:end_index].strip()
            
            # Check for key functionality
            assert "submitBribe" in auto_submit_code, \
                "autoSubmitPendingBribes should call submitBribe"
            assert 'textarea.value.trim()' in auto_submit_code, \
                "autoSubmitPendingBribes should check for content in textareas"
            assert 'button.disabled = true' in auto_submit_code, \
                "autoSubmitPendingBribes should disable the submit button after auto-submission"
        else:
            assert False, "Could not find end of function"
    else:
        assert False, "Could not find autoSubmitPendingBribes function"
    
    # Verify that socket-handlers.js uses this function when timers expire
    socket_handlers_path = os.path.join(
        os.path.dirname(__file__), '..', '..', 
        'static', 'js', 'socket-handlers.js'
    )
    
    with open(socket_handlers_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check submission phase
    submission_timer = re.search(
        r'startTimer\(data\.time_limit,.*?autoSubmitPendingBribes\(\)',
        content, 
        re.DOTALL
    )
    assert submission_timer is not None, \
        "Submission phase should use timer callback to auto-submit bribes"
    
    # Check voting phase - should auto-submit vote if selected
    voting_timer = re.search(
        r'startTimer\(data\.time_limit,.*?selectedVote.*?submitVote\(\)',
        content, 
        re.DOTALL
    )
    assert voting_timer is not None, \
        "Voting phase should auto-submit selected vote when timer expires"
    
    # Check prompt selection phase
    prompt_timer = re.search(
        r'startTimer\(data\.time_limit,.*?selectPrompt\(\)',
        content, 
        re.DOTALL
    )
    assert prompt_timer is not None, \
        "Prompt selection phase should auto-select prompt when timer expires"
