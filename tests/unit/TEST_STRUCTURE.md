# Test Structure Documentation

## Overview

This document explains the structure of our unit tests and provides guidance for maintaining and extending them.

## Testing Philosophy

We have intentionally chosen to use **only unit tests** for the following reasons:

1. **Speed** - Our entire test suite runs in under 1 second (0.54s)
2. **Reliability** - Unit tests avoid timing/flakiness issues common with integration tests
3. **Maintenance** - Unit tests are easier to maintain as they test isolated components
4. **Focus** - We can test core logic precisely without worrying about UI or network issues

## Current Test Organization

The game mechanics tests are organized in various files under `tests/unit/`, with these key test categories:

### Core Game Mechanics
Located in `tests/unit/game_mechanics/`:
1. **TestRoundFlowLogic**: Tests round progression based on submissions and votes
2. **TestScoringSystem**: Tests scoring calculations and accumulation
3. **TestGameStateManagement**: Tests state transitions and persistence
4. **TestEdgeCasesAndTolerances**: Tests edge case handling
5. **TestMultiRoundLogic**: Tests progression across multiple rounds

### Feature Tests
Individual feature tests in `tests/unit/`:
1. **test_custom_prompts.py**: Tests custom prompts implementation
2. **test_mobile_image_upload.py**: Tests mobile responsiveness and image upload
3. **test_midgame_joining.py**: Tests players joining mid-game
4. **test_host_username_flow.py**: Tests host username experience
5. **test_game_state_management.py**: Tests broader game state scenarios
6. **test_player_kick_logic.py**: Tests player kick functionality and player list data

## Test Implementation Pattern

The tests follow a consistent pattern:

1. **Setup**: Create a Game instance and add players
2. **State Manipulation**: Directly set game state properties
3. **Test Actions**: Perform actions like adding bribes or votes
4. **Assertions**: Verify the expected state

Example:
```python
def test_round_submission_completion_all_players_submit(self):
    # Setup
    game = Game("TEST1234", "host", {'rounds': 3, 'submission_time': 60, 'voting_time': 30})
    game.add_player("p1", "Player1")
    game.add_player("p2", "Player2")
    game.add_player("p3", "Player3")
    
    # State manipulation
    game.current_round = 1
    game.state = "submission"
    game.round_pairings[1] = game.generate_round_pairings()
    game.bribes[1] = {}
    
    # Test actions & assertions
    assert not self._all_submissions_complete(game)
    
    game.bribes[1]["p1"] = {"p2": {"content": "bribe1", "type": "text"}}
    assert not self._all_submissions_complete(game)
    
    # Complete all submissions
    game.bribes[1] = {
        "p1": {
            "p2": {"content": "p1 to p2", "type": "text"},
            "p3": {"content": "p1 to p3", "type": "text"}
        },
        "p2": {
            "p1": {"content": "p2 to p1", "type": "text"},
            "p3": {"content": "p2 to p3", "type": "text"}
        },
        "p3": {
            "p1": {"content": "p3 to p1", "type": "text"},
            "p2": {"content": "p3 to p2", "type": "text"}
        }
    }
    
    assert self._all_submissions_complete(game)
```

## Helper Methods

Each test class includes helper methods that support the tests:

```python
def _all_submissions_complete(self, game):
    """Helper: Check if all players have submitted all their bribes"""
    expected_submissions = len(game.players) * 2  # Each player submits 2 bribes
    actual_submissions = sum(len(bribes) for bribes in game.bribes[game.current_round].values())
    return actual_submissions >= expected_submissions
```

## Guidelines for Test Maintenance

When maintaining or extending these tests:

1. **Preserve Existing Patterns**: Follow the established patterns to maintain consistency
2. **Helper Methods**: Keep helper methods with their respective test classes
3. **Focused Tests**: Each test should verify a specific aspect of functionality
4. **Test Naming**: Use descriptive names that indicate what's being tested
5. **Unit Tests Only**: Remember we only use unit tests, not integration tests

## Guidelines for Adding New Tests

When adding new tests:

1. **Choose Appropriate Class**: Add to the existing class that best matches the functionality
2. **Create New Classes**: For entirely new features, create new test classes
3. **Follow Pattern**: Maintain the setup, state manipulation, action, assertion pattern
4. **Helper Methods**: Add helper methods as needed, but keep them scoped to the test class
5. **Keep Tests Fast**: Ensure new tests maintain our sub-second test suite performance
6. **Isolated Unit Tests**: Tests should be isolated and not depend on external services

## Modularization Strategy

If future refactoring is desired:

1. **Maintain Original File**: Keep the original test file intact
2. **Create Package**: Create a game_mechanics package with modules for each test class
3. **Extract Classes**: Copy the exact test classes to their respective modules
4. **Re-export**: Update the original file to import from the modular files
5. **Verify Tests**: Ensure all tests still pass after refactoring

## Common Pitfalls

1. **API Mismatch**: Tests assume methods that don't exist in the implementation
2. **State Dependencies**: Tests may depend on specific state being set manually
3. **Helper Method Dependencies**: Tests rely on helper methods in their class
4. **Initialization Assumptions**: Tests may assume specific initialization behavior
5. **Integration Logic**: Avoid introducing integration test logic into unit tests

## Running Tests

Run the full test suite:
```powershell
py -m pytest tests/unit/ -v
```

Run a specific test file:
```powershell
py -m pytest tests/unit/test_file_name.py -v
```

Run a specific test:
```powershell
py -m pytest tests/unit/test_file_name.py::TestClass::test_method -v
```
