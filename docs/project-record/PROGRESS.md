# Project Progress and Milestone Record

Project: StitchLab AI - Brightpath Media (demo), fictional
Owner: Arslan Khan
Platform: Windows 10 Pro, Intel Core i5-6300U, 8 GB RAM, no dedicated GPU

---

## Milestone M0.1: Environment report and setup

### 1. Files changed
- `docs/project-record/environment-report.md` (updated OS, CPU, disk, memory test)
- `docs/project-record/tool-versions.md` (pinned tools, models, licences, telemetry rules)
- `docs/project-record/PROGRESS.md` (created progress log)
- `activate-env.ps1` (environment setup directing cache/temp to F: drive)
- `requirements.txt` (pinned pre-approved packages)
- `app/paths.py` (sys.path initialization for hypenated package modules)

### 2. Done-check item by item with evidence
- **Specs and model name recorded**:
  - OS: Microsoft Windows 10 Pro (Version 10.0.18363 Build 18363)
  - CPU: Intel(R) Core(TM) i5-6300U CPU @ 2.40GHz
  - RAM: 8 GB installed (approx 7.9 GB usable)
  - Disk C: 4.05 GB free
  - Disk F: 52.24 GB free
  - Ollama program: `F:\Ollama\ollama.exe` (Model folder `F:\Ollama_Models`)
  - Installed model: `llama3.2:3b` (ID: `a80c4f17acd5`, size: 2.0 GB)
- **Test prompt returns valid output**:
  - Prompt: `"Reply with one short sentence about document assistants."`
  - Output: `"Document assistants are typically administrative professionals who provide support with tasks such as data entry, document management, and document preparation."`
- **Memory test / No out-of-memory errors**:
  - Available physical RAM before Ollama run: 2004.17 MB
  - Available physical RAM after Ollama run: 538.41 MB
  - RAM difference: 1465.76 MB
  - Elapsed time: 21.74 s
  - Out of memory error: False

### 3. Open problems / founder decisions
- None for M0.1. Hardware and local model operation verified.
