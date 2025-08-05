// Socket event handlers for game state management

// Connection and lobby events
socket.on('joined_game', (data) => {
    playerId = data.player_id;
    isHost = data.is_host;
    updateStatus('Connected to game');
    
    if (data.game_state === 'lobby') {
        hideAllScreens();
        document.getElementById('lobby').classList.remove('hidden');
    } else {
        hideAllScreens();
        document.getElementById('waiting-screen').classList.remove('hidden');
    }
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
    
    if (isHost) {
        document.getElementById('host-controls').classList.remove('hidden');
        const startBtn = document.getElementById('start-game-btn');
        startBtn.disabled = !data.can_start;
        startBtn.textContent = data.can_start ? 'Start Game' : 'Need at least 3 players';
    }
    
    updateStatus(`${data.player_count} players in lobby`);
});

// Prompt selection events
socket.on('prompt_selection_started', (data) => {
    hideAllScreens();
    document.getElementById('prompt-selection').classList.remove('hidden');
    
    document.getElementById('prompt-round-title').textContent = `Round ${data.round} of ${data.total_rounds}`;
    
    const promptSelect = document.getElementById('prompt-dropdown');
    promptSelect.innerHTML = '<option value="">Choose a prompt...</option>';
    
    data.available_prompts.forEach(prompt => {
        const option = document.createElement('option');
        option.value = prompt;
        option.textContent = prompt;
        promptSelect.appendChild(option);
    });
    
    const customOption = document.createElement('option');
    customOption.value = 'custom';
    customOption.textContent = 'Custom Prompt...';
    promptSelect.appendChild(customOption);
    
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
                <div class="drag-drop-area" id="drop-${target.id}">
                    Or drag and drop an image here
                </div>
                <button class="submit-btn" onclick="submitTargetBribe('${target.id}')">
                    Submit Bribe
                </button>
            </div>
        `;
        container.appendChild(targetEl);
        
        setupDragDrop(target.id);
    });
});

socket.on('bribe_submitted', (data) => {
    const button = document.querySelector(`button[onclick="submitTargetBribe('${data.target_id}')"]`);
    if (button) {
        button.textContent = 'Submitted ✓';
        button.disabled = true;
        button.style.background = '#28a745';
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
    
    updateStatus('Vote for your favorite bribe!');
    startTimer(data.time_limit);
    document.getElementById('submit-vote-btn').disabled = true;
});

socket.on('vote_submitted', () => {
    updateStatus('Vote submitted! Waiting for results...');
    stopTimer();
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
});

socket.on('game_restarted', () => {
    hideAllScreens();
    document.getElementById('lobby').classList.remove('hidden');
    updateStatus('Game restarted - back to lobby');
    stopTimer();
});

socket.on('error', (data) => {
    alert('Error: ' + data.message);
});
