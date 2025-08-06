"""
Unit tests for custom prompts functionality
"""

import unittest
from unittest.mock import Mock, patch
from src.game.game import Game


class TestCustomPrompts(unittest.TestCase):
    """Test custom prompts feature"""
    
    def setUp(self):
        """Set up test games"""
        # Game with custom prompts enabled
        self.custom_game = Game(
            game_id="TEST123", 
            host_id="host1", 
            settings={'custom_prompts': True, 'rounds': 3}
        )
        self.custom_game.add_player("host1", "Host")
        self.custom_game.add_player("player2", "Player2")
        self.custom_game.add_player("player3", "Player3")
        
        # Game with custom prompts disabled (traditional mode)
        self.traditional_game = Game(
            game_id="TRAD456", 
            host_id="host1", 
            settings={'custom_prompts': False, 'rounds': 3}
        )
        self.traditional_game.add_player("host1", "Host")
        self.traditional_game.add_player("player2", "Player2")
        self.traditional_game.add_player("player3", "Player3")
    
    def test_custom_prompts_enabled_check(self):
        """Test custom prompts enabled/disabled detection"""
        self.assertTrue(self.custom_game.custom_prompts_enabled())
        self.assertFalse(self.traditional_game.custom_prompts_enabled())
        
        # Test default behaviour when setting missing
        default_game = Game("DEF789", "host1", {})
        self.assertFalse(default_game.custom_prompts_enabled())
    
    def test_prompt_selection_state_initialization(self):
        """Test prompt selection state is properly initialized"""
        self.custom_game.current_round = 1
        self.custom_game.player_prompts = {1: {}}
        self.custom_game.player_prompt_ready = {1: {}}
        
        # Initially no players ready
        self.assertFalse(self.custom_game.all_players_prompt_ready(1))
        
        # Traditional game should always be ready (skips prompt selection)
        self.assertTrue(self.traditional_game.all_players_prompt_ready(1))
    
    def test_all_players_prompt_ready_logic(self):
        """Test prompt readiness detection logic"""
        round_num = 1
        self.custom_game.current_round = round_num
        self.custom_game.player_prompt_ready = {round_num: {}}
        
        # No players ready initially
        self.assertFalse(self.custom_game.all_players_prompt_ready(round_num))
        
        # Mark players ready one by one
        self.custom_game.player_prompt_ready[round_num]["host1"] = True
        self.assertFalse(self.custom_game.all_players_prompt_ready(round_num))
        
        self.custom_game.player_prompt_ready[round_num]["player2"] = True
        self.assertFalse(self.custom_game.all_players_prompt_ready(round_num))
        
        self.custom_game.player_prompt_ready[round_num]["player3"] = True
        self.assertTrue(self.custom_game.all_players_prompt_ready(round_num))
    
    def test_disconnected_players_not_counted_for_readiness(self):
        """Test that disconnected players don't block prompt readiness"""
        round_num = 1
        self.custom_game.current_round = round_num
        self.custom_game.player_prompt_ready = {round_num: {}}
        
        # Disconnect one player
        self.custom_game.players["player3"]["connected"] = False
        
        # Only need 2 ready players now (host1 and player2)
        self.custom_game.player_prompt_ready[round_num]["host1"] = True
        self.assertFalse(self.custom_game.all_players_prompt_ready(round_num))
        
        self.custom_game.player_prompt_ready[round_num]["player2"] = True
        self.assertTrue(self.custom_game.all_players_prompt_ready(round_num))
    
    def test_get_prompt_for_target_traditional_mode(self):
        """Test prompt retrieval in traditional mode"""
        self.traditional_game.current_prompt = "Traditional shared prompt"
        
        prompt = self.traditional_game.get_prompt_for_target(1, "player2")
        self.assertEqual(prompt, "Traditional shared prompt")
    
    def test_get_prompt_for_target_custom_mode(self):
        """Test prompt retrieval in custom mode"""
        round_num = 1
        self.custom_game.current_round = round_num
        self.custom_game.current_prompt = "Default fallback prompt"
        self.custom_game.player_prompts = {
            round_num: {
                "player2": "Custom prompt for player2",
                "player3": "Custom prompt for player3"
            }
        }
        
        # Get custom prompt for player2
        prompt = self.custom_game.get_prompt_for_target(round_num, "player2")
        self.assertEqual(prompt, "Custom prompt for player2")
        
        # Get custom prompt for player3
        prompt = self.custom_game.get_prompt_for_target(round_num, "player3")
        self.assertEqual(prompt, "Custom prompt for player3")
        
        # Get fallback prompt for player not in custom prompts
        prompt = self.custom_game.get_prompt_for_target(round_num, "unknown_player")
        self.assertEqual(prompt, "Default fallback prompt")
    
    def test_get_prompt_for_target_fallback_when_round_missing(self):
        """Test fallback behaviour when round data is missing"""
        self.custom_game.current_prompt = "Fallback prompt"
        
        # No round data exists
        prompt = self.custom_game.get_prompt_for_target(99, "player2")
        self.assertEqual(prompt, "Fallback prompt")
    
    def test_prompt_storage_per_round(self):
        """Test that prompts are stored separately per round"""
        self.custom_game.player_prompts = {
            1: {"player2": "Round 1 prompt for player2"},
            2: {"player2": "Round 2 prompt for player2"}
        }
        
        round1_prompt = self.custom_game.get_prompt_for_target(1, "player2")
        round2_prompt = self.custom_game.get_prompt_for_target(2, "player2")
        
        self.assertEqual(round1_prompt, "Round 1 prompt for player2")
        self.assertEqual(round2_prompt, "Round 2 prompt for player2")
        self.assertNotEqual(round1_prompt, round2_prompt)
    
    def test_multiple_rounds_custom_prompts(self):
        """Test custom prompts work across multiple rounds"""
        # Round 1
        self.custom_game.current_round = 1
        self.custom_game.player_prompts[1] = {
            "player2": "R1: Make me laugh",
            "player3": "R1: Something shiny"
        }
        self.custom_game.player_prompt_ready[1] = {
            "host1": True, "player2": True, "player3": True
        }
        
        self.assertTrue(self.custom_game.all_players_prompt_ready(1))
        self.assertEqual(
            self.custom_game.get_prompt_for_target(1, "player2"), 
            "R1: Make me laugh"
        )
        
        # Round 2
        self.custom_game.current_round = 2
        self.custom_game.player_prompts[2] = {
            "player2": "R2: Something edible", 
            "player3": "R2: A life hack"
        }
        self.custom_game.player_prompt_ready[2] = {
            "host1": True, "player2": True, "player3": True
        }
        
        self.assertTrue(self.custom_game.all_players_prompt_ready(2))
        self.assertEqual(
            self.custom_game.get_prompt_for_target(2, "player2"),
            "R2: Something edible"
        )
        
        # Verify round 1 data still intact
        self.assertEqual(
            self.custom_game.get_prompt_for_target(1, "player2"),
            "R1: Make me laugh"
        )
    
    def test_custom_prompts_mixed_ready_states(self):
        """Test prompt readiness with mixed ready states"""
        round_num = 1
        self.custom_game.current_round = round_num
        self.custom_game.player_prompt_ready = {
            round_num: {
                "host1": True,
                "player2": False,
                "player3": True
            }
        }
        
        # Not all players ready
        self.assertFalse(self.custom_game.all_players_prompt_ready(round_num))
        
        # Mark remaining player ready
        self.custom_game.player_prompt_ready[round_num]["player2"] = True
        self.assertTrue(self.custom_game.all_players_prompt_ready(round_num))
    
    def test_custom_prompts_empty_prompt_handling(self):
        """Test handling of empty or missing prompts"""
        self.custom_game.current_prompt = "Default prompt"
        self.custom_game.player_prompts = {
            1: {
                "player2": "",  # Empty prompt
                "player3": "Valid prompt"
            }
        }
        
        # Empty prompt should fall back to default
        prompt = self.custom_game.get_prompt_for_target(1, "player2")
        self.assertEqual(prompt, "Default prompt")
        
        # Valid prompt should be returned
        prompt = self.custom_game.get_prompt_for_target(1, "player3")
        self.assertEqual(prompt, "Valid prompt")


if __name__ == '__main__':
    unittest.main()
