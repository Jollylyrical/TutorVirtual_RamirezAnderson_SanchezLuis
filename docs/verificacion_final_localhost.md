# Verificación final en localhost

Esta versión fue ajustada para evitar el error de conexión a PostgreSQL en Windows.

## Corrección aplicada

- Se agregó `.env` listo para ejecución local.
- Se agregó `LOCALHOST_MODE=True` y `USE_POSTGRES=False`.
- Django usa SQLite por defecto aunque exista una variable externa `DB_ENGINE=postgres`.
- Se agregó `run_localhost.bat` para ejecutar todo automáticamente.
- Se agregó `reset_localhost.bat` para reiniciar la base local.

## Pruebas realizadas

Se ejecutaron correctamente:

```bash
python manage.py check
python manage.py migrate --noinput
python manage.py seed_demo
python manage.py test
```

También se verificaron con respuesta HTTP 200 las rutas:

```text
/
/login/
/registro/
/api/health/
/dashboard/
/arquitectura/
/conocimiento/
/tutor/
/historial/
```

La verificación se realizó con los cuatro roles demo:

- Administrador
- Gestor del conocimiento
- Tutor / Docente
- Estudiante / Aprendiz

## Ejecución recomendada

En Windows, desde la carpeta principal, ejecutar:

```text
run_localhost.bat
```

