"""
M12.1: Client Delivery Package Assembler.
Assembles client-package/ containing:
- app/
- documents/fictional-brightpath/
- requirements.txt
- activate-env.ps1 (client template)
- README.md
Excludes: .git, .venv, local-index, logs, cache, keys.
"""

import os
import shutil
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent
PACKAGE_DIR = REPO_ROOT / "client-package"

CLIENT_README = """# StitchLab AI - Private Enterprise Document Assistant
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
   .\\.venv\\Scripts\\Activate.ps1
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
"""

CLIENT_ACTIVATE_PS1 = """# StitchLab AI Client Environment Activation
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Definition
if (Test-Path "$ScriptDir\\.venv\\Scripts\\Activate.ps1") {
    & "$ScriptDir\\.venv\\Scripts\\Activate.ps1"
}

# Offline and Telemetry Protection
$env:ANONYMIZED_TELEMETRY = "False"
$env:GRADIO_ANALYTICS_ENABLED = "False"
$env:HF_HUB_OFFLINE = "1"
$env:TRANSFORMERS_OFFLINE = "1"

Write-Host "StitchLab AI client environment active. Telemetry: OFF. Offline mode: ON." -ForegroundColor Green
"""


def should_exclude(path: Path) -> bool:
    """Returns True if the path should be excluded from client package."""
    parts = path.parts
    name = path.name
    excluded_names = {
        ".git",
        ".venv",
        "local-index",
        "logs",
        "client-package",
        "__pycache__",
        "stitchlab-cache",
        ".idea",
        ".vscode",
    }
    for p in parts:
        if p in excluded_names or p.endswith(".pyc") or p.endswith(".key") or p.endswith(".pem"):
            return True

    # Exclude internal developer test scripts from client delivery package
    if name.startswith("test_"):
        return True

    return False


def copy_tree_clean(src_dir: Path, dest_dir: Path):
    """Recursively copies directory tree filtering out excluded files and directories."""
    dest_dir.mkdir(parents=True, exist_ok=True)
    for root, dirs, files in os.walk(src_dir):
        # Filter directories in place
        dirs[:] = [d for d in dirs if not should_exclude(Path(root) / d)]
        rel_path = Path(root).relative_to(src_dir)
        target_root = dest_dir / rel_path
        target_root.mkdir(parents=True, exist_ok=True)

        for f in files:
            src_file = Path(root) / f
            if not should_exclude(src_file):
                shutil.copy2(src_file, target_root / f)


def assemble_package():
    print(f"Assembling client package into: {PACKAGE_DIR}")
    if PACKAGE_DIR.exists():
        shutil.rmtree(PACKAGE_DIR)
    PACKAGE_DIR.mkdir(parents=True, exist_ok=True)

    # 1. Copy app/
    copy_tree_clean(REPO_ROOT / "app", PACKAGE_DIR / "app")

    # 2. Copy documents/fictional-brightpath/
    copy_tree_clean(
        REPO_ROOT / "documents" / "fictional-brightpath",
        PACKAGE_DIR / "documents" / "fictional-brightpath",
    )

    # 3. Copy requirements.txt
    shutil.copy2(REPO_ROOT / "requirements.txt", PACKAGE_DIR / "requirements.txt")

    # 4. Write client activate-env.ps1 template
    (PACKAGE_DIR / "activate-env.ps1").write_text(CLIENT_ACTIVATE_PS1.strip() + "\n", encoding="utf-8")

    # 5. Write client README.md
    (PACKAGE_DIR / "README.md").write_text(CLIENT_README.strip() + "\n", encoding="utf-8")

    print("Client package assembled successfully.")


if __name__ == "__main__":
    assemble_package()
