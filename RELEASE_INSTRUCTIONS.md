# 🚀 Release Instructions - Movie Organizer v0.01

**Author: Pablo Murad (runawaydevil)**  
**Repository: https://github.com/runawaydevil/organizer-movies.git**

## 📦 Building the Windows Release

### Prerequisites
- Windows 10/11
- Python 3.8+ installed
- Internet connection (for downloading dependencies)

### Build Steps

1. **Quick Build (Recommended)**:
   ```cmd
   build_exe.bat
   ```

2. **Manual Build**:
   ```cmd
   python build_release.py
   ```

### What Gets Created

The build process creates a `release` folder containing:

```
release/
├── MovieOrganizer.exe              # Main application
├── Install_MovieOrganizer.bat      # System installer (requires admin)
├── Run_MovieOrganizer_Portable.bat # Portable launcher
├── README.md                       # Full documentation
├── API_SETUP.md                    # API setup guide
├── CLI_USAGE.md                    # CLI usage guide
├── LICENSE                         # MIT License
├── README_RELEASE.txt              # Release-specific instructions
└── Images/                         # Screenshots and icons
    └── 1.jpg
```

## 📋 Distribution Options

### Option 1: System Installation (Recommended)
- User runs `Install_MovieOrganizer.bat` as administrator
- Installs to `C:\Program Files\MovieOrganizer\`
- Creates desktop shortcut and start menu entry
- PDF reports saved in movie folders
- Includes uninstaller

### Option 2: Portable Mode
- User runs `Run_MovieOrganizer_Portable.bat`
- No installation required
- Runs from current folder
- PDF reports saved in program folder
- Perfect for USB drives or temporary use

## 🔧 Technical Details

### Executable Features
- **Self-contained**: All dependencies included
- **No Python required**: Runs on any Windows system
- **Secure config**: API keys stored in user profile
- **Working directory**: Reports saved appropriately based on mode

### File Locations

**Installed Mode**:
- Program: `C:\Program Files\MovieOrganizer\`
- Config: `%LOCALAPPDATA%\MovieOrganizer\`
- Reports: Same folder as movies being organized

**Portable Mode**:
- Program: Current folder
- Config: `%LOCALAPPDATA%\MovieOrganizer\`
- Reports: Program folder

### Security
- API keys encrypted and stored locally
- No network access except to OpenAI/TMDB APIs
- No telemetry or data collection
- Configuration never goes to GitHub

## 🎯 User Experience

### First Run
1. User runs the program
2. Settings window appears (if no config found)
3. User enters OpenAI API key (required)
4. User optionally enters TMDB keys
5. Configuration saved securely
6. Ready to organize movies!

### Subsequent Runs
1. Program loads saved configuration
2. User selects movie folder
3. AI analyzes movies automatically
4. User reviews and organizes
5. PDF report generated automatically

## 📊 Build Process Details

The `build_release.py` script:

1. **Installs dependencies** (PyInstaller, etc.)
2. **Creates icon** from PIL if available
3. **Generates version info** for Windows executable
4. **Creates PyInstaller spec** with all required files
5. **Builds executable** with PyInstaller
6. **Creates installer script** with admin privileges
7. **Creates portable launcher** for current directory
8. **Packages everything** in release folder

## 🐛 Troubleshooting Build Issues

### Common Problems

**"PyInstaller not found"**
```cmd
pip install pyinstaller
```

**"Missing dependencies"**
```cmd
pip install -r requirements.txt
```

**"Build fails with import errors"**
- Check that all imports work: `python main.py`
- Verify all files exist in project directory

**"Executable won't run"**
- Test on clean Windows system
- Check Windows Defender/antivirus
- Verify all DLLs included

### Debug Build
```cmd
python -m PyInstaller --debug=all MovieOrganizer.spec
```

## 📈 Release Checklist

Before distributing:

- [ ] Test executable on clean Windows system
- [ ] Verify installer works with admin privileges
- [ ] Test portable mode in different folders
- [ ] Confirm API key storage works
- [ ] Test PDF report generation
- [ ] Verify all documentation included
- [ ] Check file sizes are reasonable
- [ ] Test uninstaller works correctly

## 🌐 Distribution

### GitHub Release
1. Create release tag: `v0.01`
2. Upload `release` folder as ZIP
3. Include release notes
4. Mark as stable release

### Direct Distribution
1. ZIP the entire `release` folder
2. Share with users
3. Include `README_RELEASE.txt` instructions

## 📞 Support

If users have issues:

1. **Check requirements**: Windows 10+, no Python needed
2. **Antivirus**: May flag executable, add exception
3. **Permissions**: Installer needs admin rights
4. **API keys**: Must be configured for program to work
5. **Logs**: Check `movie_organizer.log` for errors

---

**Movie Organizer v0.01**  
**Made with ❤️ by Pablo Murad (runawaydevil)**  
*Ready for Windows distribution! 🎬*