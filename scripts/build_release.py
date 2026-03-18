#!/usr/bin/env python3
"""
Build Release - Movie Organizer v0.1
Creates Windows executable and installer

Author: Pablo Murad (runawaydevil)
Repository: https://github.com/runawaydevil/organizer-movies.git
"""
import os
import sys
import subprocess
import shutil
from pathlib import Path

def install_dependencies():
    """Install required build dependencies"""
    print("📦 Installing build dependencies...")
    
    dependencies = [
        "pyinstaller>=5.0.0",
        "auto-py-to-exe>=2.0.0",
        "requests>=2.31.0",
        "openai>=1.0.0",
        "reportlab>=4.0.0",
        "pillow>=9.0.0",
        "cryptography>=3.4.0"
    ]
    
    for dep in dependencies:
        print(f"   Installing {dep}...")
        subprocess.run([sys.executable, "-m", "pip", "install", dep], check=True)
    
    print("✅ Dependencies installed successfully!")

def create_spec_file():
    """Create PyInstaller spec file"""
    spec_content = '''# -*- mode: python ; coding: utf-8 -*-
"""
Movie Organizer v0.1 - PyInstaller Spec File
Author: Pablo Murad (runawaydevil)
"""

from pathlib import Path

block_cipher = None

a = Analysis(
    ['../main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('../Images', 'Images'),
        ('../core', 'core'),
        ('../README.md', '.'),
        ('../LICENSE', '.'),
        ('../docs', 'docs'),
    ],
    hiddenimports=[
        'tkinter',
        'tkinter.ttk',
        'tkinter.messagebox',
        'tkinter.filedialog',
        'openai',
        'requests',
        'reportlab',
        'reportlab.pdfgen',
        'reportlab.lib',
        'reportlab.platypus',
        'PIL',
        'cryptography',
        'cryptography.fernet',
        'base64',
        'json',
        'pathlib',
        'threading',
        'logging',
        'datetime',
        'dataclasses',
        'typing',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'matplotlib',
        'numpy',
        'pandas',
        'scipy',
        'jupyter',
        'notebook',
        'IPython',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='MovieOrganizer',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    cofile=None,
    icon='../Images/icon.ico' if Path('../Images/icon.ico').exists() else None,
    version='version_info.txt'
)
'''
    
    with open('MovieOrganizer.spec', 'w') as f:
        f.write(spec_content)
    
    print("✅ Spec file created!")

def create_version_info():
    """Create version info file for Windows executable"""
    version_info = '''# UTF-8
#
# Movie Organizer v0.1 - Version Info
# Author: Pablo Murad (runawaydevil)
#

VSVersionInfo(
  ffi=FixedFileInfo(
    filevers=(0, 1, 0, 0),
    prodvers=(0, 1, 0, 0),
    mask=0x3f,
    flags=0x0,
    OS=0x40004,
    fileType=0x1,
    subtype=0x0,
    date=(0, 0)
  ),
  kids=[
    StringFileInfo(
      [
      StringTable(
        u'040904B0',
        [StringStruct(u'CompanyName', u'Pablo Murad (runawaydevil)'),
        StringStruct(u'FileDescription', u'AI-Powered Movie File Organizer with TMDB Integration'),
        StringStruct(u'FileVersion', u'0.1'),
        StringStruct(u'InternalName', u'MovieOrganizer'),
        StringStruct(u'LegalCopyright', u'© 2025 Pablo Murad (runawaydevil). Free Software under MIT License.'),
        StringStruct(u'OriginalFilename', u'MovieOrganizer.exe'),
        StringStruct(u'ProductName', u'Movie Organizer'),
        StringStruct(u'ProductVersion', u'0.1')])
      ]), 
    VarFileInfo([VarStruct(u'Translation', [1033, 1200])])
  ]
)
'''
    
    with open('version_info.txt', 'w') as f:
        f.write(version_info)
    
    print("✅ Version info created!")

