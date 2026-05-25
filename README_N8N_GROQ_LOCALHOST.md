# Tutor Virtual - Despliegue local con n8n + GroqCloud

Esta versión cambia la integración de IA para que el tutor virtual funcione con el flujo:

**Django → Webhook n8n → GroqCloud API → n8n → Django → Dashboard**

## 1. Ejecutar Django en localhost

```bat
run_localhost.bat
```

Abra:

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

## 2. Configurar GroqCloud

1. Cree una API key en GroqCloud.
2. Entre al sistema como `admin_demo`.
3. Abra el menú **n8n + Groq**.
4. Pegue la API key.
5. Deje el modelo recomendado: `llama-3.1-8b-instant`.
6. Presione **Guardar configuración**.

## 3. Ejecutar n8n local

Con Docker Desktop instalado:

```bat
run_n8n_localhost.bat
```

Abra:

```text
http://localhost:5678/
```

Importe este archivo:

```text
n8n/workflows/tutor_virtual_groq_workflow.json
```

Active el workflow. El Webhook productivo debe quedar así:

```text
http://localhost:5678/webhook/tutor-virtual-ai
```

## 4. Probar el tutor

En Django abra:

```text
http://127.0.0.1:8000/tutor/
```

Haga una pregunta. El sistema recupera contexto desde la base de conocimiento, envía el prompt a n8n, n8n consulta GroqCloud y Django guarda la respuesta en el historial.

## 5. Modo de respaldo

Si n8n todavía no está importado o activo, el sistema puede usar Groq directo como respaldo si `GROQ_API_KEY` está configurada y `N8N_FALLBACK_PROVIDER=groq`.


---

## Uso con su n8n Cloud

Como ya creó la cuenta en n8n Cloud, puede omitir Docker/n8n local. Use directamente:

```text
https://tutorvirtual.app.n8n.cloud/webhook/tutor-virtual-ai
```

Importe este archivo en n8n Cloud:

```text
n8n/workflows/tutor_virtual_groq_workflow_cloud.json
```

Después publique/active el workflow y configure Django desde:

```text
http://127.0.0.1:8000/configuracion-n8n/
```
