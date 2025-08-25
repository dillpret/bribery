# Version Management

This project uses semantic versioning (SemVer) to track changes. Version numbers follow the pattern: `MAJOR.MINOR.PATCH`.

## Automatic Versioning with GitHub Actions

When you push to the master branch, GitHub Actions will:

1. Read the current version from the `VERSION` file
2. Automatically increment the patch version (e.g., 0.0.1 → 0.0.2)
3. Commit the updated version back to the repository
4. Create a git tag with that version (e.g., v0.0.2)
5. Deploy to the Oracle Cloud instance

The version number appears as a small, inconspicuous indicator on the home page and game pages.

## Manual Version Updates

For significant changes, you should manually update the version before pushing to master:

```powershell
# Update minor version (0.1.0 -> 0.2.0)
py scripts\bump_version.py minor

# Update major version (1.0.0 -> 2.0.0)
py scripts\bump_version.py major
```

**Note:** The patch version will still be automatically incremented after deployment.

## When to Manually Update Versions

- **PATCH (0.0.1 -> 0.0.2)**: Automatically incremented by GitHub Actions for every deployment
- **MINOR (0.1.0 -> 0.2.0)**: New features that are backward compatible
- **MAJOR (1.0.0 -> 2.0.0)**: Breaking changes, major redesigns

## Best Practices

1. For minor or major version updates, manually update the version before merging to master
2. Include version updates in your commit message:
   ```
   git commit -m "Add feature X (v0.2.0)"
   ```
3. Let GitHub Actions handle patch increments and deployment

## Viewing Version History

To see the version history of your project:

```powershell
git tag -l
```

To see details about a specific version:

```powershell
git show v0.1.0
```
