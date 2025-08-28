# Version Management and Cache Busting

This project implements both automatic version management with Git hooks and a cache busting system to ensure browser clients always load the latest static assets.

## Automatic Version Management with Git Hooks

This project uses Git hooks to automatically manage version numbers. The system will automatically bump the patch version (e.g., 1.2.3 to 1.2.4) with each commit.

### How It Works

1. When you commit changes, the pre-commit hook automatically:
   - Bumps the version number in the VERSION file
   - Includes the version bump in your commit (no separate commit needed)

### Manual Version Bumping

For specific version changes (like major or minor releases), use:

```powershell
# Bump patch version (1.2.3 -> 1.2.4)
py scripts\bump_version.py patch

# Bump minor version (1.2.3 -> 1.3.0)
py scripts\bump_version.py minor

# Bump major version (1.2.3 -> 2.0.0)
py scripts\bump_version.py major
```

### Setup

The hook is configured in `.pre-commit-config.yaml` and only handles version bumping. To install the pre-commit hook:

```powershell
# Install pre-commit if you don't have it
py -m pip install pre-commit

# Install the hook in your repository
py -m pre-commit install
```

### Disabling Auto-Version Bumping

If you need to make a commit without bumping the version:

```powershell
git commit --no-verify -m "Your commit message"
```

### Checking the Current Version

The current version is stored in the `VERSION` file in the project root:

```powershell
# Display the current version
Get-Content VERSION
```

## Cache Busting Implementation

To ensure browsers always load the latest version of static files (CSS, JavaScript, images), we use a versioned URL system that leverages the version in the VERSION file.

### How It Works

1. The current version from the `VERSION` file is loaded in `routes.py` and stored in Flask's app config
2. A `versioned_static` helper function is provided via Flask's context processor
3. Templates use this helper to generate URLs with version parameters (e.g., `/static/css/index.css?v=0.1.22`)

### Components

#### In `routes.py`:
```python
# Get version from VERSION file and store in app config
version_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'VERSION')
try:
    with open(version_path, 'r') as f:
        version = f.read().strip()
except (FileNotFoundError, IOError):
    version = "0.0.0"  # Fallback version
    
# Store version in app config for use in versioned_static
app.config['VERSION'] = version
```

#### In `app.py`:
```python
# Add version-based cache busting to static URLs
@app.context_processor
def inject_version():
    def versioned_static(filename):
        version = app.config.get('VERSION', '1')
        return f"/static/{filename}?v={version}"
    return dict(versioned_static=versioned_static)
```

#### In templates:
```html
<link rel="stylesheet" href="{{ versioned_static('css/index.css') }}">
<script src="{{ versioned_static('js/index.js') }}"></script>
```

### Additional Cache Control Measures

1. Flask's default caching is disabled with:
```python
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
```

2. HTTP cache control headers are added to all templates:
```html
<meta http-equiv="Cache-Control" content="no-cache, no-store, must-revalidate">
<meta http-equiv="Pragma" content="no-cache">
<meta http-equiv="Expires" content="0">
```

## Benefits

- Automatic version management through Git hooks
- No extra commit for version bumps
- Consistent version tracking
- Automatic cache busting for static assets
- Browser clients always get the latest version of files
- Version number is displayed in UI (small text at bottom of pages)

## Troubleshooting

### Git Hooks

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

### Caching Issues

If you're still seeing cached versions of assets in production:

1. Make sure you've incremented the version number (manually or through a commit)
2. Verify that templates are using `{{ versioned_static('path/to/file') }}` and not direct `/static/` paths
3. Check browser developer tools to confirm the version parameter is being added to URLs
4. Try clearing the browser cache manually as a test
5. Verify that all HTTP cache headers are being sent properly
