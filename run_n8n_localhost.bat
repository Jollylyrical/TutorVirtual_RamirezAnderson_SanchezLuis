@echo off
chcp 65001 >nul
title n8n local para Tutor Virtual - GroqCloud

echo ==========================================================
echo   n8n LOCAL - TUTOR VIRTUAL + GROQCLOUD
echo ==========================================================
echo.
echo Este script levanta n8n con Docker en http://localhost:5678/
echo Luego importe el workflow:
echo n8n\workflows\tutor_virtual_groq_workflow.json
echo.

docker --version >nul 2>&1
if errorlevel 1 (
    echo Docker no esta instalado o no esta en PATH.
    echo Instale Docker Desktop, reinicie el equipo y vuelva a ejecutar este archivo.
    echo Mientras tanto puede usar el modo Groq directo desde http://127.0.0.1:8000/configuracion-n8n/
    pause
    exit /b 1
)

docker compose -f docker-compose.n8n.yml up -d n8n

echo.
echo n8n esta iniciando. Abra: http://localhost:5678/
echo En n8n: Workflows ^> Import from File ^> seleccione tutor_virtual_groq_workflow.json ^> Active.
echo Despues ejecute run_localhost.bat para iniciar Django.
echo.
start http://localhost:5678/
pause
