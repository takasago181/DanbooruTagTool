@echo off
setlocal
cd /d "%~dp0"

where py >nul 2>nul
if errorlevel 1 goto use_python
py -3.12 -m danbooru_tag_tool
exit /b %errorlevel%

:use_python
where python >nul 2>nul
if errorlevel 1 goto no_python
python -m danbooru_tag_tool
exit /b %errorlevel%

:no_python
echo Python 3 が見つかりません。Python 3（Tcl/Tkを含む）をインストールしてください。
pause
exit /b 1
