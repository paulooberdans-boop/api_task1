import logging
import os
from collections.abc import Callable
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FutureTimeoutError
from enum import Enum


logger = logging.getLogger(__name__)


class TaskPriority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


LLMClient = Callable[[str], object]


class PriorityAdvisor:
    """Suggest task priority without making the core API depend on an LLM."""

    def __init__(
        self,
        llm_client: LLMClient | None = None,
        api_key: str | None = None,
        timeout_seconds: float | None = None,
    ):
        self.llm_client = llm_client
        self.api_key = api_key or os.getenv("PRIORITY_LLM_API_KEY")
        configured_timeout = os.getenv("PRIORITY_LLM_TIMEOUT_SECONDS", "2.0")
        self.timeout_seconds = (
            timeout_seconds if timeout_seconds is not None else float(configured_timeout)
        )
        if self.timeout_seconds <= 0:
            raise ValueError("timeout_seconds must be greater than zero")

    def suggest_priority(self, text: str) -> TaskPriority:
        """Return an LLM suggestion when safe, otherwise use local rules."""
        local_priority = self.heuristic_priority(text)
        if self.llm_client is None or self.api_key is None:
            return local_priority

        try:
            response = self._call_llm(text)
            validated = self._validate_response(response)
            return validated or local_priority
        except Exception:
            logger.warning("Priority provider unavailable; using local heuristic")
            return local_priority

    @staticmethod
    def heuristic_priority(text: str) -> TaskPriority:
        """Classify priority deterministically without external services."""
        normalized = text.casefold()
        high_terms = ("urgente", "urgent", "crítico", "critico", "critical")
        medium_terms = (
            "importante",
            "important",
            "prazo",
            "deadline",
            "impacto alto",
        )
        if any(term in normalized for term in high_terms):
            return TaskPriority.HIGH
        if any(term in normalized for term in medium_terms):
            return TaskPriority.MEDIUM
        return TaskPriority.LOW

    def _call_llm(self, text: str) -> object:
        executor = ThreadPoolExecutor(max_workers=1)
        future = executor.submit(self.llm_client, text)
        try:
            return future.result(timeout=self.timeout_seconds)
        finally:
            future.cancel()
            executor.shutdown(wait=False, cancel_futures=True)

    @staticmethod
    def _validate_response(response: object) -> TaskPriority | None:
        candidate = response
        if isinstance(response, dict):
            candidate = response.get("priority")
        if not isinstance(candidate, str):
            return None
        try:
            return TaskPriority(candidate.strip().casefold())
        except ValueError:
            return None