# Tool and Model Versions

Date checked: 20 November 2026
Owner: Arslan Khan

This file records the pinned package versions, licenses, and official sources for StitchLab AI.

## Pre-approved Packages

| Package | Pinned Version | License | Source / Reference | Date Checked |
|---|---|---|---|---|
| `torch` | 2.15.0+cpu | Apache-2.0 / BSD-3-Clause / MIT | https://pytorch.org (CPU build index https://download.pytorch.org/whl/cpu) | 20 November 2026 |
| `docling` | 2.151.1 | MIT | https://github.com/docling-project/docling | 20 November 2026 |
| `sentence-transformers` | 6.3.0 | Apache-2.0 | https://www.sbert.net | 20 November 2026 |
| `chromadb` | 1.5.9 | Apache-2.0 | https://github.com/chroma-core/chroma | 20 November 2026 |
| `gradio` | 6.32.0 | Apache-2.0 | https://github.com/gradio-app/gradio | 20 November 2026 |
| `sqlite3` (with FTS5) | Built-in (Python 3.13) | Public Domain | https://sqlite.org/fts5.html | 20 November 2026 |

## Pre-approved Models

| Model | Purpose | Pinned Identifier / Tag | License | Source / Model Card | Date Checked |
|---|---|---|---|---|---|
| `sentence-transformers/all-MiniLM-L6-v2` | Embeddings | `sentence-transformers/all-MiniLM-L6-v2` | Apache-2.0 | https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2 | 20 November 2026 |
| `cross-encoder/ms-marco-MiniLM-L-6-v2` | Reranker | `cross-encoder/ms-marco-MiniLM-L-6-v2` | Apache-2.0 | https://huggingface.co/cross-encoder/ms-marco-MiniLM-L-6-v2 | 20 November 2026 |
| `llama3.2:3b` | Local generation (Ollama) | `llama3.2:3b` (ID: a80c4f17acd5) | Llama 3.2 Community License | https://ollama.com/library/llama3.2 | 20 November 2026 |

## Telemetry Configuration
Telemetry is disabled across all components:
- ChromaDB: `ANONYMIZED_TELEMETRY=False`
- Gradio: `GRADIO_ANALYTICS_ENABLED=False`
- Hugging Face / Transformers offline runtime: `HF_HUB_OFFLINE=1`, `TRANSFORMERS_OFFLINE=1`
