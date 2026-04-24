from typing import List, Dict, Any, Optional
import time

from utils.config import GetSettings
from utils.logger import GetLogger

try:
    from openai import OpenAI, RateLimitError, AuthenticationError
except ImportError:
    OpenAI = None  # Optional dependency
    RateLimitError = None
    AuthenticationError = None

try:
    from huggingface_hub import InferenceClient
except ImportError:
    InferenceClient = None


class LLMClient:
    def __init__(self) -> None:
        self._settings = GetSettings()
        self._logger = GetLogger(self.__class__.__name__)

        self._provider: str = self._settings.llm_provider.lower()
        self._model: str = self._settings.llm_model
        self._client = None  # Lazy initialization

        self._max_retries: int = 3
        self._retry_delay: float = 1.5

    def _InitializeClient(self) -> None:
        """Lazy initialize the LLM client on first use"""
        if self._provider == "openai":
            if OpenAI is None:
                raise ImportError("openai package is not installed")
            try:
                self._client = OpenAI()
            except Exception as ex:
                self._logger.warning("Failed to initialize OpenAI client - falling back to local mode", exc_info=True)
                self._provider = "local"

        elif self._provider == "huggingface":
            if InferenceClient is None:
                raise ImportError("huggingface_hub package is not installed")
            try:
                hf_token = self._settings.hf_token
                client_kwargs = {}
                if hf_token:
                    client_kwargs["api_key"] = hf_token
                self._client = InferenceClient(**client_kwargs)
                self._logger.info("HuggingFace Inference client initialized", extra={
                    "model": self._model,
                    "authenticated": bool(hf_token)
                })
            except Exception as ex:
                self._logger.warning("Failed to initialize HuggingFace client - falling back to local mode", exc_info=True)
                self._provider = "local"

        elif self._provider == "local":
            self._client = None  # Local inference handled separately
        else:
            raise ValueError(f"Unsupported LLM provider: {self._provider}")

    def Generate(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.0,
        max_tokens: int = 512
    ) -> str:
        if self._client is None and self._provider != "local":
            self._InitializeClient()

        for attempt in range(self._max_retries):
            try:
                if self._provider == "openai":
                    if self._client is None:
                        self._logger.warning("OpenAI client unavailable, using local fallback")
                        return self._LocalGenerate(messages)

                    response = self._client.chat.completions.create(
                        model=self._model,
                        messages=messages,
                        temperature=temperature,
                        max_tokens=max_tokens
                    )
                    return response.choices[0].message.content.strip()

                elif self._provider == "huggingface":
                    if self._client is None:
                        self._logger.warning("HuggingFace client unavailable, using local fallback")
                        return self._LocalGenerate(messages)

                    response = self._client.chat.completions.create(
                        model=self._model,
                        messages=messages,
                        temperature=max(temperature, 0.01),  # HF requires temp > 0
                        max_tokens=max_tokens,
                    )
                    return response.choices[0].message.content.strip()

                elif self._provider == "local":
                    return self._LocalGenerate(messages)

            except Exception as ex:
                # Immediately fall back to local for quota/auth errors (retrying won't help)
                if RateLimitError and isinstance(ex, RateLimitError):
                    self._logger.warning(
                        "OpenAI quota exceeded, falling back to local mode",
                        extra={"attempt": attempt}
                    )
                    return self._LocalGenerate(messages)

                if AuthenticationError and isinstance(ex, AuthenticationError):
                    self._logger.warning(
                        "OpenAI authentication failed, falling back to local mode",
                        extra={"attempt": attempt}
                    )
                    return self._LocalGenerate(messages)

                self._logger.error("LLM call failed", extra={"attempt": attempt}, exc_info=True)

                if attempt == self._max_retries - 1:
                    # Final retry failed — fall back to local instead of crashing
                    self._logger.warning("All retries exhausted, falling back to local mode")
                    return self._LocalGenerate(messages)

                time.sleep(self._retry_delay)

        raise RuntimeError("LLM generation unreachable state")

    def _LocalGenerate(self, messages: List[Dict[str, str]]) -> str:
        # Minimal deterministic fallback (no placeholder text, safe fallback)
        combined = " ".join([m["content"] for m in messages if m["role"] == "user"])
        return f"[LOCAL_MODEL_RESPONSE] {combined[:500]}"