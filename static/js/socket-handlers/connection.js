// Connection and lobby event handlers
export function registerConnectionHandlers(socket, GameState, hideAllScreens, updateStatus, Authentication) {
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

    socket.on('error', (data) => {
        alert('Error: ' + data.message);
    });
}
