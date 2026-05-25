# Proyecto: Tutor Virtual Inteligente para Gestión del Conocimiento

## Introducción
El proyecto implementa un sistema web para apoyar la gestión del conocimiento mediante captura, organización, consulta y reutilización de información institucional. La solución integra dashboards por rol, base de conocimiento, API REST, autenticación JWT y un tutor virtual con IA.

## Problema
Muchas organizaciones almacenan documentos, guías y experiencias en fuentes dispersas, lo que dificulta encontrar información relevante, transferir conocimiento y conservar trazabilidad de las consultas. Esto limita el aprendizaje organizacional y la toma de decisiones.

## Objetivo general
Desarrollar un tutor virtual inteligente que permita gestionar documentos de conocimiento, consultar información mediante IA y ofrecer dashboards diferenciados por usuario.

## Componentes funcionales
1. Registro e inicio de sesión.
2. Perfiles por rol.
3. Dashboards para administrador, gestor, tutor y estudiante.
4. Gestión de documentos.
5. Indexación semántica en MongoDB o respaldo local.
6. Consulta del tutor IA.
7. Historial de conversaciones.
8. Auditoría de documentos.
9. API REST protegida con JWT.

## Arquitectura
El cliente accede desde navegador web. El tráfico externo se protege con HTTPS/TLS mediante Nginx. La aplicación Django opera como frontend y backend, se sirve con Gunicorn/Uvicorn, expone una API REST y se conecta con PostgreSQL/SQLite, MongoDB y un proveedor de IA externo o local.

## Seguridad
El sistema aplica autenticación por sesión para la interfaz web, JWT Bearer Token para la API, control de permisos por rol, variables de entorno para secretos y separación entre configuración local y producción.

## Conclusión
El proyecto queda funcional en localhost y mantiene compatibilidad con una arquitectura de despliegue completa en Azure Web App Service, PostgreSQL, MongoDB Atlas, Nginx, Gunicorn/Uvicorn y servicios de IA externos.
