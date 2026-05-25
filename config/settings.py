import os
from datetime import timedelta
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / '.env')

SECRET_KEY = os.getenv('SECRET_KEY', 'dev-local-secret-key-change-this-value-1234567890')
DEBUG = os.getenv('DEBUG', 'True').lower() == 'true'
ALLOWED_HOSTS = ['*']
CSRF_TRUSTED_ORIGINS = [
    "https://tutorvirtual-ramirezanderson-sanchezluis.onrender.com"
]
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'rest_framework_simplejwt',
    'apps.core',
    'apps.users',
    'apps.knowledge',
    'apps.ai_assistant',
    'corsheaders',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'
ASGI_APPLICATION = 'config.asgi.application'

# Modo seguro para entrega en localhost:
# Por defecto SIEMPRE usa SQLite, aunque exista una variable del sistema DB_ENGINE=postgres.
# Para despliegue real con PostgreSQL cambie LOCALHOST_MODE=False o USE_POSTGRES=True en .env.
LOCALHOST_MODE = os.getenv('LOCALHOST_MODE', 'True').lower() == 'true'
USE_POSTGRES = os.getenv('USE_POSTGRES', 'False').lower() == 'true'
DB_ENGINE = os.getenv('DB_ENGINE', 'sqlite').lower()

if USE_POSTGRES or (not LOCALHOST_MODE and DB_ENGINE == 'postgres'):
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': os.getenv('POSTGRES_DB', 'tutor_conocimiento'),
            'USER': os.getenv('POSTGRES_USER', 'tutor_user'),
            'PASSWORD': os.getenv('POSTGRES_PASSWORD', 'tutor_password'),
            'HOST': os.getenv('POSTGRES_HOST', 'localhost'),
            'PORT': os.getenv('POSTGRES_PORT', '5432'),
            'OPTIONS': {'connect_timeout': 5},
        }
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'es-co'
TIME_ZONE = 'America/Bogota'
USE_I18N = True
USE_TZ = True

STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
    'DEFAULT_RENDERER_CLASSES': (
        'rest_framework.renderers.JSONRenderer',
        'rest_framework.renderers.BrowsableAPIRenderer',
    ),
}

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=int(os.getenv('ACCESS_TOKEN_MINUTES', '60'))),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=int(os.getenv('REFRESH_TOKEN_DAYS', '7'))),
    'AUTH_HEADER_TYPES': ('Bearer',),
}

CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOW_CREDENTIALS = True

MONGODB_URI = os.getenv('MONGODB_URI', 'mongodb://localhost:27017')
MONGODB_DB = os.getenv('MONGODB_DB', 'tutor_semantico')
MONGODB_COLLECTION = os.getenv('MONGODB_COLLECTION', 'knowledge_chunks')

AI_PROVIDER = os.getenv('AI_PROVIDER', 'local').lower()

# Orquestación n8n + proveedor IA gratuito/experimental.
N8N_WEBHOOK_URL = os.getenv('N8N_WEBHOOK_URL', 'https://tutorvirtual.app.n8n.cloud/webhook/tutor-virtual-ai')
N8N_SHARED_SECRET = os.getenv('N8N_SHARED_SECRET', 'dev-n8n-secret')
N8N_TIMEOUT = int(os.getenv('N8N_TIMEOUT', '60'))
N8N_FALLBACK_PROVIDER = os.getenv('N8N_FALLBACK_PROVIDER', 'groq').lower()

# GroqCloud: API compatible con OpenAI, útil para prototipos por su capa gratuita y velocidad.
GROQ_API_KEY = os.getenv('GROQ_API_KEY', '')
GROQ_MODEL = os.getenv('GROQ_MODEL', 'llama-3.1-8b-instant')
GROQ_TIMEOUT = int(os.getenv('GROQ_TIMEOUT', '60'))
GROQ_MAX_OUTPUT_TOKENS = int(os.getenv('GROQ_MAX_OUTPUT_TOKENS', '1200'))
GROQ_TEMPERATURE = float(os.getenv('GROQ_TEMPERATURE', '0.35'))

OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', '')
OPENAI_MODEL = os.getenv('OPENAI_MODEL', 'gpt-4o-mini')
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY', '')
GEMINI_MODEL = os.getenv('GEMINI_MODEL', 'gemini-2.0-flash')
GEMINI_TIMEOUT = int(os.getenv('GEMINI_TIMEOUT', '45'))
GEMINI_MAX_OUTPUT_TOKENS = int(os.getenv('GEMINI_MAX_OUTPUT_TOKENS', '1200'))
GEMINI_TEMPERATURE = float(os.getenv('GEMINI_TEMPERATURE', '0.35'))

SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SESSION_COOKIE_SECURE = not DEBUG
CSRF_COOKIE_SECURE = not DEBUG
SECURE_SSL_REDIRECT = False if DEBUG else os.getenv('SECURE_SSL_REDIRECT', 'True').lower() == 'true'
X_FRAME_OPTIONS = 'DENY'

LOGIN_URL = 'login'
LOGIN_REDIRECT_URL = 'dashboard'
LOGOUT_REDIRECT_URL = 'home'
