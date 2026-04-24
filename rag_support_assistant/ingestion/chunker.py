from typing import List, Dict
from dataclasses import dataclass
import uuid


@dataclass
class Chunk:
    chunk_id: str
    text: str
    page_number: int
    token_count: int
    position_index: int


class Chunker:
    def __init__(self, chunk_size: int, overlap: int) -> None:
        self._chunk_size: int = chunk_size
        self._overlap: int = overlap

    def Chunk(self, pages: List[Dict]) -> List[Chunk]:
        chunks: List[Chunk] = []
        position_index: int = 0

        for page in pages:
            words = page["text"].split()
            start: int = 0

            while start < len(words):
                end: int = start + self._chunk_size
                chunk_words = words[start:end]

                chunk_text: str = " ".join(chunk_words)

                chunk = Chunk(
                    chunk_id=str(uuid.uuid4()),
                    text=chunk_text,
                    page_number=page["page_number"],
                    token_count=len(chunk_words),
                    position_index=position_index
                )

                chunks.append(chunk)
                position_index += 1

                start += self._chunk_size - self._overlap

        return chunks