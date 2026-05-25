# Pruebas funcionales sugeridas

| Prueba | Pasos | Resultado esperado |
|---|---|---|
| Inicio de sesión | Entrar con `admin_demo` | Accede al dashboard de administrador |
| Dashboard por rol | Entrar con cada usuario demo | Muestra panel diferente según rol |
| Crear documento | Ingresar como gestor y guardar documento | Documento creado e indexado |
| Consultar tutor | Preguntar por gestión del conocimiento | Respuesta generada y contexto recuperado |
| Historial | Consultar después de preguntar | Aparece la conversación guardada |
| Health API | Abrir `/api/health/` | Respuesta JSON con estado del sistema |
| JWT | Solicitar token en `/api/auth/token/` | Retorna access y refresh token |
