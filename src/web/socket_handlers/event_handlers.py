"""
Socket.IO event handlers for the Bribery game.

This module contains the handlers for all Socket.IO events.
"""

import logging
import random
import string
import uuid

from flask import request
from flask_socketio import emit, join_room

from .game_flow import (
    check_all_submissions_complete,
    continue_or_end_game,
    emit_lobby_update,
    emit_midgame_joiner_state,
    end_submission_phase,
    end_voting_phase,
    game_manager,
    start_next_round,
    start_submission_phase,
)
from .progress_tracking import emit_voting_progress

logger = logging.getLogger(__name__)


def handle_create_game(data):
    """Handle game creation request"""
    # Input validation
    if not isinstance(data, dict):
        emit('error', {'message': 'Invalid request data'})
        return

    username = data.get('username')
    if not username or not isinstance(username, str) or not username.strip():
        emit('error', {'message': 'Username is required'})
        return

    # Generate 4-character game code (letters and digits)
    characters = string.ascii_uppercase + string.digits
    game_id = ''.join(random.choice(characters) for _ in range(4))
    
    # Ensure uniqueness (very unlikely collision with 4 chars, but check anyway)
    while game_manager.get_game(game_id) is not None:
        game_id = ''.join(random.choice(characters) for _ in range(4))
    
    player_id = str(uuid.uuid4())

    # Import here to avoid circular imports
    from game import Game, PlayerSession

    settings = {
        'rounds': data.get('rounds', 3),
        'submission_time': data.get('submission_time', 0),  # 0 means wait for all players
        'voting_time': data.get('voting_time', 0),  # 0 means wait for all players
        'results_time': data.get('results_time', 0),  # 0 means host controls next round
        'custom_prompts': data.get('custom_prompts', False)
    }

    game = Game(game_id, player_id, settings)
    game.add_player(player_id, username.strip())

    game_manager.add_game(game)
    game_manager.add_player_session(
        request.sid, PlayerSession(
            request.sid, player_id, game_id))

    join_room(game_id)

    emit('game_created', {
        'game_id': game_id,
        'player_id': player_id,
        'is_host': True
    })

    emit_lobby_update(game_id)


def handle_join_game(data):
    """Handle player joining a game"""
    # Input validation
    if not isinstance(data, dict):
        emit('error', {'message': 'Invalid request data'})
        return

    game_id = data.get('game_id')
    username = data.get('username')
    stored_player_id = data.get('player_id')  # From localStorage on page refresh

    if not game_id or not isinstance(game_id, str):
        emit('error', {'message': 'Game ID is required'})
        return

    if not username or not isinstance(username, str) or not username.strip():
        emit('error', {'message': 'Username is required'})
        return

    game_id = game_id.upper().strip()
    username = username.strip()

    game = game_manager.get_game(game_id)
    if not game:
        emit('error', {'message': 'Game not found'})
        return

    # Import here to avoid circular imports
    from game import PlayerSession

    # AUTHENTICATION FLOW: Server-side player identification
    # This implements a two-tier authentication strategy:
    # 1. Try to match by stored player ID (exact match, highest priority)
    # 2. Fall back to username matching (for device changes/direct access)
    # Check if player is rejoining (priority: stored player ID > username match)
    existing_player_id = None    # First, try to use stored player ID if provided (page refresh scenario)
    if stored_player_id and stored_player_id in game.players:
        existing_player_id = stored_player_id
        # Update username in case it changed
        game.players[existing_player_id]['username'] = username
    else:
        # Fallback to username matching (traditional rejoin)
        for pid, player in game.players.items():
            if player['username'] == username:
                existing_player_id = pid
                break

    if existing_player_id:
        # Player rejoining
        player_id = existing_player_id
        game.players[player_id]['connected'] = True
        game_manager.add_player_session(
            request.sid, PlayerSession(
                request.sid, player_id, game_id))
    else:
        # New player
        player_id = str(uuid.uuid4())
        game.add_player(player_id, username)
        game_manager.add_player_session(
            request.sid, PlayerSession(
                request.sid, player_id, game_id))

    join_room(game_id)

    emit('joined_game', {
        'game_id': game_id,
        'player_id': player_id,
        'username': username,  # Include username for client-side storage
        'is_host': player_id == game.host_id,
        'game_state': game.state
    })

    emit_lobby_update(game_id)

    # If game is in progress, send appropriate state for mid-game joiner
    if game.state != "lobby":
        emit_midgame_joiner_state(game, player_id)


