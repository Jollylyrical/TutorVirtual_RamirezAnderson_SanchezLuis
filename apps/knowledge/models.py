from django.conf import settings
from django.db import models


class KnowledgeDocument(models.Model):
    class Category(models.TextChoices):
        ACADEMIC = 'academic', 'Académico'
        INSTITUTIONAL = 'institutional', 'Institucional'
        TECHNICAL = 'technical', 'Técnico'
        FAQ = 'faq', 'Preguntas frecuentes'
        OTHER = 'other', 'Otro'

    title = models.CharField(max_length=180)
    category = models.CharField(max_length=30, choices=Category.choices, default=Category.OTHER)
    source = models.CharField(max_length=255, blank=True)
    content = models.TextField()
    tags = models.CharField(max_length=255, blank=True, help_text='Etiquetas separadas por coma')
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Documento de conocimiento'
        verbose_name_plural = 'Documentos de conocimiento'

    def __str__(self):
        return self.title


class KnowledgeAuditLog(models.Model):
    action = models.CharField(max_length=80)
    document = models.ForeignKey(KnowledgeDocument, on_delete=models.CASCADE, related_name='audit_logs')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    details = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
