from __future__ import annotations

import os
from pathlib import Path

from django.contrib import messages as dj_messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Count
from django.http import HttpRequest, HttpResponseForbidden
from django.shortcuts import redirect, render
from django.views.decorators.http import require_http_methods
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.conf import settings

from apps.ai_assistant.ai_gateway import AIGateway, AIGatewayError
from apps.ai_assistant.models import Conversation, Message
from apps.ai_assistant.prompts import build_prompt
from apps.knowledge.models import KnowledgeAuditLog, KnowledgeDocument
from apps.knowledge.mongo_repository import get_repository
from apps.users.models import UserProfile, get_or_create_profile


ROLE_DASHBOARDS = {
    UserProfile.Role.ADMIN: 'core/dashboard_admin.html',
    UserProfile.Role.MANAGER: 'core/dashboard_manager.html',
    UserProfile.Role.TUTOR: 'core/dashboard_tutor.html',
    UserProfile.Role.STUDENT: 'core/dashboard_student.html',
}

def _role(user) -> str:
    if user.is_superuser:
        return UserProfile.Role.ADMIN
    try:
        return get_or_create_profile(user).role
    except Exception:
        return UserProfile.Role.STUDENT

def _role_display(user) -> str:
    if user.is_superuser:
        return 'Administrador'
    return get_or_create_profile(user).get_role_display()


def _can_manage_knowledge(user) -> bool:
    return _role(user) in {UserProfile.Role.ADMIN, UserProfile.Role.MANAGER, UserProfile.Role.TUTOR}


def _mask_secret(value: str) -> str:
    value = (value or '').strip()
    if not value:
        return 'No configurado'
    if len(value) <= 10:
        return value[:2] + '***'
    return value[:6] + '...' + value[-4:]


def _env_path() -> Path:
    return settings.BASE_DIR / '.env'


def _update_env_file(updates: dict[str, str]) -> None:
    """Actualiza .env sin perder las demás variables.

    Se usa para localhost/demo. En producción la API key debe configurarse como
    variable de entorno en Azure/App Service, no guardarse en el repositorio.
    """
    path = _env_path()
    existing_lines = path.read_text(encoding='utf-8').splitlines() if path.exists() else []
    updated_keys = set()
    output_lines: list[str] = []

    for line in existing_lines:
        stripped = line.strip()
        if not stripped or stripped.startswith('#') or '=' not in line:
            output_lines.append(line)
            continue
        key = line.split('=', 1)[0].strip()
        if key in updates:
            output_lines.append(f'{key}={updates[key]}')
            updated_keys.add(key)
        else:
            output_lines.append(line)

    for key, value in updates.items():
        if key not in updated_keys:
            output_lines.append(f'{key}={value}')

    path.write_text('\n'.join(output_lines).rstrip() + '\n', encoding='utf-8')

    # Refresca variables en el proceso actual para no obligar a reiniciar.
    for key, value in updates.items():
        os.environ[key] = value
        if hasattr(settings, key):
            setattr(settings, key, value)
    settings.AI_PROVIDER = updates.get('AI_PROVIDER', getattr(settings, 'AI_PROVIDER', 'n8n'))
    settings.GEMINI_API_KEY = updates.get('GEMINI_API_KEY', getattr(settings, 'GEMINI_API_KEY', ''))
    settings.GEMINI_MODEL = updates.get('GEMINI_MODEL', getattr(settings, 'GEMINI_MODEL', 'gemini-2.0-flash'))
    settings.GROQ_API_KEY = updates.get('GROQ_API_KEY', getattr(settings, 'GROQ_API_KEY', ''))
    settings.GROQ_MODEL = updates.get('GROQ_MODEL', getattr(settings, 'GROQ_MODEL', 'llama-3.1-8b-instant'))
    settings.N8N_WEBHOOK_URL = updates.get('N8N_WEBHOOK_URL', getattr(settings, 'N8N_WEBHOOK_URL', 'https://tutorvirtual.app.n8n.cloud/webhook/tutor-virtual-ai'))
    settings.N8N_SHARED_SECRET = updates.get('N8N_SHARED_SECRET', getattr(settings, 'N8N_SHARED_SECRET', 'dev-n8n-secret'))
    settings.N8N_FALLBACK_PROVIDER = updates.get('N8N_FALLBACK_PROVIDER', getattr(settings, 'N8N_FALLBACK_PROVIDER', 'groq'))
    if 'GEMINI_MAX_OUTPUT_TOKENS' in updates:
        settings.GEMINI_MAX_OUTPUT_TOKENS = int(updates['GEMINI_MAX_OUTPUT_TOKENS'])
    if 'GEMINI_TEMPERATURE' in updates:
        settings.GEMINI_TEMPERATURE = float(updates['GEMINI_TEMPERATURE'])
    if 'GROQ_MAX_OUTPUT_TOKENS' in updates:
        settings.GROQ_MAX_OUTPUT_TOKENS = int(updates['GROQ_MAX_OUTPUT_TOKENS'])
    if 'GROQ_TEMPERATURE' in updates:
        settings.GROQ_TEMPERATURE = float(updates['GROQ_TEMPERATURE'])
    if 'N8N_TIMEOUT' in updates:
        settings.N8N_TIMEOUT = int(updates['N8N_TIMEOUT'])


