"""
M4.1: Evidence-only answer generation.
Calls Ollama api/chat at http://127.0.0.1:11434 with model llama3.2:3b, temperature 0.
Enforces strict citation rules [DocID, Section] and refusal fallback.
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

OLLAMA_API_URL = "http://127.0.0.1:11434/api/chat"
DEFAULT_MODEL = "llama3.2:3b"
MAX_PASSAGES = 5

SYSTEM_PROMPT = """You are a strictly evidence-based corporate policy assistant for Brightpath Media (demo, fictional).
Answer the user's question accurately using ONLY the provided passages.

Instructions:
1. Base your answer strictly on the facts in the provided passages. Never use outside facts, speculation, or unverified claims.
2. Cite the exact source document and section [DocID, Section] for each fact from the specific passage heading where that fact appears (e.g. [D01, 3], [D05, 1], or [D06, 1]). For facts located in a table (such as tiers, hours, fees, or contact matrices), cite the exact section heading above that table.
3. When asked who to contact or call, state the specific person's name, their role, and their phone number from the passages. If a passage mentions calling a number "above" or in a table, look up and provide the phone number and name from the table with its citation.
4. Keep the answer accurate, factual, concise, and complete according to the passages.
5. If NONE of the supplied passages contain any relevant information to answer the question, respond with:
Not found in your documents.
Do not say "Not found" if any passage contains relevant facts."""


def format_context(passages: List[Dict[str, Any]]) -> str:
    """Formats retrieved passages into a structured context block."""
    if not passages:
        return "No passages provided."

    formatted_parts = []
    for idx, p in enumerate(passages[:MAX_PASSAGES], start=1):
        doc_id = p.get("doc_id", "Unknown")
        section_id = p.get("section_id", "0")
        cit = p.get("citation", f"[{doc_id}, {section_id}]")
        text = p.get("text", "").strip()
        formatted_parts.append(f"Passage {idx} {cit}:\n{text}")

    return "\n\n".join(formatted_parts)


def generate_answer(
    question: str,
    passages: List[Dict[str, Any]],
    model: str = DEFAULT_MODEL,
    temperature: float = 0.0,
    api_url: str = OLLAMA_API_URL,
) -> str:
    """Calls Ollama chat endpoint with system prompt and passages."""
    context_text = format_context(passages)
    user_content = f"Supplied Passages:\n{context_text}\n\nQuestion: {question}\n\nAnswer:"

    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_content},
        ],
        "stream": False,
        "options": {
            "temperature": temperature,
        },
    }

    req_data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        api_url,
        data=req_data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            answer = data.get("message", {}).get("content", "").strip()
            return answer
    except urllib.error.URLError as e:
        raise ConnectionError(f"Could not connect to Ollama at {api_url}: {e}")
