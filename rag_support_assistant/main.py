import os
from fastapi import FastAPI
from dotenv import load_dotenv

from api.routes import router as api_router
from api.middleware import LoggingMiddleware, TimingMiddleware, ErrorHandlingMiddleware

from ingestion.ingestion_pipeline import IngestionPipeline
from vector_store.chroma_client import ChromaClient
from vector_store.index_manager import IndexManager
from utils.config import GetSettings
from utils.logger import GetLogger


# Load environment variables
load_dotenv()

logger = GetLogger("Main")


def InitializeVectorDB() -> IndexManager:
    settings = GetSettings()

    chroma_client = ChromaClient(collection_name="support_collection")
    index_manager = IndexManager(chroma_client)

    return index_manager


def RunInitialIngestion(index_manager: IndexManager) -> None:
    """
    Optional bootstrap ingestion.
    Place PDFs inside ./data folder.
    """
    settings = GetSettings()

    data_folder = "./data"

    if not os.path.exists(data_folder):
        logger.info("No data folder found, skipping ingestion")
        return

    # Skip if collection already has documents
    collection = index_manager._collection
    if collection.count() > 0:
        logger.info("Collection already has data, skipping ingestion", extra={
            "document_count": collection.count()
        })
        return

    pipeline = IngestionPipeline(
        chunk_size=settings.chunk_size,
        chunk_overlap=settings.chunk_overlap,
        embedding_model=settings.embedding_model
    )

    for file_name in os.listdir(data_folder):
        if not file_name.endswith(".pdf"):
            continue

        file_path = os.path.join(data_folder, file_name)

        try:
            logger.info("Processing PDF", extra={"file": file_name})

            result = pipeline.Process(file_path)

            index_manager.Upsert(
                chunks=result["chunks"],
                embeddings=result["embeddings"]
            )

            logger.info("Ingestion completed", extra={"file": file_name})

        except Exception:
            logger.error("Failed to ingest file", exc_info=True)


def CreateApp() -> FastAPI:
    app = FastAPI(title="RAG Customer Support Assistant")

    # Middleware
    app.add_middleware(ErrorHandlingMiddleware)
    app.add_middleware(LoggingMiddleware)
    app.add_middleware(TimingMiddleware)

    # Routes
    app.include_router(api_router)

    return app


# ---- Bootstrap ----
logger.info("Starting system initialization")

index_manager = InitializeVectorDB()
RunInitialIngestion(index_manager)

app = CreateApp()

logger.info("System ready")