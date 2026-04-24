import sqlite3
from typing import List, Dict, Any
from datetime import datetime


class FeedbackStore:
    def __init__(self, db_path: str = "feedback.db") -> None:
        self._db_path: str = db_path
        self._Initialize()

    def _GetConnection(self) -> sqlite3.Connection:
        return sqlite3.connect(self._db_path)

    def _Initialize(self) -> None:
        with self._GetConnection() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS feedback (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    query TEXT NOT NULL,
                    original_answer TEXT NOT NULL,
                    corrected_answer TEXT NOT NULL,
                    metadata TEXT,
                    timestamp TEXT NOT NULL
                )
            """)
            conn.commit()

    def AddFeedback(
        self,
        query: str,
        original_answer: str,
        corrected_answer: str,
        metadata: str = ""
    ) -> None:
        timestamp = datetime.utcnow().isoformat()

        with self._GetConnection() as conn:
            conn.execute("""
                INSERT INTO feedback (query, original_answer, corrected_answer, metadata, timestamp)
                VALUES (?, ?, ?, ?, ?)
            """, (query, original_answer, corrected_answer, metadata, timestamp))
            conn.commit()

    def GetAllFeedback(self) -> List[Dict[str, Any]]:
        with self._GetConnection() as conn:
            cursor = conn.execute("""
                SELECT query, original_answer, corrected_answer, metadata, timestamp
                FROM feedback
                ORDER BY id DESC
            """)

            rows = cursor.fetchall()

        return [
            {
                "query": row[0],
                "original_answer": row[1],
                "corrected_answer": row[2],
                "metadata": row[3],
                "timestamp": row[4]
            }
            for row in rows
        ]

    def ExportForTraining(self) -> List[Dict[str, str]]:
        records = self.GetAllFeedback()

        return [
            {
                "input": record["query"],
                "output": record["corrected_answer"]
            }
            for record in records
        ]