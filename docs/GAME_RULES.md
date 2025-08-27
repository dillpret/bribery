# Bribery Game - Canonical Business Rules

## Game Overview
**Bribery** is a multiplayer party game designed as an icebreaker for casual players. Players compete to create the most appealing "bribes" (submissions) based on creative prompts, with anonymous voting determining round winners.

## Core Game Flow

### 1. Game Setup
- **Host Creation**: One player creates a game, receives a unique Game ID and host controls
- **Player Joining**: Other players join using the Game ID or shared link
- **Lobby Phase**: Players enter usernames, host configures settings
- **Minimum Players**: 3 players required to start
- **Settings**: 
  - Number of rounds (configurable)
  - Submission time limit per round (seconds)
  - Voting time limit per round (seconds)
  - Prompt selection time limit (seconds)
  - **Custom Prompts**: Enabled/Disabled (see Custom Prompts Mode)

### 2. Round Structure
Each round consists of three or four phases depending on the Custom Prompts setting:

#### Traditional Mode (Custom Prompts: Disabled)
**Three phases**: Submission → Voting → Scoreboard

#### Custom Prompts Mode (Custom Prompts: Enabled)  
**Four phases**: Prompt Selection → Submission → Voting → Scoreboard

#### Phase 1A: Prompt Selection (Custom Prompts Mode Only)
- **Individual Choice**: Each player selects their own prompt for receiving bribes
- **Prompt Options**: Two separate sections - dropdown with preset prompts OR custom text input
- **Custom Prompts**: Players can enter completely custom prompts (up to 200 characters)
- **Completion**: Phase advances when all players select prompts OR when the configurable timer expires
- **Fallback**: Players who don't select use a default prompt

#### Phase 1B: Submission (Bribery)
- **Traditional Mode**: All players see identical creative prompt from `prompts.txt`
- **Custom Prompts Mode**: Each target's individual prompt displayed to their briber
- **Target Assignment**: Each player assigned exactly 2 other players to "bribe"
- **Submission Types**: Text, images, links, GIFs supported
- **Input Methods**: Text input, drag-and-drop, copy-paste
- **Prompt Display**: Shows target player's chosen prompt for personalized bribing
- **Completion**: Round advances when all players submit both bribes OR time expires
- **Pairing Algorithm**: Circular shuffling ensures each player receives exactly 2 bribes
- **Random Bribes**: If a player disconnects or doesn't submit in time, a random silly bribe is generated from `random_bribes.txt` and marked as "(randomly generated)"

#### Phase 2: Voting (Anonymous Selection)
- **Anonymous Display**: Players see only the 2 bribes submitted TO them (submitter names hidden)
- **Single Choice**: Each player votes for their preferred bribe
- **Winner Reveal**: Chosen bribe's creator is revealed after vote submission
- **Completion**: Phase ends when all players vote OR time expires

#### Phase 3: Scoreboard (Results)
- **Scoring**: 
  - 1 point per vote received for player-submitted bribes
  - 0.5 points per vote received for randomly generated bribes
- **Display**: Round results show who voted for whom, current standings
- **Random Bribes**: Randomly generated bribes are marked with "(randomly generated)" **only during results phase**
- **Duration**: 5-second automatic advance to next round or final results

### 3. Game Progression
- **Multi-Round**: Each round uses different random prompt and player pairings
- **Final Results**: After all rounds, podium display highlights top 3 players
- **Host Controls**: Restart game or return to lobby

## Custom Prompts Mode

### Overview
Custom Prompts mode allows each player to choose their own prompt that others will use when creating bribes for them, enabling more personalized and creative gameplay.

### Host Configuration
- **Setting**: "Custom Prompts" toggle in game creation (Enabled/Disabled)
- **Default**: Disabled (traditional shared prompt mode)
- **Once Set**: Cannot be changed after game creation

### Prompt Selection Phase (Custom Mode Only)
- **Triggers**: When custom prompts enabled, each round starts with prompt selection
- **Duration**: Configurable timer for all players to select prompts
- **Options**: 
  - Dropdown with preset prompts from `prompts.txt`
  - "Custom Prompt..." option for completely custom text (max 200 characters)
