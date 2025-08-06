#!/usr/bin/env python3
"""
Test cases for page refresh rejoining and game state management
"""

import pytest
from src.game.game import Game
from src.game.game_manager import GameManager
from src.game.player_session import PlayerSession


class TestGameStateManagement:
    """Test game state management, refreshes, and new game scenarios"""

    def setup_method(self):
        """Set up test fixtures"""
        self.game_manager = GameManager()
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
        
        self.game_manager.add_game(self.game)

    def test_page_refresh_rejoin_by_username(self):
        """Test that page refresh allows rejoining by username match"""
        # Simulate player being connected with a session
        session = PlayerSession("session1", "p1", "test-game")
        self.game_manager.add_player_session("session1", session)
        self.game.players["p1"]["connected"] = True
        
        # Simulate page refresh - session lost but game still exists
        self.game_manager.remove_player_session("session1")
        
        # Player should be marked as disconnected but still in game
        assert "p1" in self.game.players
        assert self.game.players["p1"]["username"] == "Player1"
        
        # Simulate rejoin attempt with same username
        existing_player_id = None
        for pid, player in self.game.players.items():
            if player['username'] == "Player1":
                existing_player_id = pid
                break
        
        assert existing_player_id == "p1"
        
        # Rejoin should reuse existing player ID
        new_session = PlayerSession("session2", existing_player_id, "test-game")
        self.game_manager.add_player_session("session2", new_session)
        self.game.players[existing_player_id]["connected"] = True
        
        # Verify player is reconnected with same ID and username
        assert self.game.players["p1"]["connected"] == True
        assert self.game.players["p1"]["username"] == "Player1"

    def test_new_game_after_finished_game(self):
        """Test creating new game after previous game finished"""
        # Finish the first game
        self.game.state = "finished"
        self.game.current_round = 3
        self.game.scores = {"host1": 5, "p1": 3, "p2": 7, "p3": 2}
        
        # Create new game (simulating host creating another game)
        new_game = Game("new-game", "host1", {
            'rounds': 2,  # Different settings
            'submission_time': 45,
            'voting_time': 20,
            'custom_prompts': True
        })
        
        # Add same players to new game
        new_game.add_player("host1", "Host")
        new_game.add_player("p1", "Player1")
        new_game.add_player("p2", "Player2")
        
        # Verify new game has clean state
        assert new_game.game_id == "new-game"
        assert new_game.state == "lobby"
        assert new_game.current_round == 0
        assert len(new_game.scores) == 3
        assert all(score == 0 for score in new_game.scores.values())
        assert new_game.bribes == {}
        assert new_game.votes == {}
        assert new_game.round_pairings == {}
        
        # Old game should be unchanged
        assert self.game.state == "finished"
        assert self.game.scores["p2"] == 7

    def test_game_manager_handles_multiple_games(self):
        """Test that game manager properly handles multiple concurrent games"""
        # Create second game
        game2 = Game("game2", "other-host", {
            'rounds': 1,
            'submission_time': 30,
            'voting_time': 15,
            'custom_prompts': False
        })
        game2.add_player("other-host", "OtherHost")
        game2.add_player("p4", "Player4")
        
        self.game_manager.add_game(game2)
        
        # Verify both games exist independently
        assert self.game_manager.get_game("test-game") == self.game
        assert self.game_manager.get_game("game2") == game2
        
        # Games should have independent states
        self.game.state = "submission"
        game2.state = "lobby"
        
        assert self.game_manager.get_game("test-game").state == "submission"
        assert self.game_manager.get_game("game2").state == "lobby"

    def test_player_session_cleanup_on_disconnect(self):
        """Test that player sessions are properly cleaned up"""
        # Add player sessions
        session1 = PlayerSession("sid1", "p1", "test-game")
        session2 = PlayerSession("sid2", "p2", "test-game")
        
        self.game_manager.add_player_session("sid1", session1)
        self.game_manager.add_player_session("sid2", session2)
        
        # Verify sessions exist
        assert self.game_manager.player_sessions.get("sid1") == session1
        assert self.game_manager.player_sessions.get("sid2") == session2
        
        # Remove one session
        self.game_manager.remove_player_session("sid1")
        
        # Verify only that session was removed
        assert self.game_manager.player_sessions.get("sid1") is None
        assert self.game_manager.player_sessions.get("sid2") == session2

    def test_rejoining_preserves_game_progress(self):
        """Test that rejoining preserves active game progress"""
        # Start game and make progress
        self.game.state = "voting"
        self.game.current_round = 2
        self.game.scores = {"host1": 2, "p1": 1, "p2": 3, "p3": 1}
        self.game.bribes[2] = {
            "host1": {"p1": {"content": "Test bribe", "type": "text"}}
        }
        
        # Player disconnects
        self.game.players["p1"]["connected"] = False
        
        # Player rejoins
        self.game.players["p1"]["connected"] = True
        
        # Game progress should be preserved
        assert self.game.state == "voting"
        assert self.game.current_round == 2
        assert self.game.scores["p1"] == 1
        assert 2 in self.game.bribes

    def test_username_conflict_on_rejoin(self):
        """Test handling of username conflicts when rejoining"""
        # Add another player with similar username
        self.game.add_player("p4", "Player1")  # Same username as p1
        
        # Try to find player by username - should match first occurrence
        existing_player_id = None
        for pid, player in self.game.players.items():
            if player['username'] == "Player1":
                existing_player_id = pid
                break
        
        # Should find the first player with that username
        assert existing_player_id in ["p1", "p4"]

    def test_game_state_transitions_after_finish(self):
        """Test that finished games don't accept state changes"""
        # Finish the game
        self.game.state = "finished"
        
        # Verify game is in finished state
        assert self.game.state == "finished"
        
        # Attempting to start should not work (game should be finished)
        can_start = self.game.can_start_game()
        assert not can_start  # Finished games can't be started

    def test_clean_game_initialization(self):
        """Test that new games start with completely clean state"""
        new_game = Game("clean-game", "new-host", {
            'rounds': 3,
            'submission_time': 30,
            'voting_time': 15,
            'custom_prompts': False
        })
        
        # Add host
        new_game.add_player("new-host", "NewHost")
        
        # Verify completely clean state
        assert new_game.state == "lobby"
        assert new_game.current_round == 0
        assert new_game.bribes == {}
        assert new_game.votes == {}
        assert new_game.round_pairings == {}
        assert len(new_game.scores) == 1
        assert new_game.scores["new-host"] == 0
        assert len(new_game.players) == 1
        assert new_game.players["new-host"]["active_in_round"] == True
        assert new_game.players["new-host"]["connected"] == True

    def test_game_cleanup_removes_empty_games(self):
        """Test that empty games are properly cleaned up"""
        # Start with players
        assert len(self.game.players) == 4
        
        # Remove all players
        for player_id in list(self.game.players.keys()):
            self.game.remove_player(player_id)
        
        # Game should be empty
        assert len(self.game.players) == 0
        assert self.game.get_connected_player_count() == 0
        assert self.game.get_active_player_count() == 0
        
        # Empty game should be identified for cleanup
        is_empty = len(self.game.players) == 0
        assert is_empty
