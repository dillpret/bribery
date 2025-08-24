# Copilot Instructions - Bribery Game Project

This is a Flask-SocketIO multiplayer bribery game where players submit creative bribes and vote on submissions.

## Development Environment
- **OS:** Windows with PowerShell (NOT bash/Linux)
- **Python:** Use `py -m` prefix for all Python commands (Windows compatibility)
- **Shell:** PowerShell syntax required (`;` for command chaining, not `&&`)

## Communication Style
Act as a thoughtful peer reviewer, not a cheerleader. Be direct and honest - it's okay to:
- Disagree with proposed approaches
- Point out flaws in ideas or implementations
- Suggest better alternatives
- Challenge assumptions
- Provide critical technical feedback

Focus on code quality, best practices, and potential issues rather than just being supportive.

## Language and Localisation
**Use UK English throughout** - All documentation, frontend text, comments, and user-facing content should use British English spelling and terminology
This applies to all user-facing strings, documentation files, code comments, and error messages.

## Documentation Philosophy
**Minimise documentation bloat.** Each new document is a maintenance commitment that ages the codebase if not maintained. 

**Before creating ANY new file or documentation, ask:**
1. Does this solve an actual problem the user has right now?
2. Will this need maintenance as code changes?
3. Is this information available elsewhere?
4. Does this align with lean documentation principles?

If any answer violates the principles below, **don't create the file**.

**IMPORTANT REMINDER: Follow this documentation strategy strictly! Prefer inline comments and existing documentation over creating new files.**

Prefer:
- **AI instruction files** - Actively used, therefore actively maintained
- **Inline code comments** - Maintained alongside the code they describe
- **Essential README/deployment docs only** - For external users who need them

Avoid creating standalone documentation that duplicates information or won't be regularly updated.

**Documentation Update Policy:**
- Always update documentation when modifying related code
- Keep documentation in sync with implementation details
- This includes:
  - These Copilot instructions
  - Code comments in modified files
  - Technical docs in the `docs/` folder
  - Markdown files that reference the changed functionality

## PowerShell Command Examples
```powershell
# Correct PowerShell syntax
py -m pytest tests/unit/ -v
py -m flask run
Get-ChildItem *.md | Measure-Object -Line
Remove-Item file.txt -Force
Move-Item old.txt new.txt

# AVOID Linux/bash syntax
python -m pytest     # Use 'py -m' instead
ls *.md | wc -l      # Use Get-ChildItem | Measure-Object
rm file.txt          # Use Remove-Item
mv old.txt new.txt   # Use Move-Item
command1 && command2 # Use command1; command2
```

## Project Architecture
- **Backend:** Flask + SocketIO for real-time gameplay
- **Frontend:** Modular HTML/CSS/JS components (refactored from monolithic template)
- **Testing:** Unit testing only
- **Database:** SQLite with game state management
- **Mobile:** Responsive design with touch optimization

## Technical Implementation Details

### Frontend Architecture
- **Authentication Flow:** Hybrid approach using UI forms and localStorage
  - Initial authentication via index.html forms for hosts and joiners
  - Credentials stored in localStorage with key pattern `bribery_game_${gameId}`
  - Reconnection via player ID (primary) or username matching (fallback)
  - Prompt fallback for direct URL access only

- **State Management:**
  - Client: localStorage persistence + in-memory variables (playerId, targets, etc.)
  - Server: Game objects in memory with round history and player mapping
  - Synchronization: Socket events with full state broadcasts on changes

- **Component Structure:**
  - Core Logic: game-core.js (initialization), socket-handlers.js (events), ui-handlers.js (interaction)
  - UI Components: Divided into game phases in game.html with modular CSS
  - See `docs/TECHNICAL_ARCHITECTURE.md` for component maps and flows

## Game Logic Documentation
For understanding game behaviour, rules, and implementation details:
- **`docs/GAME_RULES.md`** - Canonical business rules including Custom Prompts mode
- **`docs/GAME_MECHANICS.md`** - Technical implementation of game mechanics and testing structure
- **`docs/TECHNICAL_ARCHITECTURE.md`** - Component maps and system flows
- **`docs/initial_prompt.txt`** - Original game concept and requirements

These documents define how the game should behave and is implemented, including edge cases for reconnection, late joining, scoring, state management, and the new Custom Prompts feature. 

**When answering questions or suggesting code changes:**
1. Always check these docs first rather than scanning the entire codebase
2. For questions about game rules, refer to GAME_RULES.md
3. For questions about implementation, refer to GAME_MECHANICS.md and TECHNICAL_ARCHITECTURE.md
4. For questions about specific test classes, use GAME_MECHANICS.md to locate relevant files

