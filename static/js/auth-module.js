/**
 * Authentication Module for Bribery Game
 * 
 * Handles all user authentication and session management:
 * - Username collection and validation
 * - Session persistence (localStorage)
 * - Connection and reconnection flows
 * - Host vs player role management
 */

// Central authentication state management
const Authentication = (function() {
    // Private storage
    const _state = {
        username: null,
        playerId: null,
        gameId: null,
        isHost: false
    };
    
    /**
     * Get storage key for a specific game
     * @param {string} gameId - The game identifier
     * @returns {string} - localStorage key
     */
    function _getStorageKey(gameId) {
        return `bribery_game_${gameId}`;
    }
    
    /**
     * Save current authentication state to localStorage
     * @returns {boolean} - Whether state was saved successfully
     */
    function _persistState() {
        if (!_state.gameId) return false;
        
        const storageKey = _getStorageKey(_state.gameId);
        try {
            localStorage.setItem(storageKey, JSON.stringify({
                username: _state.username,
                playerId: _state.playerId,
                isHost: _state.isHost,
                timestamp: Date.now()
            }));
            return true;
        } catch (error) {
            console.warn('Failed to save authentication state:', error);
            return false;
        }
    }
    
    /**
     * Validate username input
     * @param {string} username - Username to validate
     * @returns {boolean} - Whether username is valid
     */
    function _validateUsername(username) {
        return username && username.trim().length > 0;
    }
    
    // Public API
    return {
        /**
         * Set up host authentication
         * @param {string} username - Host username
         * @param {string} gameId - Created game ID
         * @param {string} playerId - Server-assigned player ID
         */
        setupHost: function(username, gameId, playerId = null) {
            if (!_validateUsername(username)) return false;
            
            _state.username = username.trim();
            _state.gameId = gameId;
            _state.isHost = true;
            _state.playerId = playerId;
            
            _persistState();
            return true;
        },
        
        /**
         * Set up player authentication
         * @param {string} username - Player username
         * @param {string} gameId - Game ID to join
         */
        setupPlayer: function(username, gameId) {
            if (!_validateUsername(username)) return false;
            
            _state.username = username.trim();
            _state.gameId = gameId.toUpperCase();
            _state.isHost = false;
            
            _persistState();
            return true;
        },
        
        /**
         * Update authentication with server response
         * @param {Object} data - Server response data
         */
        updateFromServer: function(data) {
            if (data.player_id) _state.playerId = data.player_id;
            if (data.game_id) _state.gameId = data.game_id;
            
            // Only update these if we don't have them already
            if (!_state.username && data.username) _state.username = data.username;
            
            // Special case for host flag - keep it if we're already host
            if (!_state.isHost && data.is_host) _state.isHost = true;
            
            _persistState();
        },
        
        /**
         * Get current authentication state
         * @returns {Object} - Current state
         */
        getState: function() {
            return { ..._state }; // Return copy to prevent direct mutation
        },
        
        /**
         * Clear authentication state
         */
        clear: function() {
            if (_state.gameId) {
                try {
                    localStorage.removeItem(_getStorageKey(_state.gameId));
                } catch (error) {
                    console.warn('Failed to clear authentication state from localStorage:', error);
                }
            }
            
            _state.username = null;
            _state.playerId = null;
            _state.gameId = null;
            _state.isHost = false;
        }
    };
})();

// Initialize on page load if needed
document.addEventListener('DOMContentLoaded', function() {
    // Any initialization code can go here
});
