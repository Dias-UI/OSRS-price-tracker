@echo off
echo ====================================
echo OSRS Price Monitor - Installation
echo ====================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8 or higher from python.org
    pause
    exit /b 1
)

echo Python detected. Installing dependencies...
echo.

REM Install requirements
pip install -r requirements.txt

if errorlevel 1 (
    echo.
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)

echo.
echo ====================================
echo Installing item database...
echo ====================================
echo.

REM Download item database
python download_items.py

echo.
echo ====================================
echo Installation Complete!
echo ====================================
echo.
echo You can now run the app using: run.bat
echo Or double-click run.bat
echo.
pause
