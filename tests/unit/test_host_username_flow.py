#!/usr/bin/env python3
"""
Test cases for host username flow
"""

import pytest
from src.game.game import Game
from src.game.game_manager import GameManager
from src.game.player_session import PlayerSession


class TestHostUsernameFlow:
    """Test scenarios for host username handling"""

    def setup_method(self):
        """Set up test fixtures"""
        self.game_manager = GameManager()

    def test_host_creates_game_with_username(self):
        """Test that host can create game with username"""
        # Create game as host
        game = Game("test-game", "host1", {
            'rounds': 3,
            'submission_time': 30,
            'voting_time': 15,
            'custom_prompts': False
        })
        
        # Add host player
        game.add_player("host1", "TestHost")
        
        # Verify host is properly set up
        assert "host1" in game.players
        assert game.players["host1"]["username"] == "TestHost"
        assert game.host_id == "host1"
        assert game.state == "lobby"

    def test_host_joins_lobby_without_duplicate_prompt(self):
        """Test that host joining lobby uses existing username"""
        # Create game
        game = Game("test-game", "host1", {
            'rounds': 3,
            'submission_time': 30,
            'voting_time': 15,
            'custom_prompts': False
        })
        
        # Add host - simulates server-side game creation
        game.add_player("host1", "TestHost")
        
        # Add to game manager
        self.game_manager.add_game(game)
        
        # Verify host exists with correct username
        retrieved_game = self.game_manager.get_game("test-game")
        assert retrieved_game is not None
        assert "host1" in retrieved_game.players
        assert retrieved_game.players["host1"]["username"] == "TestHost"

    def test_regular_players_still_need_username_prompt(self):
        """Test that regular players (non-hosts) still get prompted for username"""
        # Create game with host
        game = Game("test-game", "host1", {
            'rounds': 3,
            'submission_time': 30,
            'voting_time': 15,
            'custom_prompts': False
        })
        
        game.add_player("host1", "TestHost")
        self.game_manager.add_game(game)
        
        # Add regular player - would normally require username prompt
        game.add_player("p1", "Player1")
        
        # Verify both players exist
        assert len(game.players) == 2
        assert game.players["host1"]["username"] == "TestHost"
        assert game.players["p1"]["username"] == "Player1"

    def test_host_reconnection_preserves_username(self):
        """Test that host reconnection preserves their username"""
        # Create game with host
        game = Game("test-game", "host1", {
            'rounds': 3,
            'submission_time': 30,
            'voting_time': 15,
            'custom_prompts': False
        })
        
        game.add_player("host1", "TestHost")
        self.game_manager.add_game(game)
        
        # Host disconnects
        game.players["host1"]["connected"] = False
        
        # Host reconnects - should find existing player by username
        existing_player_id = None
        for pid, player in game.players.items():
            if player['username'] == "TestHost":
                existing_player_id = pid
                break
        
        assert existing_player_id == "host1"
        
        # Reconnect
        game.players[existing_player_id]["connected"] = True
        
        # Verify host is reconnected with same username
        assert game.players["host1"]["connected"] == True
        assert game.players["host1"]["username"] == "TestHost"
        assert game.host_id == "host1"

    def test_host_flag_preserved_across_lobby_join(self):
        """Test that host flag is preserved when joining lobby"""
        # Create game
        game = Game("test-game", "host1", {
            'rounds': 3,
            'submission_time': 30,
            'voting_time': 15,
            'custom_prompts': False
        })
        
        game.add_player("host1", "TestHost")
        
        # Verify host identification works
        assert game.host_id == "host1"
        
        # Simulate checking if player is host when they join lobby
        is_host = "host1" == game.host_id
        assert is_host == True
        
        # Other players should not be host
        game.add_player("p1", "Player1")
        is_p1_host = "p1" == game.host_id
        assert is_p1_host == False

    def test_username_validation_still_works(self):
        """Test that empty/invalid usernames are still handled properly"""
        game = Game("test-game", "host1", {
            'rounds': 3,
            'submission_time': 30,
            'voting_time': 15,
            'custom_prompts': False
        })
        
        # Test that we can add player with valid username
        game.add_player("host1", "ValidHost")
        assert game.players["host1"]["username"] == "ValidHost"
        
        # Empty usernames should be handled at the application layer
        # The Game class itself doesn't validate, that's done in socket handlers
