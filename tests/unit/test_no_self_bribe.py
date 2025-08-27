"""
Test that players are never assigned to submit a bribe to themselves
"""

import unittest
from src.game.game import Game


class TestNoSelfBribe(unittest.TestCase):
    def setUp(self):
        self.game = Game("test_game", "host_id", {"rounds": 3})
        
        # Add players to the game
        for i in range(6):
            player_id = f"player_{i}"
            self.game.add_player(player_id, f"Player {i}")
    
    def test_no_self_assignment(self):
        """Test that players are never assigned to bribe themselves"""
        # Generate pairings for multiple rounds to catch edge cases
        for _ in range(10):  # Run multiple times to increase chance of catching the issue
            pairings = self.game.generate_round_pairings()
            
            # Verify no player is assigned to bribe themselves
            for player_id, targets in pairings.items():
                self.assertNotIn(player_id, targets, 
                                f"Player {player_id} was assigned to bribe themselves")
    
    def test_balance_bribes_no_self_assignment(self):
        """Test that the bribe balancing logic never assigns players to bribe themselves"""
        # Create an unbalanced pairing situation that might trigger the rebalancing logic
        player_ids = [f"player_{i}" for i in range(6)]
        
        # Create an intentionally unbalanced set of pairings
        unbalanced_pairings = {
            "player_0": ["player_1", "player_2"],
            "player_1": ["player_0", "player_3"],
            "player_2": ["player_0", "player_3"],  # player_3 gets 2 bribes
            "player_3": ["player_0", "player_4"],
            "player_4": ["player_1", "player_5"],
            "player_5": ["player_1", "player_2"]
        }
        
        # Call the balancing method directly
        balanced_pairings = self.game._balance_bribes(unbalanced_pairings, player_ids)
        
        # Verify no player bribes themselves after balancing
        for player_id, targets in balanced_pairings.items():
            self.assertNotIn(player_id, targets,
                            f"Player {player_id} was assigned to bribe themselves after balancing")

    def test_exhaustive_check_all_sizes(self):
        """Test with different player counts to ensure no self-bribes happen"""
        # Test with different numbers of players
        for num_players in range(3, 10):  # 3 is minimum for the game to work
            # Create a new game for each test
            game = Game("test_game", "host_id", {"rounds": 3})
            
            # Add the specified number of players
            for i in range(num_players):
                player_id = f"player_{i}"
                game.add_player(player_id, f"Player {i}")
            
            # Generate pairings multiple times
            for _ in range(5):
                pairings = game.generate_round_pairings()
                
                # Verify no player bribes themselves
                for player_id, targets in pairings.items():
                    self.assertNotIn(player_id, targets,
                                    f"With {num_players} players, {player_id} was assigned to bribe themselves")
