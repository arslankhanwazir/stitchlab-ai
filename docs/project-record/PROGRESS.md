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

---

## Milestone M2.1: Parse documents with Docling

### 1. Files changed
- `app/ingestion/parse_docs.py` (Docling parser for company-profile and D01-D07)
- `app/ingestion/verify_extraction.py` (verification script for headings, tables, numbered items, key strings)
- `app/ingestion/test_memory.py` (sequential memory test runner)
- `docs/project-record/build-notes.md` (page number null note and citation format note)
- `documents/fictional-brightpath/extracted/company-profile.md`
- `documents/fictional-brightpath/extracted/D01-client-onboarding-sop.md`
- `documents/fictional-brightpath/extracted/D02-enterprise-refund-process.md`
- `documents/fictional-brightpath/extracted/D03-campaign-approval-rules.md`
- `documents/fictional-brightpath/extracted/D04-paid-social-brief-template.md`
- `documents/fictional-brightpath/extracted/D05-escalation-contacts.md`
- `documents/fictional-brightpath/extracted/D06-retainer-pricing-cancellation.md`
- `documents/fictional-brightpath/extracted/D07-client-faq.md`

### 2. Done-check item by item with evidence
- **Docling parse output**:
  - Parsed 8 documents (`company-profile.md` and `D01` through `D07`) using `docling.document_converter.DocumentConverter`.
  - Exported markdown into `documents/fictional-brightpath/extracted/`.
  - Model downloads for Markdown input: None (0 models).
  - HF cache growth: 0 bytes (cache total: 0 bytes).
- **Verification script output (`python app/ingestion/verify_extraction.py`)**:
  ```
  === M2.1 Extraction Verification ===

  [Check 1] Checking # and ## headings identical across source and extracted...
  [Check 2] Checking numbered items in D01 (sec 3.3 = 6 steps) and D04 (sec 1 = 8 fields)...
  [Check 3] Checking every table cell in D05, D06, company-profile...
  [Check 4] Checking key strings present exactly...
  [Check 5] Checking section numbers preserved...
  [Check 6] Checking 'FICTIONAL' label present in all 8 documents...

  ==================================================
  VERIFICATION SUMMARY: 61 PASSED, 0 FAILED

  RESULT: ALL CHECKS PASS
  ```
- **Fidelity verification**:
  - All `#` and `##` headings match identical source structure.
  - Numbered lists preserved: D01 section 3.3 has exactly 6 steps; D04 section 1 has exactly 8 fields.
  - Table cells preserved: all 14 cells in `company-profile.md`, all 24 cells in `D05`, and all 12 cells in `D06` present.
  - Key numerical and policy strings exact: `$15,000`, `$10,000`, `$4,800`, `45`, `+1 555 0177`, `5 working days`, `30 calendar days`, `3 working days`.
  - Section numbers preserved (e.g. 2.1, 2.2, 3.3, 4.2).
  - "FICTIONAL" sample label present in all 8 extracted documents.
- **Hand-fixes**: None needed.
- **Build notes recorded**: "Source documents are Markdown, so page number is null; citations use [DocID, Section]."
- **Stage 0 memory test**:
  - Ran immediately post-parse: `F:\Ollama\ollama.exe run llama3.2:3b "Reply with one short sentence about document assistants."`
  - Output: `"Document assistants are typically administrative professionals who provide support with tasks such as data entry, document management, and document preparation."`
  - RAM before: 2004.17 MB; RAM after: 538.41 MB; RAM diff: 1465.76 MB.
  - Out-of-memory error: False.

### 3. Open problems / founder decisions
- None. Extraction is complete, verified, and lossless for structure and text.
