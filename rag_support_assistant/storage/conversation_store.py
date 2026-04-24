import sqlite3
from typing import List, Dict, Any, Optional
from datetime import datetime


class ConversationStore:
    def __init__(self, db_path: str = "conversations.db") -> None:
        self._db_path: str = db_path
        self._Initialize()

    def _GetConnection(self) -> sqlite3.Connection:
        return sqlite3.connect(self._db_path)

    def _Initialize(self) -> None:
        with self._GetConnection() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS conversations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT NOT NULL,
                    user_id TEXT NOT NULL,
                    query TEXT NOT NULL,
                    response TEXT NOT NULL,
                    timestamp TEXT NOT NULL
                )
            """)
            conn.commit()

    def AddMessage(
        self,
        session_id: str,
        user_id: str,
        query: str,
        response: str
    ) -> None:
        timestamp = datetime.utcnow().isoformat()

        with self._GetConnection() as conn:
            conn.execute("""
                INSERT INTO conversations (session_id, user_id, query, response, timestamp)
                VALUES (?, ?, ?, ?, ?)
            """, (session_id, user_id, query, response, timestamp))
            conn.commit()

    def GetSessionHistory(self, session_id: str, limit: int = 20) -> List[Dict[str, Any]]:
        with self._GetConnection() as conn:
            cursor = conn.execute("""
                SELECT query, response, timestamp
                FROM conversations
                WHERE session_id = ?
                ORDER BY id DESC
                LIMIT ?
            """, (session_id, limit))

            rows = cursor.fetchall()

        return [
            {
                "query": row[0],
                "response": row[1],
                "timestamp": row[2]
            }
            for row in reversed(rows)
        ]

    def ClearSession(self, session_id: str) -> None:
        with self._GetConnection() as conn:
            conn.execute("""
                DELETE FROM conversations
                WHERE session_id = ?
            """, (session_id,))
            conn.commit()