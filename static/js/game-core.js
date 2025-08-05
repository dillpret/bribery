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
    const username = prompt('Enter your username:') || 'Anonymous';
    socket.emit('join_game', {
        game_id: gameId,
        username: username
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
    
    if (dropdown.value === 'custom') {
        selectedPrompt = customInput.value.trim();
        if (!selectedPrompt) {
            alert('Please enter a custom prompt');
            return;
        }
    } else {
        selectedPrompt = dropdown.value;
        if (!selectedPrompt) {
            alert('Please select a prompt');
            return;
        }
    }
    
    socket.emit('select_prompt', { prompt: selectedPrompt });
}

function onPromptDropdownChange() {
    const dropdown = document.getElementById('prompt-dropdown');
    const customInput = document.getElementById('custom-prompt-input');
    
    if (dropdown.value === 'custom') {
        customInput.style.display = 'block';
        customInput.focus();
    } else {
        customInput.style.display = 'none';
    }
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

function preventDefaults(e) {
    e.preventDefault();
    e.stopPropagation();
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', initializeGame);
