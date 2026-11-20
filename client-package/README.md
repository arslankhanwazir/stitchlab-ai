# StitchLab AI - Private Enterprise Document Assistant
Client Delivery Package | Brightpath Media (demo), fictional

## Overview
StitchLab AI is a private, evidence-grounded document search and Q&A assistant.
It operates 100% locally by default using Ollama (`llama3.2:3b`), CPU embeddings, and SQLite FTS5.

## Security & Privacy Guarantees
- **Local-first by default**: No data leaves your premises when running with local models.
- **Strict citations**: Every answer claim is cited with `[DocID, Section]`.
- **Zero hallucinations**: Strict refusal rule (`Not found in your documents.`) when evidence is absent.
- **Deterministic conflict detection**: Automatically identifies and alerts on conflicting policy clauses across documents.
- **Reversible PII masking**: Masks emails, phones, and personnel names before any external model calls.
- **Outbound NetGuard**: Enforces strict URL allowlisting (only 127.0.0.1:11434 or active configured cloud provider).
- **Audit Logging**: Full "What was sent" logging to a local, private audit file.

## Quick Start
1. **Install Prerequisites**:
   - Python 3.10+
   - Ollama (download from https://ollama.com/download)
   - Pull the local model:
     ```powershell
     ollama pull llama3.2:3b
     ollama serve
     ```
2. **Setup Environment**:
   ```powershell
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   pip install --extra-index-url https://download.pytorch.org/whl/cpu torch
   pip install -r requirements.txt
   ```
3. **Build Knowledge Base Index**:
   ```powershell
   python app/ingestion/build_index.py
   ```
4. **Launch Web Chat Interface**:
   ```powershell
   python app/chat-interface/app.py
   ```
   Open your browser to `http://127.0.0.1:7860`.
