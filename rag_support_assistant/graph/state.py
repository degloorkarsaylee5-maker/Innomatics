from typing import TypedDict, List, Dict, Any, Annotated
import operator


def _replace(existing, new):
    """Reducer that replaces the old value with the new one."""
    return new


class GraphState(TypedDict, total=False):
    # Input
    query: str

    # Retrieval — list of dicts with chunk_id, text, score, metadata
    retrieved_docs: Annotated[List[Dict[str, Any]], _replace]

    # Generation
    answer: str
    sources: Annotated[List[Dict[str, Any]], _replace]

    # Evaluation
    confidence_score: float
    evaluation_flags: Annotated[Dict[str, bool], _replace]

    # Routing / Control
    intent: str
    decision: str
    escalation_flag: bool
    reason: str