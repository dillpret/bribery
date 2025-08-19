// Socket event handlers for game state management

// Connection and lobby events
socket.on('joined_game', (data) => {
    // Update state with server response data
    // AUTHENTICATION FLOW: This updates our state with the server-provided data
    // while preserving any existing values that might be important
    GameState.update(data);
    
    // Get the updated auth state for local use
    const authState = GameState.get('auth');
    updateStatus('Connected to game');

    // Set UI state based on game state
    if (data.game_state === 'lobby') {
        hideAllScreens();
        document.getElementById('lobby').classList.remove('hidden');
        GameState.set('ui', { activeScreen: 'lobby' });
    } else {
        hideAllScreens();
        document.getElementById('waiting-screen').classList.remove('hidden');
    }
});

// Handle mid-game joiners
socket.on('midgame_waiting', (data) => {
    hideAllScreens();
    document.getElementById('waiting-screen').classList.remove('hidden');

    const waitingScreen = document.querySelector('#waiting-screen .waiting-screen');
    waitingScreen.innerHTML = `
        <div class="waiting-spinner"></div>
        <h2>${data.message}</h2>
        <p>Current Round: ${data.current_round} / ${data.total_rounds}</p>
        <p>Game Phase: ${data.game_state}</p>
    `;

    updateStatus('Waiting for next round to begin...');
    GameState.set('ui', { activeScreen: 'waiting' });
});

socket.on('lobby_update', (data) => {
    const playerList = document.getElementById('player-list');
    playerList.innerHTML = '<h3>Players (' + data.player_count + '):</h3>';

    data.players.forEach(player => {
        const playerEl = document.createElement('div');
        playerEl.className = 'player-item' + (player.is_host ? ' host' : '');
        playerEl.textContent = player.username + (player.is_host ? ' (Host)' : '');
        playerList.appendChild(playerEl);
    });

    const settingsDisplay = document.getElementById('settings-display');
    settingsDisplay.innerHTML = `
        <h3>Game Settings:</h3>
        <p><strong>Rounds:</strong> ${data.settings.rounds}</p>
        <p><strong>Submission Time:</strong> ${data.settings.submission_time} seconds</p>
        <p><strong>Voting Time:</strong> ${data.settings.voting_time} seconds</p>
        <p><strong>Custom Prompts:</strong> ${data.settings.custom_prompts ? 'Enabled' : 'Disabled'}</p>
    `;

    // Get host status from state
    const isHost = GameState.get('auth', 'isHost');
    
    if (isHost) {
        document.getElementById('host-controls').classList.remove('hidden');
        const startBtn = document.getElementById('start-game-btn');
        startBtn.disabled = !data.can_start;
        startBtn.textContent = data.can_start ? 'Start Game' : 'Need at least 3 players';
    }

    updateStatus(`${data.player_count} players in lobby`);
    
    // Store game settings
    GameState.set('game', {
        totalRounds: data.settings.rounds,
        playerCount: data.player_count
    });
});

// Prompt selection events
socket.on('prompt_selection_started', (data) => {
    hideAllScreens();
    document.getElementById('prompt-selection').classList.remove('hidden');
    GameState.set('ui', { activeScreen: 'prompt_selection' });

    document.getElementById('prompt-round-title').textContent = `Round ${data.round} of ${data.total_rounds}`;

    const promptSelect = document.getElementById('prompt-dropdown');
    promptSelect.innerHTML = '<option value="">Select a prompt...</option>';

    data.available_prompts.forEach(prompt => {
        const option = document.createElement('option');
        option.value = prompt;
        option.textContent = prompt;
        promptSelect.appendChild(option);
    });

    // Clear custom input and reset button state
    document.getElementById('custom-prompt-input').value = '';
    document.getElementById('confirm-prompt-btn').disabled = true;

    // Add event listener to custom input for real-time button state updates
    const customInput = document.getElementById('custom-prompt-input');
    customInput.oninput = function () {
        // Clear dropdown selection when user types
        if (this.value.trim()) {
            promptSelect.value = '';
        }
        updatePromptButtonState();
    };

    updateStatus('Choose your prompt for this round!');
    startTimer(data.time_limit);
});

socket.on('prompt_selected', (data) => {
    if (data.success) {
        document.getElementById('confirm-prompt-btn').textContent = 'Prompt Selected ✓';
        document.getElementById('confirm-prompt-btn').disabled = true;
        document.getElementById('confirm-prompt-btn').style.background = '#28a745';
        updateStatus('Waiting for other players to select prompts...');
    }
});

