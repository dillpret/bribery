"""
Socket.IO event handlers for the Bribery game

This package contains all Socket.IO event handlers for the multiplayer game.
"""

import logging

logger = logging.getLogger(__name__)

# GameManager and SocketIO instance - will be set when handlers are registered
game_manager = None
socketio = None

# Export the public interface
__all__ = [
    'register_socket_handlers',
    'get_game_manager',
    'emit_submission_progress',
    'emit_voting_progress',
]


def register_socket_handlers(socketio_instance):
    """Register all Socket.IO event handlers"""
    # Set global instances that will be used by all modules in the package
    global socketio
    socketio = socketio_instance
    
    # Initialize module references after socketio is set
    from .progress_tracking import set_socketio as set_progress_socketio
    set_progress_socketio(socketio_instance)
    
    # Initialize the game manager
    from .game_flow import initialize_game_manager
    initialize_game_manager(socketio_instance)

    # Import event handlers
    from .event_handlers import (
        handle_create_game,
        handle_disconnect,
        handle_join_game,
        handle_next_round,
        handle_restart_game,
        handle_return_to_lobby,
        handle_select_prompt,
        handle_start_game,
        handle_submit_bribe,
        handle_submit_vote,
        handle_get_game_state,
    )

    # Register all handlers
    socketio.on_event('create_game', handle_create_game)
    socketio.on_event('join_game', handle_join_game)
    socketio.on_event('start_game', handle_start_game)
    socketio.on_event('select_prompt', handle_select_prompt)
    socketio.on_event('submit_bribe', handle_submit_bribe)
    socketio.on_event('submit_vote', handle_submit_vote)
    socketio.on_event('restart_game', handle_restart_game)
    socketio.on_event('return_to_lobby', handle_return_to_lobby)
    socketio.on_event('next_round', handle_next_round)
    socketio.on_event('disconnect', handle_disconnect)
    socketio.on_event('get_game_state', handle_get_game_state)


# Import these after the function definition to avoid circular imports
from .game_flow import get_game_manager
from .progress_tracking import emit_submission_progress, emit_voting_progress
