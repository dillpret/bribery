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
        <p><strong>Submission Time:</strong> ${data.settings.submission_time ? data.settings.submission_time + ' seconds' : 'Wait for all players'}</p>
        <p><strong>Voting Time:</strong> ${data.settings.voting_time ? data.settings.voting_time + ' seconds' : 'Wait for all players'}</p>
        <p><strong>Custom Prompts:</strong> ${data.settings.custom_prompts ? 'Enabled' : 'Disabled'}</p>
    `;

    // Get host status from state
    const isHost = GameState.get('auth', 'isHost');
    
    // Handle host controls and settings
    if (isHost) {
        // Show host game controls
        document.getElementById('host-controls').classList.remove('hidden');
        const startBtn = document.getElementById('start-game-btn');
        startBtn.disabled = !data.can_start;
        startBtn.textContent = data.can_start ? 'Start Game' : 'Need at least 3 players';
        
        // Show host settings
        const hostSettings = document.getElementById('host-settings');
        hostSettings.classList.remove('hidden');
        
        // Update settings form values to match current game settings
        document.getElementById('rounds').value = data.settings.rounds;
        
        // Set submission time
        const submissionTime = data.settings.submission_time;
        document.getElementById('submission-time-mode').value = submissionTime ? 'timed' : 'off';
        if (submissionTime) {
            document.getElementById('submission-time-controls').classList.remove('hidden');
            if (submissionTime >= 60 && submissionTime % 60 === 0) {
                document.getElementById('submission-time-value').value = submissionTime / 60;
                document.getElementById('submission-time-unit').value = 'minutes';
            } else {
                document.getElementById('submission-time-value').value = submissionTime;
                document.getElementById('submission-time-unit').value = 'seconds';
            }
        } else {
            document.getElementById('submission-time-controls').classList.add('hidden');
        }
        
        // Set voting time
        const votingTime = data.settings.voting_time;
        document.getElementById('voting-time-mode').value = votingTime ? 'timed' : 'off';
        if (votingTime) {
            document.getElementById('voting-time-controls').classList.remove('hidden');
            if (votingTime >= 60 && votingTime % 60 === 0) {
                document.getElementById('voting-time-value').value = votingTime / 60;
                document.getElementById('voting-time-unit').value = 'minutes';
            } else {
                document.getElementById('voting-time-value').value = votingTime;
                document.getElementById('voting-time-unit').value = 'seconds';
            }
        } else {
            document.getElementById('voting-time-controls').classList.add('hidden');
        }
        
        // Set results time
        const resultsTime = data.settings.results_time;
        document.getElementById('results-time-mode').value = resultsTime ? 'timed' : 'off';
        if (resultsTime) {
            document.getElementById('results-time-controls').classList.remove('hidden');
            if (resultsTime >= 60 && resultsTime % 60 === 0) {
                document.getElementById('results-time-value').value = resultsTime / 60;
                document.getElementById('results-time-unit').value = 'minutes';
            } else {
                document.getElementById('results-time-value').value = resultsTime;
                document.getElementById('results-time-unit').value = 'seconds';
            }
        } else {
            document.getElementById('results-time-controls').classList.add('hidden');
        }
        
        // Set custom prompts
        document.getElementById('custom-prompts').value = data.settings.custom_prompts ? 'true' : 'false';
        
        // Setup timer mode toggles
        ['submission-time', 'voting-time', 'results-time'].forEach(timerId => {
            const modeSelect = document.getElementById(`${timerId}-mode`);
            const controls = document.getElementById(`${timerId}-controls`);
            
            if (modeSelect && controls) {
                // Set initial state
                controls.classList.toggle('hidden', modeSelect.value === 'off');
                
                // Add change listener if not already added
                if (!modeSelect.dataset.listenerAdded) {
                    modeSelect.addEventListener('change', function() {
                        controls.classList.toggle('hidden', this.value === 'off');
                    });
                    modeSelect.dataset.listenerAdded = 'true';
                }
            }
        });
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
    startTimer(data.time_limit, () => {
        // Auto-select prompt if user has made a selection but not confirmed
        const dropdown = document.getElementById('prompt-dropdown');
        const customInput = document.getElementById('custom-prompt-input');
        const confirmButton = document.getElementById('confirm-prompt-btn');
        
        // Only auto-select if the button is enabled (means they've selected but not confirmed)
        if (!confirmButton.disabled && (dropdown.value || customInput.value.trim())) {
            selectPrompt();
        }
    });
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
    
    // Initialize submissions tracker
    submissions = {};
    
    // Set up auto-submission when timer expires
    startTimer(data.time_limit, () => {
        // Auto-submit any non-empty, non-submitted bribes
        autoSubmitPendingBribes();
    });

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
    
    // Display the player's prompt at the top of the voting screen
    const playerPromptElement = document.getElementById('voting-player-prompt');
    if (playerPromptElement) {
        playerPromptElement.textContent = data.player_prompt;
        playerPromptElement.classList.remove('hidden');
    }

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
    startTimer(data.time_limit, () => {
        // Auto-submit vote if one is selected but not submitted
        if (selectedVote && !document.getElementById('submit-vote-btn').disabled) {
            submitVote();
        }
    });
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

    // Show detailed vote results with prompts and bribes
    const voteResults = document.getElementById('vote-results');
    voteResults.innerHTML = '<h3>Round Results:</h3>';
    
    // Create a container for the detailed results
    const detailedResultsContainer = document.createElement('div');
    detailedResultsContainer.className = 'detailed-results-container';
    
    // Group results by player who received the prompt
    const resultsByPromptOwner = {};
    
    data.vote_results.forEach(result => {
        if (!resultsByPromptOwner[result.prompt_owner]) {
            resultsByPromptOwner[result.prompt_owner] = {
                prompt: result.prompt,
                winner: result.winner,
                winning_bribe: result.winning_bribe,
                bribe_type: result.bribe_type || 'text'
            };
        }
    });
    
    // Display each player's prompt and the winning bribe
    Object.keys(resultsByPromptOwner).forEach(promptOwner => {
        const result = resultsByPromptOwner[promptOwner];
        
        const resultCard = document.createElement('div');
        resultCard.className = 'result-card';
        
        // Create prompt section
        const promptSection = document.createElement('div');
        promptSection.className = 'prompt-section';
        promptSection.innerHTML = `
            <div class="prompt-owner">${promptOwner}'s prompt:</div>
            <div class="prompt-text">${result.prompt}</div>
        `;
        
        // Create winning bribe section
        const winningBribeSection = document.createElement('div');
        winningBribeSection.className = 'winning-bribe-section';
        
        // Handle different bribe types (text, image, gif)
        let bribeContent = '';
        if (result.bribe_type === 'image' || result.bribe_type === 'gif') {
            bribeContent = `<img src="${result.winning_bribe}" alt="Winning bribe" class="bribe-image">`;
        } else {
            bribeContent = `<div class="bribe-text">${result.winning_bribe}</div>`;
        }
        
        winningBribeSection.innerHTML = `
            <div class="winning-bribe-header">Winning bribe from <span class="winner-name">${result.winner}</span>:</div>
            <div class="bribe-content">${bribeContent}</div>
        `;
        
        // Assemble the card
        resultCard.appendChild(promptSection);
        resultCard.appendChild(winningBribeSection);
        detailedResultsContainer.appendChild(resultCard);
    });
    
    voteResults.appendChild(detailedResultsContainer);
    voteResults.classList.remove('hidden');

    // Show scoreboard
    displayScoreboard(data.scoreboard, 'scoreboard');

    // Add next round button for host if timer is disabled
    if (!data.timer_enabled && Authentication.isHost()) {
        // Create next round button
        const nextRoundBtn = document.createElement('button');
        nextRoundBtn.id = 'next-round-btn';
        nextRoundBtn.textContent = 'Continue to Next Round';
        nextRoundBtn.classList.add('action-button');
        nextRoundBtn.onclick = () => socket.emit('next_round');
        
        // Add button to scoreboard phase
        const scoreboardPhase = document.getElementById('scoreboard-phase');
        scoreboardPhase.appendChild(nextRoundBtn);
        
        updateStatus('You control when to advance to the next round');
    } else {
        updateStatus('Round complete!');
        if (data.timer_enabled) {
            startTimer(data.results_time || 5, 'Next round in: ');
        }
    }
    
    if (!data.timer_enabled && !Authentication.isHost()) {
        updateStatus('Waiting for host to start next round...');
    }
});

socket.on('host_controls_next_round', () => {
    if (Authentication.isHost()) {
        updateStatus('You control when to advance to the next round');
    } else {
        updateStatus('Waiting for host to start next round...');
    }
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