// Game round events
socket.on('round_started', (data) => {
    hideAllScreens();
    document.getElementById('submission-phase').classList.remove('hidden');

    document.getElementById('round-title').textContent = `Round ${data.round} of ${data.total_rounds}`;

    if (data.custom_prompts_enabled) {
        document.getElementById('current-prompt').textContent = 'Custom prompts enabled - each player has their own prompt';
    } else {
        document.getElementById('current-prompt').textContent = data.prompt;
    }

    updateStatus('Submit your bribes!');
    startTimer(data.time_limit);

    submissions = {};

    // Re-enable all form elements for new round
    document.querySelectorAll('textarea[id^="submission-"]').forEach(textarea => {
        textarea.disabled = false;
        textarea.style.backgroundColor = '';
        textarea.style.cursor = '';
        textarea.value = '';
    });

    document.querySelectorAll('div[id^="drop-"]').forEach(dropArea => {
        dropArea.style.pointerEvents = '';
        dropArea.style.opacity = '';
    });

    document.querySelectorAll('input[id^="file-input-"]').forEach(fileInput => {
        fileInput.disabled = false;
    });

    document.querySelectorAll('button[id^="upload-btn-"]').forEach(uploadBtn => {
        uploadBtn.disabled = false;
        uploadBtn.style.backgroundColor = '';
        uploadBtn.style.cursor = '';
    });

    document.querySelectorAll('button[onclick^="submitTargetBribe"]').forEach(button => {
        button.disabled = false;
        button.textContent = 'Submit Bribe';
        button.style.background = '';
    });
});

socket.on('your_targets', (data) => {
    const container = document.getElementById('targets-container');
    container.innerHTML = '<h3>Create bribes for these players:</h3>';

    data.targets.forEach((target) => {
        const targetEl = document.createElement('div');
        targetEl.className = 'target-item';
        targetEl.innerHTML = `
            <h4>Bribe for: ${target.name}</h4>
            <p class="target-prompt"><strong>Their prompt:</strong> "${target.prompt}"</p>
            <div class="submission-area">
                <textarea class="submission-input" id="submission-${target.id}" 
                        placeholder="Enter your bribe for this prompt (text, link, or paste an image)..."></textarea>
                <div class="image-upload-container">
                    <div class="drag-drop-area" id="drop-${target.id}">
                        <span class="drag-drop-text">Or drag and drop an image here</span>
                        <span class="mobile-upload-text">Or tap to add an image</span>
                    </div>
                    <input type="file" 
                           id="file-input-${target.id}" 
                           accept="image/*,image/gif" 
                           capture="environment"
                           style="display: none;">
                    <button type="button" class="image-upload-btn" id="upload-btn-${target.id}">
                        📷 Add Image
                    </button>
                </div>
                <button class="submit-btn" onclick="submitTargetBribe('${target.id}')">
                    Submit Bribe
                </button>
            </div>
        `;
        container.appendChild(targetEl);

        setupDragDrop(target.id);
        setupMobileImageUpload(target.id);
    });
});

socket.on('bribe_submitted', (data) => {
    const button = document.querySelector(`button[onclick="submitTargetBribe('${data.target_id}')"]`);
    if (button) {
        button.textContent = 'Submitted ✓';
        button.disabled = true;
        button.style.background = '#28a745';
    }

    // Disable the text input field for this target
    const textarea = document.getElementById(`submission-${data.target_id}`);
    if (textarea) {
        textarea.disabled = true;
        textarea.style.backgroundColor = '#f8f9fa';
        textarea.style.cursor = 'not-allowed';
    }

    // Also disable the image upload components for this target
    const fileInput = document.getElementById(`file-input-${data.target_id}`);
    const uploadBtn = document.getElementById(`upload-btn-${data.target_id}`);
    const dropArea = document.getElementById(`drop-${data.target_id}`);

    if (fileInput) fileInput.disabled = true;
    if (uploadBtn) {
        uploadBtn.disabled = true;
        uploadBtn.style.backgroundColor = '#6c757d';
        uploadBtn.style.cursor = 'not-allowed';
    }
    if (dropArea) {
        dropArea.style.pointerEvents = 'none';
        dropArea.style.opacity = '0.6';
    }
});

// Voting events
socket.on('voting_phase', (data) => {
    hideAllScreens();
    document.getElementById('voting-phase').classList.remove('hidden');

    const votingOptions = document.getElementById('voting-options');
    votingOptions.innerHTML = '';
    selectedVote = null;

    data.bribes.forEach(bribe => {
        const option = document.createElement('div');
        option.className = 'bribe-option';
        option.onclick = () => selectVote(bribe.id, option);

        if (bribe.type === 'image') {
            option.innerHTML = `<img src="${bribe.content}" class="bribe-image" alt="Bribe image">`;
        } else {
            option.innerHTML = `<div class="bribe-content">${bribe.content}</div>`;
        }

        votingOptions.appendChild(option);
    });

    updateStatus('Vote for your favourite bribe!');
    startTimer(data.time_limit);
    document.getElementById('submit-vote-btn').disabled = true;
});

