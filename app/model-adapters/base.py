"""
M6A.1: Unified Provider Adapter Interface.
Defines base interface and stub adapter for model providers.
Unified entry point: get_answer(question, passages, provider, key, model, **kwargs)
"""

import sys
from abc import ABC, abstractmethod
from pathlib import Path
from typing import List, Dict, Any, Optional

# Paths
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import paths

from app.citations.answer import SYSTEM_PROMPT, format_context


class BaseModelAdapter(ABC):
    """Abstract base class for all LLM provider adapters."""

    @abstractmethod
    def generate(
        self,
        question: str,
        passages: List[Dict[str, Any]],
        model: Optional[str] = None,
        api_key: Optional[str] = None,
        **kwargs,
    ) -> str:
        """Generates an evidence-grounded answer from question and passages."""
        pass


class StubAdapter(BaseModelAdapter):
    """Deterministic stub adapter for local testing without network/hardware."""

    def __init__(self, stub_response: Optional[str] = None):
        self.stub_response = stub_response

    def generate(
        self,
        question: str,
        passages: List[Dict[str, Any]],
        model: Optional[str] = None,
        api_key: Optional[str] = None,
        **kwargs,
    ) -> str:
        if self.stub_response:
            return self.stub_response
        if not passages:
            return "Not found in your documents."
        first_cit = passages[0].get("citation", "[D01, 1]")
        return f"According to {first_cit}, the answer for '{question}' is verified."


# Registry of provider adapters
_ADAPTER_REGISTRY: Dict[str, BaseModelAdapter] = {
    "stub": StubAdapter(),
}


def register_adapter(name: str, adapter: BaseModelAdapter):
    """Registers a new provider adapter."""
    _ADAPTER_REGISTRY[name.lower()] = adapter


def get_adapter(provider: str) -> BaseModelAdapter:
    """Retrieves registered adapter by name."""
    provider_key = provider.lower()
    if provider_key not in _ADAPTER_REGISTRY:
        raise ValueError(
            f"Unsupported provider: '{provider}'. Available: {list(_ADAPTER_REGISTRY.keys())}"
        )
    return _ADAPTER_REGISTRY[provider_key]


def get_answer(
    question: str,
    passages: List[Dict[str, Any]],
    provider: str = "stub",
    key: Optional[str] = None,
    model: Optional[str] = None,
    **kwargs,
) -> str:
    """Unified entry point for answer generation across providers."""
    adapter = get_adapter(provider)
    return adapter.generate(
        question=question,
        passages=passages,
        model=model,
        api_key=key,
        **kwargs,
    )