def handle_start_game():
    """Handle game start request"""
    player_session = game_manager.get_player_session(request.sid)
    if not player_session:
        return

    game = game_manager.get_game(player_session.game_id)
    if not game:
        return

    if player_session.player_id != game.host_id:
        emit('error', {'message': 'Only the host can start the game'})
        return

    if not game.can_start_game():
        emit('error', {'message': 'Need at least 3 players to start'})
        return

    start_next_round(game)


def handle_select_prompt(data):
    """Handle player prompt selection in custom prompt mode"""
    player_session = game_manager.get_player_session(request.sid)
    if not player_session:
        return

    game = game_manager.get_game(player_session.game_id)
    if not game:
        return

    player_id = player_session.player_id

    if game.state != "prompt_selection":
        emit('error', {'message': 'Not in prompt selection phase'})
        return

    if not game.custom_prompts_enabled():
        emit('error', {'message': 'Custom prompts not enabled for this game'})
        return

    prompt = data.get('prompt', '').strip()
    if not prompt:
        emit('error', {'message': 'Prompt cannot be empty'})
        return

    # Initialize round data if needed
    if game.current_round not in game.player_prompts:
        game.player_prompts[game.current_round] = {}
    if game.current_round not in game.player_prompt_ready:
        game.player_prompt_ready[game.current_round] = {}

    # Store player's prompt choice
    game.player_prompts[game.current_round][player_id] = prompt
    game.player_prompt_ready[game.current_round][player_id] = True

    emit('prompt_selected', {'success': True})

    # Check if all players have selected prompts
    if game.all_players_prompt_ready(game.current_round):
        if game.round_timer:
            game.round_timer.cancel()
        start_submission_phase(game)


def handle_submit_bribe(data):
    """Handle bribe submission"""
    player_session = game_manager.get_player_session(request.sid)
    if not player_session:
        return

    game = game_manager.get_game(player_session.game_id)
    if not game:
        return

    player_id = player_session.player_id

    if game.state != "submission":
        emit('error', {'message': 'Not in submission phase'})
        return

    # Input validation
    if not isinstance(data, dict):
        emit('error', {'message': 'Invalid request data'})
        return

    target_id = data.get('target_id')
    submission = data.get('submission')

    if not target_id or not isinstance(target_id, str):
        emit('error', {'message': 'Target ID is required'})
        return

    if not submission or not isinstance(
            submission, str) or not submission.strip():
        emit('error', {'message': 'Submission is required'})
        return

    target_id = target_id.strip()
    submission = submission.strip()

    # Initialize player's bribes for this round if not exists
    if player_id not in game.bribes[game.current_round]:
        game.bribes[game.current_round][player_id] = {}

    game.bribes[game.current_round][player_id][target_id] = {
        'content': submission,
        'type': data.get('type', 'text')
    }

    emit('bribe_submitted', {'target_id': target_id})

    # Check if all submissions are in
    check_all_submissions_complete(game)


