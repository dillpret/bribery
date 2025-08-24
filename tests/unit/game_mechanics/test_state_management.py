#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tests for game state transitions and management
"""

import pytest
from tests.unit.game_mechanics import Game, GameManager

class TestGameStateManagement:
    """Test game state transitions and validation"""
    
    def test_valid_state_transitions(self):
        """Test valid state transition sequences"""
        game = Game("TEST1234", "host", {'rounds': 3, 'submission_time': 60, 'voting_time': 30})
        
        # Valid sequence: lobby -> submission -> voting -> scoreboard -> submission (next round)
        assert game.state == "lobby"
        
        game.state = "submission"
        assert self._is_valid_transition("lobby", "submission")
        
        game.state = "voting"
        assert self._is_valid_transition("submission", "voting")
        
        game.state = "scoreboard"
        assert self._is_valid_transition("voting", "scoreboard")
        
        # Next round
        game.state = "submission"
        assert self._is_valid_transition("scoreboard", "submission")
        
        # Or finish game
        game.state = "finished"
        assert self._is_valid_transition("scoreboard", "finished")
    
    def test_invalid_state_transitions(self):
        """Test invalid state transitions are rejected"""
        # Can't go directly from lobby to voting
        assert not self._is_valid_transition("lobby", "voting")
        
        # Can't go backwards from voting to submission
        assert not self._is_valid_transition("voting", "submission")
        
        # Can't skip states
        assert not self._is_valid_transition("submission", "scoreboard")
    
    def test_state_persistence_during_disconnections(self):
        """Test game state remains stable during player disconnections"""
        game = Game("TEST1234", "host", {'rounds': 3, 'submission_time': 60, 'voting_time': 30})
        
        # Add players
        game.add_player("p1", "Player1")
        game.add_player("p2", "Player2")
        game.add_player("p3", "Player3")
        
        # Set game in progress
        game.state = "submission"
        game.current_round = 1
        
        # Player disconnects
        game.players["p2"]["connected"] = False
        
        # Game state should remain unchanged
        assert game.state == "submission"
        assert game.current_round == 1
        assert game.get_player_count() == 3  # Still counts disconnected players
        assert game.get_connected_player_count() == 2
    
    def _is_valid_transition(self, from_state, to_state):
        """Helper: Check if state transition is valid"""
        valid_transitions = {
            "lobby": ["submission"],
            "submission": ["voting"],
            "voting": ["scoreboard"],
            "scoreboard": ["submission", "finished"],  # Next round or end game
            "finished": ["lobby"]  # Restart
        }
        return to_state in valid_transitions.get(from_state, [])
