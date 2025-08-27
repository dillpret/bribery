// Add these event handlers to improve connection management

// Connection established
socket.on('connect', () => {
    console.log('Socket connected with ID:', socket.id);
    const authState = GameState.get('auth');
    
    // Automatically rejoin if we have credentials
    if (authState && authState.username && authState.gameId) {
        console.log('Auto-rejoining game after connection');
        socket.emit('join_game', {
            game_id: authState.gameId,
            username: authState.username,
            player_id: authState.playerId  // Send stored player ID if available
        });
    }
});

// Connection lost - show reconnection UI
socket.on('disconnect', () => {
    console.log('Socket disconnected, attempting to reconnect...');
    updateStatus('Connection lost. Attempting to reconnect...');
    
    // Show a non-intrusive reconnection message
    const reconnectOverlay = document.createElement('div');
    reconnectOverlay.id = 'reconnect-overlay';
    reconnectOverlay.innerHTML = `
        <div class="reconnect-message">
            <div class="waiting-spinner"></div>
            <p>Connection lost. Reconnecting...</p>
        </div>
    `;
    document.body.appendChild(reconnectOverlay);
});

// Reconnection successful - clear reconnection UI
socket.on('reconnect', () => {
    console.log('Socket reconnected!');
    updateStatus('Reconnected to game');
    
    // Remove reconnection overlay if it exists
    const overlay = document.getElementById('reconnect-overlay');
    if (overlay) {
        overlay.remove();
    }
});

// Connection error - show user-friendly error banner
socket.on('connect_error', (error) => {
    console.error('Connection error:', error);
    showGameNotFoundBanner();
});

// Helper function to display a user-friendly game not found banner
function showGameNotFoundBanner() {
    // Remove any existing error banners
    const existingBanner = document.getElementById('game-error-banner');
    if (existingBanner) {
        existingBanner.remove();
    }
    
    // Create error banner
    const banner = document.createElement('div');
    banner.id = 'game-error-banner';
    banner.className = 'game-error-banner';
    
    // Create banner content
    banner.innerHTML = `
        <h2>Game Not Found</h2>
        <p>The game you're trying to access doesn't exist or has ended. This can happen when:</p>
        <ul>
            <li>The game code was entered incorrectly</li>
            <li>The game has already finished</li>
            <li>The server was restarted</li>
        </ul>
        <button id="return-home-btn" class="game-error-banner-button">Return to Home Page</button>
    `;
    
    // Add to body
    document.body.prepend(banner); // Prepend to body to ensure it's at the top
    
    // Add click handler for the return button
    document.getElementById('return-home-btn').addEventListener('click', () => {
        window.location.href = '/'; // Redirect to home page
    });
}

// Make function available globally
window.showGameNotFoundBanner = showGameNotFoundBanner;

// Add this to game.css
/* 
#reconnect-overlay {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background-color: rgba(0, 0, 0, 0.7);
    z-index: 9999;
    display: flex;
    justify-content: center;
    align-items: center;
}

.reconnect-message {
    background-color: white;
    padding: 20px;
    border-radius: 8px;
    text-align: center;
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
}
*/
