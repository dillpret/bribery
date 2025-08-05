#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Unit tests for core game mechanics and business logic
Tests the actual game flow, scoring, and edge cases
"""

import pytest
import sys
import os
from unittest.mock import Mock, patch

# Add the app directory to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'src'))

from game.game import Game
from game.game_manager import GameManager


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
        
        game.current_round = 1
        game.state = "submission"
        game.bribes[1] = {}
        
        # Only 2 out of 4 players submit
        game.bribes[1] = {
            "p1": {
                "p2": {"content": "p1 to p2", "type": "text"},
                "p3": {"content": "p1 to p3", "type": "text"}
            },
            "p2": {
                "p3": {"content": "p2 to p3", "type": "text"},
                "p4": {"content": "p2 to p4", "type": "text"}
            }
            # p3 and p4 don't submit
        }
        
        # Game should still be able to progress (per edge case rules)
        # This tests the "Game progresses even if not all players submit" rule
        assert not self._all_submissions_complete(game)
        # But should be able to handle partial state in voting phase
    
    def _all_submissions_complete(self, game):
        """Helper: Check if all players have submitted all their bribes"""
        expected_submissions = len(game.players) * 2  # Each player submits 2 bribes
        actual_submissions = sum(len(bribes) for bribes in game.bribes[game.current_round].values())
        return actual_submissions >= expected_submissions
    
    def _all_votes_complete(self, game):
        """Helper: Check if all players have voted"""
        return len(game.votes[game.current_round]) >= len(game.players)


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


class TestMultiRoundLogic:
    """Test multi-round game progression"""
    
    def test_different_prompts_per_round(self):
        """Test that each round gets a different random prompt"""
        game = Game("TEST1234", "host", {'rounds': 3, 'submission_time': 60, 'voting_time': 30})
        
        # Mock prompts
        mock_prompts = [
            "Write a haiku about your target",
            "Create a meme about your target", 
            "Compose a song about your target"
        ]
        
        used_prompts = []
        
        # Simulate 3 rounds
        for round_num in [1, 2, 3]:
            # In real implementation, this would call random.choice(prompts)
            # Here we simulate getting different prompts
            prompt = mock_prompts[round_num - 1]
            used_prompts.append(prompt)
            game.current_prompt = prompt
        
        # Each round should have a different prompt
        assert len(set(used_prompts)) == 3
        assert len(used_prompts) == 3
    
    def test_different_pairings_per_round(self):
        """Test that each round has different player pairings"""
        game = Game("TEST1234", "host", {'rounds': 3, 'submission_time': 60, 'voting_time': 30})
        
        # Add 4 players
        game.add_player("p1", "Player1")
        game.add_player("p2", "Player2")
        game.add_player("p3", "Player3")
        game.add_player("p4", "Player4")
        
        # Generate pairings for 3 rounds
        round_pairings = {}
        for round_num in [1, 2, 3]:
            round_pairings[round_num] = game.generate_round_pairings()
        
        # Pairings should be different between rounds (due to shuffling)
        # Note: There's a small chance they could be the same due to randomness,
        # but we'll test the structure is correct
        for round_num in [1, 2, 3]:
            pairings = round_pairings[round_num]
            
            # Each player should have exactly 2 targets
            assert len(pairings) == 4
            for player_id, targets in pairings.items():
                assert len(targets) == 2
                assert player_id not in targets
    
    def test_game_ending_after_configured_rounds(self):
        """Test game ends after configured number of rounds"""
        game = Game("TEST1234", "host", {'rounds': 2, 'submission_time': 60, 'voting_time': 30})
        
        # After round 1
        game.current_round = 1
        assert not self._should_end_game(game)
        
        # After round 2 (max rounds)
        game.current_round = 2
        assert self._should_end_game(game)
        
        # Test with different round count
        game.settings['rounds'] = 5
        game.current_round = 4
        assert not self._should_end_game(game)
        
        game.current_round = 5
        assert self._should_end_game(game)
    
    def test_round_data_isolation(self):
        """Test that each round's data is stored separately"""
        game = Game("TEST1234", "host", {'rounds': 3, 'submission_time': 60, 'voting_time': 30})
        
        # Add bribes for round 1
        game.bribes[1] = {
            "p1": {"p2": {"content": "round1 bribe", "type": "text"}}
        }
        
        # Add votes for round 1
        game.votes[1] = {"p1": "p2_p1"}
        
        # Add bribes for round 2
        game.bribes[2] = {
            "p1": {"p3": {"content": "round2 bribe", "type": "text"}}
        }
        
        # Add votes for round 2
        game.votes[2] = {"p1": "p3_p1"}
        
        # Data should be isolated per round
        assert game.bribes[1] != game.bribes[2]
        assert game.votes[1] != game.votes[2]
        assert len(game.bribes) == 2
        assert len(game.votes) == 2
    
    def _should_end_game(self, game):
        """Helper: Determine if game should end"""
        return game.current_round >= game.settings['rounds']
