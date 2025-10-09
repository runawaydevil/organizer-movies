# 💻 CLI Usage Guide

**Movie Organizer v0.1 - Command Line Interface**  
*Author: Pablo Murad (runawaydevil)*

This guide covers the command-line interface (CLI) for Movie Organizer, perfect for batch processing, automation, and server environments.

## 🚀 Quick Start

### Prerequisites
- Movie Organizer configured with API keys (run GUI first)
- Python 3.8+ installed
- Terminal/Command Prompt access

### Basic Usage

```bash
# Show CLI help and version information
python services/cli_organizer.py
```

**Expected Output:**
```
🎬 Movie Organizer v0.1
AI-Powered Movie File Organizer with TMDB Integration
Author: Pablo Murad (runawaydevil)
Repository: https://github.com/runawaydevil/organizer-movies.git
============================================================

USAGE:
    python -m services.cli_organizer

DESCRIPTION:
    Command line interface for organizing movie files using AI and TMDB.
    
FEATURES:
    • AI-powered movie identification using OpenAI GPT
    • Optional TMDB integration for enhanced accuracy
    • Automatic folder creation and file organization
    • PDF report generation
    • Dry-run mode for preview
    
REQUIREMENTS:
    • OpenAI API Key (required)
    • TMDB API Key & Bearer Token (optional, recommended)
    
For GUI interface, run: python main.py

Author: Pablo Murad (runawaydevil)
Version: 0.1
Repository: https://github.com/runawaydevil/organizer-movies.git
```

## 📁 Organizing Movies

### Basic Organization

The CLI organizer automatically processes all movie files in a directory:

```bash
# Navigate to your movie directory
cd /path/to/your/movies

# Run the CLI organizer
python /path/to/movie-organizer/services/cli_organizer.py
```

### Example Session

**Input Directory Structure:**
```
/Movies/
├── action_movies/
│   ├── matrix.1999.mkv
│   ├── terminator.mkv
│   └── alien.mkv
├── random_folder/
│   └── pulp.fiction.1994.mp4
└── the.godfather.1972.avi
```

**CLI Output:**
```bash
$ python services/cli_organizer.py

🎬 Movie Organizer v0.1
AI-Powered Movie File Organizer with TMDB Integration
Author: Pablo Murad (runawaydevil)
Repository: https://github.com/runawaydevil/organizer-movies.git
============================================================

🎬 Initializing Hybrid Analyzer (AI + TMDB)...
📁 Scanning folder: /Movies
   Found 5 movie files

🎬 Analyzing and organizing 5 movies...
==================================================

[1/5] Processing: matrix.1999.mkv
   🔍 Analyzing with AI...
   📝 Identified: The Matrix (1999) [95.2%]
   📂 Target folder: The Matrix (1999)
   ✅ Organized: The Matrix (1999).mkv

[2/5] Processing: terminator.mkv
   🔍 Analyzing with AI...
   📝 Identified: Terminator (1984) [89.7%]
   📂 Target folder: Terminator (1984)
   ✅ Organized: Terminator (1984).mkv

[3/5] Processing: alien.mkv
   🔍 Analyzing with AI...
   📝 Identified: Alien (1979) [92.1%]
   📂 Target folder: Alien (1979)
   ✅ Organized: Alien (1979).mkv

[4/5] Processing: pulp.fiction.1994.mp4
   🔍 Analyzing with AI...
   📝 Identified: Pulp Fiction (1994) [96.8%]
   📂 Target folder: Pulp Fiction (1994)
   ✅ Organized: Pulp Fiction (1994).mp4

[5/5] Processing: the.godfather.1972.avi
   🔍 Analyzing with AI...
   📝 Identified: The Godfather (1972) [98.1%]
   📂 Target folder: The Godfather (1972)
   ✅ Organized: The Godfather (1972).avi

============================================================
📊 ORGANIZATION SUMMARY
============================================================
✅ Successfully organized: 5 movies
❌ Failed: 0 movies
📈 Success rate: 100.0%
🎬 Movie Organizer v0.1 by Pablo Murad (runawaydevil)

📄 Generating PDF report...
✅ PDF report generated successfully!
```

**Result Directory Structure:**
```
/Movies/
├── action_movies/
│   ├── Terminator (1984)/
│   │   └── Terminator (1984).mkv
│   └── Alien (1979)/
│       └── Alien (1979).mkv
├── random_folder/
│   └── Pulp Fiction (1994)/
│       └── Pulp Fiction (1994).mp4
├── The Matrix (1999)/
│   └── The Matrix (1999).mkv
├── The Godfather (1972)/
│   └── The Godfather (1972).avi
└── organized_movies_report.pdf
```

## 🔧 Configuration

### API Configuration

The CLI uses the same configuration as the GUI. Configure APIs first:

```bash
# Run GUI to configure APIs
python main.py

# Then use CLI with saved configuration
python services/cli_organizer.py
```

### Configuration Check

```bash
# Check if APIs are configured
python -c "
from services.cli_organizer import CLIOrganizer
config = {'openai_api_key': 'test'}
try:
    organizer = CLIOrganizer(config)
    print('✅ Configuration loaded successfully')
except Exception as e:
    print(f'❌ Configuration error: {e}')
"
```

## 🤖 AI vs Hybrid Mode

### AI-Only Mode
When only OpenAI API is configured:

```
🤖 Initializing AI-only Analyzer...
📁 Scanning folder: /Movies
   Found 3 movie files

🎬 Analyzing and organizing 3 movies...
==================================================

[1/3] Processing: movie.file.mkv
   🔍 Analyzing with AI...
   📝 Identified: Movie Title (2023) [87.3%]
   📂 Target folder: Movie Title (2023)
   ✅ Organized: Movie Title (2023).mkv
```

