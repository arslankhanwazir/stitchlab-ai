"""
M5.1 / M6A.4: Pipeline Orchestration for StitchLab AI.
Orchestrates:
1. Hybrid retrieval (FTS5 + Vector search)
2. Cross-encoder reranking
3. Minimum relevance threshold check (rejection of unanswerable queries)
4. Conflict detection across different documents
5. Passage cap (max 5 passages)
6. Reversible PII masking before external model dispatch (M6B.2)
7. Outbound NetGuard validation (M6B.3)
8. Audit logging of prompt and masked passages (M6B.4)
9. Evidence-only LLM answer generation (Ollama local or Google Gemini via OpenAI-compatible route)
10. Code-based citation verification and sanitization
"""

import os
import sys
import time
from pathlib import Path
from typing import Dict, Any, Optional, List

# Ensure sys.path includes app and all subfolders
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import paths

from hybrid import hybrid_search
from reranker import rerank
from threshold import MIN_RELEVANCE_SCORE, NOT_FOUND_MESSAGE
from conflicts import check_conflicts
from answer import generate_answer
from citation_check import verify_and_filter_citations
from passage_limiter import enforce_passage_limit
from masking import mask_data, unmask_data
from netguard import validate_outbound_url
from audit_log import log_what_was_sent
from openai_adapter import OpenAIAdapter, DEFAULT_GEMINI_URL

DEFAULT_MAX_PASSAGES = 5


def run_pipeline(
    query: str,
    max_passages: int = DEFAULT_MAX_PASSAGES,
    threshold: float = MIN_RELEVANCE_SCORE,
    model: Optional[str] = None,
    provider: str = "ollama",
    api_key: Optional[str] = None,
    base_url: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Executes the full query pipeline end-to-end.
    Supports local Ollama and Google Gemini (via OpenAI-compatible endpoint).
    Returns:
        dict containing answer, citations, conflict banner, retrieved passages, status, latency, what_was_sent.
    """
    start_time = time.time()
    result = {
        "query": query,
        "answer": "",
        "citations": [],
        "conflict": None,
        "passages": [],
        "status": "ANSWER",
        "latency_sec": 0.0,
        "error": None,
        "what_was_sent": None,
    }

    try:
        # Step 1: Hybrid retrieval
        hits = hybrid_search(query, top_candidates=10)

        # Step 2: Reranking
        reranked = rerank(query, hits)

        # Step 3: Threshold check on top score
        top_score = reranked[0].get("rerank_score", -999.0) if reranked else -999.0
        if top_score < threshold or not reranked:
            result["status"] = "NOT_FOUND"
            result["answer"] = NOT_FOUND_MESSAGE
            result["latency_sec"] = round(time.time() - start_time, 4)
            return result

        # Step 4: Cap passages (M6B.1 - hard cap 5)
        passages = enforce_passage_limit(reranked, limit=max_passages, hard_cap=5)
        result["passages"] = passages

        # Step 5: Deterministic conflict detection
        conflict = check_conflicts(passages)
        if conflict:
            result["status"] = "CONFLICT"
            result["conflict"] = conflict
            result["answer"] = "The answer depends on the conflicting policy rules shown above. Review both documents before acting."
            result["citations"] = [p.get("citation", "") for p in passages if p.get("citation")]
            result["latency_sec"] = round(time.time() - start_time, 4)
            return result

        # Provider determination
        provider_clean = (provider or "ollama").lower().strip()
        is_gemini = "gemini" in provider_clean

        if is_gemini:
            provider_name = "gemini"
            target_model = model.strip() if model and model.strip() else None
            if not target_model:
                result["status"] = "ERROR"
                result["error"] = "Model name is required (use a model your key can access)."
                result["answer"] = "Error: Please specify a model name for Google Gemini (use a model your key can access)."
                result["latency_sec"] = round(time.time() - start_time, 4)
                return result

            key = api_key or os.environ.get("GEMINI_API_KEY")
            if not key:
                result["status"] = "ERROR"
                result["error"] = "GEMINI_API_KEY environment variable is not set."
                result["answer"] = "Error: GEMINI_API_KEY environment variable is not set. Please set GEMINI_API_KEY to use Google Gemini."
                result["latency_sec"] = round(time.time() - start_time, 4)
                return result

            gemini_base = base_url or DEFAULT_GEMINI_URL
            endpoint = f"{gemini_base.rstrip('/')}/chat/completions"

            # Validate against NetGuard (M6B.3)
            if "127.0.0.1" in gemini_base or "localhost" in gemini_base:
                import urllib.parse
                parsed = urllib.parse.urlparse(gemini_base)
                validate_outbound_url(endpoint, active_provider_host=parsed.netloc)
            else:
                validate_outbound_url(
                    endpoint,
                    active_provider="gemini",
                    active_provider_host="generativelanguage.googleapis.com",
                )
        else:
            provider_name = "ollama"
            target_model = model or "llama3.2:3b"
            endpoint = "http://127.0.0.1:11434/api/chat"
            validate_outbound_url(endpoint)

        # Step 6: Mask PII before dispatch (M6B.2)
        masked_passages = []
        combined_mapping = {}
        for p in passages:
            p_copy = dict(p)
            masked_text, m_map = mask_data(p.get("text", ""))
            p_copy["text"] = masked_text
            combined_mapping.update(m_map)
            masked_passages.append(p_copy)

        # Log what was sent (M6B.4)
        audit_entry = log_what_was_sent(
            question=query,
            passages=masked_passages,
            provider=provider_name,
            model=target_model,
            endpoint=endpoint,
        )
        result["what_was_sent"] = audit_entry

        # Step 7: LLM Answer generation
        try:
            if is_gemini:
                adapter = OpenAIAdapter(base_url=gemini_base, is_gemini=True)
                raw_answer = adapter.generate(query, masked_passages, model=target_model, api_key=key)
            else:
                raw_answer = generate_answer(query, masked_passages, model=target_model)

            # Reversibly restore any masked tokens before display (M6B.2)
            if combined_mapping:
                raw_answer = unmask_data(raw_answer, combined_mapping)
        except ConnectionError as ce:
            result["status"] = "ERROR"
            result["error"] = str(ce)
            if is_gemini:
                result["answer"] = f"Unable to reach Google Gemini endpoint ({ce}). Please check network connectivity."
            else:
                result["answer"] = (
                    "Unable to reach the local LLM service (Ollama). "
                    "Please ensure Ollama is running at http://127.0.0.1:11434 with model llama3.2:3b."
                )
            result["latency_sec"] = round(time.time() - start_time, 4)
            return result

        # Step 8: Citation verification & sanitization
        sanitized_answer, citation_records, all_valid = verify_and_filter_citations(raw_answer, passages)
        result["answer"] = sanitized_answer
        result["citations"] = [
            f"[{r['doc_id']}, {r['section_id']}]"
            for r in citation_records
            if r.get("is_valid")
        ]
        result["status"] = "ANSWER"
        result["latency_sec"] = round(time.time() - start_time, 4)
        return result

    except Exception as e:
        result["status"] = "ERROR"
        result["error"] = str(e)
        result["answer"] = f"An unexpected error occurred during processing: {e}"
        result["latency_sec"] = round(time.time() - start_time, 4)
        return result
