#!/usr/bin/env python3
"""
Debug version to test what's wrong with the executable.
Run from project root: python scripts/debug_exe.py
"""
import sys
import os
import traceback
from pathlib import Path

# Ensure repo root is on path (for core, models, services)
REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

def debug_main():
    """Debug version of main"""
    try:
        print("=== DEBUG MODE ===")
        print(f"Python version: {sys.version}")
        print(f"Current directory: {os.getcwd()}")
        print(f"Script path: {__file__}")
        print(f"Executable: {getattr(sys, 'frozen', False)}")
        print(f"Repo root on path: {REPO_ROOT}")

        print("\nTrying to import version...")
        try:
            from core.version import get_version_string
            print(f"Version imported successfully: {get_version_string()}")
        except Exception as e:
            print(f"Failed to import version: {e}")
            traceback.print_exc()

        print("\nTrying to import GUI...")
        try:
            from models.movie_organizer_gui import MovieOrganizerGUI
            print("GUI imported successfully")
        except Exception as e:
            print(f"Failed to import GUI: {e}")
            traceback.print_exc()
            return 1

        print("\nTrying to create GUI...")
        try:
            app = MovieOrganizerGUI()
            print("GUI created successfully")
        except Exception as e:
            print(f"Failed to create GUI: {e}")
            traceback.print_exc()
            return 1

        print("\nTrying to run GUI...")
        try:
            app.run()
            print("GUI ran successfully")
        except Exception as e:
            print(f"Failed to run GUI: {e}")
            traceback.print_exc()
            return 1

    except Exception as e:
        print(f"Fatal error: {e}")
        traceback.print_exc()
        input("Press Enter to exit...")
        return 1

    return 0

if __name__ == "__main__":
    sys.exit(debug_main())
