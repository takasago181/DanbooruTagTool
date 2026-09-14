@echo off
setlocal
cd /d "%~dp0"
where py >nul 2>nul
if errorlevel 1 (
 echo Python Launcher "py" が見つかりません。
 pause
 exit /b 1
)
if not exist ".venv\Scripts\python.exe" (
 py -3 -m venv .venv
)
".venv\Scripts\python.exe" -m pip install --disable-pip-version-check -q numpy
if errorlevel 1 (
 echo numpy のインストールに失敗しました。
 pause
 exit /b 1
)
echo 約456MBの2026-05参考共起データを取得します。
".venv\Scripts\python.exe" download_reference_cooccurrence.py
pause
