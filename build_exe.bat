@echo off
REM Movie Organizer v0.1 - Quick Build Script
REM Author: Pablo Murad (runawaydevil)

echo 🎬 Movie Organizer v0.1 - Quick Build
echo Author: Pablo Murad (runawaydevil)
echo.

echo 🔨 Building Windows executable...
python build_release.py

if %errorlevel% == 0 (
    echo.
    echo ✅ Build completed successfully!
    echo 📁 Check the 'release' folder for your executable
    echo.
    echo 🚀 To distribute:
    echo    1. Copy the entire 'release' folder
    echo    2. Users can run Install_MovieOrganizer.bat as admin
    echo    3. Or use Run_MovieOrganizer_Portable.bat for portable mode
    echo.
) else (
    echo.
    echo ❌ Build failed! Check the error messages above.
    echo.
)

pause