from typing import List
from dataclasses import dataclass
import uuid

from sentence_transformers import SentenceTransformer


@dataclass
class Embedding:
    embedding_id: str
    chunk_id: str
    vector: List[float]
    dimension: int
    model_name: str


class EmbeddingGenerator:
    def __init__(self, model_name: str, batch_size: int = 32) -> None:
        self._model_name: str = model_name
        self._model = SentenceTransformer(model_name)
        self._batch_size: int = batch_size

    def Generate(self, chunks: List) -> List[Embedding]:
        texts: List[str] = [chunk.text for chunk in chunks]
        embeddings: List[List[float]] = []

        for i in range(0, len(texts), self._batch_size):
            batch = texts[i:i + self._batch_size]
            batch_embeddings = self._model.encode(batch, convert_to_numpy=True).tolist()
            embeddings.extend(batch_embeddings)

        results: List[Embedding] = []

        for chunk, vector in zip(chunks, embeddings):
            results.append(
                Embedding(
                    embedding_id=str(uuid.uuid4()),
                    chunk_id=chunk.chunk_id,
                    vector=vector,
                    dimension=len(vector),
                    model_name=self._model_name
                )
            )

        return results