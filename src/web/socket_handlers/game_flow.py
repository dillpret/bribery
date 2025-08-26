"""
Game flow management functions for the Bribery game.

This module handles the game's state transitions and round management.
"""

import logging
import random
import threading

from flask_socketio import emit
from src.game.game import Game
from src.game.game_manager import GameManager
from src.game.player_session import PlayerSession

from ..utils import get_player_room, load_prompts, generate_random_bribe
from .progress_tracking import emit_submission_progress, emit_voting_progress

logger = logging.getLogger(__name__)

# Game manager instance
game_manager = None
socketio = None


def initialize_game_manager(socketio_instance):
    """Initialize the game manager and set up socketio reference"""
    global game_manager, socketio
    game_manager = GameManager()
    socketio = socketio_instance


def get_game_manager():
    """Get the current game manager instance"""
    return game_manager


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
        'time_limit': game.settings['submission_time']  # Will be 0 for "no timer" mode
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

    # Set up timer or wait for all submissions
    if game.settings['submission_time'] > 0:
        # Start submission timer if time is set
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
        # If timer is active, cancel it
        if game.round_timer:
            game.round_timer.cancel()
        
        # Proceed to voting phase
        end_submission_phase(game)


def end_submission_phase(game):
    """End the submission phase and start voting"""
    from ..utils import generate_random_bribe
    
    # Before starting voting phase, add random bribes for any missing submissions
    active_player_ids = game.get_active_player_ids()
    
    # Check each player and their targets for missing submissions
    for player_id in active_player_ids:
        # Get the targets this player should have submitted bribes to
        targets = game.round_pairings[game.current_round].get(player_id, [])
        
        # Skip if player has no targets (shouldn't happen, but just in case)
        if not targets:
            continue
        
        # Initialize player's bribes dict if it doesn't exist
        if player_id not in game.bribes[game.current_round]:
            game.bribes[game.current_round][player_id] = {}
        
        # Check for each target if a submission exists
        for target_id in targets:
            if target_id not in game.bribes[game.current_round][player_id]:
                # Generate a random bribe for this missing submission
                random_bribe, is_random = generate_random_bribe()
                
                # Add it to the game state
                game.bribes[game.current_round][player_id][target_id] = {
                    'content': random_bribe,
                    'type': 'text',
                    'is_random': True  # Flag it as randomly generated
                }
    
    # Now change the game state to voting
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
                    # Don't add the "(randomly generated)" indicator during voting phase
                    # Players shouldn't know which bribes are random until afterwards
                    bribes_for_player.append({
                        'id': f"{submitter_id}_{target_id}",
                        'content': bribe['content'],
                        'type': bribe['type'],
                        'is_random': bribe.get('is_random', False)  # Keep track but don't show in UI yet
                    })

        # Get the player's prompt for this round
        player_prompt = game.get_prompt_for_target(game.current_round, player_id)

        socketio.emit('voting_phase', {
            'bribes': bribes_for_player,
            'time_limit': game.settings['voting_time'],  # Will be 0 for "no timer" mode
            'player_prompt': player_prompt
        }, room=get_player_room(game_manager, game.game_id, player_id))

    # Set up timer or wait for all votes
    if game.settings['voting_time'] > 0:
        # Start voting timer if time is set
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
        # Parse bribe_id to get submitter and target
        parts = bribe_id.split('_')
        if len(parts) != 2:
            continue
            
        submitter_id, target_id = parts
        
        # Check if this bribe is random
        is_random = False
        try:
            is_random = game.bribes[game.current_round][submitter_id][target_id].get('is_random', False)
        except (KeyError, AttributeError):
            pass
        
        # Award points (half point for random bribes)
        if submitter_id not in round_scores:
            round_scores[submitter_id] = 0
            
        # Award half a point for randomly generated bribes
        if is_random:
            round_scores[submitter_id] += 0.5
        else:
            round_scores[submitter_id] += 1

        # Get the bribe content and type
        bribe_content = ""
        bribe_type = "text"
        prompt_text = game.get_prompt_for_target(game.current_round, target_id)
        
        try:
            bribe = game.bribes[game.current_round][submitter_id][target_id]
            bribe_content = bribe.get('content', '')
            if is_random:
                bribe_content += " (randomly generated)"
            bribe_type = bribe.get('type', 'text')
        except (KeyError, AttributeError):
            pass

        vote_results.append({
            'voter': game.players[voter_id]['username'],
            'winner': game.players[submitter_id]['username'],
            'prompt_owner': game.players[target_id]['username'],
            'prompt': prompt_text,
            'winning_bribe': bribe_content,
            'bribe_type': bribe_type,
            'is_random': is_random
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
            'total_score': total_score,
            'player_id': player_id,
            'is_host': player_id == game.host_id
        })

    scoreboard.sort(key=lambda x: x['total_score'], reverse=True)

    socketio.emit('round_results', {
        'round': game.current_round,
        'vote_results': vote_results,
        'scoreboard': scoreboard,
        'timer_enabled': game.settings['results_time'] > 0,
        'results_time': game.settings['results_time']
    }, room=game.game_id)

    # Wait a bit then continue to next round or end game
    if game.settings['results_time'] > 0:
        # Use timer if results_time is set
        threading.Timer(game.settings['results_time'], continue_or_end_game, [game]).start()
    else:
        # Otherwise, let the host control when to continue
        socketio.emit('host_controls_next_round', {}, 
                      room=get_player_room(game_manager, game.game_id, game.host_id))


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
            'total_score': total_score,
            'player_id': player_id,
            'is_host': player_id == game.host_id
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
        player_list.append({
            'username': player['username'],
            'is_host': player_id == game.host_id,
            'connected': player['connected'],
            'score': game.scores.get(player_id, 0),
            'player_id': player_id  # Send player_id for kick functionality
        })

    socketio.emit('lobby_update', {
        'players': player_list,
        'player_count': len([p for p in player_list if p['connected']]),
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
        
        # Also send them the current player list so they can see who's playing
        socketio.emit('lobby_update', {
            'players': [
                {
                    'username': p['username'],
                    'is_host': pid == game.host_id,
                    'connected': p.get('connected', True),
                    'score': p.get('score', 0)
                }
                for pid, p in game.players.items()
            ],
            'player_count': len(game.players)
        }, room=get_player_room(game_manager, game.game_id, player_id))
        
        return

    # Player is active, send them the current game state
    emit_game_state_to_player(game, player_id)


def emit_game_state_to_player(game, player_id):
    """Send current game state to a reconnecting player"""
    player_room = get_player_room(game_manager, game.game_id, player_id)
    
    # First, always send the player list regardless of game state
    socketio.emit('lobby_update', {
        'players': [
            {
                'username': p['username'],
                'is_host': pid == game.host_id,
                'connected': p.get('connected', True),
                'score': p.get('score', 0)
            }
            for pid, p in game.players.items()
        ],
        'player_count': len(game.players)
    }, room=player_room)
    
    # Then handle specific game state
    if game.state == "submission":
        # Get targets for this player
        targets = game.round_pairings[game.current_round].get(player_id, [])
        target_data = []
        
        for target_id in targets:
            target_prompt = game.get_prompt_for_target(
                game.current_round, target_id)
            target_data.append({
                'id': target_id,
                'name': game.players[target_id]['username'],
                'prompt': target_prompt
            })

        # Send round info
        socketio.emit('round_started', {
            'round': game.current_round,
            'total_rounds': game.settings['rounds'],
            'prompt': game.current_prompt if not game.custom_prompts_enabled() else None,
            'custom_prompts_enabled': game.custom_prompts_enabled(),
            'time_limit': game.settings['submission_time']
        }, room=player_room)

        # Send targets
        socketio.emit('your_targets', {
            'targets': target_data
        }, room=player_room)
        
        # Also send progress update
        emit_submission_progress(game, player_room)

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
                        'type': bribe['type'],
                        'is_random': bribe.get('is_random', False)  # Keep track but don't show in UI yet
                    })

        socketio.emit('voting_phase', {
            'bribes': bribes_for_player,
            'time_limit': game.settings['voting_time']
        }, room=player_room)
        
        # Also send progress update
        emit_voting_progress(game, player_room)
    
    elif game.state == "scoreboard":
        # Regenerate and send scoreboard data
        round_results = game.get_round_results(game.current_round)
        if round_results:
            socketio.emit('round_results', {
                'round': game.current_round,
                'results': round_results,
                'time_limit': game.settings['results_time']
            }, room=player_room)
