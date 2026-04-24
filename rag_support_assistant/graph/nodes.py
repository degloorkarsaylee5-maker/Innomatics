from types import SimpleNamespace
from typing import Dict, Any

from graph.state import GraphState
from routing.intent_classifier import IntentClassifier
from routing.confidence_scorer import ConfidenceScorer
from routing.router import Router
from llm.response_generator import ResponseGenerator
from llm.evaluator import Evaluator
from vector_store.retriever import Retriever
from ingestion.embedding_generator import EmbeddingGenerator
from utils.config import GetSettings


class GraphNodes:
    def __init__(self, retriever: Retriever) -> None:
        settings = GetSettings()

        self._intent_classifier = IntentClassifier()
        self._confidence_scorer = ConfidenceScorer()
        self._router = Router()
        self._generator = ResponseGenerator()
        self._evaluator = Evaluator()
        self._retriever = retriever
        self._embedding_model = EmbeddingGenerator(settings.embedding_model)

    # 1. Input Node
    def InputNode(self, state: GraphState) -> Dict[str, Any]:
        intent = self._intent_classifier.Classify(state["query"])
        return {"intent": intent}

    # 2. Retrieval Node
    def RetrievalNode(self, state: GraphState) -> Dict[str, Any]:
        # Create a lightweight object that EmbeddingGenerator.Generate expects
        query_chunk = SimpleNamespace(text=state["query"], chunk_id="query")
        query_embedding = self._embedding_model.Generate([query_chunk])[0].vector

        docs = self._retriever.Retrieve(query_embedding)

        # Convert RetrievalResult objects to plain dicts for state storage
        retrieved = [
            {
                "chunk_id": doc.chunk_id,
                "text": doc.text,
                "score": doc.score,
                "metadata": doc.metadata
            }
            for doc in docs
        ]

        return {"retrieved_docs": retrieved}

    # 3. Processing Node (LLM + Evaluation)
    def ProcessingNode(self, state: GraphState) -> Dict[str, Any]:
        retrieved_docs = state.get("retrieved_docs", [])

        # Convert dicts back to objects that ResponseGenerator/Evaluator expect
        doc_objects = [
            SimpleNamespace(**doc)
            for doc in retrieved_docs
        ]

        response = self._generator.Generate(state["query"], doc_objects)

        answer = response["answer"]
        sources = response["sources"]

        eval_result = self._evaluator.Evaluate(answer, doc_objects)

        confidence_score = self._confidence_scorer.Compute(
            doc_objects,
            eval_result["confidence_score"],
            answer
        )

        return {
            "answer": answer,
            "sources": sources,
            "evaluation_flags": eval_result["flags"],
            "confidence_score": confidence_score
        }

    # 4. Decision Node
    def DecisionNode(self, state: GraphState) -> Dict[str, Any]:
        decision = self._router.Route(
            intent=state.get("intent", ""),
            confidence_score=state.get("confidence_score", 0.0),
            evaluation_flags=state.get("evaluation_flags", {})
        )

        return {
            "decision": decision.action,
            "reason": decision.reason,
            "escalation_flag": decision.action == "ESCALATE"
        }

    # 5. HITL Node
    def HitlNode(self, state: GraphState) -> Dict[str, Any]:
        # In real system: send to human queue
        return {"answer": "[ESCALATED TO HUMAN AGENT]"}

    # 6. Output Node — pass-through, state already contains everything
    def OutputNode(self, state: GraphState) -> Dict[str, Any]:
        return {}