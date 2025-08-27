// Core game variables and initialization
const socket = io();
const gameId = document.querySelector('meta[name="game-id"]').content;
let timer = null;

// Initialize game connection
function initializeGame() {
    // AUTHENTICATION FLOW: This is the main reconnection mechanism that supports:
    // 1. Page refreshes (retrieving stored credentials)
    // 2. Direct URL access (fallback to prompt)
    // 3. Returning players (via stored player ID)
    
    // Initialize authentication state from localStorage or prompt fallback
    const authState = GameState.init(gameId);
    
    // Log connection attempt
    if (authState.isHost) {
        console.log('Host joining lobby as:', authState.username);
    } else {
        console.log('Player joining as:', authState.username, 'with ID:', authState.playerId);
    }

    // Connect to game via socket
    socket.emit('join_game', {
        game_id: gameId,
        username: authState.username,
        player_id: authState.playerId  // Send stored player ID if available
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
    // Clear any existing timer
    clearInterval(timer);
    const timerEl = document.getElementById('timer');
    
    // If seconds is 0 or undefined, this is a "no timer" mode
    if (!seconds) {
        timerEl.classList.add('hidden');
        return;
    }
    
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

function updateSettings() {
    // Validate rounds input
    const roundsInput = document.getElementById('rounds');
    let rounds = parseInt(roundsInput.value);
    
    // Ensure rounds is within valid range
    if (isNaN(rounds) || rounds < 1) {
        rounds = 1;
        roundsInput.value = 1;
    } else if (rounds > 100) {
        rounds = 100;
        roundsInput.value = 100;
    }
    
    const settings = {
        rounds: rounds,
        submission_time: getTimeInSeconds('submission-time'),
        voting_time: getTimeInSeconds('voting-time'),
        results_time: getTimeInSeconds('results-time'),
        prompt_selection_time: getTimeInSeconds('prompt-selection-time'),
        custom_prompts: document.getElementById('custom-prompts').value === 'true'
    };

    socket.emit('update_settings', settings);
    updateStatus('Updating game settings...');
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
