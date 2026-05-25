from django.contrib.auth.models import User
from django.core.management.base import BaseCommand

from apps.ai_assistant.models import Conversation, Message
from apps.knowledge.models import KnowledgeAuditLog, KnowledgeDocument
from apps.knowledge.mongo_repository import get_repository
from apps.users.models import UserProfile, get_or_create_profile


DEMO_USERS = [
    ('admin_demo', 'Admin12345*', 'Administrador', 'Demo', 'admin', True, True),
    ('gestor_demo', 'Gestor12345*', 'Gestor', 'Conocimiento', 'manager', False, True),
    ('tutor_demo', 'Tutor12345*', 'Tutor', 'Docente', 'tutor', False, True),
    ('estudiante_demo', 'Estudiante12345*', 'Estudiante', 'Aprendiz', 'student', False, False),
]

DEMO_DOCUMENTS = [
    {
        'title': 'Fundamentos de gestión del conocimiento',
        'category': 'academic',
        'source': 'Material académico interno',
        'tags': 'gestión, conocimiento, aprendizaje organizacional',
        'content': (
            'La gestión del conocimiento es un proceso organizacional orientado a identificar, capturar, organizar, compartir y aplicar '
            'el conocimiento para mejorar la toma de decisiones, resolver problemas y fortalecer la innovación. Incluye conocimiento tácito, '
            'que está asociado a la experiencia de las personas, y conocimiento explícito, que puede documentarse en guías, manuales, bases de datos, '
            'procedimientos y repositorios digitales. Un sistema de tutor virtual apoya este proceso al facilitar búsquedas, respuestas contextualizadas, '
            'historial de aprendizaje y transferencia de conocimiento entre usuarios.'
        ),
    },
    {
        'title': 'Modelo SECI aplicado al tutor virtual',
        'category': 'technical',
        'source': 'Guía metodológica del proyecto',
        'tags': 'SECI, socialización, externalización, combinación, internalización',
        'content': (
            'El modelo SECI explica la creación de conocimiento mediante cuatro procesos: socialización, externalización, combinación e internalización. '
            'En el tutor virtual, la socialización se refleja en la interacción entre usuarios y tutores; la externalización ocurre cuando la experiencia se '
            'convierte en documentos; la combinación se logra al integrar varias fuentes en una base de conocimiento; y la internalización sucede cuando el usuario '
            'aprende y aplica las respuestas generadas por el sistema.'
        ),
    },
    {
        'title': 'Arquitectura tecnológica del sistema',
        'category': 'institutional',
        'source': 'Diagrama de despliegue UML',
        'tags': 'Django, API REST, JWT, PostgreSQL, MongoDB, IA, Azure',
        'content': (
            'La arquitectura del tutor virtual utiliza un navegador web como cliente, un reverse proxy Nginx para manejar HTTPS con TLS/SSL, una aplicación web Django '
            'servida mediante Gunicorn o Uvicorn, y una API REST protegida con autenticación JWT. PostgreSQL almacena datos relacionales como usuarios, documentos, '
            'auditoría y conversaciones. MongoDB almacena fragmentos documentales para búsqueda semántica. El servicio externo de IA, como Gemini u OpenAI, se consulta '
            'por HTTPS REST API mediante una API Key.'
        ),
    },
    {
        'title': 'Buenas prácticas de seguridad',
        'category': 'faq',
        'source': 'Política técnica del proyecto',
        'tags': 'seguridad, HTTPS, JWT, API Key',
        'content': (
            'El sistema debe proteger la comunicación externa mediante HTTPS sobre el puerto 443, usar certificados TLS válidos, enviar tokens JWT únicamente por canales '
            'seguros, mantener las claves API fuera del código fuente y restringir el acceso según roles. Los administradores gestionan usuarios y auditoría; los gestores '
            'y tutores cargan documentos; los estudiantes consultan conocimiento y revisan su historial.'
        ),
    },
]


class Command(BaseCommand):
    help = 'Crea usuarios, documentos y conversaciones de demostración para probar el sistema en localhost.'

    def handle(self, *args, **options):
        users = {}
        for username, password, first_name, last_name, role, is_superuser, is_staff in DEMO_USERS:
            user, created = User.objects.get_or_create(
                username=username,
                defaults={
                    'email': f'{username}@demo.local',
                    'first_name': first_name,
                    'last_name': last_name,
                    'is_superuser': is_superuser,
                    'is_staff': is_staff,
                },
            )
            user.set_password(password)
            user.is_superuser = is_superuser
            user.is_staff = is_staff
            user.email = f'{username}@demo.local'
            user.first_name = first_name
            user.last_name = last_name
            user.save()
            profile = get_or_create_profile(user)
            profile.role = role
            profile.institution = 'Institución Demo'
            profile.program = 'Gestión del conocimiento'
            profile.save()
            users[username] = user
            self.stdout.write(self.style.SUCCESS(f'Usuario listo: {username} / {password}'))

        creator = users['gestor_demo']
        repo = get_repository()
        for item in DEMO_DOCUMENTS:
            document, _ = KnowledgeDocument.objects.update_or_create(
                title=item['title'],
                defaults={
                    'category': item['category'],
                    'source': item['source'],
                    'tags': item['tags'],
                    'content': item['content'],
                    'created_by': creator,
                    'is_active': True,
                },
            )
            chunks = repo.upsert_document_chunks(
                document_id=document.id,
                title=document.title,
                content=document.content,
                metadata={'source': document.source, 'category': document.category, 'tags': document.tags},
            )
            KnowledgeAuditLog.objects.create(
                action='seed_demo_indexed',
                document=document,
                user=creator,
                details={'chunks_indexed_or_available': chunks},
            )
            self.stdout.write(self.style.SUCCESS(f'Documento listo: {document.title} ({chunks} fragmentos)'))

        student = users['estudiante_demo']
        if not Conversation.objects.filter(user=student, title__icontains='gestión del conocimiento').exists():
            conversation = Conversation.objects.create(user=student, title='¿Qué es gestión del conocimiento?')
            Message.objects.create(
                conversation=conversation,
                role=Message.Role.USER,
                content='¿Qué es gestión del conocimiento y para qué sirve?',
            )
            Message.objects.create(
                conversation=conversation,
                role=Message.Role.ASSISTANT,
                content='La gestión del conocimiento permite capturar, organizar, compartir y aplicar información útil para mejorar decisiones y aprendizaje institucional.',
                metadata={'context': [{'title': 'Fundamentos de gestión del conocimiento'}]},
            )

        self.stdout.write(self.style.SUCCESS('Datos demo creados correctamente.'))
