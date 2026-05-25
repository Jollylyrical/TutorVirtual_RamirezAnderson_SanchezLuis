@echo off
chcp 65001 >nul
title Tutor Virtual Gestion del Conocimiento - Localhost n8n + Groq
set LOCALHOST_MODE=True
set USE_POSTGRES=False
set DB_ENGINE=sqlite
set AI_PROVIDER=n8n

echo ==========================================================
echo   TUTOR VIRTUAL - GESTION DEL CONOCIMIENTO
echo   Localhost con SQLite + n8n Webhook + GroqCloud
echo ==========================================================
echo.
echo Si no ha configurado Groq, abra despues:
echo http://127.0.0.1:8000/configuracion-n8n/
echo.

if not exist .venv (
    echo Creando entorno virtual...
    python -m venv .venv
)

call .venv\Scripts\activate

echo Instalando dependencias...
python -m pip install --upgrade pip
pip install -r requirements.txt

echo Aplicando migraciones...
python manage.py migrate --noinput

echo Cargando datos demo...
python manage.py seed_demo

echo.
echo Proyecto listo. Abra: http://127.0.0.1:8000/
echo Configurar n8n + Groq: http://127.0.0.1:8000/configuracion-n8n/
echo n8n local: http://localhost:5678/
echo.
echo Usuarios demo:
echo admin_demo / Admin12345*
echo gestor_demo / Gestor12345*
echo tutor_demo / Tutor12345*
echo estudiante_demo / Estudiante12345*
echo.
start http://127.0.0.1:8000/
python manage.py runserver 127.0.0.1:8000
pause
