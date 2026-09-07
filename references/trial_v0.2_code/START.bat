@echo off
setlocal
cd /d "%~dp0"
if exist ".venv\Scripts\pythonw.exe" (
  ".venv\Scripts\pythonw.exe" app\main.py
  exit /b
)
where py >nul 2>nul
if not errorlevel 1 (
  py -3w app\main.py
  exit /b
)
where python >nul 2>nul
if not errorlevel 1 (
  pythonw app\main.py
  exit /b
)
echo Python 3 が見つかりません。
echo Python 3 をインストールしてから再実行してください。
pause
