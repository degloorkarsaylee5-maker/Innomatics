from typing import List, Dict, Any

from vector_store.chroma_client import ChromaClient
from utils.logger import GetLogger
from utils.config import GetSettings


class RetrievalResult:
    def __init__(
        self,
        chunk_id: str,
        text: str,
        score: float,
        metadata: Dict[str, Any]
    ) -> None:
        self.chunk_id: str = chunk_id
        self.text: str = text
        self.score: float = score
        self.metadata: Dict[str, Any] = metadata


class Retriever:
    def __init__(self, chroma_client: ChromaClient) -> None:
        self._client = chroma_client
        self._collection = chroma_client.GetCollection()
        self._logger = GetLogger(self.__class__.__name__)
        self._settings = GetSettings()

    def Retrieve(
        self,
        query_embedding: List[float],
        top_k: int | None = None,
        score_threshold: float = 0.0
    ) -> List[RetrievalResult]:

        k: int = top_k if top_k is not None else self._settings.top_k

        try:
            results = self._collection.query(
                query_embeddings=[query_embedding],
                n_results=k,
                include=["documents", "metadatas", "distances"]
            )

            retrieved: List[RetrievalResult] = []

            ids = results.get("ids", [[]])[0]
            docs = results.get("documents", [[]])[0]
            metas = results.get("metadatas", [[]])[0]
            distances = results.get("distances", [[]])[0]

            for idx, doc, meta, distance in zip(ids, docs, metas, distances):
                score = 1.0 - float(distance)  # convert distance → similarity

                if score < score_threshold:
                    continue

                retrieved.append(
                    RetrievalResult(
                        chunk_id=idx,
                        text=doc,
                        score=score,
                        metadata=meta
                    )
                )

            self._logger.debug("Retrieval completed", extra={
                "requested_k": k,
                "returned": len(retrieved)
            })

            return retrieved

        except Exception as ex:
            self._logger.error("Retrieval failed", exc_info=True)
            raise RuntimeError("Vector retrieval failed") from ex