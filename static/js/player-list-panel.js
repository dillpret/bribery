// Player list panel functionality
import ProgressTracker from './progress-tracker.js';

// DOM references
const playerListPanel = document.getElementById('player-list-panel');
const playerListToggle = document.getElementById('player-list-toggle');
const playerScoreList = document.getElementById('player-score-list');
const confirmationModal = document.getElementById('confirmation-modal-overlay');
const kickConfirmationMessage = document.getElementById('kick-confirmation-message');
const confirmKickButton = document.getElementById('confirm-kick');
const cancelKickButton = document.getElementById('cancel-kick');

// State variables
let playerToKick = null;
let players = [];
let isHost = false;

// Initialize player list panel
function initializePlayerListPanel() {
    // Toggle button event listener
    playerListToggle.addEventListener('click', () => {
        playerListPanel.classList.toggle('visible');
    });

    // Cancel kick button event listener
    cancelKickButton.addEventListener('click', () => {
        confirmationModal.classList.remove('visible');
        playerToKick = null;
    });

    // Confirm kick button event listener
    confirmKickButton.addEventListener('click', () => {
        if (playerToKick) {
            socket.emit('kick_player', {
                player_id: playerToKick.player_id,
                game_id: gameId
            });
            confirmationModal.classList.remove('visible');
            playerToKick = null;
        }
    });

    // Listen for submission status updates
    document.addEventListener('submissionStatusUpdated', () => {
        updatePlayerList(players);
    });

    // Check screen size for layout
    handleScreenSizeChange();
    window.addEventListener('resize', handleScreenSizeChange);
}

// Handle screen size changes for responsive layout
function handleScreenSizeChange() {
    const container = document.querySelector('.container');
    const wasAlreadyVisible = playerListPanel.classList.contains('visible');
    
    if (window.innerWidth >= 769) {
        container.classList.add('with-player-panel');
        playerListPanel.classList.add('visible');
    } else {
        container.classList.remove('with-player-panel');
        // Only hide if it wasn't explicitly opened by the user
        if (!wasAlreadyVisible) {
            playerListPanel.classList.remove('visible');
        }
    }
}

// Update player list with scores
function updatePlayerList(playerData) {
    players = playerData;
    const authState = GameState.get('auth');
    isHost = authState.isHost;
    
    // Sort players by score (descending)
    players.sort((a, b) => b.score - a.score);
    
    // Clear player list
    playerScoreList.innerHTML = '';
    
    // Get current game phase for submission status indicators
    const gamePhase = GameState.get('phase') || '';
    
    // Add players to list
    players.forEach(player => {
        const playerItem = document.createElement('li');
        playerItem.className = 'player-score-item';
        
        // Player info (status, name, host badge)
        const playerInfo = document.createElement('div');
        playerInfo.className = 'player-info';
        
        const playerStatus = document.createElement('span');
        playerStatus.className = `player-status ${player.connected ? 'online' : 'offline'}`;
        playerInfo.appendChild(playerStatus);
        
        const playerName = document.createElement('span');
        playerName.className = 'player-name';
        playerName.textContent = player.username;
        playerInfo.appendChild(playerName);
        
        if (player.is_host) {
            const hostBadge = document.createElement('span');
            hostBadge.className = 'host-badge';
            hostBadge.textContent = 'HOST';
            playerInfo.appendChild(hostBadge);
        }
        
        // Add submission status indicator for relevant game phases
        if (['prompt_selection', 'submission', 'voting'].includes(gamePhase)) {
            const submissionStatus = document.createElement('span');
            submissionStatus.className = 'submission-status';
            
            // Set status based on player's submission state and current phase
            if (player.hasOwnProperty('submitted') && player.submitted) {
                submissionStatus.className += ' submitted';
                submissionStatus.title = 'Submitted';
                submissionStatus.textContent = '✓';
            } else {
                submissionStatus.className += ' pending';
                submissionStatus.title = 'Waiting for submission';
                submissionStatus.textContent = '⋯';
            }
            
            playerInfo.appendChild(submissionStatus);
        }
        
        playerItem.appendChild(playerInfo);
        
        // Player score
        const playerScore = document.createElement('div');
        playerScore.className = 'player-score';
        playerScore.textContent = player.score;
        playerItem.appendChild(playerScore);
        
        // Kick button (only visible to host and not for self)
        if (isHost && !player.is_host) {
            const kickButton = document.createElement('button');
            kickButton.className = 'kick-button';
            kickButton.textContent = 'Kick';
            kickButton.addEventListener('click', () => {
                showKickConfirmation(player);
            });
            playerItem.appendChild(kickButton);
        }
        
        playerScoreList.appendChild(playerItem);
    });
}

// Show kick confirmation modal
function showKickConfirmation(player) {
    playerToKick = player;
    kickConfirmationMessage.textContent = `Are you sure you want to kick ${player.username} from the game?`;
    confirmationModal.classList.add('visible');
}

// Update player list from scoreboard data
function updatePlayerListFromScoreboard(scoreboardData) {
    const playerData = scoreboardData.map(player => ({
        username: player.username,
        score: player.total_score,
        connected: true, // Assume connected since they're in the scoreboard
        is_host: player.is_host || false,
        player_id: player.player_id || ''
    }));
    
    updatePlayerList(playerData);
}

// Socket event handlers
socket.on('lobby_update', (data) => {
    updatePlayerList(data.players);
});

socket.on('round_results', (data) => {
    // Update player list with scores from scoreboard
    updatePlayerListFromScoreboard(data.scoreboard);
});

socket.on('game_over', (data) => {
    // Update player list with final scores
    updatePlayerListFromScoreboard(data.final_scoreboard);
});

socket.on('player_kicked', (data) => {
    // Show notification
    updateStatus(`${data.username} has been kicked from the game`);
});

socket.on('kicked_from_game', (data) => {
    // Redirect to homepage with message
    window.location.href = `/?message=${encodeURIComponent(data.message)}`;
});

socket.on('kick_player_result', (data) => {
    if (data.success) {
        updateStatus('Player kicked successfully');
    } else {
        updateStatus('Failed to kick player');
    }
});

// Initialize when document is ready
document.addEventListener('DOMContentLoaded', initializePlayerListPanel);
