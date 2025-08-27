// Additional event handlers for game end and non-existent games

// Handle case where game has ended
socket.on('game_ended', (data) => {
    console.log('Game has ended:', data);
    
    // Remove any existing error banners
    const existingBanner = document.getElementById('game-error-banner');
    if (existingBanner) {
        existingBanner.remove();
    }
    
    // Create error banner
    const banner = document.createElement('div');
    banner.id = 'game-error-banner';
    banner.className = 'game-error-banner';
    
    // Create banner content with specific game ended message
    banner.innerHTML = `
        <h2>Game Has Ended</h2>
        <p>The game you're trying to access has already finished.</p>
        <button id="return-home-btn" class="game-error-banner-button">Return to Home Page</button>
    `;
    
    // Add to body
    document.body.prepend(banner);
    
    // Add click handler for the return button
    document.getElementById('return-home-btn').addEventListener('click', () => {
        window.location.href = '/'; // Redirect to home page
    });
});

// Handle case where no game exists with the given ID
socket.on('game_not_found', (data) => {
    console.log('Game not found:', data);
    showGameNotFoundBanner();
});
