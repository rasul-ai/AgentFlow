import re
from pathlib import Path

import chromadb

from app.config import get_settings
from app.llm.client import embed_texts

SECTION_RE = re.compile(r"^## ([A-Z])\. (.+)$", re.MULTILINE)
COLLECTION_NAME = "leave_policy"

POLICY_MD_PATH = Path(__file__).resolve().parents[2] / "data" / "policy_source.md"


def chunk_policy_markdown(md_text: str) -> list[dict]:
    """Split the policy markdown into one chunk per lettered section (A, B, C, ...)."""
    matches = list(SECTION_RE.finditer(md_text))
    chunks = []
    for i, m in enumerate(matches):
        letter, title = m.group(1), m.group(2)
        start = m.start()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(md_text)
        body = md_text[start:end].strip()
        chunks.append({"id": f"section-{letter}", "section": letter, "title": title, "text": body})
    return chunks


def get_chroma_client() -> chromadb.ClientAPI:
    settings = get_settings()
    Path(settings.chroma_dir).mkdir(parents=True, exist_ok=True)
    # anonymized_telemetry=False avoids ChromaDB's posthog telemetry calls, which otherwise
    # log a harmless but noisy "Failed to send telemetry event" error on every client/
    # collection creation due to a capture() signature mismatch between chromadb and posthog.
    return chromadb.PersistentClient(
        path=settings.chroma_dir, settings=chromadb.Settings(anonymized_telemetry=False)
    )


def get_chroma_collection():
    return get_chroma_client().get_or_create_collection(name=COLLECTION_NAME)


def build_index(force: bool = False) -> int:
    """Embed each policy section and upsert into the local Chroma collection.
    Returns the number of chunks indexed."""
    client = get_chroma_client()
    if force:
        # A different embedding model produces different vector dimensions, which a plain
        # upsert can't reconcile with an existing collection — drop and recreate instead.
        try:
            client.delete_collection(name=COLLECTION_NAME)
        except Exception:
            pass
    collection = client.get_or_create_collection(name=COLLECTION_NAME)
    if not force and collection.count() > 0:
        return collection.count()

    md_text = POLICY_MD_PATH.read_text(encoding="utf-8")
    chunks = chunk_policy_markdown(md_text)
    embeddings = embed_texts([c["text"] for c in chunks])

    collection.upsert(
        ids=[c["id"] for c in chunks],
        documents=[c["text"] for c in chunks],
        embeddings=embeddings,
        metadatas=[{"section": c["section"], "title": c["title"]} for c in chunks],
    )
    return len(chunks)
