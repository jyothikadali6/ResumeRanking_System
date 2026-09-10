"""Application configuration loaded from environment / .env."""
from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "postgresql+psycopg2://postgres:postgres@localhost:5432/resume_ranker"

    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "llama3.2"

    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    spacy_model: str = "en_core_web_sm"

    upload_dir: str = "uploads"

    semantic_weight: float = 0.7
    skill_weight: float = 0.3

    use_llm: bool = True


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
