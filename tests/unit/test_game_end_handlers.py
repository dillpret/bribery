import unittest
from unittest.mock import patch, MagicMock
import sys
import os

# Add the src directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

# Need to import these first
from flask import Flask
import flask_socketio
app = Flask(__name__)
socketio = flask_socketio.SocketIO(app)

# Now import our function
from src.web.socket_handlers.event_handlers import handle_join_game


class TestGameEndHandlers(unittest.TestCase):
    
    @patch('src.web.socket_handlers.event_handlers.join_room')
    @patch('src.web.socket_handlers.event_handlers.emit')
    @patch('src.web.socket_handlers.event_handlers.game_manager')
    def test_game_not_found(self, mock_manager, mock_emit, mock_join_room):
        # Setup mocks
        mock_manager.games = {}
        mock_manager.get_game.return_value = None
        
        # Create test app context
        with app.test_request_context('/'):
            with app.test_client() as client:
                # Need to manually set Flask-SocketIO request context
                flask_socketio.request = MagicMock()
                flask_socketio.request.sid = 'test_sid'
                
                # Call with valid data but non-existent game
                handle_join_game({'game_id': 'NOTREAL', 'username': 'TestUser'})
                
                # Verify we emit game_not_found event
                mock_emit.assert_called_with('game_not_found', 
                                          {'message': 'Game not found. Check your game code and try again.'})
    
    @patch('src.web.socket_handlers.event_handlers.join_room')
    @patch('src.web.socket_handlers.event_handlers.emit')
    @patch('src.web.socket_handlers.event_handlers.game_manager')
    def test_game_already_finished(self, mock_manager, mock_emit, mock_join_room):
        # Setup mocks
        mock_game = MagicMock()
        mock_game.state = "finished"
        mock_manager.games = {'TEST': mock_game}
        mock_manager.get_game.return_value = mock_game
        
        # Create test app context
        with app.test_request_context('/'):
            with app.test_client() as client:
                # Need to manually set Flask-SocketIO request context
                flask_socketio.request = MagicMock()
                flask_socketio.request.sid = 'test_sid'
                
                # Call with valid data but finished game
                handle_join_game({'game_id': 'TEST', 'username': 'TestUser'})
                
                # Verify we emit game_ended event
                mock_emit.assert_called_with('game_ended', 
                                           {'message': 'This game has already ended.'})


if __name__ == '__main__':
    unittest.main()
