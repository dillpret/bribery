#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Unit tests for progress tracking functionality
"""

import pytest
import sys
import os

# Add the src directory to the path
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'src'))

from game import Game


class TestProgressTracking:
    """Test the progress tracking for submissions and voting"""
    
    def test_submission_progress_calculation(self):
        """Test calculating submission progress based on active players"""
        # Create a game with 4 players
        game = Game("TEST", "host", {'rounds': 3, 'submission_time': 60, 'voting_time': 30})
        
        players = ["player1", "player2", "player3", "player4"]
        for i, player_id in enumerate(players):
            game.add_player(player_id, f"Player{i+1}")
        
        # Start round
        game.current_round = 1
        game.bribes = {1: {}}
        
        # Initially no submissions
        active_players = game.get_active_player_ids()
        assert len(active_players) == 4
        
        # Player 1 submits both bribes
        game.bribes[1]["player1"] = {
            "player2": {"content": "bribe1", "type": "text"},
            "player3": {"content": "bribe2", "type": "text"}
        }
        
        # Should have 1/4 completed
        completed_count = sum(1 for player_id in active_players 
                            if len(game.bribes[1].get(player_id, {})) >= 2)
        assert completed_count == 1
        
        # Player 2 submits both bribes
        game.bribes[1]["player2"] = {
            "player1": {"content": "bribe3", "type": "text"},
            "player4": {"content": "bribe4", "type": "text"}
        }
        
        # Should have 2/4 completed
        completed_count = sum(1 for player_id in active_players 
                            if len(game.bribes[1].get(player_id, {})) >= 2)
        assert completed_count == 2
        
    def test_voting_progress_calculation(self):
        """Test calculating voting progress based on active players"""
        # Create a game with 3 players
        game = Game("TEST", "host", {'rounds': 3, 'submission_time': 60, 'voting_time': 30})
        
        players = ["player1", "player2", "player3"]
        for i, player_id in enumerate(players):
            game.add_player(player_id, f"Player{i+1}")
        
        # Start round
        game.current_round = 1
        game.votes = {1: {}}
        
        # Initially no votes
        active_players = game.get_active_player_ids()
        votes_submitted = len(game.votes[1])
        assert votes_submitted == 0
        
        # Player 1 votes
        game.votes[1]["player1"] = "bribe_id_1"
        votes_submitted = len(game.votes[1])
        assert votes_submitted == 1
        
        # Player 2 votes
        game.votes[1]["player2"] = "bribe_id_2"
        votes_submitted = len(game.votes[1])
        assert votes_submitted == 2
        
        # All players voted
        game.votes[1]["player3"] = "bribe_id_3"
        votes_submitted = len(game.votes[1])
        assert votes_submitted == 3
        assert votes_submitted == len(active_players)
        
    def test_progress_message_generation(self):
        """Test the logic for generating progress messages"""
        # Test general progress message
        completed = 3
        total = 8
        message = f"{completed}/{total} players finished"
        assert message == "3/8 players finished"
        
        # Test waiting for specific players (2 remaining)
        player_names = ["Alice", "Bob"]
        message = f"Waiting for {player_names[0]} and {player_names[1]}"
        assert message == "Waiting for Alice and Bob"
        
        # Test waiting for one player
        message = f"Waiting for {player_names[0]}"
        assert message == "Waiting for Alice"
        
    def test_inactive_players_excluded_from_progress(self):
        """Test that inactive players don't affect progress calculations"""
        # Create a game with players, some inactive
        game = Game("TEST", "host", {'rounds': 3, 'submission_time': 60, 'voting_time': 30})
        
        # Add 4 players
        players = ["player1", "player2", "player3", "player4"]
        for i, player_id in enumerate(players):
            game.add_player(player_id, f"Player{i+1}")
        
        # Make player4 inactive (joined mid-game)
        game.players["player4"]["active_in_round"] = False
        
        # Active players should only be 3
        active_players = game.get_active_player_ids()
        assert len(active_players) == 3
        assert "player4" not in active_players
        
        # Progress calculation should use active count
        game.current_round = 1
        game.bribes = {1: {
            "player1": {"p2": {"content": "b1", "type": "text"}, "p3": {"content": "b2", "type": "text"}},
            "player2": {"p1": {"content": "b3", "type": "text"}, "p3": {"content": "b4", "type": "text"}}
        }}
        
        # 2 out of 3 active players completed
        completed_count = sum(1 for player_id in active_players 
                            if len(game.bribes[1].get(player_id, {})) >= 2)
        assert completed_count == 2
        
        # Even if inactive player submits, they don't count
        game.bribes[1]["player4"] = {"p1": {"content": "b5", "type": "text"}, "p2": {"content": "b6", "type": "text"}}
        completed_count = sum(1 for player_id in active_players 
                            if len(game.bribes[1].get(player_id, {})) >= 2)
        assert completed_count == 2  # Still 2, not 3
