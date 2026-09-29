from app.llm.client import embed_texts
from app.rag.ingest import get_chroma_collection


def retrieve_policy_chunks(query: str, top_k: int = 3) -> list[dict]:
    collection = get_chroma_collection()
    query_embedding = embed_texts([query])[0]
    result = collection.query(query_embeddings=[query_embedding], n_results=top_k)

    chunks = []
    for doc, meta, dist, cid in zip(
        result["documents"][0], result["metadatas"][0], result["distances"][0], result["ids"][0]
    ):
        chunks.append({"id": cid, "section": meta["section"], "title": meta["title"], "text": doc, "distance": dist})
    return chunks
