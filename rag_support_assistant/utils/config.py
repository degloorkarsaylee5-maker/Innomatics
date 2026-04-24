from pydantic import Field, ConfigDict
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    model_config = ConfigDict(env_file=".env", case_sensitive=False, extra="ignore")

    # LLM Configuration
    llm_provider: str = Field(..., env="LLM_PROVIDER")
    llm_model: str = Field(..., env="LLM_MODEL")

    # Embeddings
    embedding_model: str = Field(..., env="EMBEDDING_MODEL")

    # Vector DB
    chroma_path: str = Field(..., env="CHROMA_PATH")

    # Retrieval
    top_k: int = Field(5, env="TOP_K")

    # Chunking
    chunk_size: int = Field(500, env="CHUNK_SIZE")
    chunk_overlap: int = Field(50, env="CHUNK_OVERLAP")

    # Performance / Thresholds
    confidence_threshold: float = Field(0.7, env="CONFIDENCE_THRESHOLD")

    # HuggingFace (optional)
    hf_token: str = Field("", env="HF_TOKEN")


@lru_cache()
def GetSettings() -> Settings:
    return Settings()