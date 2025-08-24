// Results and game flow event handlers
export function registerResultsHandlers(socket, GameState, hideAllScreens, updateStatus, startTimer, stopTimer, displayScoreboard, Authentication, gameId) {
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

        if (Authentication.isHost()) {
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
        window.currentTargets = [];
        window.submissions = {};
        window.selectedVote = null;

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
}
