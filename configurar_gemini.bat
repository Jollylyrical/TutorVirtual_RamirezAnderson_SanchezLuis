@echo off
chcp 65001 >nul
title Configurar Gemini - Tutor Virtual
if not exist .venv (
    echo Creando entorno virtual...
    python -m venv .venv
)
call .venv\Scripts\activate
python scripts\configure_gemini.py
pause
