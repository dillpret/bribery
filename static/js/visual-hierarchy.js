// Enhanced visual hierarchy implementation

// Track current game phase
let currentGamePhase = 0;
const GAME_PHASES = ['lobby', 'prompt-selection', 'submission-phase', 'voting-phase', 'scoreboard-phase', 'final-results'];

// Add phase indicator pills to relevant phases
function initializePhaseIndicators() {
    // Create phase indicator container
    const phaseIndicatorHTML = `
        <div class="phase-indicator-container">
            <div class="phase-indicator-pill" data-phase="prompt-selection"></div>
            <div class="phase-indicator-pill" data-phase="submission-phase"></div>
            <div class="phase-indicator-pill" data-phase="voting-phase"></div>
            <div class="phase-indicator-pill" data-phase="scoreboard-phase"></div>
        </div>
    `;
    
    // Add to each game phase container
    document.querySelectorAll('#prompt-selection .phase-explanation, #submission-phase .phase-explanation, #voting-phase .phase-explanation, #scoreboard-phase .phase-explanation')
        .forEach(el => {
            el.insertAdjacentHTML('afterend', phaseIndicatorHTML);
        });
        
    // Add phase-specific classes to containers
    document.getElementById('prompt-selection').classList.add('prompt-selection');
    document.getElementById('submission-phase').classList.add('submission-phase');
    document.getElementById('voting-phase').classList.add('voting-phase');
    document.getElementById('scoreboard-phase').classList.add('scoreboard-phase');
}

// Update phase indicators based on current phase
function updatePhaseIndicators(phase) {
    currentGamePhase = GAME_PHASES.indexOf(phase);
    if (currentGamePhase <= 0) return; // Skip for lobby
    
    document.querySelectorAll('.phase-indicator-pill').forEach((pill, index) => {
        // Convert to 1-based index for matching with phases (skipping lobby)
        const pillPhase = index + 1;
        
        // Reset all classes
        pill.classList.remove('active', 'completed');
        
        // Phase 1 = prompt-selection, 2 = submission, 3 = voting, 4 = scoreboard
        if (pillPhase < currentGamePhase) {
            pill.classList.add('completed');
        } else if (pillPhase === currentGamePhase) {
            pill.classList.add('active');
        }
    });
}

// Enhanced button styling based on action type
function styleActionButtons() {
    // Start game button (primary action in lobby)
    const startGameBtn = document.getElementById('start-game-btn');
    if (startGameBtn) {
        startGameBtn.classList.add('primary-button');
    }
    
    // Vote submission (primary action in voting phase)
    const submitVoteBtn = document.getElementById('submit-vote-btn');
    if (submitVoteBtn) {
        submitVoteBtn.classList.add('primary-button');
    }
    
    // Prompt confirmation (primary action in prompt phase)
    const confirmPromptBtn = document.getElementById('confirm-prompt-btn');
    if (confirmPromptBtn) {
        confirmPromptBtn.classList.add('primary-button');
    }
    
    // Final results actions
    const finalControlsButtons = document.querySelectorAll('#host-final-controls button');
    if (finalControlsButtons.length > 0) {
        finalControlsButtons[0].classList.add('primary-button'); // Return to Lobby
    }
}

// Enhanced score display with animations
function enhanceScoreDisplay() {
    // Add score change indicators
    document.querySelectorAll('.score-item').forEach(item => {
        // Check if this is a score that changed this round
        if (item.textContent.includes('+')) {
            // Add animation class
            item.classList.add('score-changed');
            
            // Extract the points gained
            const pointsText = item.textContent.match(/\+(\d+(\.\d+)?)/);
            if (pointsText && pointsText[0]) {
                // Create and append the score change indicator
                const scoreChange = document.createElement('span');
                scoreChange.className = 'score-change';
                scoreChange.textContent = pointsText[0];
                item.appendChild(scoreChange);
            }
        }
    });
}

