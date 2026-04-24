from typing import Dict, Any

from graph.state import GraphState
from utils.logger import GetLogger


class EscalationManager:
    def __init__(self) -> None:
        self._logger = GetLogger(self.__class__.__name__)

    def ShouldEscalate(self, state: GraphState) -> bool:
        """
        Determines whether escalation is required based on graph state.
        """
        if state.escalation_flag:
            self._logger.info(
                "Escalation triggered",
                extra={
                    "reason": state.reason,
                    "confidence_score": state.confidence_score
                }
            )
            return True

        return False

    def BuildEscalationPayload(self, state: GraphState) -> Dict[str, Any]:
        """
        Prepares payload for human agent.
        """
        payload: Dict[str, Any] = {
            "query": state.query,
            "retrieved_docs": [
                {
                    "chunk_id": doc.chunk_id,
                    "text": doc.text,
                    "score": doc.score,
                    "metadata": doc.metadata
                }
                for doc in state.retrieved_docs
            ],
            "draft_answer": state.answer,
            "confidence_score": state.confidence_score,
            "reason": state.reason
        }

        return payload