"""
M6A.2: Ollama Local Adapter.
Detects if Ollama is running, lists installed models, and sends prompts.
"""

import sys
import json
import urllib.request
import urllib.error
from pathlib import Path
from typing import List, Dict, Any, Optional

# Paths
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import paths

from base import BaseModelAdapter, register_adapter
from app.citations.answer import generate_answer

DEFAULT_OLLAMA_URL = "http://127.0.0.1:11434"
DEFAULT_MODEL = "llama3.2:3b"


def is_ollama_running(base_url: str = DEFAULT_OLLAMA_URL, timeout: float = 2.0) -> bool:
    """Checks if the local Ollama server is responsive."""
    try:
        req = urllib.request.Request(f"{base_url.rstrip('/')}/", method="GET")
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.status == 200
    except Exception:
        return False


def list_installed_models(base_url: str = DEFAULT_OLLAMA_URL, timeout: float = 5.0) -> List[str]:
    """Retrieves list of locally installed model names from Ollama."""
    try:
        req = urllib.request.Request(f"{base_url.rstrip('/')}/api/tags", method="GET")
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            models = [m.get("name", "") for m in data.get("models", []) if "name" in m]
            return models
    except Exception as e:
        return []


class OllamaAdapter(BaseModelAdapter):
    """Adapter for local Ollama instance."""

    def __init__(self, base_url: str = DEFAULT_OLLAMA_URL):
        self.base_url = base_url

    def generate(
        self,
        question: str,
        passages: List[Dict[str, Any]],
        model: Optional[str] = None,
        api_key: Optional[str] = None,
        **kwargs,
    ) -> str:
        target_model = model or DEFAULT_MODEL
        chat_url = f"{self.base_url.rstrip('/')}/api/chat"
        return generate_answer(
            question=question,
            passages=passages,
            model=target_model,
            api_url=chat_url,
            **kwargs,
        )


# Register singleton instance
register_adapter("ollama", OllamaAdapter())
