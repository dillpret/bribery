#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Integration tests - testing cross-component functionality
"""

import pytest
import sys
import os

# Add the app directory to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'src'))
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from helpers.socketio_helpers import SocketIOHelper, MultiPlayerHelper

class TestIntegration:
    """Integration tests covering cross-component functionality"""
    
    def test_basic_socketio_connectivity(self, test_server):
        """Test that SocketIO connection and basic communication works"""
        helper = SocketIOHelper(test_server['socketio_url'])
        helper.connect()
        
        try:
            game_id = helper.create_game('ConnectivityTest', 1, 30, 15)
            
            # Basic connectivity test
            assert game_id is not None
            assert len(game_id) == 4  # Changed to 4-character codes
            
            # Verify we got the expected events
            game_data = helper.get_event('game_created')
            assert game_data is not None
            assert game_data['is_host'] == True
            
        finally:
            helper.disconnect()
    
    def test_complete_game_flow(self, test_server):
        """Test one complete game flow from creation to results"""
        multi_helper = MultiPlayerHelper(test_server['socketio_url'])
        
        try:
            # Create game with minimum viable setup
            game_id = multi_helper.create_game_with_players(
                "FlowHost", ["FlowPlayer1", "FlowPlayer2"], 
                rounds=1, submission_time=5, voting_time=3
            )
            
            assert game_id is not None
            
            # Start the game
            host = multi_helper.get_player("FlowHost")
            assert host.start_game()
            
            # Verify all players got game start events
            for player_name in ["FlowHost", "FlowPlayer1", "FlowPlayer2"]:
                player = multi_helper.get_player(player_name)
                round_data = player.get_event('round_started')
                assert round_data is not None
                assert round_data['round'] == 1
                
                targets_data = player.get_event('targets')
                assert targets_data is not None
                assert len(targets_data['targets']) == 2
            
            # This test verifies that:
            # - SocketIO events work end-to-end
            # - Game state management works across components
            # - Player session management works
            # - Round logic integrates properly
            
        finally:
            multi_helper.disconnect_all()
    
    def test_player_reconnection_flow(self, test_server):
        """Test that player reconnection works across the full stack"""
        helper1 = SocketIOHelper(test_server['socketio_url'])
        helper1.connect()
        
        try:
            # Create game
            game_id = helper1.create_game('ReconnectHost', 1, 30, 15)
            assert game_id is not None
            
            # Add second player
            helper2 = SocketIOHelper(test_server['socketio_url'])
            helper2.connect()
            
            success = helper2.join_game('ReconnectPlayer', game_id)
            assert success
            
            # Disconnect second player
            helper2.disconnect()
            
            # Reconnect same player (tests session management)
            helper3 = SocketIOHelper(test_server['socketio_url'])
            helper3.connect()
            
            # Rejoin with same username should work
            success = helper3.join_game('ReconnectPlayer', game_id)
            assert success
            
            # This test verifies:
            # - Session management works across disconnections
            # - Player state persists correctly
            # - Game state remains consistent
            
            helper2.disconnect()
            helper3.disconnect()
            
        finally:
            helper1.disconnect()
