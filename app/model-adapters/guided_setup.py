"""
M6A.3: Guided Setup Screen for Ollama.
If Ollama is not running, displays the 3-step setup guide:
1. Download Ollama
2. Run serve
3. Pull llama3.2:3b
"""

from typing import Optional
from ollama_adapter import is_ollama_running

SETUP_GUIDE_TEMPLATE = """### Private Local Model Setup Required

Ollama is not currently running. To use StitchLab AI locally and privately without internet access, complete these 3 steps:

1. **Download Ollama**: Download and install Ollama from [https://ollama.com/download](https://ollama.com/download).
2. **Start the Ollama Service**: Open PowerShell or Command Prompt and run:
   ```powershell
   ollama serve
   ```
   *(Or run `F:\\Ollama\\ollama.exe serve` if using a portable installation).*
3. **Pull the llama3.2:3b Model**: In a terminal window, run:
   ```powershell
   ollama pull llama3.2:3b
   ```

Once the model is downloaded and the service is running, refresh this application to start chatting.
"""


def check_and_get_setup_instructions(base_url: str = "http://127.0.0.1:11434") -> Optional[str]:
    """
    Checks if Ollama is running.
    Returns:
        3-step setup markdown if stopped, or None if running.
    """
    if not is_ollama_running(base_url, timeout=1.0):
        return SETUP_GUIDE_TEMPLATE.strip()
    return None