socket.on('vote_submitted', () => {
    updateStatus('Vote submitted! Waiting for results...');
    stopTimer();
});

// Progress tracking events
socket.on('submission_progress', (data) => {
    const progressText = document.getElementById('submission-progress-text');
    const progressContainer = document.getElementById('submission-progress');

    if (progressText) {
        progressText.textContent = data.message;

        // Style the progress indicator based on completion
        if (data.completed === data.total) {
            progressContainer.classList.add('waiting');
        } else {
            progressContainer.classList.remove('waiting');
        }
    }
});

socket.on('voting_progress', (data) => {
    const progressText = document.getElementById('voting-progress-text');
    const progressContainer = document.getElementById('voting-progress');

    if (progressText) {
        progressText.textContent = data.message;

        // Style the progress indicator based on completion
        if (data.completed === data.total) {
            progressContainer.classList.add('waiting');
        } else {
            progressContainer.classList.remove('waiting');
        }
    }
});

// Results events
socket.on('round_results', (data) => {
    hideAllScreens();
    document.getElementById('scoreboard-phase').classList.remove('hidden');

    document.getElementById('scoreboard-title').textContent = `Round ${data.round} Results`;

    // Show vote results
    const voteResults = document.getElementById('vote-results');
    voteResults.innerHTML = '<h3>Vote Results:</h3>';
    data.vote_results.forEach(result => {
        const voteItem = document.createElement('div');
        voteItem.className = 'vote-item';
        voteItem.textContent = `${result.voter} chose ${result.winner}'s bribe`;
        voteResults.appendChild(voteItem);
    });
    voteResults.classList.remove('hidden');

    // Show scoreboard
    displayScoreboard(data.scoreboard, 'scoreboard');

    updateStatus('Round complete!');
    stopTimer();
});

socket.on('game_finished', (data) => {
    hideAllScreens();
    document.getElementById('final-results').classList.remove('hidden');

    displayScoreboard(data.final_scoreboard, 'final-scoreboard', true);

    if (isHost) {
        document.getElementById('host-final-controls').classList.remove('hidden');
    }

    updateStatus('Game finished!');
    stopTimer();

    // Clear stored player data after game ends
    const storageKey = `bribery_game_${gameId}`;
    localStorage.removeItem(storageKey);
});

socket.on('game_restarted', () => {
    // Clear all client-side state for fresh start
    clearGameState();

    hideAllScreens();
    document.getElementById('lobby').classList.remove('hidden');
    updateStatus('Game restarted - back to lobby');
    stopTimer();
});

socket.on('returned_to_lobby', () => {
    // Return to lobby keeping player data
    hideAllScreens();
    document.getElementById('lobby').classList.remove('hidden');
    updateStatus('Returned to lobby. Host can modify settings.');
    stopTimer();
});

// Function to clear all client-side game state
function clearGameState() {
    // Clear variables
    currentTargets = [];
    submissions = {};
    selectedVote = null;

    // Clear UI elements
    stopTimer();
    document.querySelectorAll('.submission-item').forEach(item => item.remove());
    document.querySelectorAll('.vote-option').forEach(option => option.remove());

    // Reset form elements to enabled state
    document.querySelectorAll('textarea[id^="submission-"]').forEach(textarea => {
        textarea.disabled = false;
        textarea.style.backgroundColor = '';
        textarea.style.cursor = '';
        textarea.value = '';
    });

    document.querySelectorAll('div[id^="drop-"]').forEach(dropArea => {
        dropArea.style.pointerEvents = '';
        dropArea.style.opacity = '';
    });

    document.querySelectorAll('button[onclick^="submitTargetBribe"]').forEach(button => {
        button.disabled = false;
        button.textContent = 'Submit';
        button.style.background = '';
    });

    // Clear scoreboard displays
    document.getElementById('scoreboard').innerHTML = '';
    document.getElementById('final-scoreboard').innerHTML = '';

    // Hide all host controls
    document.querySelectorAll('.host-controls').forEach(el => el.classList.add('hidden'));

    // Clear storage for this game
    const storageKey = `bribery_game_${gameId}`;
    localStorage.removeItem(storageKey);
}

socket.on('error', (data) => {
    alert('Error: ' + data.message);
});
