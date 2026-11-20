"""
M6A.6: Secure Key Handling.
In-memory by default.
Optional persistent storage at %LOCALAPPDATA%\\StitchLabAI\\key.json (outside git repo).
Never logs or prints API keys.
"""

import os
import json
from pathlib import Path
from typing import Optional, Dict

# In-memory storage (default)
_IN_MEMORY_KEYS: Dict[str, str] = {}


def get_external_key_file_path() -> Path:
    """Returns the external persistent key storage path in %LOCALAPPDATA%."""
    local_app_data = os.environ.get("LOCALAPPDATA")
    if local_app_data:
        base_dir = Path(local_app_data)
    else:
        base_dir = Path.home() / "AppData" / "Local"

    target_dir = base_dir / "StitchLabAI"
    target_dir.mkdir(parents=True, exist_ok=True)
    return target_dir / "key.json"


def set_key(provider: str, key: str, persist_to_disk: bool = False):
    """
    Stores an API key for the specified provider.
    If persist_to_disk is False, stored in memory only.
    If persist_to_disk is True, saved to %LOCALAPPDATA%\\StitchLabAI\\key.json.
    """
    provider_key = provider.lower().strip()
    _IN_MEMORY_KEYS[provider_key] = key

    if persist_to_disk:
        key_file = get_external_key_file_path()
        existing = {}
        if key_file.exists():
            try:
                existing = json.loads(key_file.read_text(encoding="utf-8"))
            except Exception:
                existing = {}
        existing[provider_key] = key
        key_file.write_text(json.dumps(existing, indent=2), encoding="utf-8")


def get_key(provider: str, check_disk: bool = True) -> Optional[str]:
    """
    Retrieves API key for the provider.
    Checks memory first, then disk if check_disk is True.
    """
    provider_key = provider.lower().strip()
    if provider_key in _IN_MEMORY_KEYS:
        return _IN_MEMORY_KEYS[provider_key]

    if check_disk:
        key_file = get_external_key_file_path()
        if key_file.exists():
            try:
                data = json.loads(key_file.read_text(encoding="utf-8"))
                return data.get(provider_key)
            except Exception:
                return None
    return None


def clear_keys(clear_disk: bool = False):
    """Clears in-memory keys and optionally removes keys from disk."""
    _IN_MEMORY_KEYS.clear()
    if clear_disk:
        key_file = get_external_key_file_path()
        if key_file.exists():
            try:
                key_file.unlink()
            except Exception:
                pass
