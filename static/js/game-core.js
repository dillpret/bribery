// Core game variables and initialization
import { socket, isSocketInitialized } from './socket-manager.js';
import { GameState } from './game-state.js';

// Check if socket is properly initialized
if (!isSocketInitialized()) {
    console.error('Socket.IO not properly initialized!');
}

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
    console.log('Hiding all screens');
    const screens = document.querySelectorAll('#lobby, #prompt-selection, #submission-phase, #voting-phase, #scoreboard-phase, #final-results, #waiting-screen');
    console.log('Found', screens.length, 'screens to hide');
    screens.forEach(el => {
        el.classList.add('hidden');
        console.log('Added hidden class to', el.id);
    });
}

function updateStatus(message) {
    document.getElementById('game-status').textContent = message;
}

// Store timer end timestamp to handle refresh
let timerEndTime = 0;

function startTimer(seconds, callback) {
    // Clear any existing timer
    stopTimer();
    
    const timerEl = document.getElementById('timer');
    
    // If seconds is 0 or undefined, this is a "no timer" mode
    if (!seconds) {
        timerEl.classList.add('hidden');
        timerEndTime = 0;
        return;
    }
    
    // Set the end time for this timer
    timerEndTime = Date.now() + (seconds * 1000);
    
    // Store in localStorage to handle page refresh
    try {
        localStorage.setItem('bribery_timer_end', timerEndTime.toString());
    } catch (e) {
        console.error('Failed to store timer in localStorage:', e);
    }
    
    timerEl.classList.remove('hidden');

    // Update every second
    timer = setInterval(() => {
        // Calculate remaining time
        const remainingTime = Math.max(0, Math.floor((timerEndTime - Date.now()) / 1000));
        const minutes = Math.floor(remainingTime / 60);
        const remainingSeconds = remainingTime % 60;
        
        // Update display
        timerEl.textContent = `${minutes}:${remainingSeconds.toString().padStart(2, '0')}`;

        if (remainingTime <= 0) {
            stopTimer();
            timerEl.classList.add('hidden');
            if (callback) callback();
        }
    }, 1000);
}

function stopTimer() {
    if (timer) {
        clearInterval(timer);
        timer = null;
    }
    
    // Clear stored timer
    try {
        localStorage.removeItem('bribery_timer_end');
    } catch (e) {
        console.error('Failed to remove timer from localStorage:', e);
    }
    
    timerEndTime = 0;
    document.getElementById('timer').classList.add('hidden');
}

// Restore timer on page refresh if needed
function restoreTimer() {
    try {
        const storedEndTime = localStorage.getItem('bribery_timer_end');
        if (storedEndTime) {
            const endTime = parseInt(storedEndTime);
            const now = Date.now();
            
            // Only restore if timer hasn't ended yet
            if (endTime > now) {
                const remainingSeconds = Math.floor((endTime - now) / 1000);
                startTimer(remainingSeconds);
            } else {
                // Timer would have ended - remove it
                localStorage.removeItem('bribery_timer_end');
            }
        }
    } catch (e) {
        console.error('Failed to restore timer:', e);
    }
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
document.addEventListener('DOMContentLoaded', () => {
    initializeGame();
    // Restore timer if there was one
    restoreTimer();
});

// Export key functions to global scope for use in HTML
window.updateSettings = updateSettings;
window.startGame = startGame;
window.selectPrompt = selectPrompt;
window.submitVote = submitVote;
window.returnToLobby = returnToLobby;
window.restartGame = restartGame;
window.onPromptDropdownChange = onPromptDropdownChange;
