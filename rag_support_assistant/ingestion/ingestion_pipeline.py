from typing import Dict, List

from ingestion.pdf_loader import PdfLoader
from ingestion.text_cleaner import TextCleaner
from ingestion.chunker import Chunker, Chunk
from ingestion.embedding_generator import EmbeddingGenerator, Embedding


class IngestionPipeline:
    def __init__(
        self,
        chunk_size: int,
        chunk_overlap: int,
        embedding_model: str
    ) -> None:
        self._cleaner = TextCleaner()
        self._chunker = Chunker(chunk_size, chunk_overlap)
        self._embedding_generator = EmbeddingGenerator(embedding_model)

    def Process(self, file_path: str) -> Dict:
        loader = PdfLoader(file_path)

        # Step 1: Load PDF
        pages = loader.Load()

        # Step 2: Clean Text
        cleaned_pages = self._cleaner.Clean(pages)

        # Step 3: Chunking
        chunks: List[Chunk] = self._chunker.Chunk(cleaned_pages)

        # Step 4: Embedding Generation
        embeddings: List[Embedding] = self._embedding_generator.Generate(chunks)

        return {
            "chunks": chunks,
            "embeddings": embeddings
        }