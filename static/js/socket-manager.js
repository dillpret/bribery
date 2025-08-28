/**
 * Socket manager for Bribery game.
 * This module provides a centralized way to access the socket instance.
 * @module socket-manager
 */

/**
 * Initialize and get the socket instance
 * @returns {Object} Socket.IO instance
 */
function initializeSocket() {
    // Access the global socket variable created by socket.io.min.js
    if (typeof io !== 'undefined') {
        return io();
    } else {
        console.error('Socket.IO not found! Make sure socket.io.min.js is loaded first.');
        // Create a dummy socket to prevent errors
        return {
            on: () => {},
            emit: () => {},
            disconnect: () => {}
        };
    }
}

// Initialize the socket instance
const socketInstance = initializeSocket();

// Export the socket instance for use in ES modules
export const socket = socketInstance;

// Also expose socket globally for backwards compatibility
// This helps any scripts that haven't been converted to ES modules yet
window.socketManager = {
    socket: socketInstance
};

// Export a function to check if socket is properly initialized
export function isSocketInitialized() {
    return typeof socketInstance === 'object' && 
           typeof socketInstance.on === 'function' && 
           typeof socketInstance.emit === 'function';
}

// Log successful initialization
console.log('Socket manager initialized successfully');
