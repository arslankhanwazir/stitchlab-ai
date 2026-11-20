"""
M6A.5: Provider Connection Health Checker.
Runs a test call on provider or key change.
Handles and categorizes:
- Invalid key (HTTP 401)
- Credit / quota exhausted (HTTP 429)
- Network unreachable (DNS/timeout/connection refused)
"""

import sys
from pathlib import Path
from typing import Dict, Any, Optional

# Paths
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import paths

from base import get_adapter
from ollama_adapter import is_ollama_running
from openai_adapter import (
    OpenAIAdapter,
    AuthenticationError,
    QuotaExceededError,
)


def test_provider_connection(
    provider: str,
    api_key: Optional[str] = None,
    model: Optional[str] = None,
    base_url: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Executes a health test against the chosen provider.
    Returns:
        dict: {"success": bool, "status": str, "message": str}
    """
    provider_key = provider.lower().strip()

    if provider_key == "stub":
        return {
            "success": True,
            "status": "CONNECTED",
            "message": "Stub adapter connected successfully.",
        }

    elif provider_key == "ollama":
        target_url = base_url or "http://127.0.0.1:11434"
        if not is_ollama_running(target_url, timeout=2.0):
            return {
                "success": False,
                "status": "NETWORK_ERROR",
                "message": f"Ollama is not running at {target_url}.",
            }
        return {
            "success": True,
            "status": "CONNECTED",
            "message": f"Connected to local Ollama at {target_url}.",
        }

    elif provider_key == "openai":
        adapter = OpenAIAdapter(base_url=base_url) if base_url else OpenAIAdapter()
        test_passages = [
            {"doc_id": "TEST", "section_id": "1", "citation": "[TEST, 1]", "text": "Health check."}
        ]
        try:
            adapter.generate(
                question="ping",
                passages=test_passages,
                model=model,
                api_key=api_key,
                timeout=5.0,
            )
            return {
                "success": True,
                "status": "CONNECTED",
                "message": "Connected to OpenAI provider successfully.",
            }
        except AuthenticationError as ae:
            return {
                "success": False,
                "status": "INVALID_KEY",
                "message": str(ae),
            }
        except QuotaExceededError as qe:
            return {
                "success": False,
                "status": "QUOTA_EXCEEDED",
                "message": str(qe),
            }
        except ConnectionError as ce:
            return {
                "success": False,
                "status": "NETWORK_ERROR",
                "message": str(ce),
            }
        except Exception as e:
            return {
                "success": False,
                "status": "ERROR",
                "message": f"Unexpected error during connection test: {e}",
            }

    else:
        return {
            "success": False,
            "status": "UNSUPPORTED_PROVIDER",
            "message": f"Unknown provider: {provider}",
        }
