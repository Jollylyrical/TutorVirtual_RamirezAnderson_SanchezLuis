from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List

from django.conf import settings
from pymongo import MongoClient
from pymongo.errors import PyMongoError, ServerSelectionTimeoutError

from .text_processing import chunk_text, keyword_score


@dataclass
class SearchResult:
    document_id: int
    title: str
    chunk: str
    score: float
    source: str = ''
    storage: str = 'mongodb'


class MongoKnowledgeRepository:
    """Repositorio documental/semántico sobre MongoDB con respaldo local.

    El diagrama plantea MongoDB Atlas como base semántica/documental. Para que el
    proyecto funcione en localhost aunque el estudiante no tenga Mongo instalado,
    esta clase intenta MongoDB primero y, si no hay conexión, busca directamente en
    los documentos guardados en la base relacional SQLite/PostgreSQL.
    """

    def __init__(self):
        self.client = MongoClient(settings.MONGODB_URI, serverSelectionTimeoutMS=900)
        self.db = self.client[settings.MONGODB_DB]
        self.collection = self.db[settings.MONGODB_COLLECTION]

    def ping(self) -> bool:
        try:
            self.client.admin.command('ping')
            return True
        except PyMongoError:
            return False

    def upsert_document_chunks(self, document_id: int, title: str, content: str, metadata: Dict[str, Any] | None = None) -> int:
        metadata = metadata or {}
        chunks = chunk_text(content)
        try:
            self.collection.delete_many({'document_id': document_id})
            if not chunks:
                return 0
            docs = [
                {
                    'document_id': document_id,
                    'title': title,
                    'chunk_index': index,
                    'chunk': chunk,
                    'metadata': metadata,
                }
                for index, chunk in enumerate(chunks)
            ]
            self.collection.insert_many(docs)
            return len(docs)
        except (PyMongoError, ServerSelectionTimeoutError):
            # Respaldo local: los documentos quedan en SQL y se consultan desde allí.
            return len(chunks)

    def delete_document_chunks(self, document_id: int) -> int:
        try:
            result = self.collection.delete_many({'document_id': document_id})
            return result.deleted_count
        except (PyMongoError, ServerSelectionTimeoutError):
            return 0

    def search(self, query: str, limit: int = 5) -> List[SearchResult]:
        mongo_results = self._search_mongodb(query=query, limit=limit)
        if mongo_results:
            return mongo_results
        return self._search_relational_fallback(query=query, limit=limit)

    def _search_mongodb(self, query: str, limit: int = 5) -> List[SearchResult]:
        try:
            candidates = list(self.collection.find({}, {'_id': 0}).limit(500))
        except (PyMongoError, ServerSelectionTimeoutError):
            return []
        scored: list[SearchResult] = []
        for item in candidates:
            score = keyword_score(query, item.get('chunk', ''))
            if score > 0:
                metadata = item.get('metadata') or {}
                scored.append(SearchResult(
                    document_id=int(item.get('document_id')),
                    title=item.get('title', ''),
                    chunk=item.get('chunk', ''),
                    score=score,
                    source=metadata.get('source', ''),
                    storage='mongodb',
                ))
        scored.sort(key=lambda x: x.score, reverse=True)
        return scored[:limit]

    def _search_relational_fallback(self, query: str, limit: int = 5) -> List[SearchResult]:
        from .models import KnowledgeDocument

        scored: list[SearchResult] = []
        documents = KnowledgeDocument.objects.filter(is_active=True).only('id', 'title', 'source', 'content')[:250]
        for document in documents:
            for chunk in chunk_text(document.content):
                score = keyword_score(query, chunk)
                if score > 0:
                    scored.append(SearchResult(
                        document_id=document.id,
                        title=document.title,
                        chunk=chunk,
                        score=score,
                        source=document.source,
                        storage='sql-fallback',
                    ))
        scored.sort(key=lambda x: x.score, reverse=True)
        return scored[:limit]


def get_repository() -> MongoKnowledgeRepository:
    return MongoKnowledgeRepository()
