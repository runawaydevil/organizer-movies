@echo off
echo Building Movie Organizer v0.01...
echo Author: Pablo Murad (runawaydevil)
echo.

python -m PyInstaller ^
--onefile ^
--windowed ^
--name=MovieOrganizer ^
--add-data="Images;Images" ^
--add-data="version.py;." ^
--hidden-import=tkinter ^
--hidden-import=tkinter.ttk ^
--hidden-import=tkinter.messagebox ^
--hidden-import=tkinter.filedialog ^
--hidden-import=openai ^
--hidden-import=requests ^
--hidden-import=reportlab ^
--hidden-import=cryptography ^
--hidden-import=PIL ^
--clean ^
main_exe.py

if %errorlevel% == 0 (
    echo.
    echo Build completed successfully!
    echo Executable: dist\MovieOrganizer.exe
    echo.
    echo Testing executable...
    timeout /t 2 /nobreak >nul
    start "" "dist\MovieOrganizer.exe"
) else (
    echo.
    echo Build failed!
    pause
)