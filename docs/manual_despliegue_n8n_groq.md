# Manual de despliegue: n8n + GroqCloud

## Arquitectura aplicada

1. El usuario consulta desde el dashboard del tutor virtual.
2. Django autentica la sesión, recupera documentos de conocimiento y arma el prompt.
3. Django envía el prompt a `N8N_WEBHOOK_URL`.
4. n8n recibe el Webhook y ejecuta el nodo HTTP Request hacia GroqCloud.
5. GroqCloud genera la respuesta.
6. n8n responde a Django con JSON.
7. Django guarda pregunta, respuesta y contexto en el historial.

## Archivos principales

- `.env`: variables locales.
- `docker-compose.n8n.yml`: servicio n8n y opción de contenedor web.
- `n8n/workflows/tutor_virtual_groq_workflow_cloud.json`: workflow importable para n8n Cloud.
- `n8n/workflows/tutor_virtual_groq_workflow.json`: copia compatible del workflow.
- `apps/ai_assistant/ai_gateway.py`: puerta de enlace IA con proveedores `n8n`, `groq`, `gemini`, `openai` y `local`.
- `templates/ai_assistant/n8n_config.html`: interfaz de configuración.

## Variables requeridas

```text
AI_PROVIDER=n8n
N8N_WEBHOOK_URL=https://tutorvirtual.app.n8n.cloud/webhook/tutor-virtual-ai
N8N_SHARED_SECRET=dev-n8n-secret
N8N_FALLBACK_PROVIDER=groq
GROQ_API_KEY=PEGUE_AQUI_SU_API_KEY
GROQ_MODEL=llama-3.1-8b-instant
```

## Comandos rápidos

```bat
run_localhost.bat
configurar_n8n_cloud.bat
```

## Verificación

- Django: `http://127.0.0.1:8000/`
- Configuración: `http://127.0.0.1:8000/configuracion-n8n/`
- n8n Cloud: `https://tutorvirtual.app.n8n.cloud/`
- Tutor: `http://127.0.0.1:8000/tutor/`

## Nota de seguridad

No suba `.env` con claves reales a GitHub. En producción, configure `GROQ_API_KEY` como variable de entorno del servidor o del contenedor n8n.


## Configuración específica de n8n Cloud

Para esta entrega, el Webhook productivo ya está preconfigurado con:

```text
https://tutorvirtual.app.n8n.cloud/webhook/tutor-virtual-ai
```

Importe el workflow `n8n/workflows/tutor_virtual_groq_workflow_cloud.json` en su cuenta de n8n Cloud, pruebe con la URL de test y después publique/active el workflow para que Django pueda consumir la URL productiva.
