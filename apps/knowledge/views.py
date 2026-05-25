from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import KnowledgeAuditLog, KnowledgeDocument
from .mongo_repository import get_repository
from .serializers import KnowledgeDocumentSerializer


class KnowledgeDocumentViewSet(viewsets.ModelViewSet):
    queryset = KnowledgeDocument.objects.filter(is_active=True)
    serializer_class = KnowledgeDocumentSerializer

    def perform_create(self, serializer):
        document = serializer.save(created_by=self.request.user)
        repo = get_repository()
        chunks = repo.upsert_document_chunks(
            document_id=document.id,
            title=document.title,
            content=document.content,
            metadata={'source': document.source, 'category': document.category, 'tags': document.tags},
        )
        KnowledgeAuditLog.objects.create(
            action='created_and_indexed',
            document=document,
            user=self.request.user,
            details={'chunks_indexed': chunks},
        )

    def perform_update(self, serializer):
        document = serializer.save()
        repo = get_repository()
        chunks = repo.upsert_document_chunks(
            document_id=document.id,
            title=document.title,
            content=document.content,
            metadata={'source': document.source, 'category': document.category, 'tags': document.tags},
        )
        KnowledgeAuditLog.objects.create(
            action='updated_and_reindexed',
            document=document,
            user=self.request.user,
            details={'chunks_indexed': chunks},
        )

    def perform_destroy(self, instance):
        instance.is_active = False
        instance.save(update_fields=['is_active'])
        deleted_chunks = get_repository().delete_document_chunks(instance.id)
        KnowledgeAuditLog.objects.create(
            action='deactivated_and_unindexed',
            document=instance,
            user=self.request.user,
            details={'chunks_deleted': deleted_chunks},
        )

    @action(detail=False, methods=['get'])
    def search(self, request):
        query = request.query_params.get('q', '')
        if not query:
            return Response({'detail': 'Ingrese el parámetro q con la búsqueda.'}, status=status.HTTP_400_BAD_REQUEST)
        results = get_repository().search(query, limit=8)
        return Response({
            'query': query,
            'results': [r.__dict__ for r in results],
        })
