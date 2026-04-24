import json
import os
from typing import Dict, Any, List
from datetime import datetime

from utils.logger import GetLogger


class FeedbackHandler:
    def __init__(self, storage_path: str = "feedback_store.json") -> None:
        self._storage_path: str = storage_path
        self._logger = GetLogger(self.__class__.__name__)

        if not os.path.exists(self._storage_path):
            with open(self._storage_path, "w") as f:
                json.dump([], f)

    def StoreFeedback(
        self,
        query: str,
        original_answer: str,
        corrected_answer: str,
        metadata: Dict[str, Any]
    ) -> None:
        """
        Store feedback for future improvements.
        """

        record: Dict[str, Any] = {
            "timestamp": datetime.utcnow().isoformat(),
            "query": query,
            "original_answer": original_answer,
            "corrected_answer": corrected_answer,
            "metadata": metadata
        }

        try:
            data: List[Dict[str, Any]] = self._LoadAll()
            data.append(record)

            with open(self._storage_path, "w") as f:
                json.dump(data, f, indent=2)

            self._logger.info("Feedback stored successfully")

        except Exception as ex:
            self._logger.error("Failed to store feedback", exc_info=True)
            raise RuntimeError("Feedback storage failed") from ex

    def _LoadAll(self) -> List[Dict[str, Any]]:
        try:
            with open(self._storage_path, "r") as f:
                return json.load(f)
        except Exception:
            return []

    def GetAllFeedback(self) -> List[Dict[str, Any]]:
        return self._LoadAll()

    def ExportForTraining(self) -> List[Dict[str, str]]:
        """
        Prepare dataset for fine-tuning or prompt improvement.
        """
        records = self._LoadAll()

        dataset: List[Dict[str, str]] = []

        for record in records:
            dataset.append({
                "input": record["query"],
                "output": record["corrected_answer"]
            })

        return dataset