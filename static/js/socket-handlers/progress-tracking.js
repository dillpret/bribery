// Progress tracking event handlers with enhanced player tracking
import ProgressTracker from '../progress-tracker.js';

export function registerProgressHandlers(socket) {
    // Prompt selection progress tracking
    socket.on('prompt_selection_progress', (data) => {
        const progressText = document.getElementById('prompt-selection-progress-text');
        const progressContainer = document.getElementById('prompt-selection-progress');

        if (progressText) {
            // Generate detailed message with player names when appropriate
            progressText.textContent = ProgressTracker.generateDetailedProgressMessage(data);

            // Style the progress indicator based on completion
            if (data.completed === data.total) {
                progressContainer.classList.add('waiting');
            } else {
                progressContainer.classList.remove('waiting');
            }
        }
        
        // Update player status tracking
        if (data.playerStatuses) {
            Object.keys(data.playerStatuses).forEach(playerId => {
                ProgressTracker.updatePlayerStatus(playerId, data.playerStatuses[playerId]);
            });
        }
    });

    // Submission progress tracking
    socket.on('submission_progress', (data) => {
        const progressText = document.getElementById('submission-progress-text');
        const progressContainer = document.getElementById('submission-progress');

        if (progressText) {
            // Generate detailed message with player names when appropriate
            progressText.textContent = ProgressTracker.generateDetailedProgressMessage(data);

            // Style the progress indicator based on completion
            if (data.completed === data.total) {
                progressContainer.classList.add('waiting');
            } else {
                progressContainer.classList.remove('waiting');
            }
        }
        
        // Update player status tracking
        if (data.playerStatuses) {
            Object.keys(data.playerStatuses).forEach(playerId => {
                ProgressTracker.updatePlayerStatus(playerId, data.playerStatuses[playerId]);
            });
        }
    });

    // Voting progress tracking
    socket.on('voting_progress', (data) => {
        const progressText = document.getElementById('voting-progress-text');
        const progressContainer = document.getElementById('voting-progress');

        if (progressText) {
            // Generate detailed message with player names when appropriate
            progressText.textContent = ProgressTracker.generateDetailedProgressMessage(data);

            // Style the progress indicator based on completion
            if (data.completed === data.total) {
                progressContainer.classList.add('waiting');
            } else {
                progressContainer.classList.remove('waiting');
            }
        }
        
        // Update player status tracking
        if (data.playerStatuses) {
            Object.keys(data.playerStatuses).forEach(playerId => {
                ProgressTracker.updatePlayerStatus(playerId, data.playerStatuses[playerId]);
            });
        }
    });
    
    // Phase change handling
    socket.on('game_phase', (data) => {
        // Update the progress tracker with the new phase
        ProgressTracker.handlePhaseChange(data.phase);
    });
}
