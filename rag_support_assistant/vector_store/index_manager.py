from typing import List, Dict, Any

from ingestion.chunker import Chunk
from ingestion.embedding_generator import Embedding
from vector_store.chroma_client import ChromaClient
from utils.logger import GetLogger


class IndexManager:
    def __init__(self, chroma_client: ChromaClient) -> None:
        self._client = chroma_client
        self._collection = chroma_client.GetCollection()
        self._logger = GetLogger(self.__class__.__name__)

    def Upsert(self, chunks: List[Chunk], embeddings: List[Embedding]) -> None:
        try:
            if len(chunks) != len(embeddings):
                raise ValueError("Chunks and embeddings length mismatch")

            ids: List[str] = []
            documents: List[str] = []
            metadatas: List[Dict[str, Any]] = []
            vectors: List[List[float]] = []

            for chunk, embedding in zip(chunks, embeddings):
                ids.append(chunk.chunk_id)
                documents.append(chunk.text)
                vectors.append(embedding.vector)

                metadatas.append({
                    "page_number": chunk.page_number,
                    "position_index": chunk.position_index,
                    "token_count": chunk.token_count
                })

            self._collection.upsert(
                ids=ids,
                documents=documents,
                embeddings=vectors,
                metadatas=metadatas
            )

            self._client.Persist()

            self._logger.info("Upsert completed", extra={
                "count": len(ids)
            })

        except Exception as ex:
            self._logger.error("Upsert failed", exc_info=True)
            raise RuntimeError("Index upsert failed") from ex

    def Delete(self, ids: List[str]) -> None:
        try:
            self._collection.delete(ids=ids)
            self._client.Persist()

            self._logger.info("Delete completed", extra={
                "count": len(ids)
            })

        except Exception as ex:
            self._logger.error("Delete failed", exc_info=True)
            raise RuntimeError("Index delete failed") from ex

    def Update(self, chunks: List[Chunk], embeddings: List[Embedding]) -> None:
        # In Chroma, update = upsert
        self.Upsert(chunks, embeddings)