// Voting phase event handlers
export function registerVotingHandlers(socket, GameState, hideAllScreens, updateStatus, startTimer, stopTimer, selectVote) {
    // Voting events
    socket.on('voting_phase', (data) => {
        hideAllScreens();
        document.getElementById('voting-phase').classList.remove('hidden');

        const votingOptions = document.getElementById('voting-options');
        votingOptions.innerHTML = '';
        window.selectedVote = null;
        
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
        startTimer(data.time_limit);
        document.getElementById('submit-vote-btn').disabled = true;
    });

    socket.on('vote_submitted', () => {
        updateStatus('Vote submitted! Waiting for results...');
        stopTimer();
    });
}
