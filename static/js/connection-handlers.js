// Basic connection handlers
// More advanced connection monitoring is in connection-monitoring.js

// Connection established - handle rejoining
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

// Basic update status on reconnect
socket.on('reconnect', () => {
    console.log('Socket.IO built-in reconnect event triggered');
    updateStatus('Reconnected to game');
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