def home_view(request: HttpRequest):
    if request.user.is_authenticated:
        return redirect('dashboard')
    return render(request, 'core/home.html')


@require_http_methods(['GET', 'POST'])
def login_view(request: HttpRequest):
    if request.user.is_authenticated:
        return redirect('dashboard')
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            dj_messages.success(request, f'Bienvenido(a), {user.first_name or user.username}.')
            return redirect('dashboard')
        dj_messages.error(request, 'Usuario o contraseña incorrectos.')
    return render(request, 'users/login.html')


@require_http_methods(['GET', 'POST'])
def register_page_view(request: HttpRequest):
    if request.user.is_authenticated:
        return redirect('dashboard')
    roles = UserProfile.Role.choices
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        role = request.POST.get('role', UserProfile.Role.STUDENT)
        password = request.POST.get('password', '')
        password2 = request.POST.get('password2', '')

        if not username or not password:
            dj_messages.error(request, 'El usuario y la contraseña son obligatorios.')
        elif password != password2:
            dj_messages.error(request, 'Las contraseñas no coinciden.')
        elif len(password) < 8:
            dj_messages.error(request, 'La contraseña debe tener mínimo 8 caracteres.')
        elif User.objects.filter(username=username).exists():
            dj_messages.error(request, 'Ese nombre de usuario ya existe.')
        elif email and User.objects.filter(email=email).exists():
            dj_messages.error(request, 'Ese correo ya está registrado.')
        else:
            user = User.objects.create_user(
                username=username,
                email=email,
                first_name=first_name,
                last_name=last_name,
                password=password,
            )
            profile = get_or_create_profile(user)
            profile.role = role if role in dict(roles) else UserProfile.Role.STUDENT
            profile.save(update_fields=['role', 'updated_at'])
            login(request, user)
            dj_messages.success(request, 'Registro creado correctamente.')
            return redirect('dashboard')
    return render(request, 'users/register.html', {'roles': roles})


@login_required
def logout_view(request: HttpRequest):
    logout(request)
    dj_messages.success(request, 'Sesión cerrada correctamente.')
    return redirect('home')


