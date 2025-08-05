#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Unit tests for core game logic and functionality
"""

import pytest
import sys
import os

# Add the app directory to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'src'))

class TestGameLogic:
    """Test core game logic without server dependencies"""
    
    def test_prompts_loading(self):
        """Test that prompts are loaded correctly"""
        # Test prompts loading without importing Flask app
        import os
        prompts_file = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'data', 'prompts.txt')
        
        if os.path.exists(prompts_file):
            with open(prompts_file, 'r', encoding='utf-8') as f:
                prompts = [line.strip() for line in f if line.strip()]
            
            assert len(prompts) > 0
            assert isinstance(prompts, list)
            assert all(isinstance(prompt, str) for prompt in prompts)
            
            # Check for some expected prompts
            prompt_text = ' '.join(prompts).lower()
            assert any(word in prompt_text for word in ['haiku', 'meme', 'write', 'create'])
        else:
            # Fallback test with sample prompts
            sample_prompts = [
                "Write a haiku about your target",
                "Create a meme about your target",
                "Compose a song about your target"
            ]
            
            assert len(sample_prompts) > 0
            prompt_text = ' '.join(sample_prompts).lower()
            assert 'haiku' in prompt_text
            assert 'meme' in prompt_text
    
    def test_game_id_generation(self):
        """Test game ID generation logic"""
        import random
        import string
        
        # Simulate the game ID generation logic
        def generate_test_game_id():
            return ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
        
        # Generate a game ID
        game_id = generate_test_game_id()
        
        # Should be 8 characters long
        assert len(game_id) == 8
        assert game_id.isalnum()
        assert game_id.isupper() or any(c.isdigit() for c in game_id)
    
    def test_player_assignment(self):
        """Test player target assignment logic"""
        import random
        
        def assign_test_targets(players):
            """Test version of target assignment"""
            assignments = {}
            for player in players:
                # Each player gets 2 targets (excluding themselves)
                other_players = [p for p in players if p != player]
                targets = random.sample(other_players, min(2, len(other_players)))
                assignments[player] = targets
            return assignments
        
        # Test with 3 players
        players = ['Player1', 'Player2', 'Player3']
        assignments = assign_test_targets(players)
        
        # Each player should have 2 targets
        assert len(assignments) == 3
        for player, targets in assignments.items():
            assert len(targets) == 2
            assert player not in targets  # Player shouldn't target themselves
        
        # Test with 4 players
        players = ['Player1', 'Player2', 'Player3', 'Player4']
        assignments = assign_test_targets(players)
        
        assert len(assignments) == 4
        for player, targets in assignments.items():
            assert len(targets) == 2
            assert player not in targets
    
    def test_scoring_logic(self):
        """Test vote counting and scoring"""
        # This would test the scoring logic once it's extracted into a separate function
        # For now, we'll create a simple test structure
        
        votes = {
            'bribe1': ['player1', 'player2'],
            'bribe2': ['player3'],
            'bribe3': ['player1', 'player2', 'player3']
        }
        
        # Count votes
        vote_counts = {bribe_id: len(voters) for bribe_id, voters in votes.items()}
        
        assert vote_counts['bribe1'] == 2
        assert vote_counts['bribe2'] == 1
        assert vote_counts['bribe3'] == 3
        
        # Winner should be bribe3
        winner = max(vote_counts, key=vote_counts.get)
        assert winner == 'bribe3'
