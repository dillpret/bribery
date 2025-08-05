#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Socket.IO helper functions for integration tests
"""

import socketio
import time
from typing import Dict, List, Any, Optional

class SocketIOHelper:
    """Helper class for Socket.IO testing"""
    
    def __init__(self, server_url: str):
        self.server_url = server_url
        self.client = None
        self.events = {}
        
    def connect(self):
        """Connect to the Socket.IO server with retries"""
        self.client = socketio.Client(
            reconnection=False,  # Disable auto-reconnection in tests
            logger=False,        # Reduce logging overhead
            engineio_logger=False
        )
        self._setup_event_handlers()
        
        # Connect with retry logic
        max_retries = 3
        for attempt in range(max_retries):
            try:
                self.client.connect(self.server_url, wait_timeout=3)
                return self.client
            except Exception as e:
                if attempt == max_retries - 1:
                    raise Exception(f"Failed to connect after {max_retries} attempts: {e}")
                time.sleep(0.2)
        
        return self.client
    
    def disconnect(self):
        """Disconnect from the Socket.IO server"""
        if self.client and self.client.connected:
            self.client.disconnect()
    
    def _setup_event_handlers(self):
        """Set up event handlers to capture responses"""
        
        @self.client.event
        def game_created(data):
            self.events['game_created'] = data
        
        @self.client.event
        def lobby_update(data):
            self.events.setdefault('lobby_updates', []).append(data)
            self.events['lobby_update'] = data  # Keep latest
        
        @self.client.event
        def joined_game(data):
            self.events['joined_game'] = data
        
        @self.client.event
        def round_started(data):
            self.events['round_started'] = data
        
        @self.client.event
        def your_targets(data):
            self.events['targets'] = data
        
        @self.client.event
        def voting_phase(data):
            self.events['voting_phase'] = data
        
        @self.client.event
        def round_results(data):
            self.events['round_results'] = data
        
        @self.client.event
        def bribe_submitted(data):
            self.events.setdefault('bribes_submitted', []).append(data)
        
        @self.client.event
        def error(data):
            self.events.setdefault('errors', []).append(data)
            self.events['error'] = data  # Keep latest
    
    def create_game(self, username: str = "TestHost", rounds: int = 3, 
                   submission_time: int = 60, voting_time: int = 30) -> Optional[str]:
        """Create a game and return the game ID"""
        import random
        import time as time_module
        
        # Add randomness and timestamp to username to ensure uniqueness across concurrent tests
        unique_suffix = f"_{int(time_module.time() * 1000) % 100000}_{random.randint(1000, 9999)}"
        unique_username = f"{username}{unique_suffix}"
        
        self.client.emit('create_game', {
            'username': unique_username,
            'rounds': rounds,
            'submission_time': submission_time,
            'voting_time': voting_time
        })
        
        # Wait for game creation with shorter timeout
        max_wait = 2  # Reduced from 3
        wait_count = 0
        while wait_count < max_wait and 'game_created' not in self.events:
            time.sleep(0.05)  # Much faster polling
            wait_count += 1
        
        if 'game_created' in self.events:
            return self.events['game_created']['game_id']
        return None
    
    def join_game(self, username: str, game_id: str) -> bool:
        """Join a game"""
        import random
        import time as time_module
        
        # Add randomness to username to ensure uniqueness
        unique_suffix = f"_{int(time_module.time() * 1000) % 100000}_{random.randint(100, 999)}"
        unique_username = f"{username}{unique_suffix}"
        
        self.client.emit('join_game', {
            'username': unique_username,
            'game_id': game_id
        })
        
        # Wait for join confirmation with shorter timeout
        max_wait = 2  # Reduced from 3
        wait_count = 0
        while wait_count < max_wait and 'joined_game' not in self.events:
            time.sleep(0.05)  # Much faster polling
            wait_count += 1
        
        return 'joined_game' in self.events
    
    def start_game(self) -> bool:
        """Start the game"""
        self.client.emit('start_game')
        
        # Wait for round to start with better debugging
        max_wait = 30  # 30 iterations * 0.1s = 3 seconds max
        wait_count = 0
        while wait_count < max_wait:
            if 'round_started' in self.events:
                return True
            if 'error' in self.events:
                print(f"Error during game start: {self.events['error']}")
                return False
            time.sleep(0.1)  # Faster polling
            wait_count += 1
        
        print(f"Game start timed out. Events received: {list(self.events.keys())}")
        return False
    
    def submit_bribe(self, target_id: str, submission: str, bribe_type: str = 'text') -> bool:
        """Submit a bribe"""
        self.client.emit('submit_bribe', {
            'target_id': target_id,
            'submission': submission,
            'type': bribe_type
        })
        
        # Brief wait for submission
        time.sleep(0.1)  # Reduced from 0.5
        return True
    
    def submit_vote(self, bribe_id: str) -> bool:
        """Submit a vote"""
        self.client.emit('submit_vote', {'bribe_id': bribe_id})
        time.sleep(0.1)  # Reduced from 0.5
        return True
    
    def wait_for_event(self, event_name: str, timeout: float = 2.0) -> bool:
        """Wait for a specific event to occur with optimized timing"""
        wait_count = 0
        max_wait = int(timeout / 0.05)  # Check every 50ms for faster response
        
        while wait_count < max_wait and event_name not in self.events:
            time.sleep(0.05)  # Much shorter sleep
            wait_count += 1
        
        return event_name in self.events
    
    def get_event(self, event_name: str, default=None):
        """Get the data for a specific event"""
        return self.events.get(event_name, default)
    
    def clear_events(self):
        """Clear all captured events"""
        self.events.clear()


class MultiPlayerHelper:
    """Helper for managing multiple Socket.IO clients in tests"""
    
    def __init__(self, server_url: str):
        self.server_url = server_url
        self.clients: Dict[str, SocketIOHelper] = {}
    
    def add_player(self, name: str) -> SocketIOHelper:
        """Add a new player client"""
        helper = SocketIOHelper(self.server_url)
        helper.connect()
        self.clients[name] = helper
        return helper
    
    def get_player(self, name: str) -> SocketIOHelper:
        """Get a player client by name"""
        return self.clients.get(name)
    
    def disconnect_all(self):
        """Disconnect all player clients"""
        for helper in self.clients.values():
            helper.disconnect()
        self.clients.clear()
    
    def create_game_with_players(self, host_name: str = "Host", 
                                player_names: List[str] = None, 
                                rounds: int = 1, 
                                submission_time: int = 15, 
                                voting_time: int = 10) -> Optional[str]:
        """Create a game and add multiple players"""
        if player_names is None:
            player_names = ["Player1", "Player2"]
        
        # Add host
        host = self.add_player(host_name)
        game_id = host.create_game(host_name, rounds, submission_time, voting_time)
        
        if not game_id:
            return None
        
        # Add other players with better synchronization
        for player_name in player_names:
            player = self.add_player(player_name)
            if not player.join_game(player_name, game_id):
                print(f"Failed to join player: {player_name}")
                return None
            
            # Wait for lobby update to confirm join
            time.sleep(0.1)  # Reduced from 0.3
            if 'lobby_update' not in player.events and 'lobby_updates' not in player.events:
                print(f"Player {player_name} didn't receive lobby update")
        
        # Give a moment for all players to be fully synchronized
        time.sleep(0.2)  # Reduced from 0.5
        print(f"Created game {game_id} with host {host_name} and players {player_names}")
        
        return game_id
    
    def submit_bribes_for_all_players(self):
        """Submit bribes for all players"""
        for name, helper in self.clients.items():
            targets = helper.get_event('targets')
            if targets and 'target_ids' in targets:
                for i, target_id in enumerate(targets['target_ids']):
                    bribe_text = f"Bribe from {name} to target {i+1}"
                    helper.submit_bribe(target_id, bribe_text)
    
    def vote_for_all_players(self):
        """Submit votes for all players"""
        for name, helper in self.clients.items():
            voting_data = helper.get_event('voting_phase')
            if voting_data and 'bribes' in voting_data and voting_data['bribes']:
                # Vote for the first bribe
                first_bribe_id = voting_data['bribes'][0]['id']
                helper.submit_vote(first_bribe_id)
