@echo off
chcp 65001 >nul
title Reiniciar base local - Tutor Virtual
set LOCALHOST_MODE=True
set USE_POSTGRES=False
set DB_ENGINE=sqlite
set AI_PROVIDER=local

call .venv\Scripts\activate
if exist db.sqlite3 del db.sqlite3
python manage.py migrate --noinput
python manage.py seed_demo
echo Base local reiniciada correctamente.
pause
