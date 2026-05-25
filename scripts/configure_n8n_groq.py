from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
ENV_PATH = BASE_DIR / '.env'

print('==========================================================')
print(' CONFIGURAR n8n + GROQCLOUD PARA EL TUTOR VIRTUAL')
print('==========================================================')
print('Deje en blanco un campo para conservar el valor actual.')

def read_env():
    data = {}
    if ENV_PATH.exists():
        for line in ENV_PATH.read_text(encoding='utf-8').splitlines():
            if line.strip() and not line.strip().startswith('#') and '=' in line:
                k, v = line.split('=', 1)
                data[k.strip()] = v.strip()
    return data

def write_env(data):
    existing = ENV_PATH.read_text(encoding='utf-8').splitlines() if ENV_PATH.exists() else []
    keys = set(data)
    out = []
    written = set()
    for line in existing:
        if line.strip() and not line.strip().startswith('#') and '=' in line:
            k = line.split('=', 1)[0].strip()
            if k in data:
                out.append(f'{k}={data[k]}')
                written.add(k)
            else:
                out.append(line)
        else:
            out.append(line)
    for k in keys - written:
        out.append(f'{k}={data[k]}')
    ENV_PATH.write_text('\n'.join(out).rstrip() + '\n', encoding='utf-8')

env = read_env()
webhook = input(f"URL Webhook n8n [{env.get('N8N_WEBHOOK_URL','https://tutorvirtual.app.n8n.cloud/webhook/tutor-virtual-ai')}]: ").strip()
secret = input(f"Secreto compartido [{env.get('N8N_SHARED_SECRET','dev-n8n-secret')}]: ").strip()
key = input('GROQ_API_KEY [oculta en .env, pegue una nueva si desea cambiarla]: ').strip()
model = input(f"Modelo Groq [{env.get('GROQ_MODEL','llama-3.1-8b-instant')}]: ").strip()

updates = {
    'AI_PROVIDER': 'n8n',
    'N8N_WEBHOOK_URL': webhook or env.get('N8N_WEBHOOK_URL', 'https://tutorvirtual.app.n8n.cloud/webhook/tutor-virtual-ai'),
    'N8N_SHARED_SECRET': secret or env.get('N8N_SHARED_SECRET', 'dev-n8n-secret'),
    'N8N_TIMEOUT': env.get('N8N_TIMEOUT', '60'),
    'N8N_FALLBACK_PROVIDER': env.get('N8N_FALLBACK_PROVIDER', 'groq'),
    'GROQ_MODEL': model or env.get('GROQ_MODEL', 'llama-3.1-8b-instant'),
}
if key:
    updates['GROQ_API_KEY'] = key
elif 'GROQ_API_KEY' not in env:
    # Do not hardcode API keys in source. Ask user to set it in .env instead.
    # Use a placeholder so push protection won't flag this repository.
    updates['GROQ_API_KEY'] = 'REPLACE_WITH_GROQ_API_KEY'

write_env(updates)
print('\nConfiguración guardada en:', ENV_PATH)
print('Inicie Django con run_localhost.bat y abra /configuracion-n8n/ para probar.')
