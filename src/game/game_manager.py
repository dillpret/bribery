"""
GameManager class for managing multiple concurrent games and player sessions
"""

import logging
import threading
from typing import Dict, Optional

from .game import Game
from .player_session import PlayerSession

logger = logging.getLogger(__name__)


class GameManager:
    """Manages multiple concurrent games and player sessions"""

    def __init__(self):
        self.games: Dict[str, Game] = {}  # game_id -> Game
        # socket_id -> PlayerSession
        self.player_sessions: Dict[str, PlayerSession] = {}
        self.player_to_game: Dict[str, str] = {}  # player_id -> game_id
        self._lock = threading.Lock()

    def create_game(
            self,
            game_id: str,
            host_player_id: str,
            settings: dict) -> Game:
        """Create a new game instance"""
        with self._lock:
            if game_id in self.games:
                raise ValueError(f"Game {game_id} already exists")

            game = Game(game_id, host_player_id, settings)
            self.games[game_id] = game
            self.player_to_game[host_player_id] = game_id

            logger.info(f"Created game {game_id} with host {host_player_id}")
            return game

    def get_game(self, game_id: str) -> Optional[Game]:
        """Get a game by ID"""
        return self.games.get(game_id)

    def add_game(self, game: Game):
        """Add a game instance to the manager"""
        with self._lock:
            self.games[game.game_id] = game
            self.player_to_game[game.host_id] = game.game_id
            logger.info(f"Added game {game.game_id} to manager")

    def add_player_session(self, socket_id: str, session: PlayerSession):
        """Add a player session"""
        self.player_sessions[socket_id] = session
        logger.info(
            f"Added player session {session.player_id} for socket {socket_id}")

    def remove_player_session(self, socket_id: str):
        """Remove a player session"""
        if socket_id in self.player_sessions:
            session = self.player_sessions[socket_id]
            del self.player_sessions[socket_id]
            logger.info(
                f"Removed player session {session.player_id} for socket {socket_id}")

    def get_player_game(self, player_id: str) -> Optional[Game]:
        """Get the game a player is in"""
        game_id = self.player_to_game.get(player_id)
        return self.games.get(game_id) if game_id else None

    def join_game(self, game_id: str, player_id: str, username: str) -> bool:
        """Add a player to a game"""
        with self._lock:
            game = self.games.get(game_id)
            if not game:
                return False

            # Check if player is rejoining
            if player_id in game.players:
                game.players[player_id]['connected'] = True
                logger.info(
                    f"Player {username} ({player_id}) reconnected to game {game_id}")
            else:
                game.add_player(player_id, username)
                logger.info(
                    f"Player {username} ({player_id}) joined game {game_id}")

            self.player_to_game[player_id] = game_id
            return True

    def register_player_session(
            self,
            socket_id: str,
            player_id: str,
            game_id: str):
        """Register a player's socket session"""
        self.player_sessions[socket_id] = PlayerSession(
            socket_id, player_id, game_id)

    def get_player_session(self, socket_id: str) -> Optional[PlayerSession]:
        """Get player session by socket ID"""
        return self.player_sessions.get(socket_id)

    def disconnect_player(self, socket_id: str):
        """Handle player disconnection"""
        session = self.player_sessions.get(socket_id)
        if not session:
            return

        with self._lock:
            game = self.games.get(session.game_id)
            if game and session.player_id in game.players:
                game.players[session.player_id]['connected'] = False
                logger.info(
                    f"Player {session.player_id} disconnected from game {session.game_id}")

            del self.player_sessions[socket_id]

    def cleanup_empty_games(self):
        """Remove games with no connected players"""
        with self._lock:
            games_to_remove = []
            for game_id, game in self.games.items():
                if game.get_connected_player_count() == 0:
                    games_to_remove.append(game_id)

            for game_id in games_to_remove:
                game = self.games[game_id]
                game.cleanup()  # Clean up game resources
                del self.games[game_id]
                logger.info(f"Cleaned up empty game {game_id}")

                # Clean up player mappings
                players_to_remove = [
                    pid for pid, gid in self.player_to_game.items() if gid == game_id]
                for player_id in players_to_remove:
                    del self.player_to_game[player_id]