def _dashboard_context(request: HttpRequest) -> dict:
    repo = get_repository()
    try:
        mongo_status = repo.ping()
    except Exception:
        mongo_status = False

    categories = list(
        KnowledgeDocument.objects.filter(is_active=True)
        .values('category')
        .annotate(total=Count('id'))
        .order_by('-total')
    )
    category_labels = dict(KnowledgeDocument.Category.choices)
    total_category_docs = sum(item['total'] for item in categories) or 1
    for item in categories:
        item['label'] = category_labels.get(item['category'], item['category'])
        item['percent'] = max(8, round((item['total'] / total_category_docs) * 100))

    user_conversations = Conversation.objects.filter(user=request.user).prefetch_related('messages')[:5]
    latest_documents = KnowledgeDocument.objects.filter(is_active=True).select_related('created_by')[:6]
    latest_audits = KnowledgeAuditLog.objects.select_related('document', 'user')[:8]

    return {
        'role': _role(request.user),
        'role_display': _role_display(request.user),
        'can_manage_knowledge': _can_manage_knowledge(request.user),
        'ai_status': AIGateway.provider_status(),
        'stats': {
            'users': User.objects.count(),
            'documents': KnowledgeDocument.objects.filter(is_active=True).count(),
            'conversations': Conversation.objects.count(),
            'messages': Message.objects.count(),
            'my_conversations': Conversation.objects.filter(user=request.user).count(),
            'mongo_status': mongo_status,
            'ai_provider': settings.AI_PROVIDER,
            'ai_model': AIGateway.provider_status().model,
            'ai_ready': AIGateway.provider_status().api_key_configured,
            'db_engine': settings.DATABASES['default']['ENGINE'].split('.')[-1],
        },
        'categories': categories,
        'latest_documents': latest_documents,
        'latest_audits': latest_audits,
        'user_conversations': user_conversations,
        'protocols': [
            'Cliente → Internet: TCP/IP',
            'Internet → Nginx: HTTPS, TCP 443, TLS/SSL',
            'Nginx → Django/Gunicorn: HTTP interno, TCP 80/8000, WSGI/ASGI',
            'Frontend/API → Backend: REST/JSON + JWT Bearer Token',
            'Django → PostgreSQL: TCP 5432, SQL',
            'Django → MongoDB: TCP 27017, BSON/documental',
            'Django → n8n Webhook: HTTP/HTTPS REST + secreto compartido',
            'n8n → GroqCloud: HTTPS REST compatible con OpenAI + API Key',
            'n8n → Django: JSON con respuesta generada',
        ],
    }


@login_required
def dashboard_view(request: HttpRequest):
    role = _role(request.user)
    template = ROLE_DASHBOARDS.get(role, 'core/dashboard_student.html')
    return render(request, template, _dashboard_context(request))


@login_required
def architecture_view(request: HttpRequest):
    return render(request, 'core/architecture.html', _dashboard_context(request))



@login_required
@require_http_methods(['GET', 'POST'])
def n8n_config_view(request: HttpRequest):
    status = AIGateway.provider_status()
    test_answer = None

    if request.method == 'POST':
        provider_mode = request.POST.get('provider_mode', 'n8n').strip().lower()
        if provider_mode not in {'n8n', 'groq', 'local'}:
            provider_mode = 'n8n'
        webhook_url = request.POST.get('n8n_webhook_url', '').strip() or 'https://tutorvirtual.app.n8n.cloud/webhook/tutor-virtual-ai'
        shared_secret = request.POST.get('n8n_shared_secret', '').strip() or 'dev-n8n-secret'
        groq_model = request.POST.get('groq_model', '').strip() or 'llama-3.1-8b-instant'
        groq_key = request.POST.get('groq_api_key', '').strip()
        max_tokens = request.POST.get('groq_max_output_tokens', '1200').strip() or '1200'
        temperature = request.POST.get('groq_temperature', '0.35').strip() or '0.35'
        timeout = request.POST.get('n8n_timeout', '60').strip() or '60'
        fallback = request.POST.get('n8n_fallback_provider', 'groq').strip().lower()
        if fallback not in {'groq', 'local', ''}:
            fallback = 'groq'

        try:
            int(max_tokens)
            float(temperature)
            int(timeout)
        except ValueError:
            dj_messages.error(request, 'Revise tokens, temperatura y timeout. Deben ser valores numéricos.')
        else:
            updates = {
                'AI_PROVIDER': provider_mode,
                'N8N_WEBHOOK_URL': webhook_url,
                'N8N_SHARED_SECRET': shared_secret,
                'N8N_TIMEOUT': timeout,
                'N8N_FALLBACK_PROVIDER': fallback,
                'GROQ_MODEL': groq_model,
                'GROQ_MAX_OUTPUT_TOKENS': max_tokens,
                'GROQ_TEMPERATURE': temperature,
            }
            if groq_key:
                updates['GROQ_API_KEY'] = groq_key
            elif not AIGateway.groq_api_key():
                updates['GROQ_API_KEY'] = ''

            _update_env_file(updates)
            dj_messages.success(request, 'Configuración n8n + Groq guardada. El tutor usará este flujo en las próximas consultas.')
            status = AIGateway.provider_status()

            if request.POST.get('test_connection') == '1':
                try:
                    test_answer = AIGateway().generate(
                        'Responde únicamente en español con una frase corta: conexión n8n y Groq activa para el tutor virtual.'
                    )
                    dj_messages.success(request, 'Prueba de conexión realizada correctamente.')
                except AIGatewayError as exc:
                    dj_messages.error(request, f'No fue posible probar n8n/Groq: {exc}')

    current_key = AIGateway.groq_api_key()
    return render(request, 'ai_assistant/n8n_config.html', {
        **_dashboard_context(request),
        'ai_status': status,
        'masked_groq_key': _mask_secret(current_key),
        'groq_model': getattr(settings, 'GROQ_MODEL', 'llama-3.1-8b-instant'),
        'groq_max_output_tokens': getattr(settings, 'GROQ_MAX_OUTPUT_TOKENS', 1200),
        'groq_temperature': getattr(settings, 'GROQ_TEMPERATURE', 0.35),
        'n8n_webhook_url': getattr(settings, 'N8N_WEBHOOK_URL', 'https://tutorvirtual.app.n8n.cloud/webhook/tutor-virtual-ai'),
        'n8n_shared_secret': getattr(settings, 'N8N_SHARED_SECRET', 'dev-n8n-secret'),
        'n8n_timeout': getattr(settings, 'N8N_TIMEOUT', 60),
        'n8n_fallback_provider': getattr(settings, 'N8N_FALLBACK_PROVIDER', 'groq'),
        'current_provider': getattr(settings, 'AI_PROVIDER', 'n8n'),
        'env_file': str(_env_path()),
        'test_answer': test_answer,
    })

