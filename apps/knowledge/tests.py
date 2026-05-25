from django.test import SimpleTestCase
from .text_processing import chunk_text, keyword_score


class TextProcessingTests(SimpleTestCase):
    def test_chunk_text_returns_content(self):
        chunks = chunk_text('Gestión del conocimiento. ' * 100, chunk_size=200, overlap=20)
        self.assertGreater(len(chunks), 1)

    def test_keyword_score(self):
        score = keyword_score('conocimiento institucional', 'El conocimiento institucional se organiza en documentos.')
        self.assertGreater(score, 0)
