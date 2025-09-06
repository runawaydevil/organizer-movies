# 🎬 Movie Organizer

**AI-Powered Movie File Organizer with TMDB Integration**

*Version: 0.01*  
*Author: Pablo Murad (runawaydevil)*  
*Repository: https://github.com/runawaydevil/organizer-movies.git*

[![Version](https://img.shields.io/badge/Version-0.01-brightgreen.svg)](https://github.com/runawaydevil/organizer-movies)
[![Python](https://img.shields.io/badge/Python-3.8%2B-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/License-Free%20%2F%20MIT-green.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20Linux-lightgrey.svg)](#installation)
[![AI](https://img.shields.io/badge/AI-OpenAI%20GPT-orange.svg)](https://openai.com)
[![TMDB](https://img.shields.io/badge/TMDB-Integration-yellow.svg)](https://www.themoviedb.org)
[![GUI](https://img.shields.io/badge/Interface-GUI%20%2B%20CLI-purple.svg)](#usage-guide)
[![Status](https://img.shields.io/badge/Status-Active-success.svg)](https://github.com/runawaydevil/organizer-movies)

Organize your movie collection automatically using AI and The Movie Database (TMDB) API. This tool analyzes movie filenames, identifies movies using AI and TMDB, creates properly named folders, and generates comprehensive PDF reports.

![Movie Organizer Interface](Images/1.jpg)

*Movie Organizer v0.01 - Clean, intuitive interface for organizing your movie collection*

## ✨ Features

### 🤖 **Intelligent Analysis**
- **AI-Powered**: Uses OpenAI GPT models to analyze movie filenames
- **TMDB Integration**: Enhances accuracy with The Movie Database API
- **Hybrid Mode**: Combines AI + TMDB for best results
- **Smart Fallback**: Works with AI-only if TMDB is unavailable

### 📁 **Smart Organization**
- **Automatic Folder Creation**: Creates folders in format "Movie Title (Year)"
- **Intelligent Folder Management**: 
  - Single movie: Renames existing folder
  - Multiple movies: Creates individual folders for each
- **Media Server Compatible**: Works with Plex, Jellyfin, Emby, Kodi
- **Network Support**: Handles network drives and mapped drives

### 🎯 **Advanced Features**
- **Manual Search**: Search TMDB manually for difficult movies
- **Metadata Editing**: Edit movie information before organizing
- **PDF Reports**: Automatic generation of organized movies report
- **Duplicate Prevention**: Tracks organized movies to avoid reprocessing
- **Cache System**: Caches TMDB results for better performance

### 🖥️ **User Interface**
- **Modern GUI**: Clean, intuitive interface built with tkinter
- **Real-time Progress**: Live progress updates during processing
- **Confidence Indicators**: Shows analysis confidence levels
- **Network Detection**: Automatically detects and handles network paths
- **Settings Panel**: Easy configuration of all options

## 🚀 Quick Start

### Prerequisites

- **Python 3.8+** (Required)
- **OpenAI API Key** (Required - for AI movie identification)
- **TMDB API Key & Bearer Token** (Optional but recommended - for enhanced accuracy)

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/runawaydevil/organizer-movies.git
   cd organizer-movies
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application:**
   
   **Windows/Linux (GUI):**
   ```bash
   python main.py
   ```
   
   **Linux (CLI):**
   ```bash
   python services/cli_organizer.py
   ```

### First Time Setup

1. **Get API Keys:**
   - **OpenAI**: Visit [OpenAI API](https://platform.openai.com/api-keys) (Required)
   - **TMDB**: Visit [TMDB API](https://www.themoviedb.org/settings/api) (Optional)

2. **Configure in GUI:**
   - Open Settings (File → Settings or Ctrl+,)
   - Enter your OpenAI API key (required)
   - Optionally enter TMDB credentials for better accuracy
   - Keys are encrypted and stored securely locally

3. **Start Organizing:**
   - Select your movie folder
   - Review AI-identified movies
   - Click "Process Files" to organize

## 📖 Usage Guide

### Basic Workflow

1. **Select Source Folder**: Choose folder containing movie files
2. **AI Analysis**: Program analyzes all movie files automatically  
3. **Review Results**: Check identified movies and confidence scores
4. **Manual Corrections**: Edit any incorrect identifications if needed
5. **Process Files**: Organize movies into proper folder structure
6. **PDF Report**: Automatic report generation with statistics

### GUI Usage

1. **Launch the application:**
   ```bash
   python main.py
   ```

2. **Select your movie folder:**
   - Click "Browse" to select folder containing movie files
   - Supports local folders and network drives

3. **Scan and analyze:**
   - Click "🔍 Scan for Movies" to find and analyze files
   - Review the analysis results and confidence scores

4. **Organize movies:**
   - Select files to organize (or use "Select All")
   - Click "🎬 Organize Selected Movies"
   - PDF report is generated automatically

### CLI Usage (Linux)

```bash
# Show help and version information
python services/cli_organizer.py

# The CLI organizer provides command-line interface for:
# • Batch processing of movie folders
# • Automated organization without GUI
# • Integration with scripts and automation
```

### Folder Organization Examples

**Before:**
```
/Movies/
├── random_folder/
│   └── matrix.1999.mkv
├── action_movies/
│   ├── terminator.mkv
│   └── alien.mkv
```

**After:**
```
/Movies/
├── The Matrix (1999)/
│   └── The Matrix (1999).mkv
├── action_movies/
│   ├── Terminator (1984)/
│   │   └── Terminator (1984).mkv
│   └── Alien (1979)/
│       └── Alien (1979).mkv
```

### Advanced Features

#### Manual Search
- Right-click any movie → "🎬 Manual TMDB Search"
- Search TMDB database manually for difficult movies
- Select correct movie or enter information manually

#### Metadata Editing
- Right-click any movie → "✏️ Edit Metadata"
- Modify title, year, and other information
- Option to re-analyze with AI after editing

#### Settings Configuration
- **File Menu → Settings** or **Ctrl+,**
- Configure API keys, naming patterns, network settings
- Test TMDB connection before saving

### API Configuration

#### Required: OpenAI API Key
1. Visit [OpenAI API](https://platform.openai.com/api-keys)
2. Create a new API key
3. Enter in Settings → OpenAI API Configuration
4. **Note**: This is required for the application to work

#### Optional: TMDB API Keys (Recommended)
1. Visit [TMDB API](https://www.themoviedb.org/settings/api)
2. Create account and request API access
3. Get both API Key and Bearer Token
4. Enter in Settings → TMDB Integration
5. **Note**: Greatly improves identification accuracy

## 📊 Reports

The application automatically generates PDF reports containing:
- Complete list of organized movies
- Statistics (AI vs TMDB vs Manual)
- Organization dates and confidence scores
- Saved in the program directory as `organized_movies_report.pdf`

## 🔧 Configuration Options

### File Naming Patterns
- **Default**: `{title} ({year}){extension}`
- **Alternative**: `{title} - {year}{extension}`
- **Year First**: `{year} - {title}{extension}`
- **Title Only**: `{title}{extension}`

### AI Model Selection
- **GPT-3.5-turbo**: Fast and cost-effective (default)
- **GPT-4**: Higher accuracy but more expensive
- **Custom models**: Support for other OpenAI models

### TMDB Settings
- **Language**: Set preferred language for movie data
- **Original Titles**: Use original titles vs localized
- **Cache Duration**: How long to cache TMDB results

### Network Settings
- **Retry Attempts**: Number of retries for network operations
- **Retry Delay**: Delay between retry attempts  
- **Timeout**: Maximum time to wait for network operations
- **Network Drive Support**: Automatic detection and handling

## 🏗️ Project Architecture

### Core Components
- **MovieOrganizerGUI**: Main application controller with GUI interface
- **CLIOrganizer**: Command-line interface for batch processing
- **HybridAnalyzer**: Combines AI and TMDB analysis for best results
- **SmartFolderManager**: Intelligent folder organization logic
- **TMDBService**: TMDB API integration with caching and rate limiting
- **NetworkFileHandler**: Robust network file operations
- **MovieReportGenerator**: PDF report generation with statistics

### File Structure
```
organizer-movies/
├── main.py                     # GUI application entry point
├── version.py                  # Centralized version information
├── requirements.txt            # Python dependencies
├── images/
│   └── 1.jpg                   # Application screenshot
├── models/
│   ├── movie_organizer_gui.py  # Main GUI controller
│   ├── config.py               # Configuration models
│   ├── movie_metadata.py       # Movie metadata model
│   └── gui/                    # GUI components
├── services/
│   ├── cli_organizer.py        # Command-line interface
│   ├── ai_analyzer.py          # OpenAI integration
│   ├── tmdb_service.py         # TMDB API service
│   ├── hybrid_analyzer.py      # AI + TMDB analyzer
│   ├── smart_folder_manager.py # Folder management
│   ├── file_mover.py           # File operations
│   └── movie_report_generator.py # PDF reports
└── tests/                      # Test files
```

## 🧪 Testing

Run the test suite:
```bash
python -m pytest tests/ -v
```

Individual test files:
```bash
python test_integration.py      # Integration tests
python test_tmdb_cache.py       # TMDB cache tests
python test_file_mover.py       # File operations tests
```

## 🔒 Security & Privacy

### API Key Storage
- **Encrypted Storage**: API keys encrypted using Fernet (AES 128)
- **Local Only**: Keys stored locally, never transmitted except to APIs
- **Secure Locations**: 
  - Windows: `%LOCALAPPDATA%\MovieOrganizer\config\`
  - Linux: `~/.config/movie-organizer/config/`

### Data Privacy
- **No Data Collection**: No telemetry or usage data sent anywhere
- **Local Processing**: All analysis done locally on your machine
- **API Calls**: Only movie titles sent to OpenAI/TMDB APIs for identification

## 🧪 Testing

Run the test suite:
```bash
python -m pytest tests/ -v
```

Individual test files:
```bash
python tests/test_integration.py      # Integration tests
python tests/test_tmdb_cache.py       # TMDB cache tests
python tests/test_file_mover.py       # File operations tests
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

See [CONTRIBUTING.md](CONTRIBUTING.md) for detailed guidelines.

## 🐛 Troubleshooting

### Common Issues

**"No module named 'tkinter'"**
```bash
# Ubuntu/Debian
sudo apt-get install python3-tk

# CentOS/RHEL
sudo yum install tkinter
```

**"OpenAI API Error"**
- Check API key is correct and has credits
- Verify internet connection
- Check OpenAI service status

**"TMDB API Error"**
- Verify both API key and Bearer Token are correct
- Check TMDB service status
- Ensure you're not hitting rate limits

**"Permission denied"**
- Run as administrator (Windows) or with sudo (Linux)
- Check file/folder permissions
- Ensure destination folder is writable

## 📄 License

**Free & Open Source Software**

This project is **completely free** and licensed under the MIT License. You can:

✅ **Use** it for personal or commercial purposes  
✅ **Copy** and distribute it freely  
✅ **Modify** and create derivative works  
✅ **Sell** software that includes this code  

**Only requirement**: Give credit to **Pablo Murad (runawaydevil)** as the original author.

See the [LICENSE](LICENSE) file for complete details.

## 🙏 Acknowledgments

- **OpenAI** for GPT API and AI capabilities
- **The Movie Database (TMDB)** for comprehensive movie metadata
- **ReportLab** for PDF generation capabilities
- **Cryptography** library for secure API key storage
- All contributors and users who help improve this project

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/runawaydevil/organizer-movies/issues)
- **Discussions**: [GitHub Discussions](https://github.com/runawaydevil/organizer-movies/discussions)
- **Repository**: https://github.com/runawaydevil/organizer-movies.git

---

**Movie Organizer v0.01**  
**Made with ❤️ by Pablo Murad (runawaydevil)**  
*Organize your movie collection like a pro! 🎬*