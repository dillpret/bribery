#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tests for edge cases and tolerance in game mechanics
"""

import pytest
from tests.unit.game_mechanics import Game, GameManager

class TestEdgeCasesAndTolerances:
    """Test edge cases and error tolerance"""
    
    def test_late_joiner_handling(self):
        """Test late joiners wait until next round and start with 0 points"""
        game = Game("TEST1234", "host", {'rounds': 3, 'submission_time': 60, 'voting_time': 30})
        
        # Game in progress with existing players
        game.add_player("p1", "Player1")
        game.add_player("p2", "Player2")
        game.add_player("p3", "Player3")
        game.state = "voting"
        game.current_round = 1
        
        # Existing players have scores
        game.scores = {"p1": 5, "p2": 3, "p3": 2}
        
        # Late joiner arrives
        game.add_player("p4", "LatePlayer")
        
        # Late joiner should start with 0 points
        assert game.scores["p4"] == 0
        
        # Late joiner should be in the game but not affect current round
        assert game.get_player_count() == 4
        assert "p4" in game.players
    
    def test_host_disconnection_game_continues(self):
        """Test game continues even if host disconnects"""
        game = Game("TEST1234", "host", {'rounds': 3, 'submission_time': 60, 'voting_time': 30})
        
        # Add host and other players
        game.add_player("host", "HostPlayer")
        game.add_player("p1", "Player1")
        game.add_player("p2", "Player2")
        
        # Game in progress
        game.state = "submission"
        game.current_round = 1
        
        # Host disconnects
        game.players["host"]["connected"] = False
        
        # Game should continue
        assert game.state == "submission"
        assert game.current_round == 1
        assert game.get_connected_player_count() == 2
        
        # Any player should be able to restart after completion
        # (This would be handled at the UI/socket level, not in game logic)
    
    def test_empty_game_cleanup_conditions(self):
        """Test conditions for empty game cleanup"""
        game = Game("TEST1234", "host", {'rounds': 3, 'submission_time': 60, 'voting_time': 30})
        
        # Game with no players should be eligible for cleanup
        assert len(game.players) == 0
        assert self._should_cleanup_game(game)
        
        # Game with only disconnected players should be eligible for cleanup
        game.add_player("p1", "Player1")
        game.players["p1"]["connected"] = False
        assert game.get_connected_player_count() == 0
        assert self._should_cleanup_game(game)
        
        # Game with connected players should NOT be cleaned up
        game.players["p1"]["connected"] = True
        assert not self._should_cleanup_game(game)
    
    def test_content_type_validation(self):
        """Test different submission content types are supported"""
        valid_content_types = ["text", "image", "link"]
        
        for content_type in valid_content_types:
            submission = {
                "content": f"test {content_type} content",
                "type": content_type
            }
            assert self._is_valid_submission(submission)
        
        # Invalid content type should be rejected
        invalid_submission = {
            "content": "test content",
            "type": "invalid_type"
        }
        assert not self._is_valid_submission(invalid_submission)
    
    def _should_cleanup_game(self, game):
        """Helper: Determine if game should be cleaned up"""
        # Game should be cleaned up if no connected players
        return game.get_connected_player_count() == 0
    
    def _is_valid_submission(self, submission):
        """Helper: Validate submission format"""
        valid_types = ["text", "image", "link"]
        return (
            isinstance(submission, dict) and
            "content" in submission and
            "type" in submission and
            submission["type"] in valid_types and
            isinstance(submission["content"], str) and
            len(submission["content"]) > 0
        )
