# Despliegue del tutor virtual con n8n Cloud + GroqCloud

Esta versión ya quedó configurada para su instancia de n8n Cloud:

```text
https://tutorvirtual.app.n8n.cloud/webhook/tutor-virtual-ai
```

## 1. Importar workflow en n8n Cloud

1. Ingrese a `https://tutorvirtual.app.n8n.cloud/`.
2. Cree un workflow nuevo o use la opción **Import from file**.
3. Importe el archivo:

```text
n8n/workflows/tutor_virtual_groq_workflow_cloud.json
```

El nodo Webhook queda con path:

```text
tutor-virtual-ai
```

Por eso la URL productiva queda:

```text
https://tutorvirtual.app.n8n.cloud/webhook/tutor-virtual-ai
```

## 2. Probar en n8n

Mientras esté editando el workflow, use la Test URL de n8n:

```text
https://tutorvirtual.app.n8n.cloud/webhook-test/tutor-virtual-ai
```

Cuando ya funcione, publique o active el workflow y cambie a la Production URL:

```text
https://tutorvirtual.app.n8n.cloud/webhook/tutor-virtual-ai
```

## 3. Configurar Django

El archivo `.env` ya trae:

```text
AI_PROVIDER=n8n
N8N_WEBHOOK_URL=https://tutorvirtual.app.n8n.cloud/webhook/tutor-virtual-ai
N8N_FALLBACK_PROVIDER=groq
```

Debe pegar su token de Groq desde el panel web del proyecto:

```text
http://127.0.0.1:8000/configuracion-n8n/
```

También puede usar:

```text
configurar_n8n_cloud.bat
```

## 4. Ejecutar el proyecto

```bat
run_localhost.bat
```

Luego abra:

```text
http://127.0.0.1:8000/
```

Usuarios demo:

| Rol | Usuario | Contraseña |
|---|---|---|
| Administrador | admin_demo | Admin12345* |
| Gestor | gestor_demo | Gestor12345* |
| Tutor | tutor_demo | Tutor12345* |
| Estudiante | estudiante_demo | Estudiante12345* |

## 5. Ruta de prueba del tutor

```text
http://127.0.0.1:8000/tutor/
```

El flujo final queda así:

```text
Usuario → Django Dashboard → Webhook n8n Cloud → GroqCloud → n8n Cloud → Django → Historial
```

Nota: no se incluye ningún token real por seguridad. Pegue su API key de Groq en la pantalla de configuración.
