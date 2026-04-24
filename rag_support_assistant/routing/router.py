from typing import Dict, Any

from routing.intent_classifier import IntentType


class RouterDecision:
    def __init__(
        self,
        action: str,
        reason: str
    ) -> None:
        self.action: str = action
        self.reason: str = reason


class Router:
    def __init__(self) -> None:
        self._low_confidence_threshold: float = 0.5
        self._high_confidence_threshold: float = 0.75

    def Route(
        self,
        intent: IntentType,
        confidence_score: float,
        evaluation_flags: Dict[str, bool]
    ) -> RouterDecision:

        # Immediate escalation cases
        if intent == "escalation":
            return RouterDecision(
                action="ESCALATE",
                reason="User explicitly requested escalation or sensitive topic detected"
            )

        # Ambiguous query → ask clarification
        if intent == "ambiguous":
            return RouterDecision(
                action="CLARIFY",
                reason="Query lacks sufficient detail"
            )

        # Low confidence → escalate
        if confidence_score < self._low_confidence_threshold:
            return RouterDecision(
                action="ESCALATE",
                reason=f"Low confidence score: {confidence_score:.2f}"
            )

        # Evaluation flags override
        if evaluation_flags.get("low_similarity", False):
            return RouterDecision(
                action="ESCALATE",
                reason="Low retrieval similarity"
            )

        if evaluation_flags.get("vague_answer", False):
            return RouterDecision(
                action="CLARIFY",
                reason="Generated answer is vague"
            )

        # High confidence → direct answer
        if confidence_score >= self._high_confidence_threshold:
            return RouterDecision(
                action="ANSWER",
                reason=f"High confidence score: {confidence_score:.2f}"
            )

        # Medium confidence → safe fallback (clarify)
        return RouterDecision(
            action="CLARIFY",
            reason="Moderate confidence, safer to clarify user intent"
        )