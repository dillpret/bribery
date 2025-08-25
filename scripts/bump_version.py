#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Version bumping script for Bribery Game
Usage:
  py scripts\bump_version.py [major|minor|patch]
"""

import os
import sys
import re

# Get the root directory of the project
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VERSION_FILE = os.path.join(ROOT_DIR, 'VERSION')


def get_current_version():
    """Read the current version from the VERSION file"""
    try:
        with open(VERSION_FILE, 'r') as f:
            return f.read().strip()
    except (FileNotFoundError, IOError):
        # If the VERSION file doesn't exist, create it with a default version
        with open(VERSION_FILE, 'w') as f:
            f.write('1.0.0')
        return '1.0.0'


def bump_version(version_part='patch'):
    """
    Bump the version number
    :param version_part: 'major', 'minor', or 'patch'
    """
    current_version = get_current_version()
    
    # Parse the current version
    match = re.match(r'^(\d+)\.(\d+)\.(\d+)$', current_version)
    if not match:
        print(f"Error: Invalid version format: {current_version}")
        sys.exit(1)
    
    major, minor, patch = map(int, match.groups())
    
    # Bump the version based on the specified part
    if version_part == 'major':
        major += 1
        minor = 0
        patch = 0
    elif version_part == 'minor':
        minor += 1
        patch = 0
    elif version_part == 'patch':
        patch += 1
    else:
        print(f"Error: Invalid version part: {version_part}")
        print("Usage: py scripts\\bump_version.py [major|minor|patch]")
        sys.exit(1)
    
    # Create the new version string
    new_version = f"{major}.{minor}.{patch}"
    
    # Write the new version to the VERSION file
    with open(VERSION_FILE, 'w') as f:
        f.write(new_version)
    
    print(f"Version bumped from {current_version} to {new_version}")
    return new_version


if __name__ == '__main__':
    # Default to patch if no argument is provided
    version_part = 'patch'
    
    # Parse command line arguments
    if len(sys.argv) > 1:
        version_part = sys.argv[1].lower()
    
    # Ensure the version part is valid
    if version_part not in ['major', 'minor', 'patch']:
        print("Usage: py scripts\\bump_version.py [major|minor|patch]")
        sys.exit(1)
    
    # Bump the version
    bump_version(version_part)
