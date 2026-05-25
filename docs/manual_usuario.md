# Manual de usuario - Tutor Virtual Inteligente

## 1. Ingreso
Abra `http://127.0.0.1:8000/` y seleccione **Ingresar**. Puede usar los usuarios demo creados con `python manage.py seed_demo`.

## 2. Dashboards por rol
- **Administrador:** métricas generales, auditoría, protocolos y control del sistema.
- **Gestor del conocimiento:** carga, clasificación e indexación de documentos.
- **Tutor / Docente:** apoyo pedagógico, carga de material y consulta del tutor IA.
- **Estudiante / Aprendiz:** consulta de conocimiento, preguntas al tutor e historial.

## 3. Cargar documentos
Ingrese a **Conocimiento > Nuevo documento**. Esta opción está disponible para administrador, gestor y tutor. El sistema guarda el documento en la base relacional e indexa fragmentos en MongoDB o en respaldo local.

## 4. Consultar el tutor IA
Ingrese a **Tutor IA**, escriba una pregunta y presione **Preguntar al tutor**. El sistema recupera contexto documental y genera una respuesta. En modo local no se requieren claves externas.

## 5. Revisar historial
Ingrese a **Mi historial** para ver preguntas, respuestas y trazabilidad de uso.
