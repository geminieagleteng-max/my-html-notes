@echo off
title HTML Notes Auto Sync

echo ========================================
echo   Auto Syncing HTML Notes to GitHub...
echo ========================================
echo.

python generate_and_push.py

echo.
echo ========================================
echo   Sync Completed! Press any key to exit.
echo ========================================
pause > nul
