import sqlite3
from typing import List, Dict, Any, Optional
from datetime import datetime
import json


class MetadataStore:
    def __init__(self, db_path: str = "metadata.db") -> None:
        self._db_path: str = db_path
        self._Initialize()

    def _GetConnection(self) -> sqlite3.Connection:
        return sqlite3.connect(self._db_path)

    def _Initialize(self) -> None:
        with self._GetConnection() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS documents (
                    document_id TEXT PRIMARY KEY,
                    title TEXT,
                    source_path TEXT,
                    metadata TEXT,
                    created_at TEXT
                )
            """)
            conn.commit()

    def AddDocument(
        self,
        document_id: str,
        title: str,
        source_path: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        created_at = datetime.utcnow().isoformat()
        metadata_json = json.dumps(metadata or {})

        with self._GetConnection() as conn:
            conn.execute("""
                INSERT OR REPLACE INTO documents (document_id, title, source_path, metadata, created_at)
                VALUES (?, ?, ?, ?, ?)
            """, (document_id, title, source_path, metadata_json, created_at))
            conn.commit()

    def GetDocument(self, document_id: str) -> Optional[Dict[str, Any]]:
        with self._GetConnection() as conn:
            cursor = conn.execute("""
                SELECT document_id, title, source_path, metadata, created_at
                FROM documents
                WHERE document_id = ?
            """, (document_id,))

            row = cursor.fetchone()

        if not row:
            return None

        return {
            "document_id": row[0],
            "title": row[1],
            "source_path": row[2],
            "metadata": json.loads(row[3]),
            "created_at": row[4]
        }

    def ListDocuments(self) -> List[Dict[str, Any]]:
        with self._GetConnection() as conn:
            cursor = conn.execute("""
                SELECT document_id, title, source_path, metadata, created_at
                FROM documents
                ORDER BY created_at DESC
            """)

            rows = cursor.fetchall()

        return [
            {
                "document_id": row[0],
                "title": row[1],
                "source_path": row[2],
                "metadata": json.loads(row[3]),
                "created_at": row[4]
            }
            for row in rows
        ]

    def DeleteDocument(self, document_id: str) -> None:
        with self._GetConnection() as conn:
            conn.execute("""
                DELETE FROM documents WHERE document_id = ?
            """, (document_id,))
            conn.commit()