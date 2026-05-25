SOLUCION AL ERROR DE POSTGRESQL / UnicodeDecodeError

El error ocurrido se debe a que Django estaba intentando conectarse a PostgreSQL en vez de usar SQLite local.
Esta versión ya queda corregida para que en localhost use SQLite por defecto.

FORMA MAS FACIL DE EJECUTAR EN WINDOWS:
1. Descomprima el ZIP.
2. Entre a la carpeta TutorVirtual_RamirezAnderson_SanchezLuis.
3. Haga doble clic en run_localhost.bat.
4. Espere a que instale dependencias, migre y cargue usuarios demo.
5. Abra http://127.0.0.1:8000/

USUARIOS DEMO:
Administrador: admin_demo / Admin12345*
Gestor: gestor_demo / Gestor12345*
Tutor: tutor_demo / Tutor12345*
Estudiante: estudiante_demo / Estudiante12345*

EJECUCION MANUAL:
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate --noinput
python manage.py seed_demo
python manage.py runserver 127.0.0.1:8000

IMPORTANTE:
No cambie LOCALHOST_MODE=True ni USE_POSTGRES=False si solo quiere ejecutarlo en su computador.
Para PostgreSQL en despliegue real cambie USE_POSTGRES=True y configure las credenciales.
