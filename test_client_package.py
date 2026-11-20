"""
M12.1 Done-check Unit Test for Client Delivery Package.
Asserts:
1. client-package/ contains all required application files, documents, requirements, activate script, README.
2. client-package/ contains zero forbidden files (.git, .venv, local-index, logs, __pycache__, keys).
3. Recursive content scan confirms zero API keys or secrets in the package.
"""

import os
import sys
import unittest
from pathlib import Path

# Paths
sys.path.insert(0, str(Path(__file__).resolve().parent))
from make_client_package import assemble_package, PACKAGE_DIR, REPO_ROOT


class TestClientPackage(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Assemble package fresh
        assemble_package()

    def test_required_files_present(self):
        required_relative_paths = [
            "app/paths.py",
            "app/chat-interface/app.py",
            "app/chat-interface/pipeline.py",
            "app/retrieval/hybrid.py",
            "app/retrieval/reranker.py",
            "app/retrieval/threshold.py",
            "app/citations/answer.py",
            "app/citations/citation_check.py",
            "app/conflict-checks/conflicts.py",
            "app/model-adapters/base.py",
            "app/model-adapters/ollama_adapter.py",
            "app/model-adapters/openai_adapter.py",
            "app/model-adapters/masking.py",
            "app/model-adapters/netguard.py",
            "app/model-adapters/audit_log.py",
            "app/ingestion/chunker.py",
            "app/ingestion/build_index.py",
            "requirements.txt",
            "activate-env.ps1",
            "README.md",
            "documents/fictional-brightpath/D01-client-onboarding-sop.md",
            "documents/fictional-brightpath/D05-escalation-contacts.md",
        ]

        missing = []
        for rel in required_relative_paths:
            full = PACKAGE_DIR / rel
            if not full.exists():
                missing.append(rel)

        self.assertEqual(len(missing), 0, f"Missing required files in client package: {missing}")
        print(f"\nAll {len(required_relative_paths)} required files confirmed present in client-package.")

    def test_forbidden_directories_and_files_absent(self):
        forbidden_substrings = [
            ".git",
            ".venv",
            "local-index",
            "logs",
            "__pycache__",
        ]

        found_forbidden = []
        for root, dirs, files in os.walk(PACKAGE_DIR):
            for d in dirs:
                if d in forbidden_substrings:
                    found_forbidden.append(str(Path(root) / d))
            for f in files:
                if f.endswith(".key") or f.endswith(".pem") or f.endswith(".pyc"):
                    found_forbidden.append(str(Path(root) / f))

        self.assertEqual(
            len(found_forbidden),
            0,
            f"Found forbidden files/directories in client package: {found_forbidden}",
        )
        print("Verified: Zero forbidden directories (.git, .venv, local-index, logs, pycache) or key files found.")

    def test_zero_api_keys_in_package(self):
        found_key_locations = []
        for root, dirs, files in os.walk(PACKAGE_DIR):
            for f in files:
                file_path = Path(root) / f
                try:
                    content = file_path.read_text(encoding="utf-8", errors="ignore")
                    if "sk-" in content or "TEST-DUMMY" in content:
                        found_key_locations.append(str(file_path))
                except Exception:
                    pass

        self.assertEqual(
            len(found_key_locations),
            0,
            f"Found potential API keys in client package files: {found_key_locations}",
        )
        print("Verified: Zero API keys or secrets detected across all client package files.")


if __name__ == "__main__":
    unittest.main()
