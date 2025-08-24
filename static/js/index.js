// Index page functionality
const socket = io();
let currentGameId = null;
let currentPlayerId = null;

function showMainMenu() {
    hideAll();
    document.getElementById('main-menu').classList.remove('hidden');
}

function showHostGame() {
    hideAll();
    document.getElementById('host-game').classList.remove('hidden');
}

function showJoinGame() {
    hideAll();
    document.getElementById('join-game').classList.remove('hidden');
}

function hideAll() {
    document.querySelectorAll('.container > div').forEach(div => {
        div.classList.add('hidden');
    });
}

function showError(message) {
    const errorDiv = document.getElementById('error-message');
    errorDiv.textContent = message;
    errorDiv.classList.remove('hidden');
    setTimeout(() => {
        errorDiv.classList.add('hidden');
    }, 5000);
}

function getTimeInSeconds(baseId) {
    // Check if timer is set to "off"
    const modeSelect = document.getElementById(baseId + '-mode');
    if (modeSelect && modeSelect.value === 'off') {
        return 0; // 0 means timer is off
    }

    const value = parseInt(document.getElementById(baseId + '-value').value);
    const unit = document.getElementById(baseId + '-unit').value;

    if (isNaN(value) || value < 1) {
        return unit === 'minutes' ? 120 : 60; // Default fallback
    }

    return unit === 'minutes' ? value * 60 : value;
}

function createGame() {
    const username = document.getElementById('host-username').value.trim();
    if (!username) {
        showError('Please enter a username');
        return;
    }

    // Set up authentication for host
    Authentication.setupHost(username, null); // gameId will be set when server responds

    // Use default settings, which will be configurable in the lobby
    const settings = {
        rounds: 3,
        submission_time: 0,
        voting_time: 0,
        results_time: 0,
        custom_prompts: true
    };

    socket.emit('create_game', {
        username: username,
        ...settings
    });
}

function joinGame() {
    const username = document.getElementById('join-username').value.trim();
    const gameId = document.getElementById('game-id').value.trim().toUpperCase();

    if (!username || !gameId) {
        showError('Please enter both username and game ID');
        return;
    }

    // Set up authentication for player
    Authentication.setupPlayer(username, gameId);

    socket.emit('join_game', {
        username: username,
        game_id: gameId
    });
}

function copyGameLink() {
    const linkInput = document.getElementById('game-link');
    linkInput.select();
    document.execCommand('copy');

    const button = event.target;
    const originalText = button.textContent;
    button.textContent = 'Copied!';
    setTimeout(() => {
        button.textContent = originalText;
    }, 2000);
}

function goToLobby() {
    window.location.href = `/bribery/${currentGameId}`;
}

// Socket event handlers
socket.on('game_created', (data) => {
    currentGameId = data.game_id;
    currentPlayerId = data.player_id;

    // Update authentication with server-provided data
    Authentication.updateFromServer(data);

    hideAll();
    document.getElementById('game-created').classList.remove('hidden');
    document.getElementById('created-game-id').textContent = data.game_id;
    document.getElementById('game-link').value = `${window.location.origin}/bribery/${data.game_id}`;
});

socket.on('joined_game', (data) => {
    currentGameId = data.game_id;
    currentPlayerId = data.player_id;
    
    // Update authentication with server-provided data
    Authentication.updateFromServer(data);
    
    window.location.href = `/bribery/${data.game_id}`;
});

socket.on('error', (data) => {
    showError(data.message);
});

// DOM event listeners
document.addEventListener('DOMContentLoaded', () => {
    // Auto-uppercase game ID input
    const gameIdInput = document.getElementById('game-id');
    if (gameIdInput) {
        gameIdInput.addEventListener('input', function(e) {
            e.target.value = e.target.value.toUpperCase();
        });
    }

    // Enter key submission
    document.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            if (!document.getElementById('main-menu').classList.contains('hidden')) {
                return;
            } else if (!document.getElementById('host-game').classList.contains('hidden')) {
                createGame();
            } else if (!document.getElementById('join-game').classList.contains('hidden')) {
                joinGame();
            }
        }
    });
});
