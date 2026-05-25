@echo off
chcp 65001 >nul
echo ===============================================
echo CONFIGURAR n8n CLOUD + GROQ PARA TUTOR VIRTUAL
echo ===============================================
python scripts\configure_n8n_groq.py
echo.
echo Listo. Ejecute run_localhost.bat para iniciar Django.
pause
