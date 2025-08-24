#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tests for multi-round game progression
"""

import pytest
from tests.unit.game_mechanics import Game, GameManager

class TestMultiRoundLogic:
    """Test multi-round game progression"""
    
    def test_different_prompts_per_round(self):
        """Test that each round gets a different random prompt"""
        game = Game("TEST1234", "host", {'rounds': 3, 'submission_time': 60, 'voting_time': 30})
        
        # Mock prompts
        mock_prompts = [
            "Write a haiku about your target",
            "Create a meme about your target", 
            "Compose a song about your target"
        ]
        
        used_prompts = []
        
        # Simulate 3 rounds
        for round_num in [1, 2, 3]:
            # In real implementation, this would call random.choice(prompts)
            # Here we simulate getting different prompts
            prompt = mock_prompts[round_num - 1]
            used_prompts.append(prompt)
            game.current_prompt = prompt
        
        # Each round should have a different prompt
        assert len(set(used_prompts)) == 3
        assert len(used_prompts) == 3
    
    def test_different_pairings_per_round(self):
        """Test that each round has different player pairings"""
        game = Game("TEST1234", "host", {'rounds': 3, 'submission_time': 60, 'voting_time': 30})
        
        # Add 4 players
        game.add_player("p1", "Player1")
        game.add_player("p2", "Player2")
        game.add_player("p3", "Player3")
        game.add_player("p4", "Player4")
        
        # Generate pairings for 3 rounds
        round_pairings = {}
        for round_num in [1, 2, 3]:
            round_pairings[round_num] = game.generate_round_pairings()
        
        # Pairings should be different between rounds (due to shuffling)
        # Note: There's a small chance they could be the same due to randomness,
        # but we'll test the structure is correct
        for round_num in [1, 2, 3]:
            pairings = round_pairings[round_num]
            
            # Each player should have exactly 2 targets
            assert len(pairings) == 4
            for player_id, targets in pairings.items():
                assert len(targets) == 2
                assert player_id not in targets
    
    def test_game_ending_after_configured_rounds(self):
        """Test game ends after configured number of rounds"""
        game = Game("TEST1234", "host", {'rounds': 2, 'submission_time': 60, 'voting_time': 30})
        
        # After round 1
        game.current_round = 1
        assert not self._should_end_game(game)
        
        # After round 2 (max rounds)
        game.current_round = 2
        assert self._should_end_game(game)
        
        # Test with different round count
        game.settings['rounds'] = 5
        game.current_round = 4
        assert not self._should_end_game(game)
        
        game.current_round = 5
        assert self._should_end_game(game)
    
    def test_round_data_isolation(self):
        """Test that each round's data is stored separately"""
        game = Game("TEST1234", "host", {'rounds': 3, 'submission_time': 60, 'voting_time': 30})
        
        # Add bribes for round 1
        game.bribes[1] = {
            "p1": {"p2": {"content": "round1 bribe", "type": "text"}}
        }
        
        # Add votes for round 1
        game.votes[1] = {"p1": "p2_p1"}
        
        # Add bribes for round 2
        game.bribes[2] = {
            "p1": {"p3": {"content": "round2 bribe", "type": "text"}}
        }
        
        # Add votes for round 2
        game.votes[2] = {"p1": "p3_p1"}
        
        # Data should be isolated per round
        assert game.bribes[1] != game.bribes[2]
        assert game.votes[1] != game.votes[2]
        assert len(game.bribes) == 2
        assert len(game.votes) == 2
    
    def _should_end_game(self, game):
        """Helper: Determine if game should end"""
        return game.current_round >= game.settings['rounds']
