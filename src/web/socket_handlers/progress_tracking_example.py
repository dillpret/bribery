# Sample code for backend socket handlers to support the enhanced progress tracking
# This is an example implementation for the server-side to generate the progress data
# in the format expected by our new frontend components

import json
from flask_socketio import emit


def get_pending_players_by_phase(game, phase):
    """Get list of players who haven't submitted for the current phase"""
    pending_players = []
    
    if phase == "prompt_selection":
        # Check which players haven't selected prompts
        for player_id, player in game.players.items():
            if not player.has_selected_prompt:
                pending_players.append(player.username)
                
    elif phase == "submission":
        # Check which players haven't submitted bribes
        for player_id, player in game.players.items():
            if not player.has_submitted_all_bribes:
                pending_players.append(player.username)
                
    elif phase == "voting":
        # Check which players haven't voted
        for player_id, player in game.players.items():
            if not player.has_voted:
                pending_players.append(player.username)
                
    return pending_players


def get_player_statuses_by_phase(game, phase):
    """Get a dictionary mapping player IDs to their submission status for current phase"""
    player_statuses = {}
    
    if phase == "prompt_selection":
        # Track prompt selection status
        for player_id, player in game.players.items():
            player_statuses[player_id] = player.has_selected_prompt
                
    elif phase == "submission":
        # Track bribe submission status
        for player_id, player in game.players.items():
            player_statuses[player_id] = player.has_submitted_all_bribes
                
    elif phase == "voting":
        # Track voting status
        for player_id, player in game.players.items():
            player_statuses[player_id] = player.has_voted
                
    return player_statuses


def send_progress_update(game, phase):
    """Send progress update for the specified phase with enhanced information"""
    if phase == "prompt_selection":
        # Count players who have selected prompts
        completed = sum(1 for player in game.players.values() if player.has_selected_prompt)
        total = len(game.players)
        
        # Get list of pending players
        pending_players = get_pending_players_by_phase(game, phase)
        
        # Get status mapping for each player
        player_statuses = get_player_statuses_by_phase(game, phase)
        
        # Send detailed progress update
        emit('prompt_selection_progress', {
            'completed': completed,
            'total': total,
            'pendingPlayers': pending_players,
            'playerStatuses': player_statuses
        }, room=game.id)
        
    elif phase == "submission":
        # Count players who have submitted all bribes
        completed = sum(1 for player in game.players.values() if player.has_submitted_all_bribes)
        total = len(game.players)
        
        # Get list of pending players
        pending_players = get_pending_players_by_phase(game, phase)
        
        # Get status mapping for each player
        player_statuses = get_player_statuses_by_phase(game, phase)
        
        # Send detailed progress update
        emit('submission_progress', {
            'completed': completed,
            'total': total,
            'pendingPlayers': pending_players,
            'playerStatuses': player_statuses
        }, room=game.id)
        
    elif phase == "voting":
        # Count players who have voted
        completed = sum(1 for player in game.players.values() if player.has_voted)
        total = len(game.players)
        
        # Get list of pending players
        pending_players = get_pending_players_by_phase(game, phase)
        
        # Get status mapping for each player
        player_statuses = get_player_statuses_by_phase(game, phase)
        
        # Send detailed progress update
        emit('voting_progress', {
            'completed': completed,
            'total': total,
            'pendingPlayers': pending_players,
            'playerStatuses': player_statuses
        }, room=game.id)
