from typing import Literal
import re


IntentType = Literal["factual", "ambiguous", "escalation"]


class IntentClassifier:
    def __init__(self) -> None:
        self._ambiguous_patterns = [
            r"\b(it|this|that|they|them)\b",
            r"\b(thing|stuff|issue|problem)\b",
            r"^why$",
            r"^how$"
        ]

        self._escalation_keywords = [
            "agent",
            "human",
            "representative",
            "complaint",
            "legal",
            "refund dispute",
            "escalate"
        ]

    def Classify(self, query: str) -> IntentType:
        query_clean = query.strip().lower()

        if self._IsEscalation(query_clean):
            return "escalation"

        if self._IsAmbiguous(query_clean):
            return "ambiguous"

        return "factual"

    def _IsEscalation(self, query: str) -> bool:
        return any(keyword in query for keyword in self._escalation_keywords)

    def _IsAmbiguous(self, query: str) -> bool:
        if len(query.split()) <= 3:
            return True

        for pattern in self._ambiguous_patterns:
            if re.search(pattern, query):
                return True

        return False