// Enhanced podium for final results
function createPodium(finalScores) {
    // Only create if we're on final results and have scores
    if (!document.getElementById('final-results').classList.contains('hidden') && finalScores) {
        // Get top 3 players
        const topPlayers = finalScores.slice(0, 3);
        if (topPlayers.length < 1) return;
        
        // Create podium HTML
        const podiumHTML = `
            <div class="podium-container">
                ${topPlayers.length >= 2 ? `
                <div class="podium-place podium-second">
                    <div class="podium-player">
                        <div class="podium-medal">🥈</div>
                        <div class="podium-name">${topPlayers[1].name}</div>
                        <div class="podium-score">${topPlayers[1].score}</div>
                    </div>
                </div>` : ''}
                
                <div class="podium-place podium-first">
                    <div class="podium-player">
                        <div class="podium-medal">🏆</div>
                        <div class="podium-name">${topPlayers[0].name}</div>
                        <div class="podium-score">${topPlayers[0].score}</div>
                    </div>
                </div>
                
                ${topPlayers.length >= 3 ? `
                <div class="podium-place podium-third">
                    <div class="podium-player">
                        <div class="podium-medal">🥉</div>
                        <div class="podium-name">${topPlayers[2].name}</div>
                        <div class="podium-score">${topPlayers[2].score}</div>
                    </div>
                </div>` : ''}
            </div>
        `;
        
        // Add to final results, before the final scoreboard
        const finalScoreboard = document.getElementById('final-scoreboard');
        if (finalScoreboard) {
            finalScoreboard.insertAdjacentHTML('beforebegin', podiumHTML);
            
            // Add confetti for celebration
            createConfetti();
        }
    }
}

// Create confetti effect for winners
function createConfetti() {
    const confettiContainer = document.createElement('div');
    confettiContainer.className = 'confetti-container';
    document.body.appendChild(confettiContainer);
    
    // Create confetti pieces
    const colors = ['#ff6b6b', '#48dbfb', '#1dd1a1', '#5f27cd', '#feca57'];
    const confettiCount = 100;
    
    for (let i = 0; i < confettiCount; i++) {
        const confetti = document.createElement('div');
        confetti.className = 'confetti';
        confetti.style.left = `${Math.random() * 100}%`;
        confetti.style.width = `${Math.random() * 10 + 5}px`;
        confetti.style.height = `${Math.random() * 10 + 5}px`;
        confetti.style.background = colors[Math.floor(Math.random() * colors.length)];
        confetti.style.borderRadius = Math.random() > 0.5 ? '50%' : '0';
        confetti.style.animationDuration = `${Math.random() * 3 + 2}s`;
        confetti.style.animationDelay = `${Math.random() * 5}s`;
        
        confettiContainer.appendChild(confetti);
    }
    
    // Remove confetti after 10 seconds
    setTimeout(() => {
        confettiContainer.remove();
    }, 10000);
}

// Initialize enhanced visual features when document is ready
document.addEventListener('DOMContentLoaded', function() {
    initializePhaseIndicators();
    styleActionButtons();
    
    // Listen for phase changes by observing the display property changes
    GAME_PHASES.forEach(phase => {
        if (phase === 'lobby') return; // Skip lobby
        
        const phaseElement = document.getElementById(phase);
        if (!phaseElement) return;
        
        // Use MutationObserver to detect when phases become visible
        const observer = new MutationObserver(mutations => {
            mutations.forEach(mutation => {
                if (mutation.attributeName === 'class') {
                    const isHidden = phaseElement.classList.contains('hidden');
                    if (!isHidden) {
                        updatePhaseIndicators(phase);
                        
                        // Special handling for scoreboard phase
                        if (phase === 'scoreboard-phase') {
                            setTimeout(enhanceScoreDisplay, 500);
                        }
                        
                        // Special handling for final results
                        if (phase === 'final-results') {
                            // Get final scores data from the DOM
                            const scoreItems = document.querySelectorAll('#final-scoreboard .score-item');
                            const finalScores = Array.from(scoreItems).map(item => {
                                const name = item.querySelector('.player-name').textContent;
                                const score = parseFloat(item.querySelector('.player-score').textContent);
                                return { name, score };
                            });
                            
                            setTimeout(() => createPodium(finalScores), 500);
                        }
                    }
                }
            });
        });
        
        observer.observe(phaseElement, { attributes: true });
    });
});
