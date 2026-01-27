@echo off
echo ====================================
echo OSRS Price Monitor
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

REM Check if dependencies are installed
python -c "import customtkinter" >nul 2>&1
if errorlevel 1 (
    echo.
    echo Dependencies not installed!
    echo Please run install.bat first.
    echo.
    pause
    exit /b 1
)

echo Starting OSRS Price Monitor...
echo.

REM Run the application
python osrs_price_monitor.py

pause
