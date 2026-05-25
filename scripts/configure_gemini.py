from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
ENV_PATH = BASE_DIR / '.env'

DEFAULTS = {
    'AI_PROVIDER': 'gemini',
    'GEMINI_MODEL': 'gemini-2.0-flash',
    'GEMINI_TIMEOUT': '45',
    'GEMINI_MAX_OUTPUT_TOKENS': '1200',
    'GEMINI_TEMPERATURE': '0.35',
}


def update_env(updates: dict[str, str]) -> None:
    lines = ENV_PATH.read_text(encoding='utf-8').splitlines() if ENV_PATH.exists() else []
    seen = set()
    out = []
    for line in lines:
        stripped = line.strip()
        if not stripped or stripped.startswith('#') or '=' not in line:
            out.append(line)
            continue
        key = line.split('=', 1)[0].strip()
        if key in updates:
            out.append(f'{key}={updates[key]}')
            seen.add(key)
        else:
            out.append(line)
    for key, value in updates.items():
        if key not in seen:
            out.append(f'{key}={value}')
    ENV_PATH.write_text('\n'.join(out).rstrip() + '\n', encoding='utf-8')


print('Configuración de Gemini para Tutor Virtual')
print('El token se guardará solo en el archivo .env local. No lo suba a GitHub.')
api_key = input('Pegue su API key/token de Gemini: ').strip()
if not api_key:
    raise SystemExit('No se recibió token. No se hicieron cambios.')
model = input('Modelo Gemini [gemini-2.0-flash]: ').strip() or DEFAULTS['GEMINI_MODEL']
updates = {**DEFAULTS, 'GEMINI_API_KEY': api_key, 'GEMINI_MODEL': model}
update_env(updates)
print('\nListo. AI_PROVIDER=gemini quedó activo.')
print('Ahora ejecute run_localhost.bat y pruebe el tutor en http://127.0.0.1:8000/tutor/')
