@echo off
echo Stopping AutoHotkey...
taskkill /F /IM AutoHotkey64.exe 2>nul
timeout /t 1 /nobreak >nul
echo Starting AutoHotkey script...
start "" "c:\Users\simon\OneDrive\Desktop\solscan_hotkey\solscan_hotkey.ahk"
echo Done! Script restarted.
timeout /t 2