@login_required
@require_http_methods(['GET', 'POST'])
def gemini_config_view(request: HttpRequest):
    status = AIGateway.provider_status()
    test_answer = None

    if request.method == 'POST':
        model = request.POST.get('gemini_model', '').strip() or 'gemini-2.0-flash'
        api_key = request.POST.get('gemini_api_key', '').strip()
        max_tokens = request.POST.get('gemini_max_output_tokens', '1200').strip() or '1200'
        temperature = request.POST.get('gemini_temperature', '0.35').strip() or '0.35'

        try:
            int(max_tokens)
            float(temperature)
        except ValueError:
            dj_messages.error(request, 'Revise maxOutputTokens y temperature. Deben ser numéricos.')
        else:
            updates = {
                'AI_PROVIDER': 'gemini',
                'GEMINI_MODEL': model,
                'GEMINI_MAX_OUTPUT_TOKENS': max_tokens,
                'GEMINI_TEMPERATURE': temperature,
            }
            if api_key:
                updates['GEMINI_API_KEY'] = api_key
            elif not AIGateway.gemini_api_key():
                updates['GEMINI_API_KEY'] = ''

            _update_env_file(updates)
            dj_messages.success(request, 'Configuración Gemini guardada. El tutor usará Gemini en las próximas consultas.')
            status = AIGateway.provider_status()

            if request.POST.get('test_connection') == '1':
                try:
                    test_answer = AIGateway().generate(
                        'Responde únicamente en español con una frase corta: conexión Gemini activa para el tutor virtual.'
                    )
                    dj_messages.success(request, 'Prueba de conexión con Gemini realizada correctamente.')
                except AIGatewayError as exc:
                    dj_messages.error(request, f'No fue posible probar Gemini: {exc}')

    current_key = AIGateway.gemini_api_key()
    return render(request, 'ai_assistant/gemini_config.html', {
        **_dashboard_context(request),
        'ai_status': status,
        'masked_gemini_key': _mask_secret(current_key),
        'gemini_model': getattr(settings, 'GEMINI_MODEL', 'gemini-2.0-flash'),
        'gemini_max_output_tokens': getattr(settings, 'GEMINI_MAX_OUTPUT_TOKENS', 1200),
        'gemini_temperature': getattr(settings, 'GEMINI_TEMPERATURE', 0.35),
        'env_file': str(_env_path()),
        'test_answer': test_answer,
    })


