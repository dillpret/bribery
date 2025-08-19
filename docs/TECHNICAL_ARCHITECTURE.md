# Technical Architecture Reference

This document provides essential technical implementation details to understand the codebase structure, component relationships, and key user flows.

## Frontend Component Structure

```
Frontend Components Map:
- User Authentication (Spans across multiple files)
  - index.html: Initial login forms and localStorage setup for hosts/joiners
  - game-core.js: Game initialization and session reconnection
  - socket-handlers.js: Session maintenance and state synchronization

- Game UI Components
  - Lobby UI: lobby section in game.html, styled by components/lobby.css
  - Prompt Selection: prompt-selection section in game.html
  - Submission Phase: submission-phase section in game.html
  - Voting Phase: voting-phase section in game.html
  - Scoreboard: scoreboard-phase section in game.html
  - Final Results: final-results section in game.html

- Game Logic
  - game-core.js: Core state variables and initialization
  - socket-handlers.js: Socket event processing and state updates
  - ui-handlers.js: User interaction processing (clicks, inputs, etc.)

- Backend Services (Socket Handlers)
  - socket_handlers.py: All socket event handling for game actions
  - game_manager.py: Game state management and session tracking
  - player_session.py: Player session representation
  - game.py: Core game logic and state machine
```

## Authentication Flows

```
New User Flow:
1. User enters username + game ID on index.html join form
2. Username stored in localStorage with game ID as key
3. Socket 'join_game' event sent with username and game ID
4. Server creates new player with username, returns player ID
5. Client stores player ID in localStorage for future reconnection
6. User redirected to game.html

Host Creation Flow:
1. User enters username + settings on index.html host form
2. Socket 'create_game' event sent with username and settings
3. Server creates game and host player, returns game ID and player ID
4. Client stores username + host flag in localStorage
5. User redirected to game.html after "Go to Lobby" click

Reconnection Flow:
1. On page load/refresh, game-core.js checks localStorage for credentials
2. If found, sends stored player ID with 'join_game' event
3. Server validates player ID, restores session if valid
4. If not found, prompts for username as fallback
5. Server attempts username matching for existing player

Mid-Game Join Flow:
1. New player joins with standard authentication
2. Server detects game in progress (state != "lobby")
3. Emits 'midgame_waiting' event to new player
4. Player shown waiting screen until next round
5. Player included in next round when current round ends
```

## State Management

```
Client-Side State:
- LocalStorage: Persistent credentials and game association
  - Key Pattern: `bribery_game_${gameId}`
  - Values: {username, playerId, isHost, timestamp}
  
- Runtime State (game-core.js):
  - playerId: Current player's ID from server
  - isHost: Host status flag
  - currentTargets: Current round targets for bribes
  - submissions: Map of bribe content by target
  - selectedVote: Currently selected vote

Server-Side State:
- Game Manager: Map of active games by ID
- Game Object: Complete game state including:
  - players: Map of all players by ID
  - rounds: Array of round data
  - settings: Game configuration
  - state: Current game phase (FSM)
- Player Session: Maps socket ID to player ID and game ID
```

## Key Implementation Notes

### Authentication Implementation

The authentication system uses a hybrid approach:
- Primary authentication happens via the UI forms in index.html
- Credentials are stored in localStorage for persistence
- The system supports reconnection via player ID (primary) or username matching (fallback)
- A JavaScript prompt fallback exists for direct URL access scenarios

**Critical Areas**:
- The localStorage key format `bribery_game_${gameId}` must be consistent across all files
- Username storage happens in three locations:
  1. On game creation (index.html, host form submission)
  2. On game joining (index.html, join form submission)
  3. On each server response (socket-handlers.js, 'joined_game' event)

### Socket Event Handling

Socket events follow a consistent pattern:
- Client emits event with player identification and action data
- Server validates session using socket ID lookup
- Server updates game state and broadcasts updates
- Client processes updates and renders appropriate UI

**Key Events**:
- `create_game`: Initialize new game with host
- `join_game`: Join existing game (new or returning player)
- `start_game`: Transition from lobby to gameplay
- `submit_bribe`: Record player submission
- `submit_vote`: Record player vote

### Reconnection Strategy

The system prioritizes player ID matching over username matching:
1. Try to use stored player ID from localStorage
2. If unavailable or invalid, attempt username matching
3. If both fail, create new player entry

This supports various reconnection scenarios including page refresh, browser restart, and device changes (via direct URL sharing).
