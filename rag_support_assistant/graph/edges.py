from typing import Dict, Any

from graph.state import GraphState


class GraphEdges:
    @staticmethod
    def ShouldRetrieve(state: GraphState) -> bool:
        return state.get("intent") == "factual"

    @staticmethod
    def ShouldSkipRetrieval(state: GraphState) -> bool:
        return state.get("intent") != "factual"

    @staticmethod
    def ShouldEscalate(state: GraphState) -> bool:
        return state.get("escalation_flag", False)

    @staticmethod
    def ShouldAnswer(state: GraphState) -> bool:
        return not state.get("escalation_flag", False) and state.get("decision") == "ANSWER"

    @staticmethod
    def ShouldClarify(state: GraphState) -> bool:
        return state.get("decision") == "CLARIFY"