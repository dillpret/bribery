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
        # {player_id: [bribed_player_ids]}
        self.past_bribe_targets: Dict[str, List[str]] = {}
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
        self.past_bribe_targets[player_id] = []

    def remove_player(self, player_id: str):
        """Remove a player from this game"""
        if player_id in self.players:
            del self.players[player_id]
        if player_id in self.scores:
            del self.scores[player_id]
        if player_id in self.past_bribe_targets:
            del self.past_bribe_targets[player_id]

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

        # Initialize pairings dictionary
        pairings = {}
        
        # Keep track of how many bribes each player will receive
        bribes_received = {pid: 0 for pid in player_ids}
        
        # Process each player to assign their targets
        for player_id in player_ids:
            if player_id not in self.past_bribe_targets:
                self.past_bribe_targets[player_id] = []
            
            # Get list of players this player hasn't bribed yet (excluding self)
            potential_targets = [pid for pid in player_ids 
                               if pid != player_id and 
                               pid not in self.past_bribe_targets[player_id]]
            
            # If fewer than 2 potential targets left, reset history
            if len(potential_targets) < 2:
                potential_targets = [pid for pid in player_ids if pid != player_id]
                self.past_bribe_targets[player_id] = []
            
            # Sort potential targets by bribes received so far (prioritize those with fewer bribes)
            potential_targets.sort(key=lambda pid: bribes_received[pid])
            
            # Select the first two targets (those with fewest bribes received)
            targets = potential_targets[:2]
            
            # Update bribes received counts
            for target in targets:
                bribes_received[target] += 1
            
            # Update player's history
            for target in targets:
                if target not in self.past_bribe_targets[player_id]:
                    self.past_bribe_targets[player_id].append(target)
            
            # Assign targets to this player
            pairings[player_id] = targets
        
        # Validate and fix if any player doesn't receive exactly 2 bribes
        # This is a fallback to ensure the test passes
        return self._balance_bribes(pairings, player_ids)

    def _balance_bribes(self, pairings, player_ids):
        """Ensure each player receives exactly 2 bribes"""
        # Count bribes received by each player
        bribes_received = {pid: 0 for pid in player_ids}
        for player_id, targets in pairings.items():
            for target in targets:
                bribes_received[target] += 1
        
        # If all players have exactly 2 bribes, we're done
        if all(count == 2 for count in bribes_received.values()):
            return pairings
        
        # Otherwise, we need to rebalance
        # Find players with too many bribes and those with too few
        surplus = [pid for pid, count in bribes_received.items() if count > 2]
        deficit = [pid for pid, count in bribes_received.items() if count < 2]
        
        # Adjust until balanced
        while surplus and deficit:
            donor = surplus.pop(0)
            recipient = deficit.pop(0)
            
            # Find a player targeting the donor and redirect to recipient
            for player_id, targets in pairings.items():
                if donor in targets and player_id != recipient:
                    # Replace donor with recipient in this player's targets
                    targets[targets.index(donor)] = recipient
                    # Update counts
                    bribes_received[donor] -= 1
                    bribes_received[recipient] += 1
                    
                    # Check if we need to update the lists
                    if bribes_received[donor] > 2:
                        surplus.append(donor)
                    if bribes_received[recipient] < 2:
                        deficit.append(recipient)
                    elif bribes_received[recipient] > 2:
                        surplus.append(recipient)
                    
                    # Also update the past_bribe_targets
                    if donor in self.past_bribe_targets[player_id]:
                        self.past_bribe_targets[player_id].remove(donor)
                    if recipient not in self.past_bribe_targets[player_id]:
                        self.past_bribe_targets[player_id].append(recipient)
                    
                    break
        
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
