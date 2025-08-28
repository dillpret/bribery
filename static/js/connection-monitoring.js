// Connection monitoring for mobile and desktop browsers
// Handles page visibility changes and reconnection

// Track connection state
let isConnected = socket.connected;
let hasConnectedBefore = false;
let reconnectionAttempts = 0;
const MAX_RECONNECTION_ATTEMPTS = 3;

// Update the UI connection status indicator
function updateConnectionStatus(status) {
    const statusElement = document.getElementById('connection-status');
    if (!statusElement) return;
    
    // Remove all status classes
    statusElement.classList.remove('connected', 'disconnected', 'reconnecting');
    
    // Add appropriate class
    statusElement.classList.add(status);
    statusElement.setAttribute('title', status.charAt(0).toUpperCase() + status.slice(1));
}

// Handle visibility change (when user tabs back to the app)
document.addEventListener('visibilitychange', () => {
    console.log('Visibility changed. Document hidden:', document.hidden);
    
    // If the page becomes visible again and socket is disconnected
    if (!document.hidden && !socket.connected && hasConnectedBefore) {
        console.log('Page visible again and socket disconnected. Attempting manual reconnect...');
        attemptManualReconnect();
    }
});

// For iOS Safari which doesn't always trigger visibilitychange correctly
window.addEventListener('focus', () => {
    console.log('Window focused. Socket connected:', socket.connected);
    
    // If socket is disconnected when window gets focus
    if (!socket.connected && hasConnectedBefore) {
        console.log('Window focused but socket disconnected. Attempting manual reconnect...');
        // Update UI first
        updateConnectionStatus('reconnecting');
        showReconnectOverlay();
        // Then try to reconnect
        setTimeout(attemptManualReconnect, 300);
    }
});

// For Android browsers that might not trigger the other events reliably
window.addEventListener('pageshow', (event) => {
    // If the page is being restored from bfcache (back-forward cache)
    if (event.persisted && !socket.connected && hasConnectedBefore) {
        console.log('Page restored from cache. Attempting manual reconnect...');
        attemptManualReconnect();
    }
});

// Additional network status monitoring
window.addEventListener('online', () => {
    console.log('Device came online. Attempting reconnect...');
    attemptManualReconnect();
});

// Add extra socket event listeners
socket.on('connect', () => {
    console.log('Socket connected!');
    isConnected = true;
    hasConnectedBefore = true;
    reconnectionAttempts = 0;
    updateConnectionStatus('connected');
    
    // Remove reconnection overlay if it exists
    removeReconnectOverlay();
});

socket.on('disconnect', () => {
    console.log('Socket disconnected!');
    isConnected = false;
    updateConnectionStatus('disconnected');
    
    // Show reconnecting overlay if it doesn't exist yet
    showReconnectOverlay();
});

socket.on('reconnecting', (attemptNumber) => {
    console.log(`Socket reconnecting, attempt ${attemptNumber}`);
    updateConnectionStatus('reconnecting');
});

socket.on('reconnect_failed', () => {
    console.log('Socket reconnection failed after all attempts!');
    // We'll handle manual reconnection when visibility changes
});

// Manual reconnection function
function attemptManualReconnect() {
    reconnectionAttempts++;
    
    if (reconnectionAttempts > MAX_RECONNECTION_ATTEMPTS) {
        console.log('Max reconnection attempts reached. Reloading page...');
        window.location.reload();
        return;
    }
    
    console.log(`Manual reconnection attempt ${reconnectionAttempts}/${MAX_RECONNECTION_ATTEMPTS}`);
    
    // Force socket to reconnect by closing and opening
    if (socket.io && !socket.connected) {
        console.log('Manually reopening socket connection...');
        
        // First, ensure we have valid authentication state
        const authState = GameState.get('auth');
        if (!authState || !authState.gameId || !authState.username) {
            console.error('Missing authentication state for reconnection');
            showFailedReconnectMessage();
            return;
        }
        
        // Try the built-in Socket.IO reconnect first
        socket.io.reconnect();
        
        // Check if connection is successful after a short delay
        setTimeout(() => {
            if (!socket.connected) {
                console.log('Built-in reconnect unsuccessful, forcing disconnect and connect cycle');
                
                // If still not connected, try a more aggressive approach
                // Close existing connection
                socket.close();
                
                // Reopen after a short delay
                setTimeout(() => {
                    socket.open();
                    
                    // Final check - if we still can't connect, queue a page reload
                    setTimeout(() => {
                        if (!socket.connected && reconnectionAttempts >= MAX_RECONNECTION_ATTEMPTS) {
                            console.log('Failed to reconnect after multiple attempts. Suggesting page refresh...');
                            showFailedReconnectMessage();
                        }
                    }, 3000);
                }, 1000);
            }
        }, 2000);
    }
}

// UI functions for reconnection state
function showReconnectOverlay() {
    // Check if overlay already exists
    if (document.getElementById('reconnect-overlay')) return;
    
    const reconnectOverlay = document.createElement('div');
    reconnectOverlay.id = 'reconnect-overlay';
    reconnectOverlay.innerHTML = `
        <div class="reconnect-message">
            <div class="waiting-spinner"></div>
            <p>Connection lost. Reconnecting...</p>
        </div>
    `;
    document.body.appendChild(reconnectOverlay);
}

function removeReconnectOverlay() {
    const overlay = document.getElementById('reconnect-overlay');
    if (overlay) {
        overlay.remove();
    }
}

function showFailedReconnectMessage() {
    // Transform the reconnect overlay to show refresh option
    const overlay = document.getElementById('reconnect-overlay');
    if (overlay) {
        overlay.innerHTML = `
            <div class="reconnect-message">
                <p>Unable to reconnect to the game.</p>
                <button id="manual-refresh-btn" class="primary-button">Refresh Page</button>
            </div>
        `;
        
        // Add event listener for the refresh button
        document.getElementById('manual-refresh-btn').addEventListener('click', () => {
            window.location.reload();
        });
    }
}

// Initialize connection monitoring
updateConnectionStatus(socket.connected ? 'connected' : 'disconnected');
