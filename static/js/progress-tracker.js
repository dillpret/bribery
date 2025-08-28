/**
 * @fileoverview Progress Tracker Module - Tracks player submission status
 * @module progress-tracker
 * 
 * This module tracks and updates the UI to show progress in all interactive phases:
 * - Prompt selection phase
 * - Submission phase
 * - Voting phase
 * 
 * It provides detailed progress messages and status tracking for the player list.
 */

const ProgressTracker = {
    // Current phase information
    currentPhase: '',
    
    // Lists of player statuses for each phase
    promptSelectionStatus: {},
    submissionStatus: {},
    votingStatus: {},
    
    /**
     * Initialize the progress tracker
     */
    init: function() {
        // Reset all status tracking
        this.resetPhaseStatuses();
        
        // Register for phase change events
        document.addEventListener('gamePhaseChanged', (e) => {
            this.handlePhaseChange(e.detail.phase);
        });
    },
    
    /**
     * Handle phase changes - reset appropriate trackers
     * @param {string} phase - The new game phase
     */
    handlePhaseChange: function(phase) {
        this.currentPhase = phase;
        
        // Reset the appropriate phase tracker when entering a new phase
        if (phase === 'prompt_selection') {
            this.resetPhaseStatus('promptSelection');
        } else if (phase === 'submission') {
            this.resetPhaseStatus('submission');
        } else if (phase === 'voting') {
            this.resetPhaseStatus('voting');
        }
    },
    
    /**
     * Reset a specific phase's tracking status
     * @param {string} phase - The phase to reset
     */
    resetPhaseStatus: function(phase) {
        if (phase === 'promptSelection') {
            this.promptSelectionStatus = {};
        } else if (phase === 'submission') {
            this.submissionStatus = {};
        } else if (phase === 'voting') {
            this.votingStatus = {};
        }
    },
    
    /**
     * Reset all phase statuses
     */
    resetPhaseStatuses: function() {
        this.promptSelectionStatus = {};
        this.submissionStatus = {};
        this.votingStatus = {};
    },
    
    /**
     * Update player submission status for the current phase
     * @param {string} playerId - Player ID
     * @param {boolean} hasSubmitted - Whether the player has submitted
     */
    updatePlayerStatus: function(playerId, hasSubmitted) {
        if (this.currentPhase === 'prompt_selection') {
            this.promptSelectionStatus[playerId] = hasSubmitted;
        } else if (this.currentPhase === 'submission') {
            this.submissionStatus[playerId] = hasSubmitted;
        } else if (this.currentPhase === 'voting') {
            this.votingStatus[playerId] = hasSubmitted;
        }
        
        // Update any UI elements that show submission status
        this.updatePlayerListSubmissionStatus();
    },
    
    /**
     * Get current status object based on active phase
     * @returns {Object} Status object for current phase
     */
    getCurrentStatusObject: function() {
        if (this.currentPhase === 'prompt_selection') {
            return this.promptSelectionStatus;
        } else if (this.currentPhase === 'submission') {
            return this.submissionStatus;
        } else if (this.currentPhase === 'voting') {
            return this.votingStatus;
        }
        return {};
    },
    
    /**
     * Update player list with submission status
     */
    updatePlayerListSubmissionStatus: function() {
        // This function will be called when the socket handlers update player data
        // The actual update happens in the player-list-panel.js file
        const event = new CustomEvent('submissionStatusUpdated');
        document.dispatchEvent(event);
    },
    
    /**
     * Generate detailed progress message with player names for progress indicators
     * @param {Object} data - Progress data
     * @param {number} data.completed - Number of completed submissions
     * @param {number} data.total - Total number of expected submissions
     * @param {Array<string>} data.pendingPlayers - Names of players who haven't submitted
     * @returns {string} Formatted progress message
     */
    generateDetailedProgressMessage: function(data) {
        const completed = data.completed;
        const total = data.total;
        const pendingPlayers = data.pendingPlayers || [];
        
        // Basic message for most cases
        let message = `${completed}/${total} players finished`;
        
        // When almost done, show who we're waiting for
        if (completed >= total - 2 && pendingPlayers.length > 0) {
            if (pendingPlayers.length === 1) {
                message = `Waiting for ${pendingPlayers[0]}`;
            } else if (pendingPlayers.length === 2) {
                message = `Waiting for ${pendingPlayers[0]} and ${pendingPlayers[1]}`;
            }
        }
        
        return message;
    }
};

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
    ProgressTracker.init();
});

// Export as ES module
export default ProgressTracker;

// Add to window for backwards compatibility
window.ProgressTracker = ProgressTracker;
