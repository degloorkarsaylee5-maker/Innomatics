from langgraph.graph import StateGraph, END

from graph.state import GraphState
from graph.nodes import GraphNodes
from graph.edges import GraphEdges
from vector_store.retriever import Retriever


class SupportWorkflow:
    def __init__(self, retriever: Retriever) -> None:
        self._nodes = GraphNodes(retriever)

    def Build(self):
        graph = StateGraph(GraphState)

        # Register nodes
        graph.add_node("input", self._nodes.InputNode)
        graph.add_node("retrieve", self._nodes.RetrievalNode)
        graph.add_node("process", self._nodes.ProcessingNode)
        graph.add_node("decide", self._nodes.DecisionNode)
        graph.add_node("hitl", self._nodes.HitlNode)
        graph.add_node("output", self._nodes.OutputNode)

        # Entry
        graph.set_entry_point("input")

        # Edges
        graph.add_conditional_edges(
            "input",
            lambda state: (
                "retrieve" if GraphEdges.ShouldRetrieve(state)
                else "process"
            )
        )

        graph.add_edge("retrieve", "process")
        graph.add_edge("process", "decide")

        graph.add_conditional_edges(
            "decide",
            lambda state: (
                "hitl" if GraphEdges.ShouldEscalate(state)
                else "output" if GraphEdges.ShouldAnswer(state)
                else "output" if GraphEdges.ShouldClarify(state)
                else "output"
            )
        )

        graph.add_edge("hitl", "output")
        graph.add_edge("output", END)

        return graph.compile()