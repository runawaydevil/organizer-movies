#!/usr/bin/env python3
"""
Movie Organizer - Main Entry Point
AI-Powered Movie File Organizer with TMDB Integration

Author: Pablo Murad (runawaydevil)
Version: 0.01
Repository: https://github.com/runawaydevil/organizer-movies.git
"""
import sys
import os
from pathlib import Path

# Add current directory to Python path for imports
current_dir = Path(__file__).parent.absolute()
sys.path.insert(0, str(current_dir))

from version import get_startup_banner, get_version_string, VERSION, AUTHOR

def main():
    """Main entry point for Movie Organizer"""
    try:
        # Display startup banner
        print(get_startup_banner().strip())
        print("Ready to organize your movie collection!\n")
        
        # Import and run the GUI application
        from models.movie_organizer_gui import MovieOrganizerGUI
        
        # Create and run the application
        app = MovieOrganizerGUI()
        app.run()
        
    except KeyboardInterrupt:
        print(f"\n{get_version_string()} interrupted by user")
        return 0
    except Exception as e:
        print(f"ERROR: Fatal error in {get_version_string()}: {e}")
        print(f"Please report this issue at: https://github.com/runawaydevil/organizer-movies.git/issues")
        import traceback
        traceback.print_exc()
        return 1
    finally:
        # Ensure complete shutdown
        try:
            import sys
            sys.exit(0)
        except:
            import os
            os._exit(0)
    
    return 0

if __name__ == "__main__":
    sys.exit(main())