#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tests for game scoring system
"""

import pytest
from tests.unit.game_mechanics import Game, GameManager

class TestScoringSystem:
    """Test vote counting and score accumulation"""
    
    def test_basic_scoring_one_point_per_vote(self):
        """Test that players get 1 point per vote received"""
        game = Game("TEST1234", "host", {'rounds': 3, 'submission_time': 60, 'voting_time': 30})
        
        # Add 3 players
        game.add_player("p1", "Player1")
        game.add_player("p2", "Player2")
        game.add_player("p3", "Player3")
        
        # Set up round 1 votes
        game.current_round = 1
        game.votes[1] = {
            "p1": "p2_p1",  # p1 votes for p2's bribe
            "p2": "p2_p2",  # p2 votes for p2's bribe (if allowed)
            "p3": "p1_p3"   # p3 votes for p1's bribe
        }
        
        # Calculate scores
        round_scores = self._calculate_round_scores(game)
        
        # p2 gets 2 votes, p1 gets 1 vote, p3 gets 0 votes
        assert round_scores["p2"] == 2
        assert round_scores["p1"] == 1
        assert round_scores.get("p3", 0) == 0
    
    def test_score_accumulation_across_rounds(self):
        """Test scores accumulate correctly across multiple rounds"""
        game = Game("TEST1234", "host", {'rounds': 3, 'submission_time': 60, 'voting_time': 30})
        
        # Add 3 players
        game.add_player("p1", "Player1")
        game.add_player("p2", "Player2")
        game.add_player("p3", "Player3")
        
        # Round 1 scores
        game.scores["p1"] = 2
        game.scores["p2"] = 1
        game.scores["p3"] = 0
        
        # Round 2 voting
        game.current_round = 2
        game.votes[2] = {
            "p1": "p3_p1",  # p1 votes for p3
            "p2": "p1_p2",  # p2 votes for p1
            "p3": "p1_p3"   # p3 votes for p1
        }
        
        # Calculate round 2 scores
        round_scores = self._calculate_round_scores(game)
        
        # Update total scores
        for player_id, points in round_scores.items():
            game.scores[player_id] += points
        
        # Final scores: p1(2+2=4), p2(1+0=1), p3(0+1=1)
        assert game.scores["p1"] == 4
        assert game.scores["p2"] == 1
        assert game.scores["p3"] == 1
    
    def test_missing_votes_dont_affect_scoring(self):
        """Test that non-voting players don't affect scoring (edge case)"""
        game = Game("TEST1234", "host", {'rounds': 3, 'submission_time': 60, 'voting_time': 30})
        
        # Add 4 players
        game.add_player("p1", "Player1")
        game.add_player("p2", "Player2")
        game.add_player("p3", "Player3")
        game.add_player("p4", "Player4")
        
        # Only 2 out of 4 players vote
        game.current_round = 1
        game.votes[1] = {
            "p1": "p2_p1",  # p1 votes for p2
            "p3": "p2_p3"   # p3 votes for p2
            # p2 and p4 don't vote
        }
        
        round_scores = self._calculate_round_scores(game)
        
        # p2 should get 2 points from the votes that were cast
        assert round_scores["p2"] == 2
        assert round_scores.get("p1", 0) == 0
        assert round_scores.get("p3", 0) == 0
        assert round_scores.get("p4", 0) == 0
    
    def test_final_ranking_and_podium(self):
        """Test final ranking logic and top 3 podium"""
        game = Game("TEST1234", "host", {'rounds': 3, 'submission_time': 60, 'voting_time': 30})
        
        # Add 5 players with final scores
        game.add_player("p1", "Player1")
        game.add_player("p2", "Player2")
        game.add_player("p3", "Player3")
        game.add_player("p4", "Player4")
        game.add_player("p5", "Player5")
        
        # Set final scores
        game.scores = {
            "p1": 8,   # 1st place
            "p2": 6,   # 2nd place
            "p3": 6,   # Tied 2nd place
            "p4": 3,   # 4th place
            "p5": 1    # 5th place
        }
        
        # Generate final scoreboard
        final_scoreboard = self._generate_final_scoreboard(game)
        
        # Should be sorted by score (descending)
        assert final_scoreboard[0]['username'] == 'Player1'
        assert final_scoreboard[0]['total_score'] == 8
        
        # Top 3 should have podium positions
        podium_count = sum(1 for player in final_scoreboard if 'podium_position' in player)
        assert podium_count == 3
        
        # Check podium positions
        assert final_scoreboard[0]['podium_position'] == 1
        assert final_scoreboard[1]['podium_position'] == 2
        assert final_scoreboard[2]['podium_position'] == 3
    
    def _calculate_round_scores(self, game):
        """Helper: Calculate scores for current round based on votes"""
        round_scores = {}
        for voter_id, bribe_id in game.votes[game.current_round].items():
            # Parse bribe_id to get submitter (format: "submitter_target")
            submitter_id = bribe_id.split('_')[0]
            round_scores[submitter_id] = round_scores.get(submitter_id, 0) + 1
        return round_scores
    
    def _generate_final_scoreboard(self, game):
        """Helper: Generate final scoreboard with podium positions"""
        final_scoreboard = []
        for player_id, total_score in game.scores.items():
            final_scoreboard.append({
                'username': game.players[player_id]['username'],
                'total_score': total_score
            })
        
        final_scoreboard.sort(key=lambda x: x['total_score'], reverse=True)
        
        # Add podium positions to top 3
        for i, player in enumerate(final_scoreboard):
            if i < 3:
                player['podium_position'] = i + 1
        
        return final_scoreboard
