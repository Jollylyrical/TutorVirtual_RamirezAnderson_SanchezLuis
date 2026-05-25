# Verificación final: Tutor Virtual con Gemini

## Estado de la versión

La versión queda preparada para funcionar en localhost con:

- Django + Django REST Framework.
- Autenticación web y JWT.
- Dashboards por rol.
- SQLite para ejecución local inmediata.
- PostgreSQL preparado para despliegue.
- MongoDB opcional con respaldo SQL local.
- Tutor virtual conectado a Gemini API mediante `generateContent`.
- Panel visual para guardar y probar el token de Gemini.

## Rutas verificadas

- `/`
- `/login/`
- `/dashboard/`
- `/tutor/`
- `/configuracion-gemini/`
- `/conocimiento/`
- `/historial/`
- `/arquitectura/`
- `/api/health/`

## Activación del token

El proyecto no incluye un token real por seguridad. Para activar la llamada externa:

1. Ejecutar `run_localhost.bat`.
2. Iniciar sesión con `admin_demo / Admin12345*`.
3. Entrar al menú lateral `Gemini Token`.
4. Pegar la API key/token de Gemini.
5. Presionar `Guardar y probar conexión`.
6. Entrar a `Tutor IA` y realizar una pregunta.

## Comprobación técnica

Cuando la configuración es correcta, `/api/health/` debe mostrar:

```json
{
  "ai_provider": "gemini",
  "ai_ready": true
}
```

Si `ai_ready` aparece en `false`, falta pegar el token o el token no quedó guardado en `.env`.
