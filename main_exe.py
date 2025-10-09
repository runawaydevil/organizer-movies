#!/usr/bin/env python3
"""
Movie Organizer - Main Entry Point (Executable Version)
AI-Powered Movie File Organizer with TMDB Integration

Author: Pablo Murad (runawaydevil)
Version: 0.1
Repository: https://github.com/runawaydevil/organizer-movies.git
"""
import sys
import os
from pathlib import Path

# Add current directory to Python path for imports
current_dir = Path(__file__).parent.absolute()
sys.path.insert(0, str(current_dir))

def main():
    """Main entry point for Movie Organizer"""
    try:
        # Set console encoding to UTF-8 if possible
        try:
            if hasattr(sys.stdout, 'reconfigure'):
                sys.stdout.reconfigure(encoding='utf-8')
            if hasattr(sys.stderr, 'reconfigure'):
                sys.stderr.reconfigure(encoding='utf-8')
        except:
            pass  # Ignore encoding issues
        
        # Display startup info (no emojis for Windows compatibility)
        print("Movie Organizer v0.1")
        print("AI-Powered Movie File Organizer with TMDB Integration")
        print("Author: Pablo Murad (runawaydevil)")
        print("Repository: https://github.com/runawaydevil/organizer-movies.git")
        print("Ready to organize your movie collection!")
        print()
        
        # Import and run the GUI application
        from models.movie_organizer_gui import MovieOrganizerGUI
        
        # Create and run the application
        app = MovieOrganizerGUI()
        app.run()
        
    except KeyboardInterrupt:
        print("Movie Organizer v0.1 interrupted by user")
        return 0
    except Exception as e:
        print(f"ERROR: Fatal error in Movie Organizer v0.1: {e}")
        print("Please report this issue at: https://github.com/runawaydevil/organizer-movies.git/issues")
        
        # Show error details in a message box for GUI users
        try:
            import tkinter as tk
            from tkinter import messagebox
            root = tk.Tk()
            root.withdraw()
            messagebox.showerror(
                "Movie Organizer Error",
                f"Fatal error occurred:\n\n{str(e)}\n\n"
                "Please check that you have:\n"
                "1. Configured your OpenAI API key\n"
                "2. Internet connection\n"
                "3. All required permissions\n\n"
                "For help, see API_SETUP.md"
            )
        except:
            pass  # If GUI fails, just print to console
        
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())