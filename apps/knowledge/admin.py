from django.contrib import admin
from .models import KnowledgeAuditLog, KnowledgeDocument


@admin.register(KnowledgeDocument)
class KnowledgeDocumentAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'source', 'created_by', 'created_at', 'is_active')
    search_fields = ('title', 'content', 'tags', 'source')
    list_filter = ('category', 'is_active', 'created_at')


@admin.register(KnowledgeAuditLog)
class KnowledgeAuditLogAdmin(admin.ModelAdmin):
    list_display = ('action', 'document', 'user', 'created_at')
    list_filter = ('action', 'created_at')
