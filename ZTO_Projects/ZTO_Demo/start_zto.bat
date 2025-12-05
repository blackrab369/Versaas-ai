@echo off
echo Starting Zero-to-One Virtual Software Inc...
echo.
echo ========================================
echo ZTO Inc. - Virtual Company Launcher
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed or not in PATH!
    echo Please install Python 3.8+ from https://python.org
    pause
    exit /b 1
)

REM Check if requirements are installed
python -c "import pygame" >nul 2>&1
if %errorlevel% neq 0 (
    echo Installing required packages...
    pip install -r requirements.txt
)

REM Launch the main application
echo Launching ZTO Inc. main menu...
python launch_zto.py --no-shortcut

echo.
echo ZTO Inc. session ended.
pause