def create_icon():
    """Create a simple icon for the executable"""
    try:
        from PIL import Image, ImageDraw
        
        # Create a simple icon
        size = (64, 64)
        img = Image.new('RGBA', size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        # Draw a film reel icon
        draw.ellipse([8, 8, 56, 56], fill=(70, 130, 180), outline=(25, 25, 112), width=2)
        draw.ellipse([20, 20, 44, 44], fill=(255, 255, 255))
        draw.ellipse([28, 28, 36, 36], fill=(70, 130, 180))
        
        # Save as ICO
        os.makedirs('../Images', exist_ok=True)
        img.save('../Images/icon.ico', format='ICO')
        print("✅ Icon created!")
        
    except ImportError:
        print("⚠️  PIL not available, skipping icon creation")

def build_executable():
    """Build the executable using PyInstaller"""
    print("🔨 Building executable...")
    
    # Clean previous builds
    if Path('dist').exists():
        shutil.rmtree('dist')
    if Path('build').exists():
        shutil.rmtree('build')
    
    # Build with PyInstaller
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--clean",
        "--noconfirm",
        "MovieOrganizer.spec"
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode == 0:
        print("✅ Executable built successfully!")
        return True
    else:
        print("❌ Build failed!")
        print("STDOUT:", result.stdout)
        print("STDERR:", result.stderr)
        return False

def create_installer_script():
    """Create Windows batch installer script"""
    installer_content = '''@echo off
REM Movie Organizer v0.1 - Windows Installer
REM Author: Pablo Murad (runawaydevil)
REM Repository: https://github.com/runawaydevil/organizer-movies.git

echo.
echo ========================================
echo   Movie Organizer v0.1 - Installer
echo   Author: Pablo Murad (runawaydevil)
echo ========================================
echo.

REM Check for administrator privileges
net session >nul 2>&1
if %errorLevel% == 0 (
    echo ✅ Administrator privileges confirmed
) else (
    echo ❌ This installer requires administrator privileges
    echo Please right-click and select "Run as administrator"
    echo.
    pause
    exit /b 1
)

echo 📁 Creating installation directory...
set INSTALL_DIR=%ProgramFiles%\\MovieOrganizer
if not exist "%INSTALL_DIR%" mkdir "%INSTALL_DIR%"

echo 📦 Copying program files...
copy /Y "MovieOrganizer.exe" "%INSTALL_DIR%\\"
copy /Y "README.md" "%INSTALL_DIR%\\" 2>nul
copy /Y "LICENSE" "%INSTALL_DIR%\\" 2>nul

if exist "docs" (
    echo 📚 Copying documentation...
    if not exist "%INSTALL_DIR%\\docs" mkdir "%INSTALL_DIR%\\docs"
    copy /Y "docs\\*.*" "%INSTALL_DIR%\\docs\\" 2>nul
)

if exist "Images" (
    echo 📸 Copying images...
    if not exist "%INSTALL_DIR%\\Images" mkdir "%INSTALL_DIR%\\Images"
    copy /Y "Images\\*.*" "%INSTALL_DIR%\\Images\\" 2>nul
)

echo 🔗 Creating desktop shortcut...
set SHORTCUT_PATH=%USERPROFILE%\\Desktop\\Movie Organizer.lnk
powershell -Command "$WshShell = New-Object -comObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%SHORTCUT_PATH%'); $Shortcut.TargetPath = '%INSTALL_DIR%\\MovieOrganizer.exe'; $Shortcut.WorkingDirectory = '%INSTALL_DIR%'; $Shortcut.Description = 'AI-Powered Movie File Organizer v0.1'; $Shortcut.Save()"

echo 📋 Creating start menu entry...
set STARTMENU_DIR=%ProgramData%\\Microsoft\\Windows\\Start Menu\\Programs\\Movie Organizer
if not exist "%STARTMENU_DIR%" mkdir "%STARTMENU_DIR%"
set STARTMENU_SHORTCUT=%STARTMENU_DIR%\\Movie Organizer.lnk
powershell -Command "$WshShell = New-Object -comObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%STARTMENU_SHORTCUT%'); $Shortcut.TargetPath = '%INSTALL_DIR%\\MovieOrganizer.exe'; $Shortcut.WorkingDirectory = '%INSTALL_DIR%'; $Shortcut.Description = 'AI-Powered Movie File Organizer v0.1'; $Shortcut.Save()"

echo 📝 Creating uninstaller...
(
echo @echo off
echo echo Uninstalling Movie Organizer v0.1...
echo if exist "%USERPROFILE%\\Desktop\\Movie Organizer.lnk" del /q "%USERPROFILE%\\Desktop\\Movie Organizer.lnk"
echo if exist "%STARTMENU_DIR%" rmdir /s /q "%STARTMENU_DIR%"
echo if exist "%INSTALL_DIR%" rmdir /s /q "%INSTALL_DIR%"
echo echo Movie Organizer has been uninstalled.
echo pause
) > "%INSTALL_DIR%\\Uninstall.bat"

echo.
echo ========================================
echo ✅ Installation completed successfully!
echo ========================================
echo.
echo 📍 Installed to: %INSTALL_DIR%
echo 🖥️  Desktop shortcut created
echo 📋 Start menu entry created
echo.
echo 🚀 You can now run Movie Organizer from:
echo    • Desktop shortcut
echo    • Start menu
echo    • Or directly: %INSTALL_DIR%\\MovieOrganizer.exe
echo.
echo 📄 PDF reports will be generated in the same folder as your movies
echo 🔧 Configuration is stored securely in your user profile
echo.
echo 📖 For help with API setup, see: docs\\API_SETUP.md
echo 💻 For CLI usage, see: docs\\CLI_USAGE.md
echo.
echo Author: Pablo Murad (runawaydevil)
echo Repository: https://github.com/runawaydevil/organizer-movies.git
echo.
pause
'''
    
    with open('Install_MovieOrganizer.bat', 'w') as f:
        f.write(installer_content)
    
    print("✅ Installer script created!")

def create_portable_launcher():
    """Create portable launcher that sets working directory"""
    launcher_content = '''@echo off
REM Movie Organizer v0.1 - Portable Launcher
REM Author: Pablo Murad (runawaydevil)
REM Sets working directory to current folder for PDF reports

echo 🎬 Starting Movie Organizer v0.1...
echo Author: Pablo Murad (runawaydevil)
echo.
echo 📁 Working directory: %~dp0
echo 📄 PDF reports will be saved here
echo.

REM Change to the directory where this batch file is located
cd /d "%~dp0"

REM Run the executable
start "" "MovieOrganizer.exe"
'''
    
    with open('Run_MovieOrganizer_Portable.bat', 'w') as f:
        f.write(launcher_content)
    
    print("✅ Portable launcher created!")

def create_release_package():
    """Create the final release package"""
    print("📦 Creating release package...")
    
    # Create release directory
    release_dir = Path("../release")
    if release_dir.exists():
        shutil.rmtree(release_dir)
    release_dir.mkdir()
    
    # Copy executable
    if Path("dist/MovieOrganizer.exe").exists():
        shutil.copy2("dist/MovieOrganizer.exe", release_dir)
        print("   ✅ Executable copied")
    else:
        print("   ❌ Executable not found!")
        return False
    
    # Copy documentation
    docs = ["../README.md", "../LICENSE"]
    for doc in docs:
        if Path(doc).exists():
            shutil.copy2(doc, release_dir)
            print(f"   ✅ {Path(doc).name} copied")
    
    # Copy docs folder
    if Path("../docs").exists():
        shutil.copytree("../docs", release_dir / "docs")
        print("   ✅ Documentation folder copied")
    
    # Copy images
    if Path("../Images").exists():
        shutil.copytree("../Images", release_dir / "Images")
        print("   ✅ Images copied")
    
    # Copy installer and launcher
    shutil.copy2("Install_MovieOrganizer.bat", release_dir)
    shutil.copy2("Run_MovieOrganizer_Portable.bat", release_dir)
    print("   ✅ Scripts copied")
    
    # Create README for release
    release_readme = '''# Movie Organizer v0.1 - Windows Release

**AI-Powered Movie File Organizer with TMDB Integration**

Author: Pablo Murad (runawaydevil)
Repository: https://github.com/runawaydevil/organizer-movies.git

## 🚀 Quick Start

### Option 1: Install (Recommended)
1. Right-click `Install_MovieOrganizer.bat`
2. Select "Run as administrator"
3. Follow the installation prompts
4. Use desktop shortcut or start menu to run

### Option 2: Portable
1. Double-click `Run_MovieOrganizer_Portable.bat`
2. Program runs from current folder
3. PDF reports saved in this folder

## 📋 What's Included

- `MovieOrganizer.exe` - Main application
- `Install_MovieOrganizer.bat` - System installer (requires admin)
- `Run_MovieOrganizer_Portable.bat` - Portable launcher
- `README.md` - Full documentation
- `docs/` - Complete documentation folder
  - `API_SETUP.md` - API configuration guide
  - `CLI_USAGE.md` - Command line usage
  - `TROUBLESHOOTING.md` - Common issues and solutions
  - `DEVELOPER_SETUP.md` - Developer information
  - `CONTRIBUTING.md` - Contribution guidelines
- `LICENSE` - MIT License
- `Images/` - Application screenshots

## 🔑 First Time Setup

1. Get OpenAI API key from: https://platform.openai.com/api-keys
2. (Optional) Get TMDB API keys from: https://www.themoviedb.org/settings/api
3. Run Movie Organizer
4. Go to Settings and enter your API keys
5. Keys are saved securely and persist between runs

## 📄 PDF Reports

- Reports are generated automatically after organizing movies
- **Installed version**: Reports saved in your movie folders
- **Portable version**: Reports saved in the program folder

## 🆘 Support

- Issues: https://github.com/runawaydevil/organizer-movies/issues
- Documentation: See included docs/ folder
- Author: Pablo Murad (runawaydevil)

---

**Movie Organizer v0.1 - Free Software under MIT License**
'''
    
    with open(release_dir / "README_RELEASE.txt", 'w') as f:
        f.write(release_readme)
    
    print("   ✅ Release README created")
    print("✅ Release package created in '../release' folder!")
    return True

def main():
    """Main build process"""
    print("🎬 Movie Organizer v0.1 - Release Builder")
    print("Author: Pablo Murad (runawaydevil)")
    print("Repository: https://github.com/runawaydevil/organizer-movies.git")
    print("=" * 60)
    print()
    
    # Change to scripts directory
    os.chdir(Path(__file__).parent)
    
    try:
        # Step 1: Install dependencies
        install_dependencies()
        print()
        
        # Step 2: Create build files
        create_icon()
        create_version_info()
        create_spec_file()
        print()
        
        # Step 3: Build executable
        if not build_executable():
            return 1
        print()
        
        # Step 4: Create installer and launcher
        create_installer_script()
        create_portable_launcher()
        print()
        
        # Step 5: Create release package
        if not create_release_package():
            return 1
        print()
        
        print("🎉 BUILD COMPLETED SUCCESSFULLY!")
        print("=" * 60)
        print()
        print("📦 Release package created in '../release' folder")
        print("📁 Contents:")
        print("   • MovieOrganizer.exe - Main application")
        print("   • Install_MovieOrganizer.bat - System installer")
        print("   • Run_MovieOrganizer_Portable.bat - Portable launcher")
        print("   • docs/ - Complete documentation")
        print("   • Images/ - Screenshots and resources")
        print()
        print("🚀 Ready for distribution!")
        print("📋 Users can choose between installation or portable mode")
        print("📄 PDF reports will be generated in appropriate locations")
        print()
        print("Author: Pablo Murad (runawaydevil)")
        
        return 0
        
    except Exception as e:
        print(f"❌ Build failed: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())