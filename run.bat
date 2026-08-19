@echo off
title QR Digital Studio
cd /d "%~dp0"

echo ======================================================
echo    Iniciando QR Digital Studio (Servidor Local)
echo ======================================================
echo.

IF EXIST ".venv\Scripts\python.exe" (
    ".venv\Scripts\python.exe" run.py
) ELSE IF EXIST "venv\Scripts\python.exe" (
    "venv\Scripts\python.exe" run.py
) ELSE (
    python run.py
)

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [ERROR] Ocurrio un problema al iniciar. Verifica que las dependencias esten instaladas:
    echo pip install -r requirements.txt
    echo.
    pause
)
