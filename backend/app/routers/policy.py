from fastapi import APIRouter

from app.rag.retriever import retrieve_policy_chunks
from app.schemas import PolicySearchResult

router = APIRouter(prefix="/policy", tags=["policy"])


@router.get("/search", response_model=list[PolicySearchResult])
def search_policy(q: str, top_k: int = 3):
    return retrieve_policy_chunks(q, top_k=top_k)
