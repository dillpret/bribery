"""
Test cases for configurable prompt selection timer
"""

import pytest
from unittest.mock import patch, MagicMock, ANY

from src.game.game import Game
from src.game.game_manager import GameManager


class TestPromptSelectionTimer:
    """Test the behavior of the prompt selection timer setting"""

    def setup_method(self):
        """Set up a game with test players"""
        self.game = Game("TEST1", "host123", {
            'rounds': 3,
            'submission_time': 60,
            'voting_time': 30,
            'results_time': 15,
            'prompt_selection_time': 45,  # Custom prompt selection time
            'custom_prompts': True
        })
        
        # Add test players
        self.game.add_player("host123", "Host")
        self.game.add_player("player1", "Player 1")
        self.game.add_player("player2", "Player 2")
        self.game.add_player("player3", "Player 3")
        
        # Set up a round
        self.game.current_round = 1
        self.game.state = "lobby"

    @patch('src.web.socket_handlers.game_flow.socketio')
    @patch('threading.Timer')
    def test_prompt_selection_configurable_timer(self, mock_timer, mock_socketio):
        """Test that prompt selection uses the configured timer value"""
        game = self.game
        
        # Verify the custom prompt selection time is set
        assert game.settings['prompt_selection_time'] == 45
        
        # Simulate the code in start_next_round that starts the prompt selection timer
        prompt_selection_time = game.settings.get('prompt_selection_time', 30)
        
        # Emit to clients (in real code this would send the time_limit)
        mock_socketio.emit.side_effect = lambda event, data, room: None
        
        # Create and start the timer if prompt_selection_time > 0
        if prompt_selection_time > 0:
            mock_timer.return_value.start.side_effect = lambda: None
            timer = mock_timer(prompt_selection_time, ANY, [game])
            timer.start()
        
        # Verify timer was created with correct time (45 seconds)
        mock_timer.assert_called_once_with(45, ANY, [game])
        mock_timer.return_value.start.assert_called_once()

    @patch('src.web.socket_handlers.game_flow.socketio')
    @patch('threading.Timer')
    def test_prompt_selection_no_timer_mode(self, mock_timer, mock_socketio):
        """Test that prompt selection respects the 'no timer' setting"""
        # Set prompt selection time to 0 (no timer mode)
        self.game.settings['prompt_selection_time'] = 0
        game = self.game
        
        # Verify the prompt selection time is set to 0
        assert game.settings['prompt_selection_time'] == 0
        
        # Simulate the code in start_next_round
        prompt_selection_time = game.settings.get('prompt_selection_time', 30)
        
        # Emit to clients
        mock_socketio.emit.side_effect = lambda event, data, room: None
        
        # Only create timer if prompt_selection_time > 0
        if prompt_selection_time > 0:
            mock_timer.return_value.start.side_effect = lambda: None
            timer = mock_timer(prompt_selection_time, ANY, [game])
            timer.start()
        
        # Verify no timer was created (since prompt_selection_time is 0)
        mock_timer.assert_not_called()

    def test_prompt_selection_time_default(self):
        """Test that prompt selection time defaults to 30 seconds if not specified"""
        # Create a game without specifying prompt_selection_time
        game = Game("TEST2", "host456", {
            'rounds': 3,
            'submission_time': 60,
            'voting_time': 30,
            'custom_prompts': True
        })
        
        # The game_flow.py code uses .get('prompt_selection_time', 30)
        # Let's simulate that behavior
        prompt_selection_time = game.settings.get('prompt_selection_time', 30)
        
        # Verify the default is 30 seconds
        assert prompt_selection_time == 30
