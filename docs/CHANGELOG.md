# Changelog

All notable changes to Movie Organizer will be documented in this file.

## [0.1.0] - 2025-01-10

### Added
- 🎬 **First Official Release** - Complete movie organization system
- 🤖 **AI Analysis** - OpenAI GPT integration for movie identification
- 🎭 **TMDB Integration** - The Movie Database API for enhanced accuracy
- 📁 **Smart Folder Management** - Intelligent folder creation and renaming
- 🌐 **Network Support** - Handles network drives and mapped drives
- 📊 **PDF Reports** - Automatic generation of organized movies reports
- 🔍 **Manual Search** - Manual TMDB search for difficult movies
- ✏️ **Metadata Editing** - Edit movie information before organizing
- 💾 **Cache System** - TMDB results caching for better performance
- ⚙️ **Settings Panel** - Complete configuration interface
- 🎯 **Duplicate Prevention** - Tracks organized movies to avoid reprocessing

### Features
- **Hybrid Analysis**: Combines AI and TMDB for best results
- **Media Server Compatible**: Naming compatible with Plex, Jellyfin, Emby
- **Network Aware**: Automatic detection and handling of network paths
- **Progress Tracking**: Real-time progress updates and ETA
- **Error Handling**: Robust error handling with continue-on-error option
- **Confidence Scoring**: Shows confidence levels for all identifications
- **Threading**: Background operations don't block the interface

### Technical
- **Python 3.8+** support
- **Cross-platform** compatibility (Windows, Linux, macOS)
- **Modern GUI** built with tkinter
- **Comprehensive logging** for debugging
- **Secure API key storage** with AES encryption

### Supported Formats
- Video: `.mkv`, `.mp4`, `.avi`, `.mov`, `.wmv`, `.flv`, `.webm`, `.m4v`, `.3gp`, `.ogv`, `.ts`, `.m2ts`, `.mts`
- Network: UNC paths, mapped drives, local folders
- Output: PDF reports, JSON database, organized folder structure