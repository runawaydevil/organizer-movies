@echo off
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