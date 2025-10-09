#!/usr/bin/env python3
"""
Version Configuration - Movie Organizer
Centralized version and project information

Author: Pablo Murad (runawaydevil)
Version: 0.1
"""

# Project Information
VERSION = "0.1"
AUTHOR = "Pablo Murad (runawaydevil)"
REPOSITORY_URL = "https://github.com/runawaydevil/organizer-movies.git"
DESCRIPTION = "AI-Powered Movie File Organizer with TMDB Integration"
PROJECT_NAME = "Movie Organizer"

# Application Metadata
APP_TITLE = f"{PROJECT_NAME} v{VERSION}"
FULL_TITLE = f"{PROJECT_NAME} - {DESCRIPTION}"
COPYRIGHT = f"© 2025 {AUTHOR}"

# API Information
REQUIRED_APIS = ["OpenAI API Key"]
OPTIONAL_APIS = ["TMDB API Key", "TMDB Bearer Token"]

def get_version_info():
    """
    Get formatted version information
    
    Returns:
        dict: Version information dictionary
    """
    return {
        "version": VERSION,
        "author": AUTHOR,
        "repository": REPOSITORY_URL,
        "description": DESCRIPTION,
        "project_name": PROJECT_NAME,
        "app_title": APP_TITLE,
        "full_title": FULL_TITLE,
        "copyright": COPYRIGHT
    }

def get_version_string():
    """
    Get formatted version string for display
    
    Returns:
        str: Formatted version string
    """
    return f"{PROJECT_NAME} v{VERSION} by {AUTHOR}"

def get_startup_banner():
    """
    Get startup banner text
    
    Returns:
        str: Formatted startup banner
    """
    return f"""
{PROJECT_NAME} v{VERSION}
{DESCRIPTION}
Author: {AUTHOR}
Repository: {REPOSITORY_URL}
"""

if __name__ == "__main__":
    print(get_startup_banner())
    print("Version Info:", get_version_info())