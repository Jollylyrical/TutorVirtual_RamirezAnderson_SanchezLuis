from django.contrib import admin
from django.urls import include, path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from apps.core.views import (
    architecture_view,
    dashboard_view,
    document_create_view,
    documents_view,
    gemini_config_view,
    n8n_config_view,
    history_view,
    home_view,
    login_view,
    logout_view,
    register_page_view,
    tutor_view,
)

urlpatterns = [
    path('', home_view, name='home'),
    path('login/', login_view, name='login'),
    path('registro/', register_page_view, name='register_page'),
    path('logout/', logout_view, name='logout'),
    path('dashboard/', dashboard_view, name='dashboard'),
    path('arquitectura/', architecture_view, name='architecture'),
    path('conocimiento/', documents_view, name='documents'),
    path('conocimiento/nuevo/', document_create_view, name='document_create'),
    path('tutor/', tutor_view, name='tutor'),
    path('configuracion-n8n/', n8n_config_view, name='n8n_config'),
    path('configuracion-gemini/', gemini_config_view, name='gemini_config'),
    path('historial/', history_view, name='history'),
    path('admin/', admin.site.urls),
    path('api/health/', include('apps.core.urls')),
    path('api/auth/register/', include('apps.users.urls')),
    path('api/auth/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/knowledge/', include('apps.knowledge.urls')),
    path('api/ai/', include('apps.ai_assistant.urls')),
]
