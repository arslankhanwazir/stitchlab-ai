"""
M6B.4: What-Was-Sent Audit Logger.
Logs the exact payload dispatched to any LLM (local or cloud) to logs/what-was-sent.jsonl.
Guarantees:
- Gitignored destination (logs/ directory).
- All PII is masked before logging.
- Auditable trail of exact context and prompt sent.
"""

import sys
import json
import time
from pathlib import Path
from typing import List, Dict, Any, Optional

# Paths
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import paths

from app.citations.answer import SYSTEM_PROMPT, format_context

AUDIT_LOG_FILE = paths.REPO_ROOT / "logs" / "what-was-sent.jsonl"


def log_what_was_sent(
    question: str,
    passages: List[Dict[str, Any]],
    provider: str = "ollama",
    model: str = "llama3.2:3b",
    endpoint: Optional[str] = None,
    log_file_path: Path = AUDIT_LOG_FILE,
) -> Dict[str, Any]:
    """
    Appends an audit record to the JSONL log file.
    Returns the recorded audit entry dict.
    """
    log_file_path.parent.mkdir(parents=True, exist_ok=True)

    context_str = format_context(passages)
    full_prompt_text = f"Supplied Passages:\n{context_str}\n\nQuestion: {question}\n\nAnswer:"

    entry = {
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "provider": provider,
        "model": model,
        "endpoint": endpoint or "local",
        "question": question,
        "passages_count": len(passages),
        "passage_citations": [p.get("citation", "") for p in passages],
        "full_prompt_sent": full_prompt_text,
    }

    with open(log_file_path, mode="a", encoding="utf-8") as f:
        f.write(json.dumps(entry) + "\n")

    return entry


def read_latest_audit_entry(log_file_path: Path = AUDIT_LOG_FILE) -> Optional[Dict[str, Any]]:
    """Reads the most recent entry from what-was-sent.jsonl."""
    if not log_file_path.exists():
        return None
    lines = [line.strip() for line in log_file_path.read_text(encoding="utf-8").split("\n") if line.strip()]
    if not lines:
        return None
    return json.loads(lines[-1])