### Hybrid Mode (AI + TMDB)
When both APIs are configured:

```
🎬 Initializing Hybrid Analyzer (AI + TMDB)...
📁 Scanning folder: /Movies
   Found 3 movie files

🎬 Analyzing and organizing 3 movies...
==================================================

[1/3] Processing: movie.file.mkv
   🔍 Analyzing with AI...
   📝 Identified: Movie Title (2023) [95.8%] (TMDB Enhanced)
   📂 Target folder: Movie Title (2023)
   ✅ Organized: Movie Title (2023).mkv
```

## 📊 Understanding Output

### Progress Information
- **[X/Y]**: Current file number out of total
- **Processing**: Current filename being analyzed
- **Analyzing with AI**: AI identification in progress
- **Identified**: Movie title, year, and confidence percentage
- **Target folder**: Destination folder name
- **Organized**: Final result

### Confidence Scores
- **90-100%**: Excellent confidence, very likely correct
- **80-89%**: Good confidence, probably correct
- **70-79%**: Moderate confidence, review recommended
- **Below 70%**: Low confidence, manual review needed

### Status Icons
- **✅**: Success
- **❌**: Failed
- **🔍**: Processing
- **📝**: Identified
- **📂**: Folder operation
- **📄**: Report generation

## 🚨 Error Handling

### Common Errors and Solutions

**"No movie files found"**
```bash
📁 Scanning folder: /Movies
   No movie files found.
```
**Solution**: Check if directory contains video files with supported extensions

**"Failed to analyze movie"**
```bash
[1/5] Processing: corrupted.file.mkv
   🔍 Analyzing with AI...
   ❌ Failed to analyze movie
```
**Solution**: File might have unclear name or AI couldn't identify it

**"API key not configured"**
```bash
❌ Error organizing folder: OpenAI API key not configured
```
**Solution**: Run GUI first to configure API keys

### Handling Failed Files

The CLI continues processing even when individual files fail:

```bash
[1/5] Processing: unclear.filename.mkv
   🔍 Analyzing with AI...
   ❌ Failed to analyze movie

[2/5] Processing: matrix.1999.mkv
   🔍 Analyzing with AI...
   📝 Identified: The Matrix (1999) [95.2%]
   ✅ Organized: The Matrix (1999).mkv

============================================================
📊 ORGANIZATION SUMMARY
============================================================
✅ Successfully organized: 4 movies
❌ Failed: 1 movies
📈 Success rate: 80.0%
```

## 🔄 Automation & Scripting

### Batch Processing Script

Create a script to process multiple directories:

```bash
#!/bin/bash
# organize_all_movies.sh

MOVIE_ORGANIZER_PATH="/path/to/movie-organizer"
MOVIE_DIRECTORIES=(
    "/media/movies/action"
    "/media/movies/comedy"
    "/media/movies/drama"
)

for dir in "${MOVIE_DIRECTORIES[@]}"; do
    echo "Processing: $dir"
    cd "$dir"
    python "$MOVIE_ORGANIZER_PATH/services/cli_organizer.py"
    echo "Completed: $dir"
    echo "----------------------------------------"
done
```

### Cron Job Example

Automate organization with cron (Linux):

```bash
# Edit crontab
crontab -e

# Add line to run every Sunday at 2 AM
0 2 * * 0 cd /media/movies && python /path/to/movie-organizer/services/cli_organizer.py
```

### Windows Task Scheduler

Create a batch file for Windows automation:

```batch
@echo off
cd /d "C:\Movies"
python "C:\movie-organizer\services\cli_organizer.py"
pause
```

## 📈 Performance Tips

### Large Collections
- **Process in batches**: Organize folders separately for better control
- **Monitor API usage**: Check OpenAI usage to avoid unexpected costs
- **Use caching**: TMDB results are cached to improve performance

### Network Drives
- **Slower processing**: Network operations take longer
- **Stable connection**: Ensure reliable network connection
- **Local processing**: Consider copying files locally first

### Resource Usage
- **Memory**: CLI uses minimal memory
- **CPU**: Light usage during AI analysis
- **Network**: API calls for each movie file

## 🔍 Debugging

### Enable Debug Mode

```bash
# Run with Python debug output
python -v services/cli_organizer.py

# Check log files
tail -f movie_organizer.log
```

### Test Single File

```bash
# Test with one file first
mkdir test_folder
cp "single.movie.mkv" test_folder/
cd test_folder
python /path/to/movie-organizer/services/cli_organizer.py
```

## 📞 Support

For CLI-specific issues:

1. **Check configuration**: Ensure APIs are set up via GUI first
2. **Test with GUI**: Verify same files work in GUI mode
3. **Check permissions**: Ensure CLI has read/write access to directories
4. **Review logs**: Check log files for detailed error information
5. **Create issue**: [GitHub Issues](https://github.com/runawaydevil/organizer-movies/issues)

## 💡 Pro Tips

1. **Start small**: Test with a few files before processing large collections
2. **Backup first**: Always backup your movie collection before organizing
3. **Review results**: Check the generated PDF report for accuracy
4. **Use descriptive names**: Better filenames lead to better AI identification
5. **Monitor costs**: Keep track of OpenAI API usage for budget control

---

**Movie Organizer v0.1**  
**Made with ❤️ by Pablo Murad (runawaydevil)**  
*Organize your movies from the command line! 💻*