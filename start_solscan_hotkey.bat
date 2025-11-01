@echo off
REM ============================================================================
REM Solscan Hotkey Launcher
REM ============================================================================
REM Starts the AutoHotkey script silently in the background
REM ============================================================================

set SCRIPT_DIR=%~dp0
set SCRIPT_NAME=solscan_hotkey.ahk
set SCRIPT_PATH=%SCRIPT_DIR%%SCRIPT_NAME%

REM Check if AutoHotkey is installed
where ahk >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    where AutoHotkey.exe >nul 2>nul
    if %ERRORLEVEL% NEQ 0 (
        echo ERROR: AutoHotkey is not installed or not in PATH
        echo.
        echo Please install AutoHotkey from: https://www.autohotkey.com/
        echo.
        pause
        exit /b 1
    )
)

REM Check if script exists
if not exist "%SCRIPT_PATH%" (
    echo ERROR: Cannot find %SCRIPT_NAME%
    echo Expected location: %SCRIPT_PATH%
    echo.
    pause
    exit /b 1
)

REM Kill existing instance if running
taskkill /F /IM AutoHotkey.exe /FI "WINDOWTITLE eq solscan_hotkey.ahk*" >nul 2>nul

REM Start the script
echo Starting Solscan Hotkey...
start "" "%SCRIPT_PATH%"

REM Confirmation
timeout /t 2 /nobreak >nul
echo.
echo Solscan Hotkey is now active!
echo Look for the green "H" icon in your system tray.
echo.
echo Press your mouse side button (XButton1) over any Solana address.
echo.
exit /b 0
