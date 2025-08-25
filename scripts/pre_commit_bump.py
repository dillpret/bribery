#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Pre-commit wrapper for version bumping
This script runs as a Git pre-commit hook to automatically bump the version
without creating an extra commit.
"""

import os
import sys
import subprocess
from pathlib import Path

# Set environment variable to indicate we're running as a pre-commit hook
os.environ['PRE_COMMIT_HOOK'] = '1'

# Get the directory containing this script using Path for better cross-platform support
script_dir = Path(__file__).resolve().parent
project_root = script_dir.parent

# Construct path to bump_version.py
bump_script = script_dir / 'bump_version.py'

# Get version part from args or default to patch
version_part = 'patch'
if len(sys.argv) > 1 and sys.argv[1] in ['major', 'minor', 'patch']:
    version_part = sys.argv[1]

# Make sure we're in the repository root to avoid path issues
os.chdir(project_root)

# Run the bump_version script
try:
    print(f"Running version bump ({version_part}) as pre-commit hook...")
    result = subprocess.run(
        ['py', str(bump_script), version_part, '--stage'], 
        check=True,
        capture_output=True,
        text=True
    )
    if result.stdout:
        print(result.stdout.strip())
    sys.exit(0)
except subprocess.CalledProcessError as e:
    print(f"Error bumping version: {e}")
    if e.stdout:
        print(e.stdout)
    if e.stderr:
        print(e.stderr)
    sys.exit(1)
