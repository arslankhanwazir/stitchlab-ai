"""
M6A.4: OpenAI-compatible Paid API Adapter.
Supports OpenAI and Google Gemini (via Gemini's OpenAI-compatible endpoint).
Uses standard library urllib (no external SDK).
Connects to:
- OpenAI: https://api.openai.com/v1/chat/completions
- Google Gemini: https://generativelanguage.googleapis.com/v1beta/openai/chat/completions
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
from app.citations.answer import SYSTEM_PROMPT, format_context

DEFAULT_OPENAI_URL = "https://api.openai.com/v1"
DEFAULT_OPENAI_MODEL = "gpt-4o-mini"
DEFAULT_GEMINI_URL = "https://generativelanguage.googleapis.com/v1beta/openai"


class AuthenticationError(Exception):
    """Raised when the API key is rejected or invalid (HTTP 401 or 403)."""
    pass


class QuotaExceededError(Exception):
    """Raised when account balance or rate limit is exhausted (HTTP 429)."""
    pass


class ModelNotFoundError(Exception):
    """Raised when the specified model is not found (HTTP 404)."""
    pass


class NetworkBlockedError(Exception):
    """Raised when outbound request is blocked by NetGuard or network policy."""
    pass


class OpenAIAdapter(BaseModelAdapter):
    """OpenAI-compatible HTTP chat completions adapter using stdlib urllib."""

    def __init__(self, base_url: str = DEFAULT_OPENAI_URL, is_gemini: bool = False):
        self.base_url = base_url.rstrip("/")
        self.is_gemini = is_gemini or ("googleapis.com" in self.base_url)

    def generate(
        self,
        question: str,
        passages: List[Dict[str, Any]],
        model: Optional[str] = None,
        api_key: Optional[str] = None,
        timeout: float = 30.0,
        **kwargs,
    ) -> str:
        if not api_key:
            raise AuthenticationError("API key is required for paid provider calls.")

        # Gemini model name must be user-provided (do not hardcode)
        if model and model.strip():
            target_model = model.strip()
        elif not self.is_gemini:
            target_model = DEFAULT_OPENAI_MODEL
        else:
            raise ModelNotFoundError("Model name is required (use a model your key can access).")

        endpoint = f"{self.base_url}/chat/completions"

        context_text = format_context(passages)
        user_content = f"Supplied Passages:\n{context_text}\n\nQuestion: {question}\n\nAnswer:"

        payload = {
            "model": target_model,
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_content},
            ],
            "temperature": 0.0,
        }

        req_data = json.dumps(payload).encode("utf-8")
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
            "User-Agent": "StitchLabAI-Client/1.0",
        }

        req = urllib.request.Request(endpoint, data=req_data, headers=headers, method="POST")

        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                choices = data.get("choices", [])
                if not choices:
                    return ""
                return choices[0].get("message", {}).get("content", "").strip()

        except urllib.error.HTTPError as he:
            error_body = he.read().decode("utf-8", errors="ignore")
            if he.code in (401, 403):
                raise AuthenticationError(f"Authentication failed (HTTP {he.code}): Invalid API key.") from he
            elif he.code == 429:
                raise QuotaExceededError(f"Rate limit or quota exceeded (HTTP 429).") from he
            elif he.code == 404:
                raise ModelNotFoundError(f"Model not found (HTTP 404): {error_body}") from he
            elif he.code == 400 and any(k in error_body.lower() for k in ["api_key_invalid", "api key not valid", "invalid api key"]):
                raise AuthenticationError(f"Authentication failed (HTTP 400): Invalid API key.") from he
            else:
                raise RuntimeError(f"API request failed with HTTP {he.code}: {error_body}") from he

        except urllib.error.URLError as ue:
            raise ConnectionError(f"Network unreachable or provider server down: {ue.reason}") from ue


# Register singleton instances in unified adapter registry
register_adapter("openai", OpenAIAdapter(base_url=DEFAULT_OPENAI_URL, is_gemini=False))
register_adapter("gemini", OpenAIAdapter(base_url=DEFAULT_GEMINI_URL, is_gemini=True))
