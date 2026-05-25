from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Any

import requests
from django.conf import settings


class AIGatewayError(Exception):
    pass


@dataclass
class AIProviderStatus:
    provider: str
    model: str
    api_key_configured: bool
    mode_label: str
    detail: str


class AIGateway:
    """Capa de integración con proveedores externos de IA.

    AI_PROVIDER admite:
    - local: respuesta simulada/segura para pruebas académicas.
    - n8n: Django envía el prompt a un Webhook de n8n y n8n orquesta la llamada a IA.
    - groq: llamada directa a GroqCloud con API compatible con OpenAI.
    - gemini: llamada directa a Gemini Generative Language API.
    - openai: llamada HTTP compatible con OpenAI Chat Completions.
    """

    def generate(self, prompt: str) -> str:
        provider = (getattr(settings, 'AI_PROVIDER', 'local') or 'local').lower().strip()
        if provider == 'n8n':
            return self._n8n(prompt)
        if provider == 'groq':
            return self._groq(prompt)
        if provider == 'openai':
            return self._openai(prompt)
        if provider == 'gemini':
            return self._gemini(prompt)
        return self._local(prompt)

    @staticmethod
    def _not_placeholder(value: str, placeholders: set[str]) -> str:
        value = (value or '').strip()
        if value in placeholders:
            return ''
        return value

    @staticmethod
    def gemini_api_key() -> str:
        return AIGateway._not_placeholder(
            getattr(settings, 'GEMINI_API_KEY', '') or os.getenv('GEMINI_API_KEY', '') or os.getenv('GOOGLE_API_KEY', ''),
            {
                'PEGUE_AQUI_SU_TOKEN_GEMINI',
                'PEGA_AQUI_TU_TOKEN_GEMINI',
                'AQUI_TU_API_KEY',
                'YOUR_GEMINI_API_KEY',
                'YOUR_API_KEY',
            },
        )

    @staticmethod
    def groq_api_key() -> str:
        return AIGateway._not_placeholder(
            getattr(settings, 'GROQ_API_KEY', '') or os.getenv('GROQ_API_KEY', ''),
            {
                'PEGUE_AQUI_SU_TOKEN_GROQ',
                'PEGA_AQUI_TU_TOKEN_GROQ',
                'AQUI_TU_API_KEY_GROQ',
                'YOUR_GROQ_API_KEY',
                'YOUR_API_KEY',
            },
        )

    @staticmethod
    def n8n_webhook_url() -> str:
        value = getattr(settings, 'N8N_WEBHOOK_URL', '') or os.getenv('N8N_WEBHOOK_URL', '')
        return AIGateway._not_placeholder(value, {'PEGUE_AQUI_URL_WEBHOOK_N8N', 'YOUR_N8N_WEBHOOK_URL'}).strip()

    @staticmethod
    def provider_status() -> AIProviderStatus:
        provider = (getattr(settings, 'AI_PROVIDER', 'local') or 'local').lower().strip()
        if provider == 'n8n':
            model = getattr(settings, 'GROQ_MODEL', 'llama-3.1-8b-instant')
            webhook = AIGateway.n8n_webhook_url()
            fallback_ready = bool(AIGateway.groq_api_key())
            detail = 'Django enviará el prompt al Webhook de n8n; n8n llamará a GroqCloud y devolverá la respuesta al tutor.'
            if fallback_ready:
                detail += ' Si n8n no responde, queda disponible el respaldo directo con Groq.'
            return AIProviderStatus(
                provider='n8n',
                model=f'n8n → Groq · {model}',
                api_key_configured=bool(webhook),
                mode_label='n8n activo' if webhook else 'n8n pendiente de Webhook',
                detail=detail if webhook else 'Configure N8N_WEBHOOK_URL para activar el flujo n8n.',
            )
        if provider == 'groq':
            model = getattr(settings, 'GROQ_MODEL', 'llama-3.1-8b-instant')
            ready = bool(AIGateway.groq_api_key())
            return AIProviderStatus(
                provider='groq',
                model=model,
                api_key_configured=ready,
                mode_label='Groq activo' if ready else 'Groq pendiente de API key',
                detail='El tutor llamará directamente a GroqCloud.' if ready else 'Configure GROQ_API_KEY para activar la llamada externa.',
            )
        if provider == 'gemini':
            model = getattr(settings, 'GEMINI_MODEL', 'gemini-2.0-flash')
            ready = bool(AIGateway.gemini_api_key())
            return AIProviderStatus(
                provider='gemini',
                model=model,
                api_key_configured=ready,
                mode_label='Gemini activo' if ready else 'Gemini pendiente de token',
                detail='El tutor llamará a Gemini con generateContent.' if ready else 'Pegue su API key/token de Gemini para activar la llamada externa.',
            )
        if provider == 'openai':
            model = getattr(settings, 'OPENAI_MODEL', 'gpt-4o-mini')
            ready = bool(getattr(settings, 'OPENAI_API_KEY', ''))
            return AIProviderStatus(
                provider='openai',
                model=model,
                api_key_configured=ready,
                mode_label='OpenAI activo' if ready else 'OpenAI pendiente de API key',
                detail='El tutor llamará a OpenAI.' if ready else 'Configure OPENAI_API_KEY para activar la llamada externa.',
            )
        return AIProviderStatus(
            provider='local',
            model='respuesta local',
            api_key_configured=True,
            mode_label='Modo local activo',
            detail='Funciona sin internet ni token; útil para validar el sistema en clase.',
        )

    def _local(self, prompt: str) -> str:
        return (
            'Respuesta generada en modo local. El sistema recibió la pregunta y el contexto documental. '
            'Para una respuesta avanzada, configure AI_PROVIDER=n8n y GROQ_API_KEY/N8N_WEBHOOK_URL en el archivo .env o desde el panel n8n + Groq.\n\n'
            'Síntesis: el tutor virtual debe usar la base de conocimiento registrada, recuperar los fragmentos más relacionados '
            'con la pregunta y construir una respuesta clara, trazable y orientada al aprendizaje.'
        )

    def _n8n(self, prompt: str) -> str:
        webhook_url = self.n8n_webhook_url()
        if not webhook_url:
            raise AIGatewayError('N8N_WEBHOOK_URL no está configurada. Abra /configuracion-n8n/ y guarde la URL del Webhook.')

        timeout = int(getattr(settings, 'N8N_TIMEOUT', 60) or 60)
        shared_secret = getattr(settings, 'N8N_SHARED_SECRET', '') or os.getenv('N8N_SHARED_SECRET', '')
        payload = {
            'prompt': prompt,
            'provider': 'groq',
            'model': getattr(settings, 'GROQ_MODEL', 'llama-3.1-8b-instant'),
            'max_tokens': int(getattr(settings, 'GROQ_MAX_OUTPUT_TOKENS', 1200) or 1200),
            'temperature': float(getattr(settings, 'GROQ_TEMPERATURE', 0.35) or 0.35),
            'source': 'TutorVirtual-GestionConocimiento-Django',
            # En n8n Cloud normalmente no se configuran variables .env del servidor.
            # Por eso Django envía la API key de Groq de forma segura por HTTPS al Webhook propio.
            'groq_api_key': self.groq_api_key(),
            'shared_secret': shared_secret,
        }
        headers = {'Content-Type': 'application/json'}
        if shared_secret:
            headers['X-Tutor-Secret'] = shared_secret

        try:
            response = requests.post(webhook_url, headers=headers, json=payload, timeout=timeout)
        except requests.RequestException as exc:
            return self._n8n_fallback_or_raise(f'Error de red consultando n8n: {exc}', prompt)

        if response.status_code >= 400:
            return self._n8n_fallback_or_raise(self._safe_error(response), prompt)

        try:
            data: Any = response.json()
        except ValueError:
            text = (response.text or '').strip()
            if text:
                return text
            return self._n8n_fallback_or_raise('n8n devolvió una respuesta vacía o no JSON.', prompt)

        return self._extract_text_from_ai_payload(data) or self._n8n_fallback_or_raise(
            'n8n respondió, pero no se encontró el campo answer/response/text.', prompt
        )

    def _n8n_fallback_or_raise(self, message: str, prompt: str) -> str:
        fallback = (getattr(settings, 'N8N_FALLBACK_PROVIDER', '') or '').lower().strip()
        if fallback == 'groq' and self.groq_api_key():
            try:
                direct_answer = self._groq(prompt)
                return (
                    'Aviso: n8n no respondió correctamente, por eso se usó el respaldo directo con GroqCloud.\n\n'
                    f'{direct_answer}'
                )
            except AIGatewayError as exc:
                raise AIGatewayError(f'{message}. Además falló el respaldo Groq: {exc}') from exc
        raise AIGatewayError(message)

    def _groq(self, prompt: str) -> str:
        api_key = self.groq_api_key()
        if not api_key:
            raise AIGatewayError('GROQ_API_KEY no está configurada. Abra /configuracion-n8n/ o configure la variable en .env.')

        timeout = int(getattr(settings, 'GROQ_TIMEOUT', 60) or 60)
        model = getattr(settings, 'GROQ_MODEL', 'llama-3.1-8b-instant') or 'llama-3.1-8b-instant'
        max_tokens = int(getattr(settings, 'GROQ_MAX_OUTPUT_TOKENS', 1200) or 1200)
        temperature = float(getattr(settings, 'GROQ_TEMPERATURE', 0.35) or 0.35)

        payload = {
            'model': model,
            'messages': [
                {
                    'role': 'system',
                    'content': 'Eres un tutor virtual académico de gestión del conocimiento. Responde en español, claro, breve y con orientación pedagógica.',
                },
                {'role': 'user', 'content': prompt},
            ],
            'temperature': temperature,
            'max_completion_tokens': max_tokens,
        }

        try:
            response = requests.post(
                'https://api.groq.com/openai/v1/chat/completions',
                headers={
                    'Authorization': f'Bearer {api_key}',
                    'Content-Type': 'application/json',
                },
                json=payload,
                timeout=timeout,
            )
        except requests.RequestException as exc:
            raise AIGatewayError(f'Error de red consultando GroqCloud: {exc}') from exc

        if response.status_code >= 400:
            raise AIGatewayError(self._safe_error(response))

        try:
            data = response.json()
        except ValueError as exc:
            raise AIGatewayError('GroqCloud devolvió una respuesta no JSON.') from exc

        text = self._extract_text_from_ai_payload(data)
        if text:
            return text
        raise AIGatewayError('GroqCloud respondió, pero no se encontró texto en choices[0].message.content.')

    def _openai(self, prompt: str) -> str:
        if not getattr(settings, 'OPENAI_API_KEY', ''):
            raise AIGatewayError('OPENAI_API_KEY no está configurada.')
        try:
            response = requests.post(
                'https://api.openai.com/v1/chat/completions',
                headers={
                    'Authorization': f"Bearer {settings.OPENAI_API_KEY}",
                    'Content-Type': 'application/json',
                },
                json={
                    'model': settings.OPENAI_MODEL,
                    'messages': [{'role': 'user', 'content': prompt}],
                    'temperature': 0.3,
                },
                timeout=30,
            )
        except requests.RequestException as exc:
            raise AIGatewayError(f'Error de red consultando OpenAI: {exc}') from exc
        if response.status_code >= 400:
            raise AIGatewayError(self._safe_error(response))
        data = response.json()
        return data['choices'][0]['message']['content']

    def _gemini(self, prompt: str) -> str:
        api_key = self.gemini_api_key()
        if not api_key:
            raise AIGatewayError(
                'GEMINI_API_KEY no está configurada. Abra /configuracion-gemini/ o ejecute configurar_gemini.bat y pegue su API key/token.'
            )

        model = getattr(settings, 'GEMINI_MODEL', 'gemini-2.0-flash') or 'gemini-2.0-flash'
        timeout = int(getattr(settings, 'GEMINI_TIMEOUT', 45) or 45)
        max_tokens = int(getattr(settings, 'GEMINI_MAX_OUTPUT_TOKENS', 1200) or 1200)
        temperature = float(getattr(settings, 'GEMINI_TEMPERATURE', 0.35) or 0.35)

        url = f'https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent'
        payload: dict[str, Any] = {
            'contents': [
                {
                    'role': 'user',
                    'parts': [{'text': prompt}],
                }
            ],
            'generationConfig': {
                'temperature': temperature,
                'topP': 0.95,
                'maxOutputTokens': max_tokens,
            },
        }

        try:
            response = requests.post(
                url,
                params={'key': api_key},
                headers={'Content-Type': 'application/json'},
                json=payload,
                timeout=timeout,
            )
        except requests.RequestException as exc:
            raise AIGatewayError(f'Error de red consultando Gemini: {exc}') from exc

        if response.status_code >= 400:
            raise AIGatewayError(self._safe_error(response))

        try:
            data = response.json()
        except ValueError as exc:
            raise AIGatewayError('Gemini devolvió una respuesta no JSON.') from exc

        prompt_feedback = data.get('promptFeedback') or {}
        if prompt_feedback.get('blockReason'):
            raise AIGatewayError(f"Gemini bloqueó la solicitud: {prompt_feedback.get('blockReason')}")

        text = self._extract_text_from_ai_payload(data)
        if text:
            return text

        candidates = data.get('candidates') or []
        if not candidates:
            return 'Gemini no devolvió candidatos de respuesta.'

        finish_reason = candidates[0].get('finishReason', '')
        if finish_reason:
            return f'Gemini no devolvió texto. Motivo de finalización: {finish_reason}.'
        return 'Gemini respondió, pero no se encontró texto en la respuesta.'

    @staticmethod
    def _extract_text_from_ai_payload(data: Any) -> str:
        if isinstance(data, str):
            return data.strip()
        if isinstance(data, list) and data:
            return AIGateway._extract_text_from_ai_payload(data[0])
        if not isinstance(data, dict):
            return ''

        for key in ('answer', 'response', 'text', 'content', 'message'):
            value = data.get(key)
            if isinstance(value, str) and value.strip():
                return value.strip()
            if isinstance(value, dict):
                nested = AIGateway._extract_text_from_ai_payload(value)
                if nested:
                    return nested

        choices = data.get('choices') or []
        if choices:
            first = choices[0]
            if isinstance(first, dict):
                message = first.get('message') or {}
                if isinstance(message, dict) and isinstance(message.get('content'), str):
                    return message['content'].strip()
                if isinstance(first.get('text'), str):
                    return first['text'].strip()

        candidates = data.get('candidates') or []
        if candidates:
            first = candidates[0]
            if isinstance(first, dict):
                parts = (first.get('content') or {}).get('parts') or []
                text = ''.join(part.get('text', '') for part in parts if isinstance(part, dict)).strip()
                if text:
                    return text
        return ''

    @staticmethod
    def _safe_error(response: requests.Response) -> str:
        try:
            data = response.json()
            error = data.get('error') if isinstance(data, dict) else None
            if isinstance(error, dict):
                message = error.get('message') or str(error)
                status = error.get('status', '')
                return f'{response.status_code} {status}: {message}'
            return f'{response.status_code}: {data}'
        except ValueError:
            return f'{response.status_code}: {response.text[:600]}'
