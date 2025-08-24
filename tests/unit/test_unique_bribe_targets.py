"""
Test that players are assigned new bribe targets each round
"""

import unittest
from src.game.game import Game


class TestUniqueBribeTargets(unittest.TestCase):
    def setUp(self):
        self.game = Game("test_game", "host_id", {"rounds": 3})
        
        # Add 6 players to the game
        for i in range(6):
            player_id = f"player_{i}"
            self.game.add_player(player_id, f"Player {i}")
    
    def test_unique_targets_across_rounds(self):
        """Test that players get new targets each round until all players have been targeted"""
        player_id = "player_0"
        
        # Generate pairings for 3 rounds
        all_targets = set()
        for _ in range(3):
            pairings = self.game.generate_round_pairings()
            targets = pairings[player_id]
            
            # Assert that we get 2 targets
            self.assertEqual(len(targets), 2)
            
            # Add targets to our set
            all_targets.update(targets)
            
            # Track these in past_bribe_targets
            self.assertEqual(set(targets).issubset(set(self.game.past_bribe_targets[player_id])), True)
        
        # We should have at least 4 unique targets after 3 rounds
        # (with 6 players, we should never target ourselves, so max 5 possible targets)
        self.assertGreaterEqual(len(all_targets), 4)
        
        # Verify player didn't target themselves
        self.assertNotIn(player_id, all_targets)
    
    def test_reset_when_all_targeted(self):
        """Test that history resets when all possible players have been targeted"""
        player_id = "player_0"
        
        # First, manually set past_bribe_targets to include all other players
        other_players = [f"player_{i}" for i in range(1, 6)]
        self.game.past_bribe_targets[player_id] = other_players.copy()
        
        # Generate new pairings - this should reset the history
        pairings = self.game.generate_round_pairings()
        
        # Verify we still got 2 targets
        self.assertEqual(len(pairings[player_id]), 2)
        
        # Verify the history was reset and now only includes the new targets
        self.assertEqual(len(self.game.past_bribe_targets[player_id]), 2)
    
    def test_integration_with_multiple_rounds(self):
        """Test the complete feature through multiple rounds"""
        # Run for enough rounds to cycle through all players
        all_targets = {}
        
        # Track targets for each player over multiple rounds
        for round_num in range(1, 4):
            self.game.current_round = round_num
            pairings = self.game.generate_round_pairings()
            self.game.round_pairings[round_num] = pairings
            
            for player_id, targets in pairings.items():
                if player_id not in all_targets:
                    all_targets[player_id] = set()
                all_targets[player_id].update(targets)
        
        # After 3 rounds, each player should have targeted most other players
        # (with 6 players, each player can target at most 5 others)
        for player_id, targets in all_targets.items():
            # Verify player didn't target themselves
            self.assertNotIn(player_id, targets)
            
            # With 6 players and 3 rounds of 2 targets each,
            # each player should have targeted 4-5 other players
            self.assertGreaterEqual(len(targets), 4)