def handle_submit_vote(data):
    """Handle vote submission"""
    player_session = game_manager.get_player_session(request.sid)
    if not player_session:
        return

    game = game_manager.get_game(player_session.game_id)
    if not game:
        return

    player_id = player_session.player_id

    if game.state != "voting":
        emit('error', {'message': 'Not in voting phase'})
        return

    # Input validation
    if not isinstance(data, dict):
        emit('error', {'message': 'Invalid request data'})
        return

    bribe_id = data.get('bribe_id')
    if not bribe_id or not isinstance(bribe_id, str):
        emit('error', {'message': 'Bribe ID is required'})
        return

    game.votes[game.current_round][player_id] = bribe_id.strip()
    emit('vote_submitted')

    # Emit progress update
    emit_voting_progress(game)

    # Check if all votes are in
    if len(game.votes[game.current_round]) >= len(game.get_active_player_ids()):
        if game.round_timer:
            game.round_timer.cancel()
        end_voting_phase(game)


def handle_restart_game():
    """Handle game restart request"""
    player_session = game_manager.get_player_session(request.sid)
    if not player_session:
        return

    game = game_manager.get_game(player_session.game_id)
    if not game:
        return

    if player_session.player_id != game.host_id:
        emit('error', {'message': 'Only the host can restart the game'})
        return

    # Reset game state
    game.state = "lobby"
    game.current_round = 0
    game.bribes = {}
    game.votes = {}
    game.scores = {player_id: 0 for player_id in game.players}
    game.round_pairings = {}

    # Import to avoid circular imports
    from . import socketio
    socketio.emit('game_restarted', room=game.game_id)
    emit_lobby_update(game.game_id)


def handle_next_round():
    """Handle host advancing to the next round (when results_time is 0)"""
    player_session = game_manager.get_player_session(request.sid)
    if not player_session:
        return

    game = game_manager.get_game(player_session.game_id)
    if not game:
        return

    if player_session.player_id != game.host_id:
        emit('error', {'message': 'Only the host can advance to the next round'})
        return

    if game.state != "scoreboard":
        emit('error', {'message': 'Not in scoreboard phase'})
        return

    # Advance to next round or end game
    continue_or_end_game(game)


def handle_return_to_lobby():
    """Handle returning to lobby after game completion"""
    player_session = game_manager.get_player_session(request.sid)
    if not player_session:
        return

    game = game_manager.get_game(player_session.game_id)
    if not game:
        return

    if player_session.player_id != game.host_id:
        emit('error', {'message': 'Only the host can return to lobby'})
        return

    # Reset game state to lobby but keep players and settings
    game.state = "lobby"
    game.current_round = 0
    game.bribes = {}
    game.votes = {}
    game.scores = {pid: 0 for pid in game.players}
    game.current_prompt = ""
    game.round_pairings = {}

    # Keep custom prompts setting and other game settings unchanged
    # Keep all players connected

    if game.round_timer:
        game.round_timer.cancel()
        game.round_timer = None

    # Import to avoid circular imports
    from . import socketio
    socketio.emit('returned_to_lobby', room=game.game_id)
    emit_lobby_update(game.game_id)


def handle_disconnect():
    """Handle player disconnection"""
    player_session = game_manager.get_player_session(request.sid)
    if player_session:
        game = game_manager.get_game(player_session.game_id)

        if game and player_session.player_id in game.players:
            game.players[player_session.player_id]['connected'] = False
            emit_lobby_update(player_session.game_id)

        game_manager.remove_player_session(request.sid)


def handle_get_game_state(data):
    """Handle request for current game state"""
    # Input validation
    if not isinstance(data, dict):
        emit('error', {'message': 'Invalid request data'})
        return

    game_id = data.get('game_id')
    if not game_id or not isinstance(game_id, str):
        emit('error', {'message': 'Game ID is required'})
        return
    
    game = game_manager.get_game(game_id)
    if not game:
        emit('error', {'message': 'Game not found'})
        return
    
    # Return current game state
    state_data = {
        'game_id': game_id,
        'state': game.state,
        'round': game.current_round,
        'total_rounds': game.total_rounds,
        'players_count': len(game.players)
    }
    
    emit('game_state', state_data)
