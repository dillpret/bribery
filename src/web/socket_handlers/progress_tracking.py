"""
Progress tracking for game rounds, tracking submissions and votes.
"""

import logging

logger = logging.getLogger(__name__)

# Will be set in __init__
socketio = None


def set_socketio(socketio_instance):
    """Set the socketio instance for this module"""
    global socketio
    socketio = socketio_instance


def emit_submission_progress(game):
    """Emit submission progress to all players"""
    global socketio
    if not socketio:
        from . import socketio as socketio_instance
        socketio = socketio_instance
        
    active_players = game.get_active_player_ids()
    total_active = len(active_players)
    
    # Count how many players have completed all their submissions
    completed_players = []
    pending_players = []
    
    for player_id in active_players:
        player_submissions = game.bribes[game.current_round].get(player_id, {})
        # Each player needs to submit 2 bribes
        if len(player_submissions) >= 2:
            completed_players.append(player_id)
        else:
            pending_players.append(player_id)
    
    completed_count = len(completed_players)
    
    # Generate progress message
    if completed_count == total_active:
        progress_message = "All players finished! Moving to voting..."
    elif len(pending_players) <= 2 and len(pending_players) > 0:
        # Show names when 2 or fewer players remaining
        pending_names = [game.players[pid]['username'] for pid in pending_players]
        if len(pending_names) == 1:
            progress_message = f"Waiting for {pending_names[0]}"
        else:
            progress_message = f"Waiting for {pending_names[0]} and {pending_names[1]}"
    else:
        progress_message = f"{completed_count}/{total_active} players finished"
    
    socketio.emit('submission_progress', {
        'completed': completed_count,
        'total': total_active,
        'message': progress_message
    }, room=game.game_id)


def emit_voting_progress(game):
    """Emit voting progress to all players"""
    global socketio
    if not socketio:
        from . import socketio as socketio_instance
        socketio = socketio_instance
        
    active_players = game.get_active_player_ids()
    total_active = len(active_players)
    
    # Count votes submitted
    votes_submitted = len(game.votes[game.current_round])
    remaining_voters = []
    
    for player_id in active_players:
        if player_id not in game.votes[game.current_round]:
            remaining_voters.append(player_id)
    
    # Generate progress message
    if votes_submitted == total_active:
        progress_message = "All votes submitted! Calculating results..."
    elif len(remaining_voters) <= 2 and len(remaining_voters) > 0:
        # Show names when 2 or fewer players remaining
        remaining_names = [game.players[pid]['username'] for pid in remaining_voters]
        if len(remaining_names) == 1:
            progress_message = f"Waiting for {remaining_names[0]}"
        else:
            progress_message = f"Waiting for {remaining_names[0]} and {remaining_names[1]}"
    else:
        progress_message = f"{votes_submitted}/{total_active} players voted"
    
    socketio.emit('voting_progress', {
        'completed': votes_submitted,
        'total': total_active,
        'message': progress_message
    }, room=game.game_id)
