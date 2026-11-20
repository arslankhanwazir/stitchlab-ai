"""
M6A.6 Done-check Unit Test for Secure Key Handling.
Saves dummy key "sk-TEST-DUMMY-0000" to %LOCALAPPDATA%\\StitchLabAI\\key.json.
Asserts:
1. Target file exists at target path outside the repository.
2. File contains the dummy key.
3. Recursive scan across git repo and logs yields ZERO hits (excluding this test script).
"""

import os
import sys
import json
import unittest
from pathlib import Path

# Paths
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import paths

from key_store import (
    set_key,
    get_key,
    clear_keys,
    get_external_key_file_path,
)

DUMMY_KEY = "sk-TEST-DUMMY-0000"


class TestKeyStore(unittest.TestCase):
    def setUp(self):
        clear_keys(clear_disk=True)

    def tearDown(self):
        clear_keys(clear_disk=True)

    def test_key_saved_externally_and_zero_repo_hits(self):
        # 1. Save dummy key with persist_to_disk=True
        set_key("openai", DUMMY_KEY, persist_to_disk=True)

        target_path = get_external_key_file_path()
        print(f"\nExternal Key Path: {target_path}")

        # Assert 1: Exists on disk
        self.assertTrue(target_path.exists(), "Target key.json must exist.")

        # Assert 2: Target path is outside repository
        repo_root = paths.REPO_ROOT.resolve()
        target_resolved = target_path.resolve()
        self.assertFalse(
            str(target_resolved).startswith(str(repo_root)),
            f"Key path {target_resolved} must NOT be inside repo {repo_root}",
        )

        # Assert 3: Read from disk correctly
        loaded_key = get_key("openai", check_disk=True)
        self.assertEqual(loaded_key, DUMMY_KEY)

        # Assert 4: Scan entire repo to assert ZERO hits in repository files
        # (Exclude this test file test_key_store.py and .git folder)
        this_file_path = Path(__file__).resolve()
        matching_files = []

        for root, dirs, files in os.walk(repo_root):
            # Skip .git directory
            if ".git" in dirs:
                dirs.remove(".git")
            if ".venv" in dirs:
                dirs.remove(".venv")
            if "__pycache__" in dirs:
                dirs.remove("__pycache__")

            for file_name in files:
                full_path = Path(root) / file_name
                if full_path.resolve() == this_file_path:
                    continue  # Ignore test file containing the assertion literal

                try:
                    content = full_path.read_text(encoding="utf-8", errors="ignore")
                    if DUMMY_KEY in content:
                        matching_files.append(str(full_path))
                except Exception:
                    pass

        print(f"Scanned repository files. Found matches: {matching_files}")
        self.assertEqual(
            len(matching_files),
            0,
            f"Security Violation: Found dummy key in repository files: {matching_files}",
        )


if __name__ == "__main__":
    unittest.main()
