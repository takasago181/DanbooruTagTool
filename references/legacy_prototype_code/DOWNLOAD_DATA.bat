@echo off
setlocal
cd /d "%~dp0"

where py >nul 2>nul
if errorlevel 1 (
  echo Python Launcher "py" が見つかりません。
  echo Python 3 をインストールしてから再実行してください。
  pause
  exit /b 1
)

if not exist ".venv\Scripts\python.exe" (
  echo [SETUP] Python仮想環境を作成します...
  py -3 -m venv .venv
)

echo [SETUP] numpyを準備します...
".venv\Scripts\python.exe" -m pip install --disable-pip-version-check -q -r requirements.txt
if errorlevel 1 (
  echo numpyのインストールに失敗しました。
  pause
  exit /b 1
)

echo.
echo [DOWNLOAD] 共起データを取得します。
echo 約456MBあります。
echo.
".venv\Scripts\python.exe" download_data.py
if errorlevel 1 (
  pause
  exit /b 1
)

echo.
echo 完了しました。次は START.bat を実行してください。
pause
