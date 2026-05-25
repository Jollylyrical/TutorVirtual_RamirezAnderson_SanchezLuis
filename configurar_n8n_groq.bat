@echo off
chcp 65001 >nul
title Configurar n8n + Groq para Tutor Virtual
call .venv\Scripts\activate 2>nul
python scripts\configure_n8n_groq.py
pause
