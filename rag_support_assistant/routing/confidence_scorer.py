from typing import List

from vector_store.retriever import RetrievalResult


class ConfidenceScorer:
    def __init__(self) -> None:
        self._min_answer_length: int = 20

    def Compute(
        self,
        retrieved_docs: List[RetrievalResult],
        llm_confidence: float,
        answer: str
    ) -> float:

        retrieval_score: float = self._ComputeRetrievalScore(retrieved_docs)
        completeness_score: float = self._ComputeCompleteness(answer)

        final_score: float = (
            0.4 * retrieval_score +
            0.4 * llm_confidence +
            0.2 * completeness_score
        )

        return max(0.0, min(1.0, final_score))

    def _ComputeRetrievalScore(self, docs: List[RetrievalResult]) -> float:
        if not docs:
            return 0.0

        scores = [doc.score for doc in docs]
        return sum(scores) / len(scores)

    def _ComputeCompleteness(self, answer: str) -> float:
        length = len(answer.split())

        if length >= self._min_answer_length:
            return 1.0

        return length / self._min_answer_length