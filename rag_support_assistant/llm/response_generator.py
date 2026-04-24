from typing import List, Dict, Any

from llm.llm_client import LLMClient
from llm.prompt_templates import PromptTemplates
from vector_store.retriever import RetrievalResult
from utils.logger import GetLogger


class ResponseGenerator:
    def __init__(self) -> None:
        self._llm = LLMClient()
        self._logger = GetLogger(self.__class__.__name__)

    def Generate(
        self,
        query: str,
        retrieved_docs: List[RetrievalResult]
    ) -> Dict[str, Any]:

        try:
            context_chunks: List[str] = [doc.text for doc in retrieved_docs]

            system_prompt: str = PromptTemplates.GetSystemPrompt()
            rag_prompt: str = PromptTemplates.BuildRagPrompt(query, context_chunks)

            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": rag_prompt}
            ]

            answer: str = self._llm.Generate(messages)

            sources = [
                {
                    "chunk_id": doc.chunk_id,
                    "score": doc.score,
                    "page_number": doc.metadata.get("page_number")
                }
                for doc in retrieved_docs
            ]

            return {
                "answer": answer,
                "sources": sources
            }

        except Exception as ex:
            self._logger.error("Response generation failed", exc_info=True)
            raise RuntimeError("Failed to generate response") from ex