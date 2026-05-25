# Manual técnico - Tutor Virtual Inteligente

## Componentes
- Django: vistas web, autenticación por sesión y plantillas.
- Django REST Framework: API REST para autenticación JWT, documentos y tutor IA.
- PostgreSQL o SQLite: datos relacionales.
- MongoDB: fragmentos documentales para recuperación semántica.
- Fallback SQL: búsqueda local cuando MongoDB no está disponible.
- AIGateway: proveedor local, OpenAI o Gemini.
- Nginx/Gunicorn/Uvicorn: despliegue conforme al diagrama UML.

## Ejecución local rápida
```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
python manage.py migrate
python manage.py seed_demo
python manage.py runserver
```

## Variables principales
- `DB_ENGINE=sqlite` para localhost simple.
- `DB_ENGINE=postgres` para arquitectura con PostgreSQL.
- `MONGODB_URI` para MongoDB local o Atlas.
- `AI_PROVIDER=local`, `openai` o `gemini`.

## API
- `POST /api/auth/register/`
- `POST /api/auth/token/`
- `GET/POST /api/knowledge/documents/`
- `POST /api/ai/ask/`
- `GET /api/ai/history/`
- `GET /api/health/`
