"""
M6B.3: Outbound Network Guard.
Enforces strict host/port allowlisting for all outgoing HTTP/HTTPS connections.
- Allows 127.0.0.1:11434 (local Ollama)
- Allows active approved provider host (e.g. api.openai.com)
- Blocks all arbitrary URLs (e.g. evil.com)
- Blocks loopback connections on unauthorized ports (e.g. 127.0.0.1:9999)
"""

import urllib.parse
from typing import Optional

ALLOWED_LOCAL_HOSTS = {"127.0.0.1", "localhost"}
ALLOWED_OLLAMA_PORT = 11434


def is_url_allowed(url: str, active_provider_host: Optional[str] = None) -> bool:
    """
    Evaluates whether the destination URL is permitted by NetGuard policy.
    """
    try:
        parsed = urllib.parse.urlparse(url)
        hostname = (parsed.hostname or "").lower()
        port = parsed.port

        # 1. Check local Ollama service (127.0.0.1:11434 or localhost:11434)
        if hostname in ALLOWED_LOCAL_HOSTS:
            effective_port = port if port is not None else (80 if parsed.scheme == "http" else 443)
            return effective_port == ALLOWED_OLLAMA_PORT

        # 2. Check active provider host (e.g. api.openai.com)
        if active_provider_host:
            clean_provider_host = active_provider_host.lower().strip()
            # If provider host specifies a port, compare against netloc, else compare hostname
            if ":" in clean_provider_host:
                if parsed.netloc.lower() == clean_provider_host:
                    return True
            else:
                if hostname == clean_provider_host:
                    return True

        # Everything else is blocked
        return False

    except Exception:
        return False


def validate_outbound_url(url: str, active_provider_host: Optional[str] = None) -> None:
    """
    Validates URL against policy; raises PermissionError if blocked.
    """
    if not is_url_allowed(url, active_provider_host=active_provider_host):
        raise PermissionError(
            f"Security Policy Violation: Outbound request to '{url}' blocked by NetGuard. "
            f"Only 127.0.0.1:11434 and active provider host are permitted."
        )
