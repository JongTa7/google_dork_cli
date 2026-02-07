@echo off
REM Google Dork CLI - Windows Batch Wrapper
REM This script makes it easy to run the tool on Windows

setlocal enabledelayedexpansion

echo.
echo 🔍 Google Dork CLI Tool
echo ========================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    echo Please install Python from https://www.python.org/
    pause
    exit /b 1
)

REM Check if dependencies are installed
python -c "import requests, click, bs4" >nul 2>&1
if errorlevel 1 (
    echo Installing dependencies...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo Error installing dependencies
        pause
        exit /b 1
    )
)

echo Choose an option:
echo 1. Basic search (fastest)
echo 2. Search with stealth (recommended)
echo 3. Search with proxy support (advanced)
echo 4. Search and preview results
echo 5. Exit
echo.

set /p choice="Enter choice [1-5]: "

if "%choice%"=="1" (
    echo Running basic search...
    python google_dork_cli.py -f dorks.txt
) else if "%choice%"=="2" (
    echo Running search with stealth ^(5s delay^)...
    python google_dork_cli.py -f dorks.txt -d 5
) else if "%choice%"=="3" (
    echo Running search with proxies...
    python advanced.py -f dorks.txt --proxies proxies.txt -d 3
) else if "%choice%"=="4" (
    echo Running search with console output...
    python google_dork_cli.py -f dorks.txt --console
) else if "%choice%"=="5" (
    exit /b 0
) else (
    echo Invalid choice
    pause
    exit /b 1
)

echo.
echo Done! Check the results_*.csv and results_*.json files
pause
