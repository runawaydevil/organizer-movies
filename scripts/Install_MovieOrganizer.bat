@echo off
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
set INSTALL_DIR=%ProgramFiles%\MovieOrganizer
if not exist "%INSTALL_DIR%" mkdir "%INSTALL_DIR%"

echo 📦 Copying program files...
copy /Y "MovieOrganizer.exe" "%INSTALL_DIR%\"
copy /Y "README.md" "%INSTALL_DIR%\" 2>nul
copy /Y "LICENSE" "%INSTALL_DIR%\" 2>nul

if exist "docs" (
    echo 📚 Copying documentation...
    if not exist "%INSTALL_DIR%\docs" mkdir "%INSTALL_DIR%\docs"
    copy /Y "docs\*.*" "%INSTALL_DIR%\docs\" 2>nul
)

if exist "Images" (
    echo 📸 Copying images...
    if not exist "%INSTALL_DIR%\Images" mkdir "%INSTALL_DIR%\Images"
    copy /Y "Images\*.*" "%INSTALL_DIR%\Images\" 2>nul
)

echo 🔗 Creating desktop shortcut...
set SHORTCUT_PATH=%USERPROFILE%\Desktop\Movie Organizer.lnk
powershell -Command "$WshShell = New-Object -comObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%SHORTCUT_PATH%'); $Shortcut.TargetPath = '%INSTALL_DIR%\MovieOrganizer.exe'; $Shortcut.WorkingDirectory = '%INSTALL_DIR%'; $Shortcut.Description = 'AI-Powered Movie File Organizer v0.1'; $Shortcut.Save()"

echo 📋 Creating start menu entry...
set STARTMENU_DIR=%ProgramData%\Microsoft\Windows\Start Menu\Programs\Movie Organizer
if not exist "%STARTMENU_DIR%" mkdir "%STARTMENU_DIR%"
set STARTMENU_SHORTCUT=%STARTMENU_DIR%\Movie Organizer.lnk
powershell -Command "$WshShell = New-Object -comObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%STARTMENU_SHORTCUT%'); $Shortcut.TargetPath = '%INSTALL_DIR%\MovieOrganizer.exe'; $Shortcut.WorkingDirectory = '%INSTALL_DIR%'; $Shortcut.Description = 'AI-Powered Movie File Organizer v0.1'; $Shortcut.Save()"

echo 📝 Creating uninstaller...
(
echo @echo off
echo echo Uninstalling Movie Organizer v0.1...
echo if exist "%USERPROFILE%\Desktop\Movie Organizer.lnk" del /q "%USERPROFILE%\Desktop\Movie Organizer.lnk"
echo if exist "%STARTMENU_DIR%" rmdir /s /q "%STARTMENU_DIR%"
echo if exist "%INSTALL_DIR%" rmdir /s /q "%INSTALL_DIR%"
echo echo Movie Organizer has been uninstalled.
echo pause
) > "%INSTALL_DIR%\Uninstall.bat"

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
echo    • Or directly: %INSTALL_DIR%\MovieOrganizer.exe
echo.
echo 📄 PDF reports will be generated in the same folder as your movies
echo 🔧 Configuration is stored securely in your user profile
echo.
echo 📖 For help with API setup, see: docs\API_SETUP.md
echo 💻 For CLI usage, see: docs\CLI_USAGE.md
echo.
echo Author: Pablo Murad (runawaydevil)
echo Repository: https://github.com/runawaydevil/organizer-movies.git
echo.
pause