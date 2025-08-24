# Game Mechanics Implementation Guide

## Overview

This document focuses on how the game mechanics are implemented in code and tested. It serves as a technical reference for developers working on the codebase, explaining how the game's features are structured in code rather than the business rules (see GAME_RULES.md for those).

## Game Architecture

The game is built with the following key components:

1. **Game**: Represents a single game instance with isolated state.
2. **GameManager**: Manages multiple games and player sessions.
3. **Player**: Represents a player in the game.

## Implementation Structure

The game implementation follows these key patterns:

The game implementation follows these key patterns:

1. **State-Based Progression**: Game transitions through states (lobby→submission→voting→scoreboard)
2. **Round-Based Structure**: Multiple rounds with player pairings and submissions
3. **Scoring System**: Vote tracking and point accumulation
4. **Error Tolerance**: Handling edge cases like disconnections and late joiners

## Test Structure

The game mechanics are tested through a modular structure in `tests/unit/game_mechanics/`:

### Round Flow Logic (TestRoundFlowLogic)

Tests how rounds progress based on player submissions and votes:
- Tests complete submissions from all players
- Tests voting completion
- Tests partial submissions edge case

Implementation: `tests/unit/game_mechanics/test_round_flow.py`

### Scoring System (TestScoringSystem)

Tests how scores are calculated and accumulated:
- Basic scoring (1 point per vote)
- Score accumulation across rounds
- Handling missing votes
- Final ranking and podium positions

Implementation: `tests/unit/game_mechanics/test_scoring.py`

### Game State Management (TestGameStateManagement)

Tests state transitions and validation:
- Valid state transitions (lobby→submission→voting→scoreboard→finished)
- Invalid state transitions (preventing incorrect jumps)
- State persistence during disconnections

Implementation: `tests/unit/game_mechanics/test_state_management.py`

### Edge Cases and Tolerances (TestEdgeCasesAndTolerances)

Tests handling of edge cases:
- Late joiners waiting until next round
- Game continuing after host disconnection
- Empty game cleanup conditions
- Content type validation

Implementation: `tests/unit/game_mechanics/test_edge_cases.py`

### Multi-Round Logic (TestMultiRoundLogic)

Tests progression across multiple rounds:
- Different prompts per round
- Different player pairings each round
- Game ending after configured number of rounds
- Data isolation between rounds

Implementation: `tests/unit/game_mechanics/test_multi_round.py`

## Implementation Details

### Game Initialization

```python
game = Game("GAME_ID", "HOST_ID", {'rounds': 3, 'submission_time': 60, 'voting_time': 30})
```

### Player Management

```python
game.add_player("player_id", "Player Name")
```

### Game State Manipulation

The tests directly manipulate game state:

```python
game.current_round = 1
game.state = "submission"
game.round_pairings[1] = game.generate_round_pairings()
game.bribes[1] = {}
```

### Round Progression

Rounds progress when submissions and votes are complete:

```python
# After all submissions are in, state changes to voting
# After all votes are in, round advances
```

### Scoring

```python
# Scores are tallied based on votes
round_scores = {}
for voter_id, bribe_id in game.votes[game.current_round].items():
    submitter_id = bribe_id.split('_')[0]
    round_scores[submitter_id] = round_scores.get(submitter_id, 0) + 1
```

## Testing Considerations

1. **Direct State Manipulation**: Tests directly set properties rather than using API methods
2. **Implicit API**: Many tests assume an API that differs from the actual implementation
3. **Helper Methods**: Tests use helper methods that don't exist in the actual classes
4. **Test Isolation**: Each test class tests a specific aspect of the game mechanics

## Socket.IO Testing Approach

Socket.IO testing is inherently complex due to its asynchronous nature. Our implementation uses robust patterns to ensure test reliability:

### Key Testing Patterns

1. **Unique Test Identifiers**: Each test uses unique identifiers that incorporate:
   - Test run ID (shared across the test session)
   - Timestamp
   - Random component
   - Test-specific prefix

2. **Server Readiness**: Tests verify server readiness before proceeding:
   ```python
   ensure_server_ready(test_server)
   ```

3. **Explicit Event Clearing**: Clear events before critical operations:
   ```python
   helper.clear_events()
   ```

4. **Retry Logic**: Implement retries for potentially flaky operations:
   ```python
   for attempt in range(max_attempts):
       game_id = host.create_game(...)
       if game_id is not None:
           break
   ```

5. **Progressive Timing**: Use appropriate delays at critical points:
   ```python
   time.sleep(0.3)  # Brief pause before game start
   ```

6. **Detailed Diagnostics**: Capture detailed state on failures:
   ```python
   if not start_result:
       host_status = host.get_detailed_connection_status()
       logger.error(f"Game start failed. Status: {host_status}")
   ```

These patterns are implemented in `tests/integration/test_socketio_integration.py` which serves as the canonical reference for Socket.IO testing in this project.

## Recommendations for Future Development

1. **API Consistency**: Align the tested API with the actual implementation
2. **Documentation**: Keep this documentation updated as the game mechanics evolve
3. **Refactoring**: Consider gradually refactoring tests to use public API methods
4. **Modularity**: When adding new features, create separate test files rather than expanding existing ones
