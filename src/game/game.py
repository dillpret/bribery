"""
Game class representing a single game instance with isolated state
"""

import random
import threading
import time
from typing import Dict, List, Optional


class Game:
    """Represents a single game instance with isolated state"""

    def __init__(self, game_id: str, host_id: str, settings: dict):
        self.game_id = game_id
        self.host_id = host_id
        self.players: Dict[str, dict] = {}
        self.state = "lobby"  # lobby, prompt_selection, submission, voting, scoreboard, finished
        self.current_round = 0
        self.settings = settings
        self.round_timer: Optional[threading.Timer] = None
        # {round: {player_id: {target_id: submission}}}
        self.bribes: Dict[int, Dict[str, Dict[str, dict]]] = {}
        # {round: {player_id: chosen_bribe_id}}
        self.votes: Dict[int, Dict[str, str]] = {}
        self.scores: Dict[str, int] = {}  # {player_id: total_score}
        self.current_prompt = ""
        # {round: {player_id: [target1, target2]}}
        self.round_pairings: Dict[int, Dict[str, List[str]]] = {}
        # {round: {player_id: chosen_prompt}}
        self.player_prompts: Dict[int, Dict[str, str]] = {}
        # {round: {player_id: ready_status}}
        self.player_prompt_ready: Dict[int, Dict[str, bool]] = {}
        self.created_at = time.time()

    def add_player(self, player_id: str, username: str):
        """Add a player to this game"""
        self.players[player_id] = {
            'username': username,
            'connected': True,
            'ready': False,
            'active_in_round': self.state == "lobby"  # Only active if joining during lobby
        }
        self.scores[player_id] = 0

    def remove_player(self, player_id: str):
        """Remove a player from this game"""
        if player_id in self.players:
            del self.players[player_id]
        if player_id in self.scores:
            del self.scores[player_id]

    def get_connected_player_count(self) -> int:
        """Get count of connected players"""
        return len([p for p in self.players.values() if p['connected']])

    def get_active_player_count(self) -> int:
        """Get count of players active in current round"""
        return len([p for p in self.players.values() if p['connected'] and p.get('active_in_round', True)])

    def get_active_player_ids(self) -> list:
        """Get list of player IDs active in current round"""
        return [pid for pid, player in self.players.items()
                if player['connected'] and player.get('active_in_round', True)]

    def get_player_count(self) -> int:
        """Get total player count (including disconnected)"""
        return len(self.players)

    def can_start_game(self) -> bool:
        """Check if game can be started"""
        return self.get_active_player_count() >= 3 and self.state == "lobby"

    def generate_round_pairings(self):
        """Generate pairings so each player bribes exactly 2 others and receives bribes from exactly 2 others"""
        # Only include active players in pairings
        player_ids = self.get_active_player_ids()
        n = len(player_ids)

        if n < 3:
            return {}

        # Shuffle players for this round
        shuffled = player_ids.copy()
        random.shuffle(shuffled)

        pairings = {}

        # Simple pairing strategy: each player bribes the next 2 players in the
        # shuffled list
        for i, player_id in enumerate(shuffled):
            target1 = shuffled[(i + 1) % n]
            target2 = shuffled[(i + 2) % n]

            # Make sure player doesn't bribe themselves
            if target1 == player_id:
                target1 = shuffled[(i + 3) %
                                   n] if n > 3 else shuffled[(i + 1) %
                                                             n]
            if target2 == player_id:
                target2 = shuffled[(i + 3) %
                                   n] if n > 3 else shuffled[(i + 1) %
                                                             n]

            pairings[player_id] = [target1, target2]

        return pairings

    def custom_prompts_enabled(self) -> bool:
        """Check if custom prompts are enabled for this game"""
        return self.settings.get('custom_prompts', False)

    def all_players_prompt_ready(self, round_num: int) -> bool:
        """Check if all active players have selected their prompts for the round"""
        if not self.custom_prompts_enabled():
            return True

        if round_num not in self.player_prompt_ready:
            return False

        active_players = self.get_active_player_ids()
        ready_players = [
            pid for pid,
            ready in self.player_prompt_ready[round_num].items() if ready]

        return len(ready_players) >= len(active_players)

    def get_prompt_for_target(
            self,
            round_num: int,
            target_player_id: str) -> str:
        """Get the prompt for bribing a specific target player"""
        if not self.custom_prompts_enabled():
            return self.current_prompt

        # Get the custom prompt for this target player
        custom_prompt = self.player_prompts.get(
            round_num, {}).get(
            target_player_id, "")

        # Fall back to default prompt if custom prompt is empty or missing
        if not custom_prompt or not custom_prompt.strip():
            return self.current_prompt

        return custom_prompt

    def activate_waiting_players(self):
        """Activate players who joined mid-game for the next round"""
        for player_id, player in self.players.items():
            if player['connected'] and not player.get('active_in_round', True):
                player['active_in_round'] = True

    def cleanup(self):
        """Clean up game resources"""
        if self.round_timer:
            self.round_timer.cancel()
            self.round_timer = None

    def __repr__(self):
        return f"Game(id='{self.game_id}', state='{self.state}', players={len(self.players)}, round={self.current_round})"
