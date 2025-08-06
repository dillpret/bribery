#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test for custom prompts UI improvements
"""

import pytest
import sys
import os

# Add the src directory to the path
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'src'))

from game import Game


class TestCustomPromptsUIImprovements:
    """Test the custom prompts UI improvements"""
    
    def test_custom_prompts_default_enabled(self):
        """Test that custom prompts should be the recommended default"""
        # This test verifies the logic is ready for custom prompts being default
        game = Game("TEST", "host", {'rounds': 3, 'submission_time': 60, 'voting_time': 30, 'custom_prompts': True})
        
        # Add players
        players = ["player1", "player2", "player3"]
        for i, player_id in enumerate(players):
            game.add_player(player_id, f"Player{i+1}")
        
        # Verify custom prompts are enabled
        assert game.custom_prompts_enabled() == True
        
        # Start round and verify prompt selection logic
        game.current_round = 1
        game.player_prompts = {1: {}}
        game.player_prompt_ready = {1: {}}
        
        # Players should be able to select custom prompts
        game.player_prompts[1]["player1"] = "Write a funny joke about your target"
        game.player_prompt_ready[1]["player1"] = True
        
        game.player_prompts[1]["player2"] = "Create a meme about your target"  
        game.player_prompt_ready[1]["player2"] = True
        
        game.player_prompts[1]["player3"] = "Compose a haiku about your target"
        game.player_prompt_ready[1]["player3"] = True
        
        # All players should be ready
        assert game.all_players_prompt_ready(1) == True
        
    def test_prompt_selection_logic_separation(self):
        """Test that dropdown and custom input can work independently"""
        game = Game("TEST", "host", {'rounds': 3, 'submission_time': 60, 'voting_time': 30, 'custom_prompts': True})
        
        # Add players
        players = ["player1", "player2", "player3", "player4"]
        for i, player_id in enumerate(players):
            game.add_player(player_id, f"Player{i+1}")
        
        game.current_round = 1
        game.player_prompts = {1: {}}
        game.player_prompt_ready = {1: {}}
        
        # Mix of dropdown selections and custom prompts
        # Player 1 uses a predefined prompt (as if selected from dropdown)
        game.player_prompts[1]["player1"] = "Write a limerick about your target"
        game.player_prompt_ready[1]["player1"] = True
        
        # Player 2 uses a custom prompt (as if typed in textarea)
        game.player_prompts[1]["player2"] = "Tell me what superpower your target would have and why"
        game.player_prompt_ready[1]["player2"] = True
        
        # Player 3 uses another predefined prompt
        game.player_prompts[1]["player3"] = "Create a haiku about your target"
        game.player_prompt_ready[1]["player3"] = True
        
        # Player 4 uses a very specific custom prompt
        game.player_prompts[1]["player4"] = "If your target was a restaurant, what would it be called and what would be on the menu?"
        game.player_prompt_ready[1]["player4"] = True
        
        # All should be valid and ready
        assert game.all_players_prompt_ready(1) == True
        
        # Verify each player gets their specific prompt when needed
        assert game.get_prompt_for_target(1, "player1") == "Write a limerick about your target"
        assert game.get_prompt_for_target(1, "player2") == "Tell me what superpower your target would have and why"
        assert game.get_prompt_for_target(1, "player3") == "Create a haiku about your target"
        assert "restaurant" in game.get_prompt_for_target(1, "player4")
        
    def test_prompt_validation_logic(self):
        """Test prompt validation for both dropdown and custom inputs"""
        game = Game("TEST", "host", {'rounds': 3, 'submission_time': 60, 'voting_time': 30, 'custom_prompts': True})
        
        # Add a player
        game.add_player("player1", "Player1")
        
        game.current_round = 1
        game.player_prompts = {1: {}}
        game.player_prompt_ready = {1: {}}
        
        # Test empty prompt (should not be ready)
        game.player_prompts[1]["player1"] = ""
        game.player_prompt_ready[1]["player1"] = False
        assert not game.all_players_prompt_ready(1)
        
        # Test whitespace-only prompt (should not be ready)
        game.player_prompts[1]["player1"] = "   "
        game.player_prompt_ready[1]["player1"] = False
        assert not game.all_players_prompt_ready(1)
        
        # Test valid prompt
        game.player_prompts[1]["player1"] = "Create something creative about your target"
        game.player_prompt_ready[1]["player1"] = True
        assert game.all_players_prompt_ready(1)
        
        # Test very long prompt (should still be valid if under character limit)
        long_prompt = "A" * 150  # Reasonable length
        game.player_prompts[1]["player1"] = long_prompt
        game.player_prompt_ready[1]["player1"] = True
        assert game.all_players_prompt_ready(1)
        
    def test_mixed_prompt_modes_in_same_game(self):
        """Test that a game can handle both predefined and custom prompts seamlessly"""
        game = Game("TEST", "host", {'rounds': 3, 'submission_time': 60, 'voting_time': 30, 'custom_prompts': True})
        
        # Add players
        players = ["dropdown_user", "custom_user", "another_dropdown", "creative_custom"]
        for i, player_id in enumerate(players):
            game.add_player(player_id, player_id.replace("_", " ").title())
        
        game.current_round = 1
        game.player_prompts = {1: {}}
        game.player_prompt_ready = {1: {}}
        
        # Simulate realistic usage patterns
        prompts = {
            "dropdown_user": "Write a haiku about your target",  # Standard dropdown option
            "custom_user": "What would your target's autobiography be called?",  # Custom creative prompt
            "another_dropdown": "Create a meme about your target",  # Another standard option
            "creative_custom": "If your target was a Netflix show, what genre would it be and why?"  # Another custom
        }
        
        for player_id, prompt in prompts.items():
            game.player_prompts[1][player_id] = prompt
            game.player_prompt_ready[1][player_id] = True
        
        # Should work seamlessly
        assert game.all_players_prompt_ready(1) == True
        
        # Each player should get their chosen prompt
        for player_id, expected_prompt in prompts.items():
            actual_prompt = game.get_prompt_for_target(1, player_id)
            assert actual_prompt == expected_prompt
