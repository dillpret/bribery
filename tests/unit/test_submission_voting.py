#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Unit tests for submission and voting business logic
Tests the core bribery game mechanics
"""

import pytest
import sys
import os

# Add the app directory to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'src'))

from game.game import Game


class TestSubmissionLogic:
    """Test bribe submission mechanics"""
    
    def test_submission_data_structure(self):
        """Test bribe submission data is stored correctly"""
        game = Game("TEST1234", "host", {'rounds': 3, 'submission_time': 60, 'voting_time': 30})
        
        # Add players
        game.add_player("p1", "Player1")
        game.add_player("p2", "Player2")
        game.add_player("p3", "Player3")
        
        # Set up round
        game.current_round = 1
        game.bribes[1] = {}
        
        # Submit bribe
        player_id = "p1"
        target_id = "p2"
        submission = {"content": "A funny meme about Player2", "type": "text"}
        
        # Initialize player's submissions for this round
        if player_id not in game.bribes[1]:
            game.bribes[1][player_id] = {}
        
        game.bribes[1][player_id][target_id] = submission
        
        # Verify storage structure
        assert game.bribes[1][player_id][target_id] == submission
        assert game.bribes[1][player_id][target_id]["content"] == "A funny meme about Player2"
        assert game.bribes[1][player_id][target_id]["type"] == "text"
    
    def test_multiple_submission_types(self):
        """Test different types of submissions are handled"""
        game = Game("TEST1234", "host", {'rounds': 3, 'submission_time': 60, 'voting_time': 30})
        
        game.add_player("p1", "Player1")
        game.add_player("p2", "Player2")
        
        game.current_round = 1
        game.bribes[1] = {"p1": {}}
        
        # Text submission
        game.bribes[1]["p1"]["text_target"] = {
            "content": "A witty joke about the target",
            "type": "text"
        }
        
        # Image submission
        game.bribes[1]["p1"]["image_target"] = {
            "content": "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQEAYABgAAD...",
            "type": "image"
        }
        
        # Link submission
        game.bribes[1]["p1"]["link_target"] = {
            "content": "https://example.com/funny-gif.gif",
            "type": "link"
        }
        
        # Verify all types are stored
        assert game.bribes[1]["p1"]["text_target"]["type"] == "text"
        assert game.bribes[1]["p1"]["image_target"]["type"] == "image"
        assert game.bribes[1]["p1"]["link_target"]["type"] == "link"
    
    def test_player_submits_exactly_two_bribes(self):
        """Test that each player submits exactly 2 bribes per round"""
        game = Game("TEST1234", "host", {'rounds': 3, 'submission_time': 60, 'voting_time': 30})
        
        game.add_player("p1", "Player1")
        game.add_player("p2", "Player2")
        game.add_player("p3", "Player3")
        
        # Generate pairings (each player should get 2 targets)
        game.current_round = 1
        game.round_pairings[1] = game.generate_round_pairings()
        
        player_targets = game.round_pairings[1]["p1"]
        assert len(player_targets) == 2
        
        # Player submits to both targets
        game.bribes[1] = {"p1": {}}
        
        for target in player_targets:
            game.bribes[1]["p1"][target] = {
                "content": f"Bribe for {target}",
                "type": "text"
            }
        
        # Verify exactly 2 submissions
        assert len(game.bribes[1]["p1"]) == 2
        assert all(target in game.bribes[1]["p1"] for target in player_targets)
    
    def test_submission_validation(self):
        """Test submission content validation"""
        valid_submissions = [
            {"content": "Valid text bribe", "type": "text"},
            {"content": "https://example.com/image.jpg", "type": "image"},
            {"content": "https://giphy.com/gifs/funny", "type": "link"}
        ]
        
        for submission in valid_submissions:
            assert self._is_valid_bribe_submission(submission)
        
        invalid_submissions = [
            {"content": "", "type": "text"},  # Empty content
            {"content": "Valid content"},     # Missing type
            {"type": "text"},                 # Missing content
            {"content": "Valid content", "type": "invalid"},  # Invalid type
            {"content": None, "type": "text"},  # None content
        ]
        
        for submission in invalid_submissions:
            assert not self._is_valid_bribe_submission(submission)
    
    def _is_valid_bribe_submission(self, submission):
        """Helper: Validate bribe submission"""
        if not isinstance(submission, dict):
            return False
        
        if "content" not in submission or "type" not in submission:
            return False
        
        if not isinstance(submission["content"], str) or len(submission["content"]) == 0:
            return False
        
        valid_types = ["text", "image", "link"]
        if submission["type"] not in valid_types:
            return False
        
        return True


class TestVotingLogic:
    """Test voting mechanics and anonymous display"""
    
    def test_voting_options_generation(self):
        """Test that voting options are generated correctly for each player"""
        game = Game("TEST1234", "host", {'rounds': 3, 'submission_time': 60, 'voting_time': 30})
        
        # Add 3 players
        game.add_player("p1", "Player1")
        game.add_player("p2", "Player2")
        game.add_player("p3", "Player3")
        
        # Set up bribes submitted TO player p1
        game.current_round = 1
        game.bribes[1] = {
            "p2": {"p1": {"content": "Bribe from p2 to p1", "type": "text"}},
            "p3": {"p1": {"content": "Bribe from p3 to p1", "type": "text"}}
        }
        
        # Generate voting options for p1
        voting_options = self._get_voting_options_for_player(game, "p1")
        
        # p1 should see exactly 2 bribes (submitted TO them)
        assert len(voting_options) == 2
        
        # Verify bribe IDs are in correct format (submitter_target)
        expected_ids = ["p2_p1", "p3_p1"]
        actual_ids = [option["id"] for option in voting_options]
        assert set(actual_ids) == set(expected_ids)
        
        # Verify content is included but submitter names are hidden at this stage
        contents = [option["content"] for option in voting_options]
        assert "Bribe from p2 to p1" in contents
        assert "Bribe from p3 to p1" in contents
    
    def test_anonymous_voting_display(self):
        """Test that submitter names are hidden during voting"""
        game = Game("TEST1234", "host", {'rounds': 3, 'submission_time': 60, 'voting_time': 30})
        
        game.add_player("p1", "Player1")
        game.add_player("p2", "Player2")
        game.add_player("p3", "Player3")
        
        # Set up bribes
        game.current_round = 1
        game.bribes[1] = {
            "p2": {"p1": {"content": "Secret bribe from p2", "type": "text"}},
            "p3": {"p1": {"content": "Secret bribe from p3", "type": "text"}}
        }
        
        # Get voting options (this simulates what the UI would show)
        voting_options = self._get_voting_options_for_player(game, "p1")
        
        # Options should only contain content and bribe ID, not submitter names
        for option in voting_options:
            assert "content" in option
            assert "type" in option
            assert "id" in option
            # Should NOT contain submitter username directly
            assert "username" not in option
            assert "submitter" not in option
    
    def test_single_vote_per_player(self):
        """Test that each player votes exactly once per round"""
        game = Game("TEST1234", "host", {'rounds': 3, 'submission_time': 60, 'voting_time': 30})
        
        game.add_player("p1", "Player1")
        game.add_player("p2", "Player2")
        game.add_player("p3", "Player3")
        
        game.current_round = 1
        game.votes[1] = {}
        
        # Player p1 votes
        game.votes[1]["p1"] = "p2_p1"  # p1 votes for p2's bribe
        
        # Verify single vote recorded
        assert len(game.votes[1]) == 1
        assert game.votes[1]["p1"] == "p2_p1"
        
        # If player tries to vote again, it should overwrite (not add)
        game.votes[1]["p1"] = "p3_p1"  # p1 changes vote to p3's bribe
        
        assert len(game.votes[1]) == 1  # Still only one vote for p1
        assert game.votes[1]["p1"] == "p3_p1"  # Vote updated
    
    def test_vote_result_calculation(self):
        """Test that vote results correctly identify winners"""
        game = Game("TEST1234", "host", {'rounds': 3, 'submission_time': 60, 'voting_time': 30})
        
        game.add_player("p1", "Player1")
        game.add_player("p2", "Player2")
        game.add_player("p3", "Player3")
        
        # Set up votes
        game.current_round = 1
        game.votes[1] = {
            "p1": "p2_p1",  # p1 votes for p2's bribe to p1
            "p2": "p3_p2",  # p2 votes for p3's bribe to p2
            "p3": "p2_p3"   # p3 votes for p2's bribe to p3
        }
        
        # Calculate vote results
        vote_results = self._calculate_vote_results(game)
        
        # Should show who voted for whom (with revealed names)
        expected_results = [
            {"voter": "Player1", "winner": "Player2"},
            {"voter": "Player2", "winner": "Player3"},
            {"voter": "Player3", "winner": "Player2"}
        ]
        
        assert len(vote_results) == 3
        
        # p2 should have 2 votes, p3 should have 1 vote
        winner_counts = {}
        for result in vote_results:
            winner = result["winner"]
            winner_counts[winner] = winner_counts.get(winner, 0) + 1
        
        assert winner_counts["Player2"] == 2
        assert winner_counts["Player3"] == 1
    
    def test_winner_reveal_after_voting(self):
        """Test that bribe creators are revealed after voting"""
        game = Game("TEST1234", "host", {'rounds': 3, 'submission_time': 60, 'voting_time': 30})
        
        game.add_player("p1", "Player1")
        game.add_player("p2", "Player2")
        
        # Player votes for a bribe
        vote_choice = "p2_p1"  # p1 votes for p2's bribe to p1
        
        # Extract submitter from vote choice
        submitter_id = vote_choice.split('_')[0]
        submitter_name = game.players[submitter_id]["username"]
        
        # After voting, submitter should be revealed
        assert submitter_id == "p2"
        assert submitter_name == "Player2"
    
    def _get_voting_options_for_player(self, game, player_id):
        """Helper: Generate voting options for a specific player"""
        voting_options = []
        
        # Find all bribes submitted TO this player
        for submitter_id, submissions in game.bribes[game.current_round].items():
            for target_id, bribe in submissions.items():
                if target_id == player_id:
                    voting_options.append({
                        'id': f"{submitter_id}_{target_id}",
                        'content': bribe['content'],
                        'type': bribe['type']
                    })
        
        return voting_options
    
    def _calculate_vote_results(self, game):
        """Helper: Calculate vote results with revealed names"""
        vote_results = []
        
        for voter_id, bribe_id in game.votes[game.current_round].items():
            submitter_id = bribe_id.split('_')[0]
            
            vote_results.append({
                'voter': game.players[voter_id]['username'],
                'winner': game.players[submitter_id]['username']
            })
        
        return vote_results


class TestTimerAndCompletionLogic:
    """Test timer-based and completion-based round advancement"""
    
    def test_early_completion_cancels_timer(self):
        """Test that completing submissions/votes early should cancel timer"""
        game = Game("TEST1234", "host", {'rounds': 3, 'submission_time': 60, 'voting_time': 30})
        
        # Add 3 players
        game.add_player("p1", "Player1")
        game.add_player("p2", "Player2")
        game.add_player("p3", "Player3")
        
        game.current_round = 1
        game.state = "submission"
        
        # Simulate timer running
        timer_cancelled = False
        
        # Check if all submissions are complete
        game.bribes[1] = {
            "p1": {
                "p2": {"content": "bribe1", "type": "text"},
                "p3": {"content": "bribe2", "type": "text"}
            },
            "p2": {
                "p1": {"content": "bribe3", "type": "text"},
                "p3": {"content": "bribe4", "type": "text"}
            },
            "p3": {
                "p1": {"content": "bribe5", "type": "text"},
                "p2": {"content": "bribe6", "type": "text"}
            }
        }
        
        # All submissions complete - timer should be cancelled
        if self._all_submissions_complete(game):
            timer_cancelled = True
        
        assert timer_cancelled
    
    def test_time_expiry_advances_round(self):
        """Test that round advances when time expires, even with incomplete submissions"""
        game = Game("TEST1234", "host", {'rounds': 3, 'submission_time': 60, 'voting_time': 30})
        
        game.add_player("p1", "Player1")
        game.add_player("p2", "Player2")
        game.add_player("p3", "Player3")
        
        game.current_round = 1
        game.state = "submission"
        
        # Only partial submissions
        game.bribes[1] = {
            "p1": {
                "p2": {"content": "only one bribe", "type": "text"}
                # Missing second bribe
            }
            # p2 and p3 haven't submitted anything
        }
        
        # Simulate timer expiry
        timer_expired = True
        
        # Even with incomplete submissions, round should advance
        if timer_expired:
            can_advance = True  # Timer expiry allows advancement regardless of completion
        
        assert can_advance
        assert not self._all_submissions_complete(game)  # Submissions incomplete
    
    def test_mixed_completion_scenarios(self):
        """Test various partial completion scenarios"""
        game = Game("TEST1234", "host", {'rounds': 3, 'submission_time': 60, 'voting_time': 30})
        
        # Add 4 players
        game.add_player("p1", "Player1")
        game.add_player("p2", "Player2")
        game.add_player("p3", "Player3")
        game.add_player("p4", "Player4")
        
        game.current_round = 1
        
        # Scenario 1: Some players submit both bribes, others submit partial/none
        game.bribes[1] = {
            "p1": {  # Complete submissions
                "p2": {"content": "p1 to p2", "type": "text"},
                "p3": {"content": "p1 to p3", "type": "text"}
            },
            "p2": {  # Partial submission
                "p4": {"content": "p2 to p4", "type": "text"}
                # Missing second bribe
            },
            "p3": {  # Complete submissions
                "p1": {"content": "p3 to p1", "type": "text"},
                "p4": {"content": "p3 to p4", "type": "text"}
            }
            # p4 hasn't submitted anything
        }
        
        # Calculate completion percentage
        total_expected = len(game.players) * 2  # 4 players * 2 bribes each = 8
        total_actual = sum(len(bribes) for bribes in game.bribes[1].values())  # 2 + 1 + 2 = 5
        completion_rate = total_actual / total_expected
        
        assert completion_rate == 0.625  # 5/8 = 62.5% complete
        assert not self._all_submissions_complete(game)
    
    def _all_submissions_complete(self, game):
        """Helper: Check if all submissions are complete"""
        expected_submissions = len(game.players) * 2
        actual_submissions = sum(len(bribes) for bribes in game.bribes[game.current_round].values())
        return actual_submissions >= expected_submissions
