"""
Tests to verify that players always receive exactly two bribes and are assigned
exactly two targets to bribe, even in edge cases like disconnections.
"""

import unittest
from src.game.game import Game


class TestBribeBalance(unittest.TestCase):
    def setUp(self):
        self.game = Game("test_game", "host_id", {"rounds": 3})
        
        # Add players to the game
        for i in range(6):
            player_id = f"player_{i}"
            self.game.add_player(player_id, f"Player {i}")
    
    def test_each_player_receives_exactly_two_bribes(self):
        """Test that each player receives exactly two bribes from others"""
        # Generate pairings
        pairings = self.game.generate_round_pairings()
        
        # Count bribes received by each player
        bribes_received = {pid: 0 for pid in self.game.get_active_player_ids()}
        
        for player_id, targets in pairings.items():
            for target in targets:
                bribes_received[target] += 1
        
        # Verify each player receives exactly 2 bribes
        for player_id, count in bribes_received.items():
            self.assertEqual(count, 2, f"Player {player_id} received {count} bribes instead of 2")
    
    def test_each_player_bribes_exactly_two_others(self):
        """Test that each player bribes exactly two other players"""
        # Generate pairings
        pairings = self.game.generate_round_pairings()
        
        # Verify each player is assigned exactly 2 targets
        for player_id, targets in pairings.items():
            self.assertEqual(len(targets), 2, f"Player {player_id} was assigned {len(targets)} targets instead of 2")
    
    def test_uneven_player_count(self):
        """Test that bribe balance works with uneven player counts"""
        # Test with odd number of players (5)
        self.game.remove_player("player_5")
        
        # Generate pairings with 5 players
        pairings = self.game.generate_round_pairings()
        
        # Count bribes received by each player
        bribes_received = {pid: 0 for pid in self.game.get_active_player_ids()}
        
        for player_id, targets in pairings.items():
            for target in targets:
                bribes_received[target] += 1
        
        # Verify each player receives exactly 2 bribes
        for player_id, count in bribes_received.items():
            self.assertEqual(count, 2, f"Player {player_id} received {count} bribes instead of 2 with 5 players")
        
        # Verify each player bribes exactly 2 others
        for player_id, targets in pairings.items():
            self.assertEqual(len(targets), 2, f"Player {player_id} bribes {len(targets)} others instead of 2 with 5 players")
    
    def test_disconnection_after_pairing(self):
        """Test what happens when a player disconnects after pairings are generated"""
        # Generate initial pairings
        self.game.current_round = 1
        pairings = self.game.generate_round_pairings()
        self.game.round_pairings[1] = pairings
        
        # Find a player who has been assigned as a target
        target_player = None
        for player_id, targets in pairings.items():
            if "player_1" in targets:
                target_player = player_id
                break
        
        # Simulate disconnection by marking as not connected
        # NOTE: This test highlights that we don't currently rebalance
        # when a player disconnects mid-round
        self.game.players["player_1"]["connected"] = False
        
        # In a real scenario, we would need to rebalance here
        # but our current implementation doesn't do this automatically
        
        # Count bribes received by connected players
        bribes_received = {pid: 0 for pid in self.game.get_active_player_ids()}
        
        for player_id, targets in pairings.items():
            for target in targets:
                # Only count bribes to connected players
                if target in bribes_received:
                    bribes_received[target] += 1
        
        # This test documents current behavior - not ideal but factual
        # Some players may receive fewer than 2 bribes if others disconnect mid-round
        # Ideally, we would rebalance, but that's not implemented yet
        self.assertNotIn("player_1", bribes_received, "Disconnected player should not be counted")
        
        # The player who was targeting the disconnected player now has a "wasted" bribe
        if target_player:
            self.assertIn("player_1", pairings[target_player], 
                          "The disconnected player is still assigned as a target")
    
    def test_minimum_player_count(self):
        """Test that the minimum player count for balanced bribes is 3"""
        # Remove all but 3 players
        for i in range(3, 6):
            self.game.remove_player(f"player_{i}")
        
        # Generate pairings with exactly 3 players
        pairings = self.game.generate_round_pairings()
        
        # Count bribes received by each player
        bribes_received = {pid: 0 for pid in self.game.get_active_player_ids()}
        
        for player_id, targets in pairings.items():
            for target in targets:
                bribes_received[target] += 1
        
        # Verify each player receives exactly 2 bribes
        for player_id, count in bribes_received.items():
            self.assertEqual(count, 2, f"Player {player_id} received {count} bribes instead of 2 with 3 players")
        
        # Verify each player bribes exactly 2 others
        for player_id, targets in pairings.items():
            self.assertEqual(len(targets), 2, f"Player {player_id} bribes {len(targets)} others instead of 2 with 3 players")
            
            # With 3 players, each player must bribe the other two
            other_players = [pid for pid in self.game.get_active_player_ids() if pid != player_id]
            self.assertEqual(set(targets), set(other_players), 
                            f"With 3 players, each player must bribe both others")
