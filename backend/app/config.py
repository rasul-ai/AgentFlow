from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # Ollama Cloud (https://ollama.com) hosts large chat/generation models but does NOT serve
    # the /api/embed endpoint — embeddings must run on a local `ollama serve` instance instead.
    ollama_chat_host: str = "https://ollama.com"
    ollama_chat_api_key: str = ""
    ollama_chat_model: str = "gpt-oss:20b"  # qwen3.5:cloud

    ollama_embed_host: str = "http://localhost:11434"
    ollama_embed_api_key: str = ""
    hf_embed_model: str = "embeddinggemma:300m"

    database_url: str = "sqlite:///./data/app.db"
    chroma_dir: str = "./data/chroma"
    policy_pdf_path: str = "./data/leave_policy.pdf"

    cors_origins: str = "http://localhost:5173"

    company_name: str = "Code 19"
    policy_year: str = "2022"

    # Demo-grade auth — fine for a local prototype with seeded fake accounts. Override
    # JWT_SECRET in .env for anything beyond a local demo.
    jwt_secret: str = "code19-dev-secret-change-me"
    jwt_expire_minutes: int = 60 * 24

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
