@echo off
REM Build Resume Tailor as a Windows executable
REM This creates a single .exe file you can put on your desktop

echo ╔═══════════════════════════════════════════════════════════╗
echo ║        Resume Tailor - Executable Builder             ║
echo ╚═══════════════════════════════════════════════════════════╝
echo.

REM Check if PyInstaller is installed
python -c "import PyInstaller" 2>nul
if errorlevel 1 (
    echo Installing PyInstaller...
    pip install pyinstaller
    echo.
)

echo Building executable...
echo.

REM Build the executable
python -m PyInstaller --onefile ^
    --windowed ^
    --name "Resume Tailor" ^
    --icon=NONE ^
    --add-data "import_career_data.py;." ^
    --add-data "generator.py;." ^
    --add-data "pdf_generator.py;." ^
    --add-data "html_template.py;." ^
    --add-data "docx_generator.py;." ^
    --add-data "conflict_detector.py;." ^
    --add-data ".env;." ^
    --hidden-import anthropic ^
    --hidden-import dotenv ^
    --hidden-import markdown ^
    --hidden-import weasyprint ^
    --hidden-import docx ^
    --hidden-import reportlab ^
    resume_tailor_gui.py

echo.
echo ╔═══════════════════════════════════════════════════════════╗
echo ║              BUILD COMPLETE!                           ║
echo ╚═══════════════════════════════════════════════════════════╝
echo.
echo Your executable is ready at:
echo   dist\Resume Tailor.exe
echo.
echo You can copy this file to your desktop and double-click to run!
echo.
pause
