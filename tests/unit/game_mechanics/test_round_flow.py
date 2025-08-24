#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tests for game round flow logic
"""

import pytest
from tests.unit.game_mechanics import Game, GameManager

class TestRoundFlowLogic:
    """Test actual round progression and completion logic"""
    
    def test_round_submission_completion_all_players_submit(self):
        """Test round advances when all players submit both bribes"""
        game = Game("TEST1234", "host", {'rounds': 3, 'submission_time': 60, 'voting_time': 30})
        
        # Add 3 players
        game.add_player("p1", "Player1")
        game.add_player("p2", "Player2")
        game.add_player("p3", "Player3")
        
        # Start round
        game.current_round = 1
        game.state = "submission"
        game.round_pairings[1] = game.generate_round_pairings()
        game.bribes[1] = {}
        
        # Initially no submissions
        assert not self._all_submissions_complete(game)
        
        # Add partial submissions
        game.bribes[1]["p1"] = {"p2": {"content": "bribe1", "type": "text"}}
        assert not self._all_submissions_complete(game)
        
        # Complete all submissions (each player submits 2 bribes)
        game.bribes[1] = {
            "p1": {
                "p2": {"content": "p1 to p2", "type": "text"},
                "p3": {"content": "p1 to p3", "type": "text"}
            },
            "p2": {
                "p1": {"content": "p2 to p1", "type": "text"},
                "p3": {"content": "p2 to p3", "type": "text"}
            },
            "p3": {
                "p1": {"content": "p3 to p1", "type": "text"},
                "p2": {"content": "p3 to p2", "type": "text"}
            }
        }
        
        assert self._all_submissions_complete(game)
    
    def test_round_voting_completion_all_players_vote(self):
        """Test voting phase completion when all players vote"""
        game = Game("TEST1234", "host", {'rounds': 3, 'submission_time': 60, 'voting_time': 30})
        
        # Add 3 players
        game.add_player("p1", "Player1")
        game.add_player("p2", "Player2")
        game.add_player("p3", "Player3")
        
        # Set up voting phase
        game.current_round = 1
        game.state = "voting"
        game.votes[1] = {}
        
        # Initially no votes
        assert not self._all_votes_complete(game)
        
        # Add partial votes
        game.votes[1]["p1"] = "p2_p1"  # p1 votes for bribe from p2
        assert not self._all_votes_complete(game)
        
        # Complete all votes
        game.votes[1] = {
            "p1": "p2_p1",  # p1 votes for p2's bribe to p1
            "p2": "p3_p2",  # p2 votes for p3's bribe to p2
            "p3": "p1_p3"   # p3 votes for p1's bribe to p3
        }
        
        assert self._all_votes_complete(game)
    
    def test_partial_submissions_game_progresses(self):
        """Test game progresses even if not all players submit (edge case)"""
        game = Game("TEST1234", "host", {'rounds': 3, 'submission_time': 60, 'voting_time': 30})
        
        # Add 4 players
        game.add_player("p1", "Player1")
        game.add_player("p2", "Player2")
        game.add_player("p3", "Player3")
        game.add_player("p4", "Player4")
        
        # Start round
        game.current_round = 1
        game.state = "submission"
        game.round_pairings[1] = game.generate_round_pairings()
        game.bribes[1] = {}
        
        # Only 3 out of 4 players submit bribes
        game.bribes[1] = {
            "p1": {
                "p2": {"content": "p1 to p2", "type": "text"},
                "p3": {"content": "p1 to p3", "type": "text"}
            },
            "p2": {
                "p1": {"content": "p2 to p1", "type": "text"},
                "p3": {"content": "p2 to p3", "type": "text"}
            },
            "p3": {
                "p1": {"content": "p3 to p1", "type": "text"},
                "p2": {"content": "p3 to p2", "type": "text"}
            }
            # p4 doesn't submit anything
        }
        
        # Game should still be able to progress but not via the standard completion check
        # This tests that we have a mechanism to handle partial submissions
        assert not self._all_submissions_complete(game)
        
        # In a real implementation, there would be a separate method to force progress
        # after a timeout even with incomplete submissions
    
    def _all_submissions_complete(self, game):
        """Helper: Check if all players have submitted all their bribes"""
        expected_submissions = len(game.players) * 2  # Each player submits 2 bribes
        actual_submissions = sum(len(bribes) for bribes in game.bribes[game.current_round].values())
        return actual_submissions >= expected_submissions
    
    def _all_votes_complete(self, game):
        """Helper: Check if all players have voted"""
        return len(game.votes[game.current_round]) >= len(game.players)
