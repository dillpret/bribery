/**
 * Socket manager for Bribery game.
 * This module provides a centralized way to access the socket instance.
 */

// Access the global socket variable created by socket.io.min.js
let socketInstance;

// Attempt to get the global socket
if (typeof io !== 'undefined') {
    socketInstance = io();
} else {
    console.error('Socket.IO not found! Make sure socket.io.min.js is loaded first.');
    // Create a dummy socket to prevent errors
    socketInstance = {
        on: () => {},
        emit: () => {},
        disconnect: () => {}
    };
}

// Export the socket instance for use in modules
export const socket = socketInstance;

// Export a function to check if socket is properly initialized
export function isSocketInitialized() {
    return typeof socketInstance === 'object' && 
           typeof socketInstance.on === 'function' && 
           typeof socketInstance.emit === 'function';
}
