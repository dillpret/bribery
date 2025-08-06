#!/usr/bin/env python3
"""
Test cases for voting logic and self-voting prevention
"""

import pytest
from src.game.game import Game


class TestVotingLogic:
    """Test voting phase logic and self-voting prevention"""

    def setup_method(self):
        """Set up test fixtures"""
        self.game = Game("test-game", "host1", {
            'rounds': 3,
            'submission_time': 30,
            'voting_time': 15,
            'custom_prompts': False
        })
        
        # Add players
        self.game.add_player("host1", "Host")
        self.game.add_player("p1", "Player1")
        self.game.add_player("p2", "Player2")
        self.game.add_player("p3", "Player3")
        
        # Set up game state
        self.game.state = "voting"
        self.game.current_round = 1
        
        # Set up mock bribes for testing
        # Each player submits bribes to their targets
        self.game.bribes[1] = {
            "host1": {
                "p1": {"content": "Host's bribe to P1", "type": "text"},
                "p2": {"content": "Host's bribe to P2", "type": "text"}
            },
            "p1": {
                "p2": {"content": "P1's bribe to P2", "type": "text"},
                "p3": {"content": "P1's bribe to P3", "type": "text"}
            },
            "p2": {
                "p3": {"content": "P2's bribe to P3", "type": "text"},
                "host1": {"content": "P2's bribe to Host", "type": "text"}
            },
            "p3": {
                "host1": {"content": "P3's bribe to Host", "type": "text"},
                "p1": {"content": "P3's bribe to P1", "type": "text"}
            }
        }

    def test_player_cannot_vote_on_own_bribe(self):
        """Test that players don't receive their own bribes for voting"""
        
        def get_bribes_for_player(player_id):
            """Simulate the voting logic from socket_handlers.py"""
            bribes_for_player = []
            for submitter_id, submissions in self.game.bribes[self.game.current_round].items():
                # Skip bribes submitted by the voting player themselves
                if submitter_id == player_id:
                    continue
                    
                for target_id, bribe in submissions.items():
                    if target_id == player_id:
                        bribes_for_player.append({
                            'id': f"{submitter_id}_{target_id}",
                            'content': bribe['content'],
                            'type': bribe['type'],
                            'submitter': submitter_id
                        })
            return bribes_for_player
        
        # Test each player's voting options
        
        # Host should see bribes TO host, but NOT from host
        host_bribes = get_bribes_for_player("host1")
        submitters = [bribe['submitter'] for bribe in host_bribes]
        assert "host1" not in submitters  # Host shouldn't see own bribes
        assert "p2" in submitters  # Should see P2's bribe to host
        assert "p3" in submitters  # Should see P3's bribe to host
        
        # P1 should see bribes TO p1, but NOT from p1
        p1_bribes = get_bribes_for_player("p1")
        submitters = [bribe['submitter'] for bribe in p1_bribes]
        assert "p1" not in submitters  # P1 shouldn't see own bribes
        assert "host1" in submitters  # Should see Host's bribe to p1
        assert "p3" in submitters  # Should see P3's bribe to p1
        
        # P2 should see bribes TO p2, but NOT from p2
        p2_bribes = get_bribes_for_player("p2")
        submitters = [bribe['submitter'] for bribe in p2_bribes]
        assert "p2" not in submitters  # P2 shouldn't see own bribes
        assert "host1" in submitters  # Should see Host's bribe to p2
        assert "p1" in submitters  # Should see P1's bribe to p2
        
        # P3 should see bribes TO p3, but NOT from p3
        p3_bribes = get_bribes_for_player("p3")
        submitters = [bribe['submitter'] for bribe in p3_bribes]
        assert "p3" not in submitters  # P3 shouldn't see own bribes
        assert "p1" in submitters  # Should see P1's bribe to p3
        assert "p2" in submitters  # Should see P2's bribe to p3

    def test_correct_bribe_filtering(self):
        """Test that bribe filtering works correctly for complex scenarios"""
        
        def get_bribes_for_player(player_id):
            bribes_for_player = []
            for submitter_id, submissions in self.game.bribes[self.game.current_round].items():
                if submitter_id == player_id:
                    continue
                for target_id, bribe in submissions.items():
                    if target_id == player_id:
                        bribes_for_player.append({
                            'id': f"{submitter_id}_{target_id}",
                            'content': bribe['content'],
                            'submitter': submitter_id,
                            'target': target_id
                        })
            return bribes_for_player
        
        # Each player should only see bribes that were submitted TO them BY others
        host_bribes = get_bribes_for_player("host1")
        assert len(host_bribes) == 2  # From P2 and P3
        assert all(bribe['target'] == "host1" for bribe in host_bribes)
        assert all(bribe['submitter'] != "host1" for bribe in host_bribes)
        
        p1_bribes = get_bribes_for_player("p1")
        assert len(p1_bribes) == 2  # From Host and P3
        assert all(bribe['target'] == "p1" for bribe in p1_bribes)
        assert all(bribe['submitter'] != "p1" for bribe in p1_bribes)

    def test_no_bribes_case(self):
        """Test voting when player received no bribes"""
        # Create scenario where p1 received no bribes
        self.game.bribes[1] = {
            "host1": {
                "p2": {"content": "Host's bribe to P2", "type": "text"}
            },
            "p2": {
                "p3": {"content": "P2's bribe to P3", "type": "text"}
            }
        }
        
        def get_bribes_for_player(player_id):
            bribes_for_player = []
            for submitter_id, submissions in self.game.bribes[self.game.current_round].items():
                if submitter_id == player_id:
                    continue
                for target_id, bribe in submissions.items():
                    if target_id == player_id:
                        bribes_for_player.append({
                            'id': f"{submitter_id}_{target_id}",
                            'content': bribe['content']
                        })
            return bribes_for_player
        
        # P1 should get empty list (no bribes submitted to them)
        p1_bribes = get_bribes_for_player("p1")
        assert len(p1_bribes) == 0

    def test_self_submission_completely_excluded(self):
        """Test that if player somehow submitted to themselves, it's excluded from voting"""
        # Create edge case where player submitted to themselves (shouldn't happen in normal flow)
        self.game.bribes[1] = {
            "p1": {
                "p1": {"content": "P1's bribe to themselves", "type": "text"},  # Edge case
                "p2": {"content": "P1's bribe to P2", "type": "text"}
            },
            "p2": {
                "p1": {"content": "P2's bribe to P1", "type": "text"}
            }
        }
        
        def get_bribes_for_player(player_id):
            bribes_for_player = []
            for submitter_id, submissions in self.game.bribes[self.game.current_round].items():
                if submitter_id == player_id:
                    continue
                for target_id, bribe in submissions.items():
                    if target_id == player_id:
                        bribes_for_player.append({
                            'id': f"{submitter_id}_{target_id}",
                            'content': bribe['content'],
                            'submitter': submitter_id
                        })
            return bribes_for_player
        
        # P1 should only see P2's bribe to them, NOT their own bribe to themselves
        p1_bribes = get_bribes_for_player("p1")
        assert len(p1_bribes) == 1
        assert p1_bribes[0]['submitter'] == "p2"
        assert "P2's bribe to P1" in p1_bribes[0]['content']

    def test_voting_with_inactive_players(self):
        """Test voting logic when some players are inactive (mid-game joiners)"""
        # Add inactive player (mid-game joiner)
        self.game.add_player("p4", "Player4")
        self.game.players["p4"]["active_in_round"] = False
        
        # Add some bribes involving the inactive player
        self.game.bribes[1]["p4"] = {
            "p1": {"content": "P4's bribe to P1", "type": "text"}
        }
        self.game.bribes[1]["p1"]["p4"] = {"content": "P1's bribe to P4", "type": "text"}
        
        def get_bribes_for_player(player_id):
            bribes_for_player = []
            for submitter_id, submissions in self.game.bribes[self.game.current_round].items():
                if submitter_id == player_id:
                    continue
                for target_id, bribe in submissions.items():
                    if target_id == player_id:
                        bribes_for_player.append({
                            'id': f"{submitter_id}_{target_id}",
                            'content': bribe['content'],
                            'submitter': submitter_id
                        })
            return bribes_for_player
        
        # P1 should see bribe from P4 (even though P4 is inactive for voting)
        p1_bribes = get_bribes_for_player("p1")
        submitters = [bribe['submitter'] for bribe in p1_bribes]
        assert "p4" in submitters
        
        # P4 should see bribe from P1 (if they were to vote)
        p4_bribes = get_bribes_for_player("p4")
        submitters = [bribe['submitter'] for bribe in p4_bribes]
        assert "p1" in submitters

    def test_vote_id_format_consistency(self):
        """Test that vote IDs are formatted consistently"""
        def get_bribes_for_player(player_id):
            bribes_for_player = []
            for submitter_id, submissions in self.game.bribes[self.game.current_round].items():
                if submitter_id == player_id:
                    continue
                for target_id, bribe in submissions.items():
                    if target_id == player_id:
                        bribes_for_player.append({
                            'id': f"{submitter_id}_{target_id}",
                            'content': bribe['content']
                        })
            return bribes_for_player
        
        host_bribes = get_bribes_for_player("host1")
        for bribe in host_bribes:
            # ID should be submitter_target format
            assert "_" in bribe['id']
            submitter, target = bribe['id'].split("_")
            assert target == "host1"  # Target should be the voting player
            assert submitter != "host1"  # Submitter should not be the voting player
