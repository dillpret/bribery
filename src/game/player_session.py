"""
PlayerSession class for managing individual player socket connections
"""

import time


class PlayerSession:
    """Represents a player's socket session"""

    def __init__(self, socket_id: str, player_id: str, game_id: str):
        self.socket_id = socket_id
        self.player_id = player_id
        self.game_id = game_id
        self.connected_at = time.time()

    def __repr__(self):
        return f"PlayerSession(socket_id='{self.socket_id}', player_id='{self.player_id}', game_id='{self.game_id}')"
