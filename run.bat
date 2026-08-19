@echo off
title QR Digital Studio
echo Iniciando QR Digital Studio...

IF EXIST .venv\Scripts\activate.bat (
    call .venv\Scripts\activate.bat
    python run.py
) ELSE (
    python run.py
)
pause
