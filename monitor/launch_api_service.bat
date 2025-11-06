@echo off
REM ============================================================================
REM Gun Del Sol API Service Launcher
REM ============================================================================
REM Starts the Flask REST API service that receives address registrations
REM ============================================================================

set SCRIPT_DIR=%~dp0
set PYTHON_SCRIPT=%SCRIPT_DIR%api_service.py

REM Check if Python is installed
where python >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Python is not installed or not in PATH
    echo.
    echo Please install Python 3.8+ from: https://www.python.org/downloads/
    echo Make sure to check "Add Python to PATH" during installation
    echo.
    pause
    exit /b 1
)

REM Check if script exists
if not exist "%PYTHON_SCRIPT%" (
    echo ERROR: Cannot find api_service.py
    echo Expected location: %PYTHON_SCRIPT%
    echo.
    pause
    exit /b 1
)

REM Check if Flask is installed
python -c "import flask" 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo Flask is not installed. Installing dependencies...
    echo.
    python -m pip install -r "%SCRIPT_DIR%requirements.txt"
    if %ERRORLEVEL% NEQ 0 (
        echo.
        echo ERROR: Failed to install Flask
        echo Please manually run: pip install flask
        echo.
        pause
        exit /b 1
    )
)

REM Start the API service
echo.
echo Starting Gun Del Sol API Service...
echo.
python "%PYTHON_SCRIPT%"

REM If we get here, the service was stopped
echo.
echo API service stopped.
pause