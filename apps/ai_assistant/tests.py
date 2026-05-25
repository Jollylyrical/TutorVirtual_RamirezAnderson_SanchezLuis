from django.test import SimpleTestCase
from .prompts import build_prompt


class PromptTests(SimpleTestCase):
    def test_prompt_contains_question(self):
        prompt = build_prompt('¿Qué es gestión del conocimiento?', [])
        self.assertIn('¿Qué es gestión del conocimiento?', prompt)
