#!/usr/bin/env python3
"""
Debug script for testing startup logic.

This allows you to:
1. Set breakpoints in your IDE
2. Step through the startup logic
3. Inspect variables

Usage:
    python debug_startup.py
"""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import after path is set
from backend.main import startup_logic

if __name__ == "__main__":
    print("=" * 60)
    print("DEBUG: Running startup logic...")
    print("=" * 60)

    try:
        startup_logic()
        print("\n" + "=" * 60)
        print("DEBUG: Startup logic completed successfully!")
        print("=" * 60)
    except Exception as e:
        print("\n" + "=" * 60)
        print(f"DEBUG: Startup logic failed with error:")
        print(f"{type(e).__name__}: {e}")
        print("=" * 60)
        import traceback

        traceback.print_exc()
        sys.exit(1)