@login_required
def documents_view(request: HttpRequest):
    documents = KnowledgeDocument.objects.filter(is_active=True).select_related('created_by')
    category = request.GET.get('category', '')
    q = request.GET.get('q', '').strip()
    if category:
        documents = documents.filter(category=category)
    if q:
        documents = documents.filter(title__icontains=q) | KnowledgeDocument.objects.filter(is_active=True, content__icontains=q)
    return render(request, 'knowledge/document_list.html', {
        **_dashboard_context(request),
        'documents': documents.distinct(),
        'category_filter': category,
        'q': q,
        'category_choices': KnowledgeDocument.Category.choices,
    })


@login_required
@require_http_methods(['GET', 'POST'])
def document_create_view(request: HttpRequest):
    if not _can_manage_knowledge(request.user):
        return HttpResponseForbidden('Su rol puede consultar el conocimiento, pero no crear documentos.')
    if request.method == 'POST':
        title = request.POST.get('title', '').strip()
        category = request.POST.get('category', KnowledgeDocument.Category.OTHER)
        source = request.POST.get('source', '').strip()
        tags = request.POST.get('tags', '').strip()
        content = request.POST.get('content', '').strip()
        if not title or not content:
            dj_messages.error(request, 'El título y el contenido son obligatorios.')
        else:
            document = KnowledgeDocument.objects.create(
                title=title,
                category=category,
                source=source,
                tags=tags,
                content=content,
                created_by=request.user,
            )
            chunks = get_repository().upsert_document_chunks(
                document_id=document.id,
                title=document.title,
                content=document.content,
                metadata={'source': document.source, 'category': document.category, 'tags': document.tags},
            )
            KnowledgeAuditLog.objects.create(
                action='created_from_dashboard',
                document=document,
                user=request.user,
                details={'chunks_indexed_or_available': chunks},
            )
            dj_messages.success(request, f'Documento guardado e indexado. Fragmentos disponibles: {chunks}.')
            return redirect('documents')
    return render(request, 'knowledge/document_form.html', {
        **_dashboard_context(request),
        'category_choices': KnowledgeDocument.Category.choices,
    })


@login_required
@require_http_methods(['GET', 'POST'])
def tutor_view(request: HttpRequest):
    context = _dashboard_context(request)
    answer = None
    question = ''
    context_used = []
    if request.method == 'POST':
        question = request.POST.get('question', '').strip()
        if len(question) < 3:
            dj_messages.error(request, 'Escriba una pregunta de mínimo 3 caracteres.')
        else:
            repository = get_repository()
            search_results = repository.search(question, limit=5)
            context_used = [r.__dict__ for r in search_results]
            prompt = build_prompt(question, context_used)
            try:
                answer = AIGateway().generate(prompt)
            except AIGatewayError as exc:
                answer = f'No fue posible consultar el servicio de IA: {exc}'

            conversation = Conversation.objects.create(user=request.user, title=question[:80])
            Message.objects.create(conversation=conversation, role=Message.Role.USER, content=question)
            Message.objects.create(
                conversation=conversation,
                role=Message.Role.ASSISTANT,
                content=answer,
                metadata={'context': context_used},
            )
            dj_messages.success(request, 'Consulta registrada en el historial.')
    return render(request, 'ai_assistant/tutor.html', {
        **context,
        'answer': answer,
        'question': question,
        'context_used': context_used,
    })


@login_required
def history_view(request: HttpRequest):
    conversations = Conversation.objects.filter(user=request.user).prefetch_related('messages')
    return render(request, 'ai_assistant/history.html', {
        **_dashboard_context(request),
        'conversations': conversations,
    })


@api_view(['GET'])
@permission_classes([AllowAny])
def health_check(request):
    repo = get_repository()
    try:
        mongo_status = repo.ping()
    except Exception:
        mongo_status = False
    return Response({
        'status': 'ok',
        'service': 'Tutor Virtual Inteligente',
        'database': settings.DATABASES['default']['ENGINE'],
        'mongodb_available': mongo_status,
        'mongodb_mode': 'MongoDB Atlas/local' if mongo_status else 'SQL fallback para localhost',
        'ai_provider': settings.AI_PROVIDER,
        'ai_model': AIGateway.provider_status().model,
        'ai_ready': AIGateway.provider_status().api_key_configured,
        'protocols': ['HTTPS/TLS', 'REST/JSON', 'JWT Bearer Token', 'SQL TCP 5432', 'MongoDB TCP 27017'],
    })
