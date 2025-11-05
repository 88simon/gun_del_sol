@echo off
echo Starting Solana Monitor Service...
echo.
cd /d "%~dp0"
python monitor_service.py
pause