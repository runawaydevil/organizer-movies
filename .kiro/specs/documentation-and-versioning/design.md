# Design Document

## Overview

This design outlines the approach for organizing and enhancing the Movie Organizer project documentation, adding proper versioning information, author credits, and ensuring comprehensive documentation of all features including the CLI organizer functionality.

## Architecture

### Version Management System
- **Centralized Version Configuration**: Create a single source of truth for version information
- **Version Display Integration**: Integrate version display into both GUI and CLI interfaces
- **Consistent Version Headers**: Apply version information across all Python modules

### Documentation Structure
- **Enhanced README**: Update main README with comprehensive feature documentation
- **API Configuration Guide**: Clear instructions for both OpenAI and TMDB API setup
- **Usage Examples**: Both GUI and CLI usage examples with screenshots/outputs
- **Repository Information**: Correct GitHub repository URL and project metadata

## Components and Interfaces

### 1. Version Configuration Module
```python
# version.py or config update
VERSION = "0.01"
AUTHOR = "Pablo Murad"
REPOSITORY_URL = "https://github.com/runawaydevil/organizer-movies.git"
```

### 2. Application Header Updates
- **Main Application**: Update main.py to display version and author
- **GUI Interface**: Add version/author info to GUI title or about section
- **CLI Interface**: Update CLI organizer to show version information
- **Report Generation**: Include version/author in PDF reports

### 3. Documentation Updates
- **README.md**: Comprehensive update with current features
- **API Setup Guide**: Clear instructions for both APIs
- **Usage Examples**: Both GUI and CLI examples
- **Installation Guide**: Updated with correct repository URL

## Data Models

### Version Information Structure
```python
class AppInfo:
    version: str = "0.01"
    author: str = "Pablo Murad"
    repository: str = "https://github.com/runawaydevil/organizer-movies.git"
    description: str = "AI-Powered Movie File Organizer with TMDB Integration"
```

### Documentation Sections
- **Project Overview**: Updated description and features
- **Installation**: Correct repository and setup instructions
- **Configuration**: Clear API key setup for both OpenAI and TMDB
- **Usage**: Both GUI and CLI usage examples
- **Features**: Complete feature list including CLI organizer
- **Architecture**: Updated component descriptions

## Error Handling

### API Configuration Errors
- **Missing OpenAI Key**: Clear error message with setup instructions
- **Missing TMDB Keys**: Informative message about optional but recommended setup
- **Invalid Keys**: Helpful troubleshooting information

### Documentation Validation
- **Link Verification**: Ensure all repository links are correct
- **Example Validation**: Verify all code examples work correctly
- **Consistency Checks**: Ensure version information is consistent across all files

## Testing Strategy

### Documentation Testing
- **Link Testing**: Verify all URLs and repository links work
- **Example Testing**: Test all provided code examples
- **Installation Testing**: Verify installation instructions work from scratch

### Version Display Testing
- **GUI Testing**: Verify version appears correctly in GUI
- **CLI Testing**: Verify version appears in CLI output
- **Report Testing**: Verify version appears in generated reports

### API Documentation Testing
- **Setup Instructions**: Test API key setup instructions
- **Error Messages**: Verify helpful error messages appear when keys are missing
- **Configuration Validation**: Test that configuration examples work correctly