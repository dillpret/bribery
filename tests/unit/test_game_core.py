#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Comprehensive unit tests for core game functionality
"""

import pytest
import sys
import os
import uuid

# Add the app directory to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'src'))

from game.game import Game
from game.game_manager import GameManager

class TestGameCore:
    """Test core game functionality without network dependencies"""
    
    def test_game_creation(self):
        """Test basic game creation and initialization"""
        game_id = "TEST1234"
        host_id = str(uuid.uuid4())
        settings = {'rounds': 3, 'submission_time': 60, 'voting_time': 30}
        
        game = Game(game_id, host_id, settings)
        
        assert game.game_id == game_id
        assert game.host_id == host_id
        assert game.settings == settings
        assert game.state == "lobby"
        assert game.current_round == 0
        assert len(game.players) == 0
        assert len(game.scores) == 0
    
    def test_player_management(self):
        """Test adding, removing, and counting players"""
        game = Game("TEST1234", "host123", {'rounds': 3, 'submission_time': 60, 'voting_time': 30})
        
        # Add players
        game.add_player("host123", "HostUser")
        game.add_player("player1", "Player1")
        game.add_player("player2", "Player2")
        
        assert len(game.players) == 3
        assert game.players["host123"]["username"] == "HostUser"
        assert game.players["host123"]["connected"] == True
        assert game.get_connected_player_count() == 3
        assert game.get_player_count() == 3
        
        # Disconnect a player
        game.players["player1"]["connected"] = False
        assert game.get_connected_player_count() == 2
        assert game.get_player_count() == 3  # Still counts disconnected players
        
        # Remove player
        game.remove_player("player2")
        assert len(game.players) == 2
        assert "player2" not in game.players
        assert "player2" not in game.scores
    
    def test_game_start_conditions(self):
        """Test when game can be started"""
        game = Game("TEST1234", "host123", {'rounds': 3, 'submission_time': 60, 'voting_time': 30})
        
        # Can't start with no players
        assert not game.can_start_game()
        
        # Can't start with 1 player
        game.add_player("host123", "Host")
        assert not game.can_start_game()
        
        # Can't start with 2 players
        game.add_player("player1", "Player1")
        assert not game.can_start_game()
        
        # Can start with 3 players
        game.add_player("player2", "Player2")
        assert game.can_start_game()
        
        # Can start with more players
        game.add_player("player3", "Player3")
        assert game.can_start_game()
        
        # Can't start if not in lobby state
        game.state = "submission"
        assert not game.can_start_game()
    
    def test_round_pairings_algorithm(self):
        """Test round pairing generation logic"""
        game = Game("TEST1234", "host123", {'rounds': 3, 'submission_time': 60, 'voting_time': 30})
        
        # Test with minimum players (3)
        game.add_player("p1", "Player1")
        game.add_player("p2", "Player2")
        game.add_player("p3", "Player3")
        
        pairings = game.generate_round_pairings()
        
        # Each player should have exactly 2 targets
        assert len(pairings) == 3
        for player_id, targets in pairings.items():
            assert len(targets) == 2
            assert player_id not in targets  # Can't target self
            assert len(set(targets)) == 2  # No duplicate targets
        
        # Test with more players (5)
        game.add_player("p4", "Player4")
        game.add_player("p5", "Player5")
        
        pairings = game.generate_round_pairings()
        assert len(pairings) == 5
        
        # Verify each player receives exactly 2 bribes
        target_counts = {}
        for targets in pairings.values():
            for target in targets:
                target_counts[target] = target_counts.get(target, 0) + 1
        
        for player_id in game.players.keys():
            assert target_counts[player_id] == 2
    
    def test_game_state_transitions(self):
        """Test valid game state transitions"""
        game = Game("TEST1234", "host123", {'rounds': 3, 'submission_time': 60, 'voting_time': 30})
        
        # Initial state
        assert game.state == "lobby"
        
        # Valid transitions
        game.state = "submission"
        assert game.state == "submission"
        
        game.state = "voting"
        assert game.state == "voting"
        
        game.state = "scoreboard"
        assert game.state == "scoreboard"
        
        game.state = "finished"
        assert game.state == "finished"
    
    def test_scoring_initialization(self):
        """Test that scores are properly initialized"""
        game = Game("TEST1234", "host123", {'rounds': 3, 'submission_time': 60, 'voting_time': 30})
        
        # Add players
        game.add_player("p1", "Player1")
        game.add_player("p2", "Player2")
        game.add_player("p3", "Player3")
        
        # All players should start with 0 score
        assert len(game.scores) == 3
        assert all(score == 0 for score in game.scores.values())
        
        # Scores can be updated
        game.scores["p1"] = 10
        game.scores["p2"] = 15
        game.scores["p3"] = 5
        
        assert game.scores["p1"] == 10
        assert game.scores["p2"] == 15
        assert game.scores["p3"] == 5


class TestGameManager:
    """Test game manager functionality"""
    
    def test_game_manager_basic_operations(self):
        """Test basic game manager operations"""
        manager = GameManager()
        
        # Create a game
        game = Game("TEST1234", "host123", {'rounds': 3, 'submission_time': 60, 'voting_time': 30})
        manager.add_game(game)
        
        # Retrieve game
        retrieved_game = manager.get_game("TEST1234")
        assert retrieved_game is not None
        assert retrieved_game.game_id == "TEST1234"
        assert retrieved_game is game  # Same object
        
        # Game not found
        assert manager.get_game("NOTFOUND") is None
        assert manager.get_game("notfound") is None  # Case sensitive
    
    def test_multiple_games(self):
        """Test managing multiple games"""
        manager = GameManager()
        
        # Add multiple games
        game1 = Game("GAME0001", "host1", {'rounds': 3, 'submission_time': 60, 'voting_time': 30})
        game2 = Game("GAME0002", "host2", {'rounds': 5, 'submission_time': 90, 'voting_time': 45})
        
        manager.add_game(game1)
        manager.add_game(game2)
        
        # Both games should be retrievable
        assert manager.get_game("GAME0001") is game1
        assert manager.get_game("GAME0002") is game2
        
        # Games should be independent
        assert manager.get_game("GAME0001").settings['rounds'] == 3
        assert manager.get_game("GAME0002").settings['rounds'] == 5


class TestUtilityFunctions:
    """Test utility functions"""
    
    def test_prompt_caching(self):
        """Test that prompts are loaded and cached correctly"""
        import sys
        import os
        
        # Add src to path temporarily for testing
        src_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'src')
        if src_path not in sys.path:
            sys.path.insert(0, src_path)
            
        try:
            # Try to import without Flask dependencies
            from web.utils import load_prompts
            
            # First call should load prompts
            prompts1 = load_prompts()
            assert len(prompts1) > 0
            assert isinstance(prompts1, list)
            assert all(isinstance(prompt, str) for prompt in prompts1)
            
            # Second call should return cached prompts (same object)
            prompts2 = load_prompts()
            assert prompts1 is prompts2  # Same object reference confirms caching
            
            # Content validation
            prompt_text = ' '.join(prompts1).lower()
            expected_words = ['haiku', 'meme', 'joke', 'fact', 'quote', 'gif', 'cute']
            assert any(word in prompt_text for word in expected_words)
            
        except ImportError as e:
            # If Flask isn't available, skip this test
            pytest.skip(f"Flask dependencies not available: {e}")
            
    def test_game_id_format_validation(self):
        """Test game ID format requirements"""
        # Game IDs should be 8 characters, alphanumeric, uppercase
        valid_ids = ["ABC12345", "XYZE7890", "TEST1234", "12345678"]
        
        for game_id in valid_ids:
            game = Game(game_id, "host", {})
            assert game.game_id == game_id
            assert len(game_id) == 8
            assert game_id.isalnum()
