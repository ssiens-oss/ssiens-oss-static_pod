#!/usr/bin/env python3
"""
Integration test runner that avoids Python's antigravity Easter egg
"""
import os
import sys
from pathlib import Path

# Change to the parent directory to avoid import conflicts
os.chdir(Path(__file__).parent.parent)
sys.path.insert(0, str(Path(__file__).parent.parent))

# Now import and run the test
from antigravity import test_integration

if __name__ == "__main__":
    sys.exit(test_integration.main())
