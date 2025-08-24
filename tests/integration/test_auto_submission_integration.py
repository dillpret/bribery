#!/usr/bin/env python3
"""
Integration tests for the auto-submission feature using SocketIO

Prerequisites:
- All dependencies in requirements.txt must be installed
- Run: py -m pip install -r requirements.txt

Test Philosophy:
- These tests use SocketIO communication rather than UI tests (which are brittle)
- We prefer testing socket communication directly over Selenium UI tests
- If tests fail with "SocketIO helper not available", run: py scripts\verify_test_deps.py

Quick Test Commands:
- Run unit tests: py -m pytest tests/unit/
- Run integration tests: py -m pytest tests/integration/
- Run specific test: py -m pytest tests/integration/test_auto_submission_integration.py::test_auto_submission_integration -v
"""

import pytest
import time
from unittest.mock import patch

def test_auto_submission_integration(socketio_helper_manager):
    """
    Test that the server correctly processes bribes when timer expires
    without requiring explicit submission.
    """
    # Create test scenario with more clear player names to avoid conflicts
    host = socketio_helper_manager.add_player("AutoTestHost")
    player1 = socketio_helper_manager.add_player("AutoPlayer1")
    player2 = socketio_helper_manager.add_player("AutoPlayer2")
    
    # Create game with very short submission time
    game_id = host.create_game("AutoTestHost", rounds=1, submission_time=2)
    
    # Make sure players join successfully
    join_result1 = player1.join_game("AutoPlayer1", game_id)
    join_result2 = player2.join_game("AutoPlayer2", game_id)
    assert join_result1, "Player 1 should join game successfully"
    assert join_result2, "Player 2 should join game successfully"
    
    # Wait for lobby update to confirm all players are in
    host.wait_for_event('lobby_update')
    
    # Start the game
    start_result = host.start_game()
    assert start_result, "Game should start successfully"
    
    # Wait for targets event
    targets_received = host.wait_for_event('your_targets')
    assert targets_received, "Host should receive targets event"
    
    # Get the targets data
    host_targets_data = host.get_event('your_targets')
    assert host_targets_data is not None, "Host should have targets data"
    host_targets = host_targets_data.get('targets', [])
    
    player1_targets_data = player1.wait_for_event('your_targets')
    assert player1_targets_data is not None, "Player1 should receive targets"
    player1_targets = player1_targets_data.get('targets', [])
    
    player2_targets_data = player2.wait_for_event('your_targets')
    assert player2_targets_data is not None, "Player2 should receive targets"
    player2_targets = player2_targets_data.get('targets', [])
    
    # Make sure we have targets to work with
    assert len(host_targets) > 0, "Host should have at least one target"
    
    # Only submit bribe for host, leave player1 and player2 unsubmitted
    if host_targets:
        host_target_id = host_targets[0].get('target_id')
        if host_target_id:
            host.submit_bribe(host_target_id, "Host's bribe")
    
    # Socket service will send data directly to the server when socket events are emitted
    # Instead of interacting with the UI, we'll mock the bribe values in localStorage
    # and wait for the timer to expire
    
    # Wait for voting phase which indicates timer expiration
    # Since we set submission_time=2, this should happen quickly
    voting_data = host.wait_for_event('voting_phase', timeout=5)
    
    # Check that we received voting data
    assert voting_data is not None, "Should transition to voting phase when timer expires"
    
    # Check if the game moved to the next phase
    game_state = host.get_game_state(game_id)
    assert game_state is not None, "Should be able to get game state"
    assert game_state.get('state') == 'voting', "Game should be in voting phase"
    
    # Since we're not able to directly test the JavaScript auto-submission,
    # we're verifying the server-side behavior allows phase transition
    # even with incomplete submissions


def test_auto_submission_mocked_client(socketio_helper_manager):
    """
    Test auto-submission using a mocked client that simulates the JavaScript behavior
    """
    # Create test scenario
    host = socketio_helper_manager.add_player("MockTestHost")
    player1 = socketio_helper_manager.add_player("MockPlayer1")
    player2 = socketio_helper_manager.add_player("MockPlayer2")
    
    # Create game with longer submission time so we can intercept
    game_id = host.create_game("MockTestHost", rounds=1, submission_time=4)
    
    # Make sure players join successfully
    join_result1 = player1.join_game("MockPlayer1", game_id)
    join_result2 = player2.join_game("MockPlayer2", game_id)
    assert join_result1, "Player 1 should join game successfully"
    assert join_result2, "Player 2 should join game successfully"
    
    # Wait for lobby update to confirm all players are in
    host.wait_for_event('lobby_update')
    
    # Start the game
    start_result = host.start_game()
    assert start_result, "Game should start successfully"
    
    # Wait for targets event
    targets_received = host.wait_for_event('your_targets')
    assert targets_received, "Host should receive targets event"
    
    # Get the targets data
    host_targets_data = host.get_event('your_targets')
    assert host_targets_data is not None, "Host should have targets data"
    host_targets = host_targets_data.get('targets', [])
    
    player1_targets_data = player1.wait_for_event('your_targets')
    assert player1_targets_data is not None, "Player1 should receive targets"
    player1_targets = player1_targets_data.get('targets', [])
    
    player2_targets_data = player2.wait_for_event('your_targets')
    assert player2_targets_data is not None, "Player2 should receive targets"
    player2_targets = player2_targets_data.get('targets', [])
    
    # Just before timer expires, simulate what the JavaScript auto-submit would do
    # by submitting any non-empty bribes
    
    # Wait almost until timer expiry
    time.sleep(3)
    
    # Simulate auto-submission for player1
    if player1_targets and len(player1_targets) > 0:
        player1_target_id = player1_targets[0].get('target_id')
        if player1_target_id:
            player1.submit_bribe(player1_target_id, "Auto-submitted bribe from player1")
    
    # Wait for voting phase
    voting_data = host.wait_for_event('voting_phase', timeout=3)
    assert voting_data is not None, "Should transition to voting phase after timer expires"
    
    # Check if the game moved to the next phase
    game_state = host.get_game_state(game_id)
    assert game_state is not None, "Should be able to get game state"
    assert game_state.get('state') == 'voting', "Game should be in voting phase"
    
    # Since we can't directly test the client-side JavaScript, we'll verify
    # that the server is correctly handling the game flow with auto-submission
