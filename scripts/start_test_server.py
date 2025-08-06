#!/usr/bin/env python3
"""
Cross-platform test server startup script
"""

import subprocess
import sys
import os
from pathlib import Path

def main():
    """Start the test server for manual testing"""
    print("🚀 Starting test server for manual testing...")
    print("Press Ctrl+C to stop")
    print()
    
    # Change to project root
    project_root = Path(__file__).parent.parent
    os.chdir(project_root)
    
    # Run the test server
    try:
        cmd = [sys.executable, "tests/test_server.py", "--port", "5001", "--debug"]
        subprocess.run(cmd)
    except KeyboardInterrupt:
        print("\n👋 Server stopped by user")
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