## Key Development Standards
- Use `py -m pytest` for all testing (Windows PowerShell compatibility)
- Component-based CSS architecture in `static/css/components/`
- Modular JavaScript in `static/js/` (game-core, socket-handlers, ui-handlers)
- Mobile-first responsive design principles

## Testing Standards
- **Test-Driven Development**: Write tests before or alongside new functionality
- **Complete Coverage**: Every feature must have corresponding unit tests
- **Test Isolation**: Tests should not depend on external services or state
- **Mock Dependencies**: Use mocks and patches for external dependencies
- **Test Organization**: Group tests by feature in dedicated files under `tests/unit/`
- **Naming Convention**: Test files should be named `test_*.py` and test classes `Test*`
- **Test Both Paths**: Cover both happy paths and error/edge cases
- **Test Readability**: Tests should clearly show what they're verifying

## Test Server Architecture
The testing framework uses a session-scoped Flask test server on port 5001 managed by `tests/conftest.py`:

**Test Server Requirements:**
- **Unit Tests (`tests/unit/`)** - Do NOT require test server (pure unit testing)

**Test Environment Setup:**
- Install ALL dependencies before running tests: 
  ```powershell
  py -m pip install -r requirements.txt
  py -m pip install -r requirements-dev.txt
  ```
- Core test dependencies are in requirements.txt
- Virtual environment is recommended but not required

**Test Server Behaviour:**
- Automatically starts on port 5001 if not already running
- Session-scoped - shared across all tests in a run
- Uses optimised configuration (reduced logging, CSRF disabled)

**Common Issues:**
- Test timeouts usually indicate port conflicts or server startup failures
- Development servers on port 5000 can interfere with test server startup
- Check terminal output for server error details if tests fail
- Do NOT attempt to read terminal output after running integration tests, as they may block or produce unexpected results

**SocketIO Test Behavior:**
- Wait for manual output from the user rather than trying to read test output after running tests

## Project Structure
```
src/game_logic/           # Core game mechanics (unit tested)
static/css/components/    # Modular CSS components
static/js/               # Modular JavaScript
tests/unit/              # Fast unit tests (0.69s)
templates/              # Clean modular HTML templates
deployment/             # Oracle Cloud deployment (tested, ready)
```

## Deployment Status
- **Oracle Cloud Ready:** `deployment/` folder contains validated deployment scripts
- **WSGI Entry Point:** Production-ready with automatic game cleanup 
- **Production Features:** Error handling and resource management included
- **Always Free Eligible:** Designed for Oracle Always Free tier limits

## Development Focus
- Production readiness (security, persistence, scalability)
- Mobile-first responsive design
- Maintainable component architecture
- Fast, reliable test suite

## Code Quality Enforcement
Automated tools are in place to maintain Python best practices:

**Quick Quality Commands:**
```powershell
# Run all quality checks
py scripts\quality_check.py

# Auto-fix formatting issues  
scripts\fix_quality.bat

# Individual checks
py -m flake8 src/ --max-line-length=120
py -m black --check src/
py -m isort --check-only src/
```

**Pre-commit Setup (Optional):**
```powershell
py -m pre_commit install  # Enable automatic checks before commits
```

**Configuration Files:**
- `.pre-commit-config.yaml` - Pre-commit hook configuration
- `pyproject.toml` - Tool configurations (Black, isort, mypy, pytest)
- `.vscode/settings.json` - VS Code auto-formatting settings

**Key Quality Standards Enforced:**
- Input validation on all socket handlers
- PEP8 compliance (flake8)
- Consistent code formatting (Black)
- Organised imports (isort)
- Type hints for new functions
- Comprehensive test coverage

## Testing Philosophy
**Avoid UI/Selenium Tests:** We've found UI tests with Selenium to be too brittle and difficult to maintain:
- They often break with minor UI changes
- They introduce timing/flakiness issues
- They're slow to run
- They require significant maintenance effort

**We only do unit tests, no integration tests.** This decision was made to:
- Keep the test suite fast and reliable
- Reduce maintenance overhead
- Avoid timing-related issues with asynchronous socket events
- Focus on testing core logic in isolation

**IMPORTANT: Every new feature or change must include corresponding unit tests.** When implementing new functionality:
- Create dedicated test files in `tests/unit/` that verify all aspects of the feature
- Test both happy paths and edge cases
- Verify error handling where applicable
- Mock external dependencies for isolation
- Ensure tests are fast and deterministic

**Instead, prefer:**
1. **Pure Unit Tests:** Test specific components in isolation
2. **Static Analysis Tests:** Verify code structure without actual execution
3. **Manual Testing:** For complex UI interactions during development

For JavaScript features, use static analysis of the code structure instead of UI-driven tests.
