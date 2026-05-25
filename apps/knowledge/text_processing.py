import re
from typing import Iterable, List


def normalize_text(text: str) -> str:
    text = text or ''
    text = re.sub(r'\s+', ' ', text).strip()
    return text


def chunk_text(text: str, chunk_size: int = 900, overlap: int = 120) -> List[str]:
    """Divide texto en fragmentos con solapamiento para recuperación semántica simple."""
    clean = normalize_text(text)
    if not clean:
        return []
    if len(clean) <= chunk_size:
        return [clean]

    chunks = []
    start = 0
    while start < len(clean):
        end = min(start + chunk_size, len(clean))
        boundary = clean.rfind('.', start, end)
        if boundary > start + int(chunk_size * 0.55):
            end = boundary + 1
        chunks.append(clean[start:end].strip())
        if end >= len(clean):
            break
        start = max(0, end - overlap)
    return chunks


def tokenize(text: str) -> set[str]:
    return set(re.findall(r'[a-záéíóúñü0-9]{3,}', (text or '').lower()))


def keyword_score(query: str, text: str) -> float:
    q = tokenize(query)
    t = tokenize(text)
    if not q or not t:
        return 0.0
    overlap = len(q.intersection(t))
    return overlap / max(len(q), 1)
