#!/usr/bin/env python3
"""
Test cases for mid-game joining scenarios
"""

import pytest
from src.game.game import Game


class TestMidGameJoining:
    """Test scenarios for players joining during an active game"""

    def setup_method(self):
        """Set up test fixtures"""
        self.game = Game("test-game", "host1", {
            'rounds': 3,
            'submission_time': 30,
            'voting_time': 15,
            'custom_prompts': False
        })
        
        # Add initial players
        self.game.add_player("host1", "Host")
        self.game.add_player("p1", "Player1")
        self.game.add_player("p2", "Player2")
        self.game.add_player("p3", "Player3")

    def test_lobby_joiners_are_active(self):
        """Test that players joining in lobby are immediately active"""
        # All players should be active in lobby
        assert self.game.get_active_player_count() == 4
        assert self.game.get_active_player_ids() == ["host1", "p1", "p2", "p3"]
        
        # New player joins in lobby
        self.game.add_player("p4", "Player4")
        assert self.game.get_active_player_count() == 5
        assert self.game.players["p4"]["active_in_round"] == True

    def test_midgame_joiners_are_inactive(self):
        """Test that players joining mid-game are not active until next round"""
        # Start the game (move out of lobby)
        self.game.state = "submission"
        self.game.current_round = 1
        
        # Active players should remain the same
        initial_active_count = self.game.get_active_player_count()
        initial_active_ids = self.game.get_active_player_ids()
        
        # New player joins mid-game
        self.game.add_player("p4", "Player4")
        
        # Player count increases but active count stays same
        assert self.game.get_connected_player_count() == 5
        assert self.game.get_active_player_count() == initial_active_count
        assert self.game.get_active_player_ids() == initial_active_ids
        assert self.game.players["p4"]["active_in_round"] == False

    def test_activate_waiting_players(self):
        """Test activating players who joined mid-game"""
        # Start game and add waiting player
        self.game.state = "submission"
        self.game.current_round = 1
        self.game.add_player("p4", "Player4")
        self.game.add_player("p5", "Player5")
        
        # Verify they're not active
        assert self.game.players["p4"]["active_in_round"] == False
        assert self.game.players["p5"]["active_in_round"] == False
        assert self.game.get_active_player_count() == 4
        
        # Activate waiting players
        self.game.activate_waiting_players()
        
        # Now they should be active
        assert self.game.players["p4"]["active_in_round"] == True
        assert self.game.players["p5"]["active_in_round"] == True
        assert self.game.get_active_player_count() == 6

    def test_pairings_only_include_active_players(self):
        """Test that round pairings only include active players"""
        # Start game
        self.game.state = "submission"
        self.game.current_round = 1
        
        # Generate pairings with only active players
        pairings = self.game.generate_round_pairings()
        
        # Should have pairings for all 4 active players
        assert len(pairings) == 4
        assert set(pairings.keys()) == {"host1", "p1", "p2", "p3"}
        
        # Add waiting player
        self.game.add_player("p4", "Player4")
        
        # Generate pairings again - should still only include active players
        pairings = self.game.generate_round_pairings()
        assert len(pairings) == 4
        assert set(pairings.keys()) == {"host1", "p1", "p2", "p3"}
        assert "p4" not in pairings

    def test_pairings_include_newly_activated_players(self):
        """Test that pairings include players activated for new round"""
        # Start game and add waiting players
        self.game.state = "submission"
        self.game.current_round = 1
        self.game.add_player("p4", "Player4")
        self.game.add_player("p5", "Player5")
        
        # Initial pairings exclude waiting players
        pairings = self.game.generate_round_pairings()
        assert len(pairings) == 4
        
        # Activate waiting players (simulating new round)
        self.game.activate_waiting_players()
        
        # New pairings should include activated players
        pairings = self.game.generate_round_pairings()
        assert len(pairings) == 6
        assert set(pairings.keys()) == {"host1", "p1", "p2", "p3", "p4", "p5"}

    def test_custom_prompts_only_check_active_players(self):
        """Test that custom prompt readiness only checks active players"""
        # Enable custom prompts
        self.game.settings['custom_prompts'] = True
        self.game.state = "prompt_selection"
        self.game.current_round = 1
        
        # Add waiting player
        self.game.add_player("p4", "Player4")
        
        # Initialize prompt readiness for active players
        self.game.player_prompt_ready[1] = {
            "host1": True,
            "p1": True,
            "p2": True,
            "p3": False  # One active player not ready
        }
        
        # Should not be ready (active player p3 not ready)
        assert not self.game.all_players_prompt_ready(1)
        
        # Mark last active player as ready
        self.game.player_prompt_ready[1]["p3"] = True
        assert self.game.all_players_prompt_ready(1)
        
        # Waiting player readiness shouldn't matter
        self.game.player_prompt_ready[1]["p4"] = False
        assert self.game.all_players_prompt_ready(1)  # Still ready

    def test_can_start_game_uses_active_count(self):
        """Test that game start uses active player count"""
        # Should be able to start with 4 active players
        assert self.game.can_start_game()
        
        # Remove players until below threshold
        self.game.remove_player("p3")
        self.game.remove_player("p2")
        assert not self.game.can_start_game()  # Only 2 active players
        
        # Add waiting players (mid-game joiners)
        self.game.state = "submission"  # Simulate mid-game
        self.game.add_player("p4", "Player4")
        self.game.add_player("p5", "Player5")
        self.game.state = "lobby"  # Back to lobby
        
        # Still can't start because waiting players aren't active
        assert not self.game.can_start_game()
        
        # Activate waiting players
        self.game.activate_waiting_players()
        assert self.game.can_start_game()  # Now have enough active players

    def test_waiting_player_scores_initialized(self):
        """Test that waiting players get initialized scores"""
        # Start game
        self.game.state = "submission"
        self.game.current_round = 1
        
        # Add waiting player
        self.game.add_player("p4", "Player4")
        
        # Should have score initialized to 0
        assert "p4" in self.game.scores
        assert self.game.scores["p4"] == 0

    def test_multiple_midgame_joiners_same_round(self):
        """Test multiple players joining during the same round"""
        # Start game
        self.game.state = "voting"
        self.game.current_round = 2
        
        # Add multiple waiting players
        self.game.add_player("p4", "Player4")
        self.game.add_player("p5", "Player5")
        self.game.add_player("p6", "Player6")
        
        # All should be waiting
        for player_id in ["p4", "p5", "p6"]:
            assert self.game.players[player_id]["active_in_round"] == False
        
        assert self.game.get_active_player_count() == 4
        assert self.game.get_connected_player_count() == 7
        
        # Activate all at once
        self.game.activate_waiting_players()
        
        # All should now be active
        for player_id in ["p4", "p5", "p6"]:
            assert self.game.players[player_id]["active_in_round"] == True
        
        assert self.game.get_active_player_count() == 7

    def test_rejoining_player_maintains_active_status(self):
        """Test that rejoining players maintain their active status"""
        # Start game with player active
        self.game.state = "submission"
        self.game.current_round = 1
        
        # Player disconnects (but stays in game)
        self.game.players["p2"]["connected"] = False
        
        # Player rejoins - should maintain active status
        self.game.players["p2"]["connected"] = True
        
        # Should still be active (not treated as new mid-game joiner)
        assert self.game.players["p2"]["active_in_round"] == True
        assert "p2" in self.game.get_active_player_ids()
