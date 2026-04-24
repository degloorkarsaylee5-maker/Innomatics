from typing import List, Dict, Any

from vector_store.retriever import RetrievalResult


class Evaluator:
    def __init__(self) -> None:
        self._min_similarity_threshold: float = 0.3
        self._vague_indicators = [
            "i don't know",
            "not enough information",
            "cannot determine",
            "unclear"
        ]

    def Evaluate(
        self,
        answer: str,
        retrieved_docs: List[RetrievalResult]
    ) -> Dict[str, Any]:

        similarity_score: float = self._ComputeSimilarityScore(retrieved_docs)
        vagueness_penalty: float = self._DetectVagueness(answer)
        coverage_score: float = self._EstimateCoverage(answer, retrieved_docs)

        confidence: float = (
            0.5 * similarity_score +
            0.3 * coverage_score +
            0.2 * (1.0 - vagueness_penalty)
        )

        confidence = max(0.0, min(1.0, confidence))

        return {
            "confidence_score": confidence,
            "flags": {
                "low_similarity": similarity_score < self._min_similarity_threshold,
                "vague_answer": vagueness_penalty > 0.5
            }
        }

    def _ComputeSimilarityScore(self, docs: List[RetrievalResult]) -> float:
        if not docs:
            return 0.0

        scores = [doc.score for doc in docs]
        return sum(scores) / len(scores)

    def _DetectVagueness(self, answer: str) -> float:
        answer_lower = answer.lower()

        hits = sum(1 for phrase in self._vague_indicators if phrase in answer_lower)

        return min(1.0, hits / len(self._vague_indicators))

    def _EstimateCoverage(
        self,
        answer: str,
        docs: List[RetrievalResult]
    ) -> float:

        if not docs or not answer:
            return 0.0

        answer_tokens = set(answer.lower().split())
        context_tokens = set()

        for doc in docs:
            context_tokens.update(doc.text.lower().split())

        overlap = answer_tokens.intersection(context_tokens)

        if not answer_tokens:
            return 0.0

        return len(overlap) / len(answer_tokens)