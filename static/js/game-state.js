// Centralized state management for Bribery Game
// Handles both localStorage persistence and runtime state

/**
 * GameState - Centralized state management module
 * 
 * This module provides structured state management for the Bribery game:
 * - Handles localStorage persistence
 * - Provides consistent API for state operations
 * - Separates concerns: authentication, game state, user preferences
 * - Implements proper error handling and validation
 */

// State namespaces to organize different types of state
const STATE_TYPES = {
    AUTH: 'auth',        // Authentication state (playerId, username, isHost)
    GAME: 'game',        // Game state (currentTargets, submissions, etc.)
    UI: 'ui',            // UI state (selected options, form values, etc.)
    PREFERENCES: 'prefs' // User preferences (if added in future)
};

// Internal state storage (in-memory)
const _state = {
    [STATE_TYPES.AUTH]: {
        playerId: null,
        username: null,
        isHost: false,
        gameId: null
    },
    [STATE_TYPES.GAME]: {
        currentTargets: [],
        submissions: {},
        selectedVote: null,
        currentRound: 0,
        totalRounds: 0
    },
    [STATE_TYPES.UI]: {
        activeScreen: null
    },
    [STATE_TYPES.PREFERENCES]: {}
};

/**
 * Get localStorage key for the specified game ID
 * @param {string} gameId - Game identifier
 * @returns {string} - localStorage key
 */
function getStorageKey(gameId) {
    return `bribery_game_${gameId}`;
}

/**
 * Save authentication state to localStorage
 * @param {string} gameId - Game ID
 */
function persistAuthState(gameId) {
    if (!gameId) gameId = _state[STATE_TYPES.AUTH].gameId;
    if (!gameId) return; // Can't persist without gameId
    
    const storageKey = getStorageKey(gameId);
    const authState = _state[STATE_TYPES.AUTH];
    
    localStorage.setItem(storageKey, JSON.stringify({
        playerId: authState.playerId,
        username: authState.username,
        isHost: authState.isHost,
        timestamp: Date.now()
    }));
}

/**
 * Load authentication state from localStorage
 * @param {string} gameId - Game ID
 * @returns {boolean} - Whether state was successfully loaded
 */
function loadAuthState(gameId) {
    if (!gameId) return false;
    
    const storageKey = getStorageKey(gameId);
    const storedData = localStorage.getItem(storageKey);
    
    if (!storedData) return false;
    
    try {
        const parsedData = JSON.parse(storedData);
        setState(STATE_TYPES.AUTH, {
            playerId: parsedData.playerId || null,
            username: parsedData.username || null,
            isHost: !!parsedData.isHost,
            gameId: gameId
        });
        return true;
    } catch (error) {
        console.error('Error loading auth state:', error);
        return false;
    }
}

/**
 * Set state values in the specified namespace
 * @param {string} namespace - State namespace (auth, game, ui, prefs)
 * @param {object} values - Values to set
 */
function setState(namespace, values) {
    if (!STATE_TYPES[namespace.toUpperCase()]) {
        console.error(`Invalid state namespace: ${namespace}`);
        return;
    }
    
    const ns = STATE_TYPES[namespace.toUpperCase()];
    _state[ns] = { ..._state[ns], ...values };
    
    // Auto-persist auth state changes
    if (ns === STATE_TYPES.AUTH && _state[ns].gameId) {
        persistAuthState(_state[ns].gameId);
    }
}

/**
 * Get state from the specified namespace
 * @param {string} namespace - State namespace (auth, game, ui, prefs)
 * @param {string|null} key - Specific key to retrieve (null for entire namespace)
 * @returns {*} - Requested state
 */
function getState(namespace, key = null) {
    if (!STATE_TYPES[namespace.toUpperCase()]) {
        console.error(`Invalid state namespace: ${namespace}`);
        return null;
    }
    
    const ns = STATE_TYPES[namespace.toUpperCase()];
    
    if (key === null) {
        // Return a copy of the entire namespace to prevent direct mutation
        return { ..._state[ns] };
    }
    
    return _state[ns][key];
}

/**
 * Clear all game state but preserve authentication if keepAuth=true
 * @param {boolean} keepAuth - Whether to preserve auth state
 */
function clearGameState(keepAuth = false) {
    // Reset game and UI state
    _state[STATE_TYPES.GAME] = {
        currentTargets: [],
        submissions: {},
        selectedVote: null,
        currentRound: 0,
        totalRounds: 0
    };
    
    _state[STATE_TYPES.UI] = {
        activeScreen: null
    };
    
    // Optionally clear auth state too
    if (!keepAuth) {
        _state[STATE_TYPES.AUTH] = {
            playerId: null,
            username: null,
            isHost: false,
            gameId: null
        };
    }
}

/**
 * Initialize auth state from existing localStorage or prompt
 * @param {string} gameId - Game ID
 * @returns {object} - Current auth state
 */
function initializeAuthState(gameId) {
    const wasLoaded = loadAuthState(gameId);
    
    if (!wasLoaded) {
        // Only prompt if we don't have stored credentials
        const username = prompt('Enter your name:');
        // If user cancels or enters empty username, redirect to home page
        if (!username || username.trim() === '') {
            window.location.href = '/?message=' + encodeURIComponent('Name is required to join a game');
            return getState(STATE_TYPES.AUTH);
        }
        
        setState(STATE_TYPES.AUTH, {
            username: username.trim(),
            gameId: gameId
        });
    }
    
    return getState(STATE_TYPES.AUTH);
}

/**
 * Update auth state from server response
 * @param {object} data - Server response data
 */
function updateAuthFromServer(data) {
    // Update with server-provided values while preserving locally set values if they exist
    const currentAuth = getState(STATE_TYPES.AUTH);
    
    const updatedAuth = {
        // Always use server-provided player_id as the source of truth
        playerId: data.player_id || currentAuth.playerId,
        
        // Username strategy: keep local value if exists, otherwise use server's
        username: currentAuth.username || data.username,
        
        // Host status: if either says we're host, we're host
        isHost: !!currentAuth.isHost || !!data.is_host,
        
        // Game ID: prefer server value as source of truth, fall back to local
        gameId: data.game_id || currentAuth.gameId
    };
    
    // Only update if we have meaningful data
    if (updatedAuth.playerId && updatedAuth.username && updatedAuth.gameId) {
        setState(STATE_TYPES.AUTH, updatedAuth);
        console.log('Updated auth state from server:', updatedAuth);
    }
}

// Export the public API
window.GameState = {
    init: initializeAuthState,
    get: getState,
    set: setState,
    update: updateAuthFromServer,
    clear: clearGameState,
    persist: persistAuthState
};
