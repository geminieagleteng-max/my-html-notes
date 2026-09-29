@echo off
chcp 65001 > nul
title 雲端 HTML 筆記一鍵同步工具

echo ========================================
echo    🚀 開始自動同步 HTML 筆記至 GitHub
echo ========================================
echo.

python generate_and_push.py

echo.
echo ========================================
echo    ✅ 同步作業已完成！按任意鍵關閉視窗...
echo ========================================
pause > nul
