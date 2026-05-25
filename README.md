# Tutor Virtual Inteligente - Gestión del Conocimiento

## Versión actual: n8n + GroqCloud

Esta entrega queda preparada para funcionar en localhost con dashboards por rol y con el tutor virtual integrado mediante **n8n Webhook + GroqCloud API**.

Arranque rápido:

```bat
run_localhost.bat
```

Para n8n local con Docker:

```bat
run_n8n_localhost.bat
```

Importe en n8n el archivo:

```text
n8n/workflows/tutor_virtual_groq_workflow.json
```

La guía completa está en `README_N8N_GROQ_LOCALHOST.md`.

---

# Tutor Virtual Inteligente para Gestión del Conocimiento

Proyecto Django completo basado en los diagramas UML entregados: cliente web, Nginx reverse proxy, Django, servidor WSGI/ASGI, API REST, autenticación JWT, base relacional PostgreSQL/SQLite, repositorio documental MongoDB y conexión con IA local, OpenAI o Gemini.

## Qué incluye esta versión final

- Frontend profesional con barra lateral, dashboards por rol, tarjetas, métricas, rutas de aprendizaje, panel de arquitectura y repositorio visual.
- Funcionamiento en localhost con SQLite sin depender de PostgreSQL ni MongoDB.
- Fallback SQL para búsqueda documental cuando MongoDB no está activo.
- API REST con Django REST Framework y JWT.
- Login, registro, roles y dashboards diferenciados.
- Carga de documentos de conocimiento e indexación de fragmentos.
- Tutor IA funcional en modo local (`AI_PROVIDER=local`).
- Historial de preguntas y respuestas.
- Datos demo incluidos.
- Preparación para despliegue con Docker, Gunicorn, Nginx y Azure Web App Service.

## Ejecución rápida en Windows

Opción recomendada: haga doble clic en `run_localhost.bat`. Este archivo fuerza SQLite, instala dependencias, aplica migraciones, carga datos demo y abre el navegador.

Ejecución manual desde la carpeta del proyecto:

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py seed_demo
python manage.py runserver
```

Abra en el navegador:

```text
http://127.0.0.1:8000/
```

## Usuarios demo

| Rol | Usuario | Contraseña |
|---|---|---|
| Administrador | `admin_demo` | `Admin12345*` |
| Gestor del conocimiento | `gestor_demo` | `Gestor12345*` |
| Tutor / Docente | `tutor_demo` | `Tutor12345*` |
| Estudiante / Aprendiz | `estudiante_demo` | `Estudiante12345*` |

## Rutas principales

```text
/                       Inicio
/login/                 Login
/registro/              Registro
/dashboard/             Dashboard por rol
/tutor/                 Tutor IA
/conocimiento/          Base de conocimiento
/conocimiento/nuevo/    Cargar documento
/historial/             Historial del usuario
/arquitectura/          Arquitectura y protocolos
/api/health/            Estado de servicio
/api/auth/token/        Obtener JWT
/api/knowledge/         API de documentos
/api/ai/                API de IA
```

## Variables de entorno

Puede crear un archivo `.env` desde `.env.example`. Para localhost no es obligatorio modificar nada.

```env
DEBUG=True
DB_ENGINE=sqlite
AI_PROVIDER=local
ALLOWED_HOSTS=127.0.0.1,localhost
```

Para usar PostgreSQL en despliegue real:

```env
LOCALHOST_MODE=False
USE_POSTGRES=True
DB_ENGINE=postgres
POSTGRES_DB=tutor_conocimiento
POSTGRES_USER=tutor_user
POSTGRES_PASSWORD=tutor_password
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
```

Para usar MongoDB:

```env
MONGODB_URI=mongodb://localhost:27017
MONGODB_DB=tutor_semantico
MONGODB_COLLECTION=knowledge_chunks
```

Para IA externa:

```env
AI_PROVIDER=openai
OPENAI_API_KEY=su_clave
OPENAI_MODEL=gpt-4o-mini
```

o:

```env
AI_PROVIDER=gemini
GEMINI_API_KEY=su_clave
GEMINI_MODEL=gemini-1.5-flash
```

## Arquitectura aplicada

El proyecto implementa los componentes del diagrama:

1. Usuario/Cliente mediante navegador web.
2. Comunicación TCP/IP y HTTPS.
3. Reverse proxy Nginx para TLS/SSL en despliegue.
4. Aplicación Django con frontend HTML/CSS/JS.
5. Servidor WSGI/ASGI con Gunicorn/Uvicorn.
6. API REST con JWT Bearer Token.
7. PostgreSQL o SQLite para datos relacionales.
8. MongoDB Atlas/local o fallback SQL para conocimiento documental.
9. Servicio de IA externo mediante HTTPS REST API + API Key, o modo local.

## Verificación realizada

Se ejecutó:

```bash
python manage.py check
python manage.py migrate --noinput
python manage.py seed_demo
```

También se verificaron las rutas principales con los cuatro roles demo en localhost.


## Corrección de ejecución local

Esta versión incluye `.env` listo para localhost, `run_localhost.bat` y `reset_localhost.bat`. Por seguridad académica, el proyecto usa SQLite por defecto y solo usa PostgreSQL cuando `USE_POSTGRES=True` o `LOCALHOST_MODE=False`.

## Activación del tutor con Gemini API

Esta versión queda configurada para que el tutor virtual use Gemini como proveedor de IA externa.

1. Ejecute `run_localhost.bat`.
2. Inicie sesión con un usuario demo.
3. Abra el menú `Gemini Token`.
4. Pegue su API key/token de Gemini.
5. Use `Guardar y probar conexión`.
6. Regrese a `Tutor IA` y realice una pregunta.

También puede configurar el token con `configurar_gemini.bat` o editando el archivo `.env`:

```env
AI_PROVIDER=gemini
GEMINI_API_KEY=PEGUE_AQUI_SU_TOKEN_REAL
GEMINI_MODEL=gemini-2.0-flash
```

El proyecto no incluye una API key real por seguridad. Si no se configura el token, la aplicación sigue abriendo en localhost, pero el tutor mostrará el aviso correspondiente al intentar llamar Gemini.


## Configuración rápida con n8n Cloud

Esta entrega está preparada para usar su instancia:

```text
https://tutorvirtual.app.n8n.cloud/webhook/tutor-virtual-ai
```

Importe en n8n Cloud el workflow:

```text
n8n/workflows/tutor_virtual_groq_workflow_cloud.json
```

Después publique/active el workflow, ejecute `run_localhost.bat`, entre a `/configuracion-n8n/`, pegue su `GROQ_API_KEY` y presione **Guardar y probar conexión**.

Más detalles en `README_N8N_CLOUD_GROQ.md`.
