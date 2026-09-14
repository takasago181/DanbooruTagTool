@echo off
setlocal
rem Legacy Python/Tk entrypoint; this is not the accepted WPF practical-v1 app.
echo This is the legacy Python/Tk entrypoint, not the accepted WPF practical-v1 app.
cd /d "%~dp0..\.."
if defined PYTHONPATH (
    set "PYTHONPATH=%~dp0python;%PYTHONPATH%"
) else (
    set "PYTHONPATH=%~dp0python"
)

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
