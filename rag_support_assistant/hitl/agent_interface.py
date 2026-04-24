from typing import Dict, Any

from utils.logger import GetLogger


class AgentInterface:
    def __init__(self) -> None:
        self._logger = GetLogger(self.__class__.__name__)

    def HandleEscalation(self, payload: Dict[str, Any]) -> str:
        """
        CLI-based human-in-the-loop interface.
        Displays context and allows agent to provide final answer.
        """

        print("\n========== ESCALATION ==========")
        print(f"Query: {payload['query']}")
        print(f"Confidence: {payload['confidence_score']:.2f}")
        print(f"Reason: {payload['reason']}\n")

        print("---- Retrieved Context ----")
        for i, doc in enumerate(payload["retrieved_docs"][:5]):
            print(f"[{i+1}] (Score: {doc['score']:.2f})")
            print(doc["text"][:300])
            print("-----")

        print("\n---- Draft Answer ----")
        print(payload["draft_answer"])
        print("------------------------------")

        print("\nEnter final answer (or press Enter to accept draft):")
        human_input = input("> ").strip()

        final_answer = human_input if human_input else payload["draft_answer"]

        self._logger.info(
            "Human response captured",
            extra={"used_draft": human_input == ""}
        )

        return final_answer