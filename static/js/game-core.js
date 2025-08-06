// Core game variables and initialization
const socket = io();
const gameId = document.querySelector('meta[name="game-id"]').content;
let isHost = false;
let playerId = null;
let currentTargets = [];
let submissions = {};
let selectedVote = null;
let timer = null;

// Initialize game connection
function initializeGame() {
    // Check if we have stored player info for this game (page refresh or host coming from creation)
    const storageKey = `bribery_game_${gameId}`;
    const storedPlayer = localStorage.getItem(storageKey);

    let username, storedPlayerId = null;

    if (storedPlayer) {
        const playerData = JSON.parse(storedPlayer);
        username = playerData.username;
        storedPlayerId = playerData.playerId;

        if (playerData.isHost) {
            console.log('Host joining lobby as:', username);
        } else {
            console.log('Attempting to rejoin as:', username, 'with ID:', storedPlayerId);
        }
    } else {
        // Only prompt for username if we don't have stored data
        username = prompt('Enter your username:') || 'Anonymous';
    }

    socket.emit('join_game', {
        game_id: gameId,
        username: username,
        player_id: storedPlayerId  // Send stored player ID if available
    });
}

// Utility functions
function hideAllScreens() {
    document.querySelectorAll('#lobby, #prompt-selection, #submission-phase, #voting-phase, #scoreboard-phase, #final-results, #waiting-screen').forEach(el => {
        el.classList.add('hidden');
    });
}

function updateStatus(message) {
    document.getElementById('game-status').textContent = message;
}

function startTimer(seconds, callback) {
    clearInterval(timer);
    const timerEl = document.getElementById('timer');
    timerEl.classList.remove('hidden');

    timer = setInterval(() => {
        const minutes = Math.floor(seconds / 60);
        const remainingSeconds = seconds % 60;
        timerEl.textContent = `${minutes}:${remainingSeconds.toString().padStart(2, '0')}`;

        if (seconds <= 0) {
            clearInterval(timer);
            timerEl.classList.add('hidden');
            if (callback) callback();
        }
        seconds--;
    }, 1000);
}

function stopTimer() {
    clearInterval(timer);
    document.getElementById('timer').classList.add('hidden');
}

// Game action functions
function startGame() {
    socket.emit('start_game');
}

function selectPrompt() {
    const dropdown = document.getElementById('prompt-dropdown');
    const customInput = document.getElementById('custom-prompt-input');

    let selectedPrompt = '';

    // Check if user selected from dropdown
    if (dropdown.value && dropdown.value !== '') {
        selectedPrompt = dropdown.value;
    }
    // Otherwise check if they typed a custom prompt
    else if (customInput.value.trim()) {
        selectedPrompt = customInput.value.trim();
    }

    if (!selectedPrompt) {
        alert('Please either select a prompt from the dropdown or type your own custom prompt');
        return;
    }

    socket.emit('select_prompt', { prompt: selectedPrompt });
}

function onPromptDropdownChange() {
    const dropdown = document.getElementById('prompt-dropdown');
    const customInput = document.getElementById('custom-prompt-input');
    const confirmButton = document.getElementById('confirm-prompt-btn');

    // If user selects from dropdown, clear custom input and enable button
    if (dropdown.value && dropdown.value !== '') {
        customInput.value = '';
        confirmButton.disabled = false;
    }

    // Update button state
    updatePromptButtonState();
}

function updatePromptButtonState() {
    const dropdown = document.getElementById('prompt-dropdown');
    const customInput = document.getElementById('custom-prompt-input');
    const confirmButton = document.getElementById('confirm-prompt-btn');

    // Enable button if either dropdown has value or custom input has text
    const hasDropdownSelection = dropdown.value && dropdown.value !== '';
    const hasCustomText = customInput.value.trim().length > 0;

    confirmButton.disabled = !(hasDropdownSelection || hasCustomText);
}

function submitBribe(targetId, content, type = 'text') {
    socket.emit('submit_bribe', {
        target_id: targetId,
        submission: content,
        type: type
    });
}

function submitVote() {
    if (selectedVote) {
        socket.emit('submit_vote', { bribe_id: selectedVote });
        document.getElementById('submit-vote-btn').disabled = true;
        updateStatus('Vote submitted! Waiting for others...');
    }
}

function restartGame() {
    socket.emit('restart_game');
}

function returnToLobby() {
    socket.emit('return_to_lobby');
}

function preventDefaults(e) {
    e.preventDefault();
    e.stopPropagation();
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', initializeGame);
