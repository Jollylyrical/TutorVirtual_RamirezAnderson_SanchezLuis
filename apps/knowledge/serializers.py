from rest_framework import serializers

from .models import KnowledgeDocument


class KnowledgeDocumentSerializer(serializers.ModelSerializer):
    created_by_username = serializers.CharField(source='created_by.username', read_only=True)

    class Meta:
        model = KnowledgeDocument
        fields = [
            'id', 'title', 'category', 'source', 'content', 'tags',
            'created_by', 'created_by_username', 'created_at', 'updated_at', 'is_active'
        ]
        read_only_fields = ['created_by', 'created_at', 'updated_at']
