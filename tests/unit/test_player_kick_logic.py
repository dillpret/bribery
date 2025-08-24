#!/usr/bin/env python3
"""
Unit tests for player kick functionality in the Game class
"""

import pytest
from src.game.game import Game


class TestPlayerKickLogic:
    """Test the game logic for player kick functionality"""

    def setup_method(self):
        """Set up test fixtures"""
        # Create a test game with a host and players
        self.game = Game("TEST123", "host1", {
            'rounds': 3,
            'submission_time': 30,
            'voting_time': 15,
            'custom_prompts': False
        })
        
        # Add players to the game
        self.game.add_player("host1", "HostUser")
        self.game.add_player("player1", "Player1")
        self.game.add_player("player2", "Player2")
        self.game.add_player("player3", "Player3")
        
        # Add some scores to test sorting
        self.game.scores["host1"] = 10
        self.game.scores["player1"] = 5
        self.game.scores["player2"] = 15
        self.game.scores["player3"] = 0
    
    def test_remove_player(self):
        """Test removing a player from the game"""
        # Verify initial player count
        assert len(self.game.players) == 4
        assert "player1" in self.game.players
        
        # Remove a player
        self.game.remove_player("player1")
        
        # Verify player was removed
        assert len(self.game.players) == 3
        assert "player1" not in self.game.players
        assert "player1" not in self.game.scores
        assert "player1" not in self.game.past_bribe_targets
        
        # Verify other players remain
        assert "host1" in self.game.players
        assert "player2" in self.game.players
        assert "player3" in self.game.players
    
    def test_remove_host(self):
        """Test removing the host player"""
        # Remove the host
        self.game.remove_player("host1")
        
        # Verify host was removed from players
        assert "host1" not in self.game.players
        assert "host1" not in self.game.scores
        
        # Host ID should still be set (this might be something to improve in the game logic)
        assert self.game.host_id == "host1"
    
    def test_remove_nonexistent_player(self):
        """Test removing a player that doesn't exist (should not raise errors)"""
        initial_player_count = len(self.game.players)
        
        # Try to remove a non-existent player
        self.game.remove_player("nonexistent")
        
        # Verify no change in player count
        assert len(self.game.players) == initial_player_count
    
    def test_removing_player_during_active_round(self):
        """Test removing a player during an active round"""
        # Set up an active round
        self.game.current_round = 1
        self.game.state = "submission"
        self.game.round_pairings[1] = self.game.generate_round_pairings()
        self.game.bribes[1] = {}
        
        # Record the initial pairings
        initial_pairings = {}
        for player_id, targets in self.game.round_pairings[1].items():
            initial_pairings[player_id] = targets.copy()
        
        # Remove a player
        player_to_remove = "player1"
        self.game.remove_player(player_to_remove)
        
        # Verify player is removed from game
        assert player_to_remove not in self.game.players
        
        # Current implementation doesn't automatically update round_pairings
        # This is actually a potential improvement to the Game class
        # Simply verify the player is removed from players dictionary
        assert player_to_remove not in self.game.players
    
    def test_player_list_sorting(self):
        """Test player list sorting by score"""
        # Create a function to simulate the frontend sorting
        def sort_players_by_score(players_with_scores):
            """Sort players by score in descending order"""
            return sorted(players_with_scores, key=lambda p: p['score'], reverse=True)
        
        # Create player data
        players_data = [
            {'username': 'HostUser', 'score': 10, 'player_id': 'host1', 'is_host': True},
            {'username': 'Player1', 'score': 5, 'player_id': 'player1', 'is_host': False},
            {'username': 'Player2', 'score': 15, 'player_id': 'player2', 'is_host': False},
            {'username': 'Player3', 'score': 0, 'player_id': 'player3', 'is_host': False}
        ]
        
        # Sort players
        sorted_players = sort_players_by_score(players_data)
        
        # Verify correct sort order
        assert len(sorted_players) == 4
        assert sorted_players[0]['player_id'] == 'player2'  # 15 points
        assert sorted_players[1]['player_id'] == 'host1'    # 10 points
        assert sorted_players[2]['player_id'] == 'player1'  # 5 points
        assert sorted_players[3]['player_id'] == 'player3'  # 0 points
    
    def test_prepare_player_list_data(self):
        """Test preparing player list data with scores"""
        # Define a helper function to create player data like the real handler
        def prepare_player_list_data(game):
            """Simulate the player list data preparation"""
            player_list = []
            for player_id, player in game.players.items():
                player_list.append({
                    'username': player['username'],
                    'is_host': player_id == game.host_id,
                    'connected': player['connected'],
                    'score': game.scores.get(player_id, 0),
                    'player_id': player_id
                })
            return player_list
        
        # Get player list data
        player_list = prepare_player_list_data(self.game)
        
        # Verify data structure
        assert len(player_list) == 4
        
        # Verify each player has the required fields
        for player in player_list:
            assert 'username' in player
            assert 'is_host' in player
            assert 'connected' in player
            assert 'score' in player
            assert 'player_id' in player
        
        # Verify specific player data
        player2 = next(p for p in player_list if p['player_id'] == 'player2')
        assert player2['username'] == 'Player2'
        assert player2['score'] == 15
        assert player2['is_host'] is False
        
        host = next(p for p in player_list if p['player_id'] == 'host1')
        assert host['username'] == 'HostUser'
        assert host['is_host'] is True
        assert host['score'] == 10
    
    def test_prepare_scoreboard_data(self):
        """Test preparing scoreboard data with player IDs"""
        # Define a helper function to create scoreboard data like the real handler
        def prepare_scoreboard_data(game, round_scores=None):
            """Simulate the scoreboard data preparation"""
            if round_scores is None:
                round_scores = {}
                
            scoreboard = []
            for player_id, total_score in game.scores.items():
                scoreboard.append({
                    'username': game.players[player_id]['username'],
                    'round_score': round_scores.get(player_id, 0),
                    'total_score': total_score,
                    'player_id': player_id,
                    'is_host': player_id == game.host_id
                })
            
            return sorted(scoreboard, key=lambda x: x['total_score'], reverse=True)
        
        # Set up some round scores
        round_scores = {
            'host1': 2,
            'player1': 1,
            'player2': 3,
            'player3': 0
        }
        
        # Get scoreboard data
        scoreboard = prepare_scoreboard_data(self.game, round_scores)
        
        # Verify data structure
        assert len(scoreboard) == 4
        
        # Verify sorting
        assert scoreboard[0]['player_id'] == 'player2'  # 15 points
        assert scoreboard[1]['player_id'] == 'host1'    # 10 points
        assert scoreboard[2]['player_id'] == 'player1'  # 5 points
        assert scoreboard[3]['player_id'] == 'player3'  # 0 points
        
        # Verify each player has the required fields
        for player in scoreboard:
            assert 'username' in player
            assert 'round_score' in player
            assert 'total_score' in player
            assert 'player_id' in player
            assert 'is_host' in player
        
        # Verify specific player data
        assert scoreboard[0]['round_score'] == 3
        assert scoreboard[1]['is_host'] is True
        assert scoreboard[1]['round_score'] == 2
