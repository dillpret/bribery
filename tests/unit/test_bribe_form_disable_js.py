#!/usr/bin/env python3
"""
Test cases for bribe form disable JavaScript functionality
"""

import pytest
import os
import re


class TestBribeFormDisableCode:
    """Test the JavaScript code for disabling bribe forms after submission"""

    def test_socket_handler_disables_textarea_on_submission(self):
        """Test that bribe_submitted handler disables textarea"""
        # Read the socket-handlers.js file
        socket_handlers_path = os.path.join(
            os.path.dirname(__file__), '..', '..', 
            'static', 'js', 'socket-handlers.js'
        )
        
        with open(socket_handlers_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check that bribe_submitted handler exists
        assert "socket.on('bribe_submitted'," in content
        
        # Check that textarea is disabled
        assert 'textarea.disabled = true' in content
        
        # Check that visual styling is applied
        assert 'backgroundColor' in content
        assert 'cursor' in content
        
        # Check that drop area is also disabled
        assert 'pointerEvents' in content
        assert 'opacity' in content

    def test_round_started_resets_form_elements(self):
        """Test that round_started handler re-enables form elements"""
        socket_handlers_path = os.path.join(
            os.path.dirname(__file__), '..', '..', 
            'static', 'js', 'socket-handlers.js'
        )
        
        with open(socket_handlers_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check that round_started handler exists and resets forms
        assert "socket.on('round_started'," in content
        
        # Find the round_started section
        round_started_match = re.search(
            r"socket\.on\('round_started',.*?(?=socket\.on|\Z)", 
            content, 
            re.DOTALL
        )
        
        assert round_started_match is not None
        round_started_section = round_started_match.group(0)
        
        # Verify form reset logic exists
        assert 'textarea.disabled = false' in round_started_section
        assert 'button.disabled = false' in round_started_section
        assert 'button.textContent = \'Submit Bribe\'' in round_started_section

    def test_clear_game_state_resets_forms(self):
        """Test that clearGameState function resets form elements"""
        socket_handlers_path = os.path.join(
            os.path.dirname(__file__), '..', '..', 
            'static', 'js', 'socket-handlers.js'
        )
        
        with open(socket_handlers_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check that clearGameState function exists and resets forms
        assert 'function clearGameState()' in content
        
        # Find the clearGameState function
        clear_state_match = re.search(
            r"function clearGameState\(\).*?(?=socket\.on|function|\Z)", 
            content, 
            re.DOTALL
        )
        
        assert clear_state_match is not None
        clear_state_section = clear_state_match.group(0)
        
        # Verify form reset logic exists in clearGameState
        assert 'textarea.disabled = false' in clear_state_section
        assert 'button.disabled = false' in clear_state_section
        assert 'textarea.value = \'\'' in clear_state_section

    def test_selectors_target_correct_elements(self):
        """Test that JavaScript selectors target the correct DOM elements"""
        socket_handlers_path = os.path.join(
            os.path.dirname(__file__), '..', '..', 
            'static', 'js', 'socket-handlers.js'
        )
        
        with open(socket_handlers_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check for correct element selectors
        assert 'submission-${data.target_id}' in content  # textarea selector
        assert 'drop-${data.target_id}' in content        # drop area selector
        assert 'submitTargetBribe' in content             # button onclick selector
        
        # Check for querySelector patterns that target form elements
        assert 'querySelectorAll(\'textarea[id^="submission-"]\')' in content
        assert 'querySelectorAll(\'div[id^="drop-"]\')' in content
        assert 'querySelectorAll(\'button[onclick^="submitTargetBribe"]\')' in content

    def test_visual_feedback_is_applied(self):
        """Test that proper visual feedback is applied to disabled elements"""
        socket_handlers_path = os.path.join(
            os.path.dirname(__file__), '..', '..', 
            'static', 'js', 'socket-handlers.js'
        )
        
        with open(socket_handlers_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check that visual styling changes are applied when disabling
        assert '#f8f9fa' in content              # Light grey background
        assert 'not-allowed' in content         # Cursor change
        assert 'Submitted ✓' in content         # Button text change
        assert '#28a745' in content             # Success green color
        
        # Check that styles are cleared when re-enabling
        assert "style.backgroundColor = ''" in content
        assert "style.cursor = ''" in content
        assert "style.background = ''" in content
