SYSTEM_PROMPT = """
Eres un tutor virtual para gestión del conocimiento. Responde en español, con tono claro,
académico y útil. Usa el contexto institucional recuperado cuando esté disponible.
Si no hay contexto suficiente, dilo de manera transparente y entrega una orientación general.
No inventes fuentes ni datos. Propón pasos concretos para aprender, documentar y aplicar el conocimiento.
""".strip()


def build_prompt(question: str, context_chunks: list[dict]) -> str:
    context = '\n\n'.join(
        f"[Documento: {item.get('title')} | Fuente: {item.get('source', 'sin fuente')}]\n{item.get('chunk')}"
        for item in context_chunks
    ) or 'No se encontró contexto documental suficiente.'

    return f"""
{SYSTEM_PROMPT}

CONTEXTO RECUPERADO:
{context}

PREGUNTA DEL USUARIO:
{question}

RESPUESTA DEL TUTOR:
""".strip()
