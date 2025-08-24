#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Integration test for progress tracking events
"""

import pytest
import sys
import os
import json
from unittest.mock import Mock, patch

# Add the src directory to the path  
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'src'))

from game import Game, GameManager


class TestProgressTrackingIntegration:
    """Integration tests for progress tracking with socket events"""
    
    def setup_method(self):
        """Set up test environment"""
        self.game_manager = GameManager()
        self.mock_socketio = Mock()
        
    def test_submission_progress_integration(self):
        """Test that submission progress events are emitted correctly"""
        # Create a game with 3 players
        game = Game("TEST", "host", {'rounds': 3, 'submission_time': 60, 'voting_time': 30})
        
        players = ["player1", "player2", "player3"]
        for i, player_id in enumerate(players):
            game.add_player(player_id, f"Player{i+1}")
        
        game.current_round = 1
        game.bribes = {1: {}}
        
        # Mock the socketio emit function  
        with patch('src.web.socket_handlers.progress_tracking.socketio', self.mock_socketio):
            # Import here to get the patched version
            from src.web.socket_handlers.progress_tracking import emit_submission_progress
            
            # Test initial state (0/3)
            emit_submission_progress(game)
            
            # Verify the call
            self.mock_socketio.emit.assert_called_with(
                'submission_progress',
                {
                    'completed': 0,
                    'total': 3,
                    'message': '0/3 players finished'
                },
                room='TEST'
            )
            
            # Add one complete submission
            game.bribes[1]["player1"] = {
                "player2": {"content": "bribe1", "type": "text"},
                "player3": {"content": "bribe2", "type": "text"}
            }
            
            emit_submission_progress(game)
            
            # Should now show 1/3
            expected_call = (
                'submission_progress',
                {
                    'completed': 1,
                    'total': 3,
                    'message': '1/3 players finished'
                },
            )
            # Check if this call was made (args[0] for positional args)
            calls = self.mock_socketio.emit.call_args_list
            assert any(call[0][0] == expected_call[0] and 
                      call[0][1]['completed'] == expected_call[1]['completed'] 
                      for call in calls)
                      
    def test_voting_progress_integration(self):
        """Test that voting progress events are emitted correctly"""
        # Create a game with 4 players
        game = Game("TEST", "host", {'rounds': 3, 'submission_time': 60, 'voting_time': 30})
        
        players = ["player1", "player2", "player3", "player4"]
        for i, player_id in enumerate(players):
            game.add_player(player_id, f"Player{i+1}")
        
        game.current_round = 1
        game.votes = {1: {}}
        
        # Mock the socketio emit function
        with patch('src.web.socket_handlers.progress_tracking.socketio', self.mock_socketio):
            from src.web.socket_handlers.progress_tracking import emit_voting_progress
            
            # Test with 2 remaining players (should show names)
            game.votes[1]["player1"] = "bribe1"
            game.votes[1]["player2"] = "bribe2"
            
            emit_voting_progress(game)
            
            # Should show waiting for the remaining 2 players by name
            calls = self.mock_socketio.emit.call_args_list
            last_call = calls[-1]
            
            assert last_call[0][0] == 'voting_progress'
            message = last_call[0][1]['message']
            assert 'Player3' in message and 'Player4' in message
            assert 'Waiting for' in message
            
    def test_progress_with_inactive_players(self):
        """Test progress tracking excludes inactive players"""
        # Create a game with mixed active/inactive players
        game = Game("TEST", "host", {'rounds': 3, 'submission_time': 60, 'voting_time': 30})
        
        # Add 5 players, make 2 inactive
        players = ["player1", "player2", "player3", "player4", "player5"]
        for i, player_id in enumerate(players):
            game.add_player(player_id, f"Player{i+1}")
        
        # Make players 4 and 5 inactive (mid-game joiners)
        game.players["player4"]["active_in_round"] = False
        game.players["player5"]["active_in_round"] = False
        
        game.current_round = 1
        game.bribes = {1: {}}
        
        with patch('src.web.socket_handlers.progress_tracking.socketio', self.mock_socketio):
            from src.web.socket_handlers.progress_tracking import emit_submission_progress
            
            # Should only count 3 active players
            emit_submission_progress(game)
            
            calls = self.mock_socketio.emit.call_args_list
            last_call = calls[-1]
            
            assert last_call[0][1]['total'] == 3  # Only active players
            assert '0/3 players finished' == last_call[0][1]['message']
