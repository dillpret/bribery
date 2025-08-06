#!/usr/bin/env python3
"""
Cross-platform quality fix script for Bribery game project
Auto-fixes code formatting and import issues
"""

import subprocess
import sys
from pathlib import Path

def run_command(command, description):
    """Run a command and report results"""
    print(f"\n🔧 {description}...")
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ {description} completed")
            if result.stdout.strip():
                print(result.stdout)
            return True
        else:
            print(f"⚠️ {description} had issues:")
            if result.stdout.strip():
                print(result.stdout)
            if result.stderr.strip():
                print(result.stderr)
            return False
    except Exception as e:
        print(f"❌ {description} error: {e}")
        return False

def main():
    """Run all quality fixes"""
    print("🚀 Running code quality fixes for Bribery game...")
    
    # Change to project root
    project_root = Path(__file__).parent.parent
    import os
    os.chdir(project_root)
    
    # Auto-fix commands
    fixes = [
        ("py -m black --line-length=120 src/", "Auto-formatting with Black"),
        ("py -m isort --profile=black src/", "Organizing imports with isort"),
    ]
    
    # Check commands
    checks = [
        ("py -m flake8 src/ --max-line-length=120 --ignore=E501,W503,E203", "Flake8 linting check"),
        ("py -m pytest tests/unit/ --tb=short -q", "Quick unit tests"),
    ]
    
    print("\n" + "="*50)
    print("APPLYING FIXES")
    print("="*50)
    
    for command, description in fixes:
        run_command(command, description)
    
    print("\n" + "="*50)
    print("RUNNING CHECKS")
    print("="*50)
    
    failed_checks = []
    for command, description in checks:
        if not run_command(command, description):
            failed_checks.append(description)
    
    print(f"\n{'='*50}")
    if failed_checks:
        print(f"⚠️ {len(failed_checks)} checks still have issues:")
        for check in failed_checks:
            print(f"  - {check}")
        print("\n💡 You may need to fix these manually!")
        return 1
    else:
        print("✅ All fixes applied and checks passed!")
        print("🎉 Code is ready!")
        return 0

if __name__ == "__main__":
    sys.exit(main())
