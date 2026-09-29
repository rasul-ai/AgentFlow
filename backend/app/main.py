import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.db import init_db
from app.rag.ingest import build_index
from app.routers import auth, chat, employees, hr, leave, policy
from app.seed import seed_if_empty

logger = logging.getLogger("code19-hr")


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    seed_if_empty()
    try:
        build_index()
    except Exception as exc:  # e.g. embedding host unreachable or chat key not set yet
        logger.warning(
            "Could not build the policy RAG index at startup (%s). The server will still start; leave "
            "requests and chat will fail until OLLAMA_CHAT_API_KEY and a running OLLAMA_EMBED_HOST are "
            "both valid and the backend is restarted.",
            exc,
        )
    yield


settings = get_settings()
app = FastAPI(title=f"{settings.company_name} HR Leave Assistant", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(employees.router)
app.include_router(leave.router)
app.include_router(hr.router)
app.include_router(policy.router)
app.include_router(chat.router)


@app.get("/health")
def health():
    return {"status": "ok", "company": settings.company_name, "policy_year": settings.policy_year}