- **Completion**: Phase advances when all connected players select OR timer expires
- **Fallback**: Players who don't select use default prompt from `prompts.txt`

### Submission Phase Differences
- **Traditional Mode**: Single shared prompt displayed to all players
- **Custom Mode**: Each target's specific prompt shown when creating bribes for them
- **UI Display**: Target name + their chosen prompt clearly shown
- **Example**: "Bribe for Alice: Her prompt: 'Something that makes you smile'"

### Prompt Storage
- **Per Round**: Each round stores individual player prompt choices
- **Data Isolation**: Round 1 prompts separate from Round 2 prompts
- **Persistence**: Prompts maintained even if players disconnect/reconnect

### Strategic Implications
- **Prompt Strategy**: Players can choose prompts that inspire funnier/better bribes
- **Personalization**: Enables inside jokes, preferences, or themed prompts
- **Creativity**: Encourages more thoughtful and targeted bribery

## Player Management Rules

### Connection Handling
- **Rejoin Support**: Players can disconnect and rejoin with same username
- **Mid-Game Joining**: New players can join during active game, wait in lobby until next round
- **Starting Score**: Late joiners start with 0 points
- **No Authentication**: No persistent accounts or login required

### Player States
- **Connected/Disconnected**: Tracked but doesn't affect game flow
- **Active Participation**: Game continues regardless of disconnections
- **Username Requirements**: Simple string, no validation beyond existence

## Technical Implementation Rules

### Game States (Finite State Machine)
1. **"lobby"**: Waiting for players, host can configure settings
2. **"prompt_selection"**: Players choosing individual prompts (Custom Prompts mode only)
3. **"submission"**: Players creating bribes for assigned targets
4. **"voting"**: Players voting on bribes submitted to them
5. **"scoreboard"**: Displaying round results, brief pause
6. **"finished"**: Final results, restart/lobby options

### Timing Rules
- **Configurable Timers**: Host sets prompt selection, submission, and voting time limits
- **Automatic Progression**: Phases advance on timer expiry regardless of completion status
- **Timer Cancellation**: Early completion cancels remaining time

### Data Structure Rules
- **Round Isolation**: Each round's data stored separately (bribes, votes, pairings)
- **Score Accumulation**: Player scores persist across rounds
- **Game Cleanup**: Resources released when game ends or expires

## Pairing Algorithm
```
For N players in round R:
1. Shuffle all player IDs randomly
2. Each player P at index i bribes:
   - Target 1: Player at index (i+1) % N
   - Target 2: Player at index (i+2) % N
3. Self-targeting prevention ensures valid pairings
4. Result: Each player sends 2 bribes, receives 2 bribes
```

## Scoring System
- **Point Award**: 1 point per vote received in any round
- **Vote Calculation**: Each player votes once per round for best bribe received
- **Tie Breaking**: Natural leaderboard ordering (no explicit tie-breaking)
- **Final Ranking**: Total points across all rounds, top 3 podium positions

## Content Rules
- **Prompt Pool**: Random selection from `prompts.txt` (40+ creative prompts)
- **Submission Formats**: 
  - Text: Plain text responses
  - Images: Mobile camera/gallery or drag-and-drop on desktop
  - Links: URLs for gifs, memes, articles
- **Content Persistence**: Submissions stored per round, cleared between games

## Edge Cases and Tolerances
- **Partial Submissions**: Game progresses even if not all players submit
- **Missing Votes**: Non-voting players don't affect scoring
- **Host Disconnection**: Game continues, any player can restart after completion
- **Empty Games**: Games auto-cleanup after inactivity
- **Late Joiners**: Queue until next round starts, maintain separate waiting screen

This document represents the canonical business logic as implemented in the current system. Any AI assistance should reference these rules to understand expected game behaviour, especially for edge cases involving reconnection, late joining, and mid-game state management.
