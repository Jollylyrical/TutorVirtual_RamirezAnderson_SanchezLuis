# Despliegue en Azure Web App Service

## Arquitectura de despliegue

El usuario accede desde el navegador mediante HTTPS. Azure recibe el tráfico seguro y lo dirige al servicio web. Dentro del contenedor o del App Service, Gunicorn expone Django por HTTP interno. Django se conecta a PostgreSQL por TCP 5432 y a MongoDB Atlas por el protocolo MongoDB/TCP 27017. La comunicación con IA externa se realiza por HTTPS REST API con API Key.

## Variables de entorno sugeridas

```text
SECRET_KEY=<valor-seguro>
DEBUG=False
ALLOWED_HOSTS=<nombre-app>.azurewebsites.net
CSRF_TRUSTED_ORIGINS=https://<nombre-app>.azurewebsites.net
DB_ENGINE=postgres
POSTGRES_DB=<db>
POSTGRES_USER=<usuario>
POSTGRES_PASSWORD=<clave>
POSTGRES_HOST=<host-postgres>
POSTGRES_PORT=5432
MONGODB_URI=mongodb+srv://<usuario>:<clave>@<cluster>.mongodb.net/?retryWrites=true&w=majority
MONGODB_DB=tutor_semantico
AI_PROVIDER=openai  # o gemini
OPENAI_API_KEY=<clave>
GEMINI_API_KEY=<clave>
```

## Comando de inicio recomendado

```bash
gunicorn config.wsgi:application --bind 0.0.0.0:8000 --workers 3
```

## Pasos generales

1. Crear Azure Web App Service para contenedor o Python App Service.
2. Configurar variables de entorno en Configuration > Application settings.
3. Conectar Azure Database for PostgreSQL o una base PostgreSQL externa.
4. Configurar MongoDB Atlas y permitir acceso desde Azure.
5. Ejecutar migraciones:

```bash
python manage.py migrate
python manage.py collectstatic --noinput
```

6. Activar HTTPS only en Azure.
7. Verificar `/api/health/`.

## Buenas prácticas de seguridad

- No subir `.env` real al repositorio.
- Usar HTTPS obligatorio.
- Rotar claves de API.
- Limitar CORS a dominios autorizados.
- Usar contraseñas fuertes y roles mínimos en bases de datos.
- Registrar auditoría de documentos y consultas.
