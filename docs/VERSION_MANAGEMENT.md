# Version Management with Git Hooks

This project uses Git hooks to automatically manage version numbers. The system will automatically bump the patch version (e.g., 1.2.3 to 1.2.4) with each commit.

## How It Works

1. When you commit changes, the pre-commit hook automatically:
   - Bumps the version number in the VERSION file
   - Includes the version bump in your commit (no separate commit needed)

## Manual Version Bumping

For specific version changes (like major or minor releases), use:

```powershell
# Bump patch version (1.2.3 -> 1.2.4)
py scripts\bump_version.py patch

# Bump minor version (1.2.3 -> 1.3.0)
py scripts\bump_version.py minor

# Bump major version (1.2.3 -> 2.0.0)
py scripts\bump_version.py major
```

## Setup

The hook is configured in `.pre-commit-config.yaml` and only handles version bumping. To install the pre-commit hook:

```powershell
# Install pre-commit if you don't have it
py -m pip install pre-commit

# Install the hook in your repository
py -m pre-commit install
```

## Disabling Auto-Version Bumping

If you need to make a commit without bumping the version:

```powershell
git commit --no-verify -m "Your commit message"
```

## Checking the Current Version

The current version is stored in the `VERSION` file in the project root:

```powershell
# Display the current version
Get-Content VERSION
```

## Benefits

- No extra commit for version bumps
- Consistent version tracking
- Automatic staging of the VERSION file
- Works with the project's PowerShell environment
- Minimal configuration - only does version bumping

## Troubleshooting

If the version isn't being bumped automatically:

1. Check if pre-commit is installed:
   ```powershell
   py -m pre_commit --version
   ```

2. Ensure the hook is installed in your repository:
   ```powershell
   Test-Path .git/hooks/pre-commit
   ```

3. Reinstall the hook if needed:
   ```powershell
   py -m pre_commit install
   ```

4. Test the hook manually:
   ```powershell
   py -m pre_commit run bump-version
   ```
   Note: When testing the hook manually, it will show as "Failed" because it modifies files. This is expected behavior and not an actual failure.
