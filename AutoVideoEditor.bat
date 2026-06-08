@echo off
chcp 65001 >nul
cd /d "%~dp0"

py main.py

if errorlevel 1 (
    echo.
    echo La aplicacion se cerro con un error.
    echo Revisa el archivo video_editor_debug.log
    echo.
    pause
)
