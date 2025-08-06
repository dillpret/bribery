"""
Socket.IO event handlers for the Bribery game
"""

import logging
import random
import string
import threading
import uuid

from flask import request
from flask_socketio import emit, join_room

from game import Game, GameManager, PlayerSession

from .utils import get_player_room, load_prompts

logger = logging.getLogger(__name__)

# We'll need to get the game manager instance
# This will be set when the handlers are registered
game_manager = None
socketio = None


def register_socket_handlers(socketio_instance):
    """Register all Socket.IO event handlers"""
    global socketio, game_manager
    socketio = socketio_instance

    # Import the game manager - we'll need to refactor this
    # For now, we'll create a new instance
    game_manager = GameManager()

    # Register all handlers
    socketio.on_event('create_game', handle_create_game)
    socketio.on_event('join_game', handle_join_game)
    socketio.on_event('start_game', handle_start_game)
    socketio.on_event('select_prompt', handle_select_prompt)
    socketio.on_event('submit_bribe', handle_submit_bribe)
    socketio.on_event('submit_vote', handle_submit_vote)
    socketio.on_event('restart_game', handle_restart_game)
    socketio.on_event('return_to_lobby', handle_return_to_lobby)
    socketio.on_event('disconnect', handle_disconnect)


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

    settings = {
        'rounds': data.get('rounds', 3),
        'submission_time': data.get('submission_time', 60),
        'voting_time': data.get('voting_time', 30),
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
    game.scores = {pid: 0 for pid in game.players}
    game.current_prompt = ""
    game.round_pairings = {}

    if game.round_timer:
        game.round_timer.cancel()
        game.round_timer = None

    socketio.emit('game_restarted', room=game.game_id)
    emit_lobby_update(game.game_id)


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


# Game flow functions
def start_next_round(game):
    """Start the next round of the game"""
    game.current_round += 1

    # Activate any players who joined mid-game and were waiting
    game.activate_waiting_players()

    # Generate new pairings for this round
    game.round_pairings[game.current_round] = game.generate_round_pairings()

    # Initialize bribes and votes for this round
    game.bribes[game.current_round] = {}
    game.votes[game.current_round] = {}

    if game.custom_prompts_enabled():
        # Start prompt selection phase
        game.state = "prompt_selection"

        # Initialize prompt selection data
        game.player_prompts[game.current_round] = {}
        game.player_prompt_ready[game.current_round] = {}

        # Load available prompts
        prompts = load_prompts()

        # Emit prompt selection to all players
        socketio.emit('prompt_selection_started', {
            'round': game.current_round,
            'total_rounds': game.settings['rounds'],
            'available_prompts': prompts,
            'time_limit': 30  # 30 seconds to select prompts
        }, room=game.game_id)

        # Start prompt selection timer
        game.round_timer = threading.Timer(30, start_submission_phase, [game])
        game.round_timer.start()
    else:
        # Skip directly to submission phase with shared prompt
        start_submission_phase(game)


def start_submission_phase(game):
    """Start the submission phase"""
    game.state = "submission"

    # If not using custom prompts, select a random shared prompt
    if not game.custom_prompts_enabled():
        prompts = load_prompts()
        game.current_prompt = random.choice(prompts)

    # Emit round start to all players
    socketio.emit('round_started', {
        'round': game.current_round,
        'total_rounds': game.settings['rounds'],
        'prompt': game.current_prompt if not game.custom_prompts_enabled() else None,
        'custom_prompts_enabled': game.custom_prompts_enabled(),
        'time_limit': game.settings['submission_time']
    }, room=game.game_id)

    # Send individual pairings to each player with their specific prompts
    for player_id, targets in game.round_pairings[game.current_round].items():
        target_data = []
        for target_id in targets:
            target_prompt = game.get_prompt_for_target(
                game.current_round, target_id)
            target_data.append({
                'id': target_id,
                'name': game.players[target_id]['username'],
                'prompt': target_prompt
            })

        socketio.emit('your_targets', {
            'targets': target_data
        }, room=get_player_room(game_manager, game.game_id, player_id))

    # Start submission timer
    game.round_timer = threading.Timer(
        game.settings['submission_time'],
        end_submission_phase,
        [game])
    game.round_timer.start()
    
    # Emit initial submission progress
    emit_submission_progress(game)


def check_all_submissions_complete(game):
    """Check if all players have submitted all their bribes"""
    expected_submissions = len(game.get_active_player_ids()) * \
        2  # Each active player submits 2 bribes
    actual_submissions = sum(len(bribes)
                             for bribes in game.bribes[game.current_round].values())

    # Emit progress update
    emit_submission_progress(game)

    if actual_submissions >= expected_submissions:
        if game.round_timer:
            game.round_timer.cancel()
        end_submission_phase(game)


def emit_submission_progress(game):
    """Emit submission progress to all players"""
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


def end_submission_phase(game):
    """End the submission phase and start voting"""
    game.state = "voting"

    # Send voting options to each active player
    for player_id in game.get_active_player_ids():
        bribes_for_player = []

        # Find all bribes submitted TO this player, but exclude their own submissions
        for submitter_id, submissions in game.bribes[game.current_round].items():
            # Skip bribes submitted by the voting player themselves
            if submitter_id == player_id:
                continue

            for target_id, bribe in submissions.items():
                if target_id == player_id:
                    bribes_for_player.append({
                        'id': f"{submitter_id}_{target_id}",
                        'content': bribe['content'],
                        'type': bribe['type']
                    })

        socketio.emit('voting_phase', {
            'bribes': bribes_for_player,
            'time_limit': game.settings['voting_time']
        }, room=get_player_room(game_manager, game.game_id, player_id))

    # Start voting timer
    game.round_timer = threading.Timer(
        game.settings['voting_time'], end_voting_phase, [game])
    game.round_timer.start()
    
    # Emit initial voting progress
    emit_voting_progress(game)


def end_voting_phase(game):
    """End the voting phase and show results"""
    game.state = "scoreboard"

    # Calculate scores for this round
    round_scores = {}
    vote_results = []

    for voter_id, bribe_id in game.votes[game.current_round].items():
        # Parse bribe_id to get submitter
        submitter_id = bribe_id.split('_')[0]

        if submitter_id not in round_scores:
            round_scores[submitter_id] = 0
        round_scores[submitter_id] += 1

        vote_results.append({
            'voter': game.players[voter_id]['username'],
            'winner': game.players[submitter_id]['username']
        })

    # Update total scores
    for player_id, points in round_scores.items():
        game.scores[player_id] += points

    # Prepare scoreboard data
    scoreboard = []
    for player_id, total_score in game.scores.items():
        scoreboard.append({
            'username': game.players[player_id]['username'],
            'round_score': round_scores.get(player_id, 0),
            'total_score': total_score
        })

    scoreboard.sort(key=lambda x: x['total_score'], reverse=True)

    socketio.emit('round_results', {
        'round': game.current_round,
        'vote_results': vote_results,
        'scoreboard': scoreboard
    }, room=game.game_id)

    # Wait a bit then continue to next round or end game
    threading.Timer(5.0, continue_or_end_game, [game]).start()


def continue_or_end_game(game):
    """Continue to next round or end the game"""
    if game.current_round >= game.settings['rounds']:
        # Game is over
        end_game(game)
    else:
        # Start next round
        start_next_round(game)


def end_game(game):
    """End the game and show final results"""
    game.state = "finished"

    # Final scoreboard
    final_scoreboard = []
    for player_id, total_score in game.scores.items():
        final_scoreboard.append({
            'username': game.players[player_id]['username'],
            'total_score': total_score
        })

    final_scoreboard.sort(key=lambda x: x['total_score'], reverse=True)

    # Add podium positions
    for i, player in enumerate(final_scoreboard):
        if i < 3:
            player['podium_position'] = i + 1

    socketio.emit('game_finished', {
        'final_scoreboard': final_scoreboard
    }, room=game.game_id)

    # Schedule game cleanup after players have time to see results
    threading.Timer(30.0, cleanup_finished_game, [game.game_id]).start()


def cleanup_finished_game(game_id):
    """Clean up a finished game after delay"""
    game = game_manager.get_game(game_id)
    if game and game.state == "finished":
        # Remove the game from the manager after it's been finished for a while
        # This prevents memory leaks from old games
        logger.info(f"Cleaning up finished game {game_id}")
        # Note: Only cleanup if no players are still connected
        connected_players = sum(1 for p in game.players.values() if p.get('connected', False))
        if connected_players == 0:
            game_manager.games.pop(game_id, None)


def emit_lobby_update(game_id):
    """Emit lobby update to all players in the game"""
    game = game_manager.get_game(game_id)
    if not game:
        return

    player_list = []
    for player_id, player in game.players.items():
        if player['connected']:
            player_list.append({
                'username': player['username'],
                'is_host': player_id == game.host_id
            })

    socketio.emit('lobby_update', {
        'players': player_list,
        'player_count': len(player_list),
        'settings': game.settings,
        'can_start': game.can_start_game()
    }, room=game_id)


def emit_midgame_joiner_state(game, player_id):
    """Send appropriate state to a player who joined mid-game"""
    # Check if player is active in current round
    player = game.players.get(player_id)
    if not player or not player.get('active_in_round', True):
        # Player is waiting for next round - show waiting screen
        socketio.emit('midgame_waiting', {
            'message': 'You joined mid-game. Please wait for the next round to begin!',
            'current_round': game.current_round,
            'total_rounds': game.settings['rounds'],
            'game_state': game.state
        }, room=get_player_room(game_manager, game.game_id, player_id))
        return

    # Player is active, send them the current game state
    emit_game_state_to_player(game, player_id)


def emit_game_state_to_player(game, player_id):
    """Send current game state to a reconnecting player"""
    if game.state == "submission":
        targets = game.round_pairings[game.current_round].get(player_id, [])
        target_names = [game.players[tid]['username'] for tid in targets]

        socketio.emit('round_started', {
            'round': game.current_round,
            'total_rounds': game.settings['rounds'],
            'prompt': game.current_prompt,
            'time_limit': game.settings['submission_time']
        }, room=get_player_room(game_manager, game.game_id, player_id))

        socketio.emit('your_targets', {
            'targets': target_names,
            'target_ids': targets
        }, room=get_player_room(game_manager, game.game_id, player_id))

    elif game.state == "voting":
        # Send voting options, but exclude bribes player submitted themselves
        bribes_for_player = []
        for submitter_id, submissions in game.bribes[game.current_round].items():
            # Skip bribes submitted by the voting player themselves
            if submitter_id == player_id:
                continue

            for target_id, bribe in submissions.items():
                if target_id == player_id:
                    bribes_for_player.append({
                        'id': f"{submitter_id}_{target_id}",
                        'content': bribe['content'],
                        'type': bribe['type']
                    })

        socketio.emit('voting_phase', {
            'bribes': bribes_for_player,
            'time_limit': game.settings['voting_time']
        }, room=get_player_room(game_manager, game.game_id, player_id))


# Export the game manager for external access
def get_game_manager():
    """Get the current game manager instance"""
    return game_manager
