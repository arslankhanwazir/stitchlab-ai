"""
M6A.5: Provider Connection Health Checker.
Runs a test call on provider, model, or key change.
Handles and categorizes:
- Connected ("Connected")
- Invalid key (HTTP 401/403 -> INVALID_KEY)
- Credit / quota exhausted (HTTP 429 -> NO_CREDIT / QUOTA_EXCEEDED)
- Model not found (HTTP 404 -> MODEL_NOT_FOUND)
- Network blocked (NetGuard rejection / connection timeout -> NETWORK_BLOCKED / NETWORK_ERROR)
"""

import os
import sys
import urllib.parse
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
    ModelNotFoundError,
    NetworkBlockedError,
    DEFAULT_GEMINI_URL,
    DEFAULT_OPENAI_URL,
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
            "message": "Connected",
        }

    elif "ollama" in provider_key:
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

    elif "gemini" in provider_key:
        target_base = base_url or DEFAULT_GEMINI_URL
        key = api_key or os.environ.get("GEMINI_API_KEY")
        if not key:
            return {
                "success": False,
                "status": "INVALID_KEY",
                "message": "Invalid key: GEMINI_API_KEY environment variable is not set.",
            }
        if not model or not model.strip():
            return {
                "success": False,
                "status": "MODEL_NOT_FOUND",
                "message": "Model not found: please enter a model name (use a model your key can access).",
            }

        adapter = OpenAIAdapter(base_url=target_base, is_gemini=True)
        test_passages = [
            {"doc_id": "TEST", "section_id": "1", "citation": "[TEST, 1]", "text": "Health check."}
        ]
        try:
            adapter.generate(
                question="ping",
                passages=test_passages,
                model=model.strip(),
                api_key=key,
                timeout=5.0,
            )
            return {
                "success": True,
                "status": "CONNECTED",
                "message": "Connected",
            }
        except AuthenticationError as ae:
            return {
                "success": False,
                "status": "INVALID_KEY",
                "message": f"Invalid key: {ae}",
            }
        except QuotaExceededError as qe:
            return {
                "success": False,
                "status": "NO_CREDIT",
                "message": f"No credit: {qe}",
            }
        except ModelNotFoundError as mne:
            return {
                "success": False,
                "status": "MODEL_NOT_FOUND",
                "message": f"Model not found: {mne}",
            }
        except (NetworkBlockedError, PermissionError) as nbe:
            return {
                "success": False,
                "status": "NETWORK_BLOCKED",
                "message": f"Network blocked: {nbe}",
            }
        except ConnectionError as ce:
            return {
                "success": False,
                "status": "NETWORK_BLOCKED",
                "message": f"Network blocked or unreachable: {ce}",
            }
        except Exception as e:
            return {
                "success": False,
                "status": "ERROR",
                "message": f"Connection error: {e}",
            }

    elif "openai" in provider_key:
        target_base = base_url or DEFAULT_OPENAI_URL
        adapter = OpenAIAdapter(base_url=target_base, is_gemini=False)
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
