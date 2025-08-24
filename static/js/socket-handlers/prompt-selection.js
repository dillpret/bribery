// Prompt selection event handlers
export function registerPromptHandlers(socket, GameState, hideAllScreens, updateStatus, startTimer, updatePromptButtonState) {
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
}
