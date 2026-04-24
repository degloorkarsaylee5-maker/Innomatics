import os
from typing import Optional

import chromadb
from chromadb.api.models.Collection import Collection

from utils.config import GetSettings
from utils.logger import GetLogger


class ChromaClient:
    def __init__(self, collection_name: str) -> None:
        self._logger = GetLogger(self.__class__.__name__)
        self._settings = GetSettings()

        self._persist_path: str = self._settings.chroma_path
        self._collection_name: str = collection_name

        self._client = self._InitializeClient()
        self._collection: Collection = self._GetOrCreateCollection()

    def _InitializeClient(self) -> chromadb.ClientAPI:
        try:
            os.makedirs(self._persist_path, exist_ok=True)

            # Use PersistentClient (correct API for chromadb >= 0.4.0)
            client = chromadb.PersistentClient(path=self._persist_path)

            self._logger.info("ChromaDB client initialized", extra={
                "persist_path": self._persist_path
            })

            return client

        except Exception as ex:
            self._logger.error("Failed to initialize ChromaDB", exc_info=True)
            raise RuntimeError("ChromaDB initialization failed") from ex

    def _GetOrCreateCollection(self) -> Collection:
        try:
            collection = self._client.get_or_create_collection(
                name=self._collection_name,
                metadata={"hnsw:space": "cosine"}
            )

            self._logger.info("Collection ready", extra={
                "collection_name": self._collection_name
            })

            return collection

        except Exception as ex:
            self._logger.error("Failed to get/create collection", exc_info=True)
            raise RuntimeError("Collection initialization failed") from ex

    def GetCollection(self) -> Collection:
        return self._collection

    def Persist(self) -> None:
        # ChromaDB >= 0.4.0 with PersistentClient handles persistence automatically
        self._logger.debug("ChromaDB persistence (automatic)")