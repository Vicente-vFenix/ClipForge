@echo off
chcp 65001 >nul
cd /d "%~dp0"

REM ClipForge necesita Python 3.12 (otras versiones como la 3.14 rompen PyTorch).
REM Comprobamos que Python 3.12 esta instalado antes de arrancar.
py -3.12 --version >nul 2>&1
if errorlevel 1 (
    echo.
    echo ============================================================
    echo   No se ha encontrado Python 3.12 en este equipo.
    echo.
    echo   ClipForge necesita Python 3.12 para funcionar.
    echo   Descargalo desde:
    echo     https://www.python.org/downloads/release/python-3120/
    echo.
    echo   Despues, ejecuta primero "instalar.py" con:
    echo     py -3.12 instalar.py
    echo ============================================================
    echo.
    pause
    exit /b 1
)

REM Arrancamos el programa con Python 3.12
py -3.12 main.py

if errorlevel 1 (
    echo.
    echo La aplicacion se cerro con un error.
    echo Revisa el archivo video_editor.log
    echo.
    pause
)
