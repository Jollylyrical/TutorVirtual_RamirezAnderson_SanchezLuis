# Tutor Virtual con Gemini API en localhost

Esta versión deja el proyecto funcionando en localhost con SQLite y el tutor virtual preparado para llamar a Gemini.

## Ejecución rápida

1. Descomprima el ZIP.
2. Entre a la carpeta `TutorVirtual_RamirezAnderson_SanchezLuis`.
3. Ejecute `run_localhost.bat`.
4. Abra `http://127.0.0.1:8000/`.

## Usuarios demo

| Rol | Usuario | Contraseña |
|---|---|---|
| Administrador | `admin_demo` | `Admin12345*` |
| Gestor | `gestor_demo` | `Gestor12345*` |
| Tutor | `tutor_demo` | `Tutor12345*` |
| Estudiante | `estudiante_demo` | `Estudiante12345*` |

## Activar Gemini

Tiene dos opciones:

### Opción A: desde la interfaz

1. Inicie sesión.
2. Entre a `Gemini Token` en el menú lateral.
3. Pegue su API key/token de Gemini.
4. Deje el modelo `gemini-2.0-flash` o seleccione otro.
5. Presione `Guardar y probar conexión`.

### Opción B: desde archivo .env

Abra `.env` y configure:

```env
AI_PROVIDER=gemini
GEMINI_API_KEY=PEGUE_AQUI_SU_TOKEN_REAL
GEMINI_MODEL=gemini-2.0-flash
```

Después reinicie `run_localhost.bat`.

### Opción C: asistente por consola

Ejecute:

```bat
configurar_gemini.bat
```

Pegue su token cuando el sistema lo pida.

## Cómo funciona el flujo

1. El usuario hace una pregunta en `/tutor/`.
2. Django busca contexto en MongoDB o en SQLite si MongoDB no está activo.
3. Se construye un prompt con el contexto recuperado.
4. `AIGateway` llama al endpoint `generateContent` de Gemini mediante HTTPS REST.
5. La respuesta, la pregunta y los fragmentos usados quedan guardados en el historial.

## Archivos principales modificados

- `apps/ai_assistant/ai_gateway.py`: integración robusta con Gemini API.
- `apps/core/views.py`: panel de configuración del token Gemini.
- `templates/ai_assistant/gemini_config.html`: interfaz visual para el token.
- `templates/ai_assistant/tutor.html`: estado del proveedor IA y enlace a Gemini.
- `.env` y `.env.example`: `AI_PROVIDER=gemini` preparado.
- `configurar_gemini.bat`: configuración rápida por consola.
