import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

# Attempt to run migrations on startup so production hosts that don't run
# release commands still get the database schema initialized. This is
# defensive: if migrations fail we'll print the exception but continue
# so the server doesn't crash repeatedly.
try:
	import django
	django.setup()
	from django.core.management import call_command

	try:
		call_command('migrate', '--noinput')
		print('Applied migrations at startup')
	except Exception as exc:
		# Print to stdout/stderr so hosting logs capture the failure
		print('Auto-migrate failed:', exc)
except Exception as exc:
	print('Startup migration attempt skipped or failed:', exc)

application = get_wsgi_application()
