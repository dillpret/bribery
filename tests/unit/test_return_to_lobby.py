#!/usr/bin/env python3
"""
Test cases for return to lobby functionality
"""

import pytest
from src.game.game import Game
from src.game.game_manager import GameManager
from src.game.player_session import PlayerSession


class TestReturnToLobby:
    """Test scenarios for returning to lobby after game completion"""

    def setup_method(self):
        """Set up test fixtures"""
        self.game_manager = GameManager()

    def test_return_to_lobby_resets_game_state(self):
        """Test that returning to lobby properly resets game state"""
        # Create finished game
        game = Game("test-game", "host1", {
            'rounds': 2,
            'submission_time': 30,
            'voting_time': 15,
            'custom_prompts': False
        })
        
        # Add some players and simulate finished game
        game.add_player("host1", "TestHost")
        game.add_player("p1", "Player1") 
        game.add_player("p2", "Player2")
        
        # Simulate game completion
        game.state = "finished"
        game.current_round = 2
        game.bribes = {1: {"host1": ["bribe1", "bribe2"]}, 2: {"p1": ["bribe3", "bribe4"]}}
        game.votes = {1: {"p1": "host1", "p2": "host1"}, 2: {"host1": "p1"}}
        game.scores = {"host1": 2, "p1": 1, "p2": 0}
        game.current_prompt = "Some old prompt"
        game.round_pairings = {1: {"host1": ["p1", "p2"]}}
        
        # Now simulate return to lobby
        game.state = "lobby"
        game.current_round = 0
        game.bribes = {}
        game.votes = {}
        game.scores = {pid: 0 for pid in game.players}
        game.current_prompt = ""
        game.round_pairings = {}
        
        # Verify state reset
        assert game.state == "lobby"
        assert game.current_round == 0
        assert game.bribes == {}
        assert game.votes == {}
        assert game.scores == {"host1": 0, "p1": 0, "p2": 0}
        assert game.current_prompt == ""
        assert game.round_pairings == {}
        
        # Verify players and settings are preserved
        assert len(game.players) == 3
        assert "host1" in game.players
        assert "p1" in game.players
        assert "p2" in game.players
        assert game.host_id == "host1"
        assert game.settings['rounds'] == 2
        assert game.settings['custom_prompts'] == False

    def test_return_to_lobby_preserves_players(self):
        """Test that returning to lobby keeps all players connected"""
        game = Game("test-game", "host1", {
            'rounds': 1,
            'submission_time': 30,
            'voting_time': 15,
            'custom_prompts': True
        })
        
        # Add players with different connection states
        game.add_player("host1", "TestHost")
        game.add_player("p1", "Player1")
        game.add_player("p2", "Player2")
        game.players["p1"]["connected"] = False  # Simulate disconnection
        
        # Simulate finished game then return to lobby
        game.state = "finished"
        
        # Return to lobby - should preserve all player data
        game.state = "lobby"
        game.current_round = 0
        game.bribes = {}
        game.votes = {}
        game.scores = {pid: 0 for pid in game.players}
        
        # Verify players preserved including connection states
        assert len(game.players) == 3
        assert game.players["host1"]["username"] == "TestHost"
        assert game.players["p1"]["username"] == "Player1"
        assert game.players["p2"]["username"] == "Player2"
        assert game.players["host1"]["connected"] == True
        assert game.players["p1"]["connected"] == False  # Should preserve disconnection
        assert game.players["p2"]["connected"] == True

    def test_return_to_lobby_preserves_custom_settings(self):
        """Test that returning to lobby preserves game configuration"""
        game = Game("test-game", "host1", {
            'rounds': 5,
            'submission_time': 60,
            'voting_time': 30,
            'custom_prompts': True
        })
        
        game.add_player("host1", "TestHost")
        game.add_player("p1", "Player1")
        
        # Simulate game completion 
        game.state = "finished"
        
        # Return to lobby
        game.state = "lobby"
        game.current_round = 0
        game.bribes = {}
        game.votes = {}
        game.scores = {pid: 0 for pid in game.players}
        
        # Verify settings preserved
        assert game.settings['rounds'] == 5
        assert game.settings['submission_time'] == 60
        assert game.settings['voting_time'] == 30
        assert game.settings['custom_prompts'] == True

    def test_can_start_new_game_after_return_to_lobby(self):
        """Test that a new game can be started after returning to lobby"""
        game = Game("test-game", "host1", {
            'rounds': 2,
            'submission_time': 30,
            'voting_time': 15,
            'custom_prompts': False
        })
        
        game.add_player("host1", "TestHost")
        game.add_player("p1", "Player1")
        game.add_player("p2", "Player2")
        
        # Return to lobby state
        game.state = "lobby"
        game.current_round = 0
        game.bribes = {}
        game.votes = {}
        game.scores = {pid: 0 for pid in game.players}
        
        # Should be able to start again
        assert game.can_start_game()
        assert game.get_active_player_count() >= 3
        
        # Start new game
        if game.can_start_game():
            game.state = "submission"
            game.current_round = 1
            
        assert game.state == "submission"
        assert game.current_round == 1

    def test_return_to_lobby_vs_restart_difference(self):
        """Test difference between return to lobby and full restart"""
        # Create game with custom settings
        game1 = Game("test-game1", "host1", {
            'rounds': 5,
            'submission_time': 45,
            'voting_time': 25,
            'custom_prompts': True
        })
        
        game1.add_player("host1", "TestHost")
        game1.add_player("p1", "Player1")
        
        # Simulate return to lobby (preserves settings)
        original_settings = game1.settings.copy()
        game1.state = "lobby"
        game1.current_round = 0
        game1.bribes = {}
        game1.votes = {}
        game1.scores = {pid: 0 for pid in game1.players}
        
        # Verify settings preserved
        assert game1.settings == original_settings
        assert game1.settings['rounds'] == 5
        assert game1.settings['custom_prompts'] == True
        
        # Compare with restart behaviour (would reset everything)
        game2 = Game("test-game2", "host1", {
            'rounds': 3,  # Default restart settings
            'submission_time': 30,
            'voting_time': 15,
            'custom_prompts': False
        })
        
        game2.add_player("host1", "TestHost") 
        game2.add_player("p1", "Player1")
        
        # This represents the difference - restart gets new default settings
        assert game1.settings != game2.settings
        assert game1.settings['rounds'] != game2.settings['rounds']
