@echo off
setlocal
cd /d "%~dp0"

if not exist ".venv\Scripts\python.exe" (
  echo 初回セットアップが必要です。
  echo 先に DOWNLOAD_DATA.bat を実行してください。
  pause
  exit /b 1
)

if not exist "data\available_tags.csv" (
  echo 共起タグ索引がありません。
  echo DOWNLOAD_DATA.bat を実行してください。
  pause
  exit /b 1
)

if not exist "data\cooccurrence_all_normalized.npz" (
  echo 共起行列がありません。
  echo DOWNLOAD_DATA.bat を実行してください。
  pause
  exit /b 1
)

".venv\Scripts\pythonw.exe" app.py
