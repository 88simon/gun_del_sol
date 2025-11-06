@echo off
REM ============================================================================
REM Gun Del Sol Launcher
REM ============================================================================
REM Starts the Gun Del Sol AutoHotkey script in the background
REM ============================================================================

set SCRIPT_DIR=%~dp0
set SCRIPT_NAME=gun_del_sol.ahk
set SCRIPT_PATH=%SCRIPT_DIR%%SCRIPT_NAME%

REM Check if AutoHotkey v2 is installed
where AutoHotkeyU64.exe >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    where AutoHotkey64.exe >nul 2>nul
    if %ERRORLEVEL% NEQ 0 (
        where AutoHotkey.exe >nul 2>nul
        if %ERRORLEVEL% NEQ 0 (
            echo ERROR: AutoHotkey v2 is not installed or not in PATH
            echo.
            echo Please install AutoHotkey v2 from: https://www.autohotkey.com/
            echo Make sure to install v2.0+, not v1.1
            echo.
            pause
            exit /b 1
        )
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

REM Kill existing instance if running (try all possible v2 executables)
taskkill /F /IM AutoHotkeyU64.exe /FI "WINDOWTITLE eq gun_del_sol.ahk*" >nul 2>nul
taskkill /F /IM AutoHotkey64.exe /FI "WINDOWTITLE eq gun_del_sol.ahk*" >nul 2>nul
taskkill /F /IM AutoHotkey.exe /FI "WINDOWTITLE eq gun_del_sol.ahk*" >nul 2>nul

REM Start the script
echo Starting Gun Del Sol...
start "" "%SCRIPT_PATH%"

REM Confirmation
timeout /t 2 /nobreak >nul
echo.
echo Gun Del Sol is now active!
echo Look for the green "H" icon in your system tray.
echo.
echo Press your mouse side button (XButton1) over any Solana address.
echo.
exit /b 0
