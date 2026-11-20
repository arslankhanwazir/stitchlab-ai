"""
Paths configuration for StitchLab AI.
Adds app/ and each subfolder (including hyphenated folder names) to sys.path
so modules and test scripts can import cleanly across packages.
"""

import sys
from pathlib import Path

import sys
import types
from pathlib import Path

APP_DIR = Path(__file__).resolve().parent
REPO_ROOT = APP_DIR.parent

# Guarantee app is registered as a package module
if "app" not in sys.modules or not hasattr(sys.modules["app"], "__path__"):
    app_pkg = types.ModuleType("app")
    app_pkg.__path__ = [str(APP_DIR)]
    app_pkg.__file__ = str(APP_DIR / "__init__.py")
    sys.modules["app"] = app_pkg

# Ensure REPO_ROOT is at sys.path[0]
repo_root_str = str(REPO_ROOT)
if repo_root_str in sys.path:
    sys.path.remove(repo_root_str)
sys.path.insert(0, repo_root_str)

SUBFOLDERS = [
    APP_DIR,
    APP_DIR / "ingestion",
    APP_DIR / "retrieval",
    APP_DIR / "model-adapters",
    APP_DIR / "citations",
    APP_DIR / "conflict-checks",
    APP_DIR / "chat-interface",
]

for folder in SUBFOLDERS:
    folder_str = str(folder)
    if folder_str not in sys.path:
        sys.path.append(folder_str)
