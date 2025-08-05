#!/usr/bin/env python3
"""
Quality check script for Bribery game project
Run this before committing to ensure code quality standards
"""

import subprocess
import sys
from pathlib import Path

def run_command(command, description):
    """Run a command and report results"""
    print(f"\n🔍 {description}...")
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ {description} passed")
            return True
        else:
            print(f"❌ {description} failed:")
            print(result.stdout)
            print(result.stderr)
            return False
    except Exception as e:
        print(f"❌ {description} error: {e}")
        return False

def main():
    """Run all quality checks"""
    print("🚀 Running code quality checks for Bribery game...")
    
    # Change to project root
    project_root = Path(__file__).parent.parent
    import os
    os.chdir(project_root)
    
    checks = [
        ("py -m flake8 src/ --max-line-length=120 --ignore=E501,W503,E203", "Flake8 linting"),
        ("py -m black --check --line-length=120 src/", "Black formatting check"),
        ("py -m isort --check-only --profile=black src/", "Import sorting check"),
        ("py -m pytest tests/unit/ --tb=short -q", "Unit tests"),
        ("py -m pytest tests/integration/ --tb=short -q", "Integration tests"),
    ]
    
    failed_checks = []
    
    for command, description in checks:
        if not run_command(command, description):
            failed_checks.append(description)
    
    print(f"\n{'='*50}")
    if failed_checks:
        print(f"❌ {len(failed_checks)} checks failed:")
        for check in failed_checks:
            print(f"  - {check}")
        print("\n💡 Fix these issues before committing!")
        return 1
    else:
        print("✅ All quality checks passed!")
        print("🎉 Ready to commit!")
        return 0

if __name__ == "__main__":
    sys.exit(main())
