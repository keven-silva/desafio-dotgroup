from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

PACKAGE_ROOT = Path(__file__).resolve().parent.parent.parent.parent


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    embedding_provider: str = "sentence-transformers"
    # multilingual: os artigos de exemplo são em português, e o all-MiniLM-L6-v2 (inglês)
    # rankeia mal consultas em PT-BR — validado empiricamente antes de fixar este default.
    embedding_model: str = "paraphrase-multilingual-MiniLM-L12-v2"
    openai_api_key: str = ""

    rag_data_dir: Path = PACKAGE_ROOT / "data" / "raw"
    rag_index_dir: Path = PACKAGE_ROOT / "data" / "index"

    chunk_size: int = 800
    chunk_overlap: int = 120

    log_level: str = "INFO"
    log_json: bool = True


@lru_cache
def get_settings() -> Settings:
    return Settings()
