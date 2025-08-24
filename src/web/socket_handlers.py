"""
Socket.IO event handlers for the Bribery game

This module is maintained for backward compatibility.
The actual handlers have been moved to the socket_handlers package.
"""

import logging

# Re-export all public interfaces from the package
from .socket_handlers import (
    register_socket_handlers,
    get_game_manager,
    emit_submission_progress,
    emit_voting_progress,
)

# Re-export the public interface for backward compatibility
__all__ = [
    "register_socket_handlers",
    "get_game_manager",
    "emit_submission_progress",
    "emit_voting_progress",
]

logger = logging.getLogger(__name__)
