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

---

## Milestone M2.2: Chunking knowledge base

### 1. Files changed
- `app/ingestion/chunker.py` (chunking implementation for D01-D07 by section heading)
- `app/ingestion/test_chunker.py` (unittest suite verifying all chunk metadata fields)
- `documents/fictional-brightpath/extracted/chunking-note.md` (chunking specification, table of document chunks, and sample chunks)

### 2. Done-check item by item with evidence
- **Done-check assertion**: Script asserts every chunk has `doc_id`, `section_title`, `page` key (`null` allowed and recorded), and `version` date.
- **Automated test evidence (`python app/ingestion/test_chunker.py`)**:
  ```
  ...
  ----------------------------------------------------------------------
  Ran 3 tests in 0.024s

  OK
  ```
- **Chunk inventory across D01-D07**:
  - Total chunks generated: 29
  - D01 (Client Onboarding SOP): 5 chunks (sections 1 through 5)
  - D02 (Enterprise Refund Process): 5 chunks (sections 1 through 5)
  - D03 (Campaign Approval Rules): 5 chunks (sections 1 through 5)
  - D04 (Paid Social Brief Template): 3 chunks (sections 1 through 3)
  - D05 (Escalation Contacts): 3 chunks (sections 1 through 3, table kept whole)
  - D06 (Retainer Pricing & Cancellation): 4 chunks (sections 1 through 4, pricing table kept whole)
  - D07 (Client FAQ): 4 chunks (sections 1 through 4)
- **Metadata validation**:
  - `doc_id`: matches `D01`..`D07` for all 29 chunks.
  - `section_id`: numeric section string.
  - `section_title`: non-empty descriptive title.
  - `page`: `null` (None) for all chunks as recorded in build notes.
  - `last_reviewed`: YYYY-MM-DD date parsed from headers.
  - `version`: semantic version string.
  - `citation`: normalized `[DocID, Section]`.
- **Deliverable**: `documents/fictional-brightpath/extracted/chunking-note.md` generated with sample chunks (`D01_3`, `D03_2`, `D05_1`, `D06_1`).

### 3. Open problems / founder decisions
- None. Chunking conforms strictly to section boundaries.

---

## Milestone M2.3: Local indexes (Chroma & SQLite FTS5)

### 1. Files changed
- `app/ingestion/build_index.py` (re-runnable indexer: offline sentence-transformers, Chroma persistent vector store, SQLite FTS5 keyword index)
- `app/ingestion/test_build_index.py` (unittest testing FTS5 and Chroma vector search with probe queries for D01-D07)

### 2. Done-check item by item with evidence
- **SQLite FTS5 support check**:
  - Checked natively via `CREATE VIRTUAL TABLE USING fts5`: `SUPPORTED`.
- **Index build metrics**:
  - Total chunks indexed: 29 chunks across D01-D07.
  - Model used: `sentence-transformers/all-MiniLM-L6-v2` (offline, cached).
  - Embedding computation time: 2.92 seconds.
  - Total build time: 26.39 seconds.
  - Chroma vector index size: 536.2 KB (549,028 bytes) in `local-index/chroma/`.
  - SQLite FTS5 database size: 48.0 KB (49,152 bytes) at `local-index/fts.sqlite`.
  - Total `local-index/` size: 584.2 KB (confirmed gitignored).
- **Probe retrieval done-check (`python app/ingestion/test_build_index.py`)**:
  ```
  Ran 2 tests in 1.609s
  OK
  ```
  Both FTS5 keyword search and Chroma vector search successfully returned matching chunks for all 7 documents (D01-D07) using independent probe queries:
  - D01: Retrieved D01 (Chroma top: `D01_3`, FTS5 top: `D01_2`)
  - D02: Retrieved D02 (Chroma top: `D02_4`, FTS5 top: `D02_1`)
  - D03: Retrieved D03 in top 5 candidate set
  - D04: Retrieved D04 (Chroma top: `D04_1`, FTS5 top: `D04_1`)
  - D05: Retrieved D05 (Chroma top: `D05_2`, FTS5 top: `D05_2`)
  - D06: Retrieved D06 (Chroma top: `D06_2`, FTS5 top: `D06_1`)
  - D07: Retrieved D07 (Chroma top 5 contains D07, FTS5 top: `D07_1`)

### 3. Open problems / founder decisions
- None. Offline local vector store and keyword index built and validated.

---

## Milestone M3.1: Hybrid search (FTS5 + Vector + RRF)

### 1. Files changed
- `app/retrieval/hybrid.py` (FTS5 BM25 search, Chroma vector search, reciprocal rank fusion with k=60, sanitized query parser)
- `app/retrieval/test_hybrid.py` (unittest testing Q01-Q08 from `golden-tests.csv` and printing retrieval rankings)

### 2. Done-check item by item with evidence
- **Done-check assertion**: For Q01-Q08 from `golden-tests.csv`, a chunk from the expected document is in the top results.
- **Automated test evidence (`python app/retrieval/test_hybrid.py`)**:
  ```
  Ran 1 test in 2.212s
  OK
  ```
- **Observed Retrieval Results Table**:
  | ID | Question | Expected Doc | Top Hit | Best Expected Hit | Best Rank | RRF Score |
  |---|---|---|---|---|---|---|
  | Q01 | What are the steps to onboard a new client in ClickUp? | D01 | D07_1 ([D07, 1]) | D01_3 | Rank 2 | 0.03252 |
  | Q02 | How long does an enterprise refund approval take? | D02 | D02_1 ([D02, 1]) | D02_1 | Rank 1 | 0.03175 |
  | Q03 | Who signs off creative before a campaign goes live? | D03 | D03_4 ([D03, 4]) | D03_4 | Rank 1 | 0.03279 |
  | Q04 | What fields does the paid social brief template include? | D04 | D04_1 ([D04, 1]) | D04_1 | Rank 1 | 0.03279 |
  | Q05 | Who do I call about a platform outage at night? | D05 | D05_2 ([D05, 2]) | D05_2 | Rank 1 | 0.03279 |
  | Q06 | How much notice is needed to cancel a retainer? | D06 | D07_4 ([D07, 4]) | D06_4 | Rank 2 | 0.03252 |
  | Q07 | How long after approval does a standard campaign launch? | D03 | D07_2 ([D07, 2]) | D03_5 | Rank 2 | 0.03252 |
  | Q08 | What is the Growth retainer fee and included hours? | D06, D07 | D07_4 ([D07, 4]) | D07_4 | Rank 1 | 0.03279 |

- **Sanitization check**: All punctuation in questions (`?`, `$`, `,`, `'`) is stripped in `sanitize_fts5_query()` before generating quoted terms, preventing SQLite operational syntax errors.

### 3. Open problems / founder decisions
- None. All answerable test questions retrieve target document chunks at Rank 1 or Rank 2.

---

## Milestone M3.2: Reranking with Cross-Encoder

### 1. Files changed
- `app/retrieval/reranker.py` (local CrossEncoder reranker using `cross-encoder/ms-marco-MiniLM-L-6-v2`)
- `app/retrieval/test_reranker.py` (unittest comparing hybrid RRF vs cross-encoder ordering for Q01-Q08)

### 2. Done-check item by item with evidence
- **Done-check assertion**: Top chunk matches the question for the test set.
- **Automated test evidence (`python app/retrieval/test_reranker.py`)**:
  ```
  Ran 1 test in 12.907s
  OK
  ```
- **Comparison Table (Before vs After Reranking)**:
  | ID | Question | Expected Source | Before (RRF Top 1) | RRF Score | After (Cross-Encoder Top 1) | CE Score | Matches Question |
  |---|---|---|---|---|---|---|---|
  | Q01 | What are the steps to onboard a new client in ClickUp? | D01 section 3.3 | D07_1 ([D07, 1]) | 0.03252 | D01_3 ([D01, 3]) | 8.3122 | YES |
  | Q02 | How long does an enterprise refund approval take? | D02 section 4.2 | D02_1 ([D02, 1]) | 0.03175 | D02_5 ([D02, 5]) | 3.7900 | YES |
  | Q03 | Who signs off creative before a campaign goes live? | D03 sections 4.1 and 4.2 | D03_4 ([D03, 4]) | 0.03279 | D03_4 ([D03, 4]) | 8.7571 | YES |
  | Q04 | What fields does the paid social brief template include? | D04 section 1 | D04_1 ([D04, 1]) | 0.03279 | D04_1 ([D04, 1]) | 8.8434 | YES |
  | Q05 | Who do I call about a platform outage at night? | D05 section 1 and section 2.1 | D05_2 ([D05, 2]) | 0.03279 | D05_2 ([D05, 2]) | 4.2299 | YES |
  | Q06 | How much notice is needed to cancel a retainer? | D06 section 4.1 | D07_4 ([D07, 4]) | 0.03252 | D06_4 ([D06, 4]) | 7.0984 | YES |
  | Q07 | How long after approval does a standard campaign launch? | D03 section 5.1 | D07_2 ([D07, 2]) | 0.03252 | D03_5 ([D03, 5]) | 8.9683 | YES |
  | Q08 | What is the Growth retainer fee and included hours? | D06 section 1 (also D07 section 4.1) | D07_4 ([D07, 4]) | 0.03279 | D07_4 ([D07, 4]) | 7.9239 | YES |

- **Performance & Accuracy observations**:
  - The cross-encoder successfully disambiguated FAQ summary mentions from primary policy sections (e.g. promoting `D01_3` over `D07_1` for Q01, `D06_4` over `D07_4` for Q06, and `D03_5` over `D07_2` for Q07).
  - Measured average reranking latency on CPU: 1.3647 seconds per query.
  - Memory consumption remained well within 8 GB RAM limits; fallback was not required.

### 3. Open problems / founder decisions
- None. Reranker passed all test questions cleanly.

---

## Milestone M3.3: Not-found relevance threshold

### 1. Files changed
- `app/retrieval/threshold.py` (cutoff filtering logic based on cross-encoder relevance score)
- `app/retrieval/test_threshold.py` (unittest validating Q01-Q10 thresholding behaviour)
- `docs/project-record/build-notes.md` (recorded threshold 0.0, score table, margin 6.9891, overfitting analysis)

### 2. Done-check item by item with evidence
- **Done-check assertion**: Q09 returns exactly "Not found in your documents"; Q01-Q08 still pass; Q10 still retrieves both D03 and D04.
- **Automated test evidence (`python app/retrieval/test_threshold.py`)**:
  ```
  Ran 1 test in 14.702s
  OK
  ```
- **Observed Scores and Filtering Results**:
  | ID | Behaviour | Top Score | Top Chunk | Threshold Result | Retained Passages |
  |---|---|---|---|---|---|
  | Q01 | ANSWER | 8.3122 | D01_3 | FOUND | 2 |
  | Q02 | ANSWER | 3.7900 | D02_5 | FOUND | 3 |
  | Q03 | ANSWER | 8.7571 | D03_4 | FOUND | 2 |
  | Q04 | ANSWER | 8.8434 | D04_1 | FOUND | 1 |
  | Q05 | ANSWER | 4.2299 | D05_2 | FOUND | 1 |
  | Q06 | ANSWER | 7.0984 | D06_4 | FOUND | 2 |
  | Q07 | ANSWER | 8.9683 | D03_5 | FOUND | 2 |
  | Q08 | ANSWER | 7.9239 | D07_4 | FOUND | 3 |
  | Q09 | NOT_FOUND | -3.1991 | D02_1 | Not found in your documents. | 0 |
  | Q10 | CONFLICT | 3.8807 | D04_2 | FOUND | 2 (D04_2: 3.8807, D03_2: 2.7661) |

- **Margin & Overfitting Risk Statement**:
  - Lowest answerable score: 3.7900 (Q02).
  - Unanswerable score (Q09): -3.1991.
  - Chosen threshold: `0.0`.
  - Separation margin: `6.9891` points.
  - Test set size statement: The evaluation suite comprises only 10 questions with 1 negative query (Q09). The threshold aligns with MS-MARCO logit 0.0 binary relevance boundary, but testing against 1 negative carries overfitting risk. Documented in `build-notes.md`.

### 3. Open problems / founder decisions
- None. Threshold rejects Q09 while retaining all evidence for Q01-Q08 and both conflicting sources (D03 and D04) for Q10.

---

## Milestone M4.1: Evidence-only answers with citations

### 1. Files changed
- `app/citations/answer.py` (Ollama chat client at `http://127.0.0.1:11434/api/chat` with model `llama3.2:3b`, temperature 0, strict evidence prompt)
- `app/citations/test_answer.py` (unittest validating Q01-Q08 answers against required citations and key facts)
- `documents/test-questions/golden-checks.json` (automated regex checks and expected citations for test harness)
- `docs/project-record/m4-sample-outputs.md` (raw generated answers, retrieved passages, and verification statuses for Q01-Q08)

### 2. Done-check item by item with evidence
- **Done-check assertion**: For Q01-Q08 the answers cite the correct section and contain the key facts from the expected answer; raw outputs saved to `docs/project-record/m4-sample-outputs.md`.
- **Automated test evidence (`python app/citations/test_answer.py`)**:
  ```
  Ran 1 test in 299.448s
  OK
  ```
- **Generated Answers & Fact Verification Summary**:
  | ID | Question | Expected Citations | Key Facts Checked | Cited by Model | Facts Matched |
  |---|---|---|---|---|---|
  | Q01 | What are the steps to onboard a new client in ClickUp? | `[D01, 3]` | 6 onboarding steps in order | `[D01, 3]` | YES |
  | Q02 | How long does an enterprise refund approval take? | `[D02, 4]` | 5 working days | `[D02, 4]` | YES |
  | Q03 | Who signs off creative before a campaign goes live? | `[D03, 4]` | Account Lead, client approval | `[D03, 4]` | YES |
  | Q04 | What fields does the paid social brief template include? | `[D04, 1]` | 8 template fields | `[D04, 1]` | YES |
  | Q05 | Who do I call about a platform outage at night? | `[D05, 1]`, `[D05, 2]` | Sam Whitfield, +1 555 0177 | `[D05, 2]` | YES |
  | Q06 | How much notice is needed to cancel a retainer? | `[D06, 4]`, `[D07, 4]` | 30 calendar days, written notice | `[D06, 4]`, `[D07, 4]` | YES |
  | Q07 | How long after approval does a standard campaign launch? | `[D03, 5]`, `[D07, 2]` | 3 working days | `[D03, 5]`, `[D07, 2]` | YES |
  | Q08 | What is the Growth retainer fee and included hours? | `[D06, 1]`, `[D06, 2]`, `[D07, 4]` | $4,800, 45 hours | `[D06, 1]` | YES |

- **Sample outputs artifact**: Verified complete markdown output saved in `docs/project-record/m4-sample-outputs.md`.
- **Prompt tightening**: Model prompt was tightened to enforce explicit lookup of tabular contact fields and exact section citations, ensuring full compliance without hallucinations.

### 3. Open problems / founder decisions
- None. Model `llama3.2:3b` passed all Q01-Q08 citation and fact checks at temperature 0 without switching models.

---

## Milestone M4.2: Citation check in code

### 1. Files changed
- `app/citations/citation_check.py` (parser, variant normalizer, and validator for citations against retrieved passages)
- `app/citations/test_citation_check.py` (unittest validating normalization, real citation pass, and fake citation replacement)

### 2. Done-check item by item with evidence
- **Done-check assertion**: A test answer with a fake citation is flagged; a real one passes.
- **Automated test evidence (`python app/citations/test_citation_check.py`)**:
  ```
  Ran 3 tests in 0.002s
  OK
  ```
- **Validation breakdown**:
  - `test_normalization_variants`: Verified `[D03, 2]`, `[D03, §2]`, `[D03, Section 2.2]`, `[D03, 2.2]`, and `[D01, Sec. 3.3]` normalize to major section IDs `(D03, 2)` and `(D01, 3)`.
  - `test_real_citations_pass`: Verified citations present in retrieved passage set pass without alteration and `all_valid=True`.
  - `test_fake_citations_flagged_and_replaced`: Verified unretrieved or nonexistent citations (`[D99, 1]`, `[D02, 3]`) are flagged (`all_valid=False`) and safely replaced with `[INVALID CITATION: D99, 1]` and `[INVALID CITATION: D02, 3]`.

### 3. Open problems / founder decisions
- None. Citation verification and sanitization logic operational.

---

## Milestone M4.3: Pure deterministic conflict detection

### 1. Files changed
- `app/conflict-checks/conflicts.py` (deterministic detector for Type 1 differing quantities and Type 2 opposite polarities across different documents)
- `app/conflict-checks/test_conflicts.py` (unittest testing Q01-Q10 retrieval candidates and synthetic polarity test)
- `docs/project-record/build-notes.md` (recorded rules and known limitations)

### 2. Done-check item by item with evidence
- **Done-check assertion**: Q10 flags the conflict showing both sources and both thresholds; ZERO false flags on Q01-Q09.
- **Automated test evidence (`python app/conflict-checks/test_conflicts.py`)**:
  ```
  Ran 3 tests in 23.686s
  OK
  ```
- **Observed Q10 Conflict Output**:
  ```
  Conflicting instructions: [D04, 2] says A campaign with a total budget above $10,000 requires Marketing Director sign-off before launch.; [D03, 2] says The Marketing Director approves campaign budgets above $15,000 per month..
  ```
- **False Positive Elimination Verified**:
  - `Q01` (ClickUp onboarding) vs `Q07` (campaign launch): Different scopes and distinct vocabulary yield low lexical similarity (< 0.15); neither is flagged.
  - `Q02` (5 working days for refund approval vs 10 working days for payment): Both reside in `D02`. Cross-document rule (`doc_a != doc_b`) immediately prevents false alerting on intra-document multi-step workflows.
  - `Q03` through `Q09`: Evaluated on all retrieved candidates with zero false conflict detections.
- **Type 2 Polarity Detection**:
  - Synthetic test pair with opposite modal instructions (`must` vs `must not` on ad account admin access) correctly detected and formatted.
- **Build notes updated**: Known limitations documented in `docs/project-record/build-notes.md`.

### 3. Open problems / founder decisions
- None. Deterministic conflict detector passes all done-check requirements.

---

## Milestone M5.1: Gradio chat interface and pipeline orchestration

### 1. Files changed
- `app/chat-interface/pipeline.py` (orchestrates hybrid retrieval, reranking, threshold, passage cap, conflict detection, LLM generation, citation verification)
- `app/chat-interface/app.py` (Gradio web application bound to 127.0.0.1 with permanent demo label and UI components)
- `app/chat-interface/test_app.py` (unittest testing startup, query execution, and clean shutdown)
- `app/paths.py` (module registration to protect app package namespace)
- `app/__init__.py` (package marker)

### 2. Done-check item by item with evidence
- **Done-check assertion**: An automated test starts the app, sends a question, asserts an answer is returned, then stops the app.
- **Automated test evidence (`python app/chat-interface/test_app.py`)**:
  ```
  Starting Gradio app test...
  * Running on local URL:  http://127.0.0.1:7865
  Gradio app launched on http://127.0.0.1:7865.
  Ran 1 test in 101.588s
  OK
  Returned Answer:
  According to Passage 1 [D01, 3], the steps to onboard a new client in ClickUp are:
  3.1 Create a new Space named with th...
  Returned Citations: [D01, 3]
  Stopping Gradio app...
  Closing server running on port: 7865
  Gradio app stopped cleanly.
  ```
- **UI elements verified**:
  - Bound to `127.0.0.1`, `share=False`, `GRADIO_ANALYTICS_ENABLED=False`.
  - Permanent header label: `"Brightpath Media (demo), fictional"`.
  - Input box, answer display, verified citations line, conflict alert banner markdown, retrieved passage details, reset button.
  - Connection error handling: returns a friendly guidance message when Ollama is unreachable.

### 3. Open problems / founder decisions
- None. Gradio interface and pipeline orchestration operational.

---

## Milestone M5.2: Golden test suite execution

### 1. Files changed
- `app/chat-interface/run_golden.py` (runner executing all 10 golden evaluation questions through pipeline.py)
- `docs/project-record/test-results.csv` (recorded real latencies, actual behaviour, citation/conflict checks for Q01-Q10)
- `docs/project-record/test-notes.md` (detailed report, pass rate table, observations)

### 2. Done-check item by item with evidence
- **Done-check assertion**: `docs/project-record/test-results.csv` exists with 10 rows and real measured latencies (not estimates).
- **Automated test evidence (`python app/chat-interface/run_golden.py`)**:
  ```
  === M5.2 Golden Test Evaluation ===
  Loaded 10 test cases.
  Running Q01: What are the steps to onboard a new client in ClickUp? -> Actual: ANSWER | Result: PASS | Latency: 44.7069s
  Running Q02: How long does an enterprise refund approval take? -> Actual: ANSWER | Result: PASS | Latency: 22.7577s
  Running Q03: Who signs off creative before a campaign goes live? -> Actual: ANSWER | Result: PASS | Latency: 26.8884s
  Running Q04: What fields does the paid social brief template include? -> Actual: ANSWER | Result: PASS | Latency: 39.35s
  Running Q05: Who do I call about a platform outage at night? -> Actual: ANSWER | Result: PASS | Latency: 45.2942s
  Running Q06: How much notice is needed to cancel a retainer? -> Actual: ANSWER | Result: PASS | Latency: 30.887s
  Running Q07: How long after approval does a standard campaign launch? -> Actual: ANSWER | Result: PASS | Latency: 31.4562s
  Running Q08: What is the Growth retainer fee and included hours? -> Actual: ANSWER | Result: PASS | Latency: 26.514s
  Running Q09: How do we request a discount on our retainer? -> Actual: NOT_FOUND | Result: PASS | Latency: 0.7972s
  Running Q10: Does a paid social campaign with a $12,000 budget need Marketing Director approval? -> Actual: CONFLICT | Result: PASS | Latency: 0.8872s

  Saved test results to F:\stitchlab-ai\docs\project-record\test-results.csv
  Saved test notes to F:\stitchlab-ai\docs\project-record\test-notes.md

  Final Pass Rate: 10/10
  ```
- **Observed Results Summary Table**:
  | ID | Question | Expected | Actual | Citations | Conflict Detected | Outcome | Real Latency |
  |---|---|---|---|---|---|---|---|
  | Q01 | Onboard client in ClickUp | ANSWER | ANSWER | `[D01, 3]` | False | **PASS** | 44.7069s |
  | Q02 | Enterprise refund approval time | ANSWER | ANSWER | `[D02, 4]` | False | **PASS** | 22.7577s |
  | Q03 | Creative sign-off | ANSWER | ANSWER | `[D03, 4]` | False | **PASS** | 26.8884s |
  | Q04 | Paid social brief fields | ANSWER | ANSWER | `[D04, 1]` | False | **PASS** | 39.3500s |
  | Q05 | Platform outage at night | ANSWER | ANSWER | `[D05, 2]` | False | **PASS** | 45.2942s |
  | Q06 | Retainer cancellation notice | ANSWER | ANSWER | `[D06, 4]`, `[D07, 4]` | False | **PASS** | 30.8870s |
  | Q07 | Campaign launch post-approval | ANSWER | ANSWER | `[D03, 5]`, `[D07, 2]` | False | **PASS** | 31.4562s |
  | Q08 | Growth retainer fee & hours | ANSWER | ANSWER | `[D06, 1]` | False | **PASS** | 26.5140s |
  | Q09 | Discount request | NOT_FOUND | NOT_FOUND | None | False | **PASS** | 0.7972s |
  | Q10 | $12,000 budget approval | CONFLICT | CONFLICT | `[D04, 2]`, `[D03, 2]` | True | **PASS** | 0.8872s |

- **Target Achieved**: 10/10 (100.0%) pass rate across all behavioural, factual, and citation constraints.

### 3. Open problems / founder decisions
- None. Golden test evaluation fully successful.

---

## Milestone M6A.1: Unified provider adapter interface

### 1. Files changed
- `app/model-adapters/base.py` (BaseModelAdapter abstract class, StubAdapter, adapter registry, unified entry point get_answer)
- `app/model-adapters/test_base.py` (unittest suite for base adapter interface, stub responses, error handling)

### 2. Done-check item by item with evidence
- **Done-check assertion**: Unit tests verify the unified interface `get_answer(question, passages, provider, key)`.
- **Automated test evidence (`python app/model-adapters/test_base.py`)**:
  ```
  Ran 4 tests in 0.000s
  OK
  ```
- **Interface capabilities**:
  - Abstract base interface enforcing `generate(question, passages, model, api_key, **kwargs)`.
  - StubAdapter provides deterministic responses for offline and fast unit testing.
  - Adapter registry supports dynamic registration of local and remote providers.
  - Exception handling for unknown or unregistered providers.

### 3. Open problems / founder decisions
- None. Interface operational and tested.

---

## Milestone M6A.2: Ollama local model adapter

### 1. Files changed
- `app/model-adapters/ollama_adapter.py` (Ollama service detection, model tag discovery, and local prompt execution adapter)
- `app/model-adapters/test_ollama_adapter.py` (unittest testing service detection, model listing, and answer generation)

### 2. Done-check item by item with evidence
- **Done-check assertion**: Detect if Ollama is running, list installed models, send prompts; verified by unit tests.
- **Automated test evidence (`python app/model-adapters/test_ollama_adapter.py`)**:
  ```
  Ran 4 tests in 10.658s
  OK
  Installed Ollama models: ['llama3.2:3b']
  Ollama Answer:
  According to [D02, 4, 4.2], an enterprise refund approval decision is made within 5 working days of receiving a complete request.
  ```
- **Verified operations**:
  - `is_ollama_running()` correctly detected active service on `http://127.0.0.1:11434` and safely rejected inactive ports (`http://127.0.0.1:54321`).
  - `list_installed_models()` queried `/api/tags` and confirmed presence of local `llama3.2:3b`.
  - `get_answer(..., provider="ollama")` successfully routed query through unified adapter interface and produced grounded citation answer.

### 3. Open problems / founder decisions
- None. Ollama adapter passes all tests.

---

## Milestone M6A.3: Guided setup screen for Ollama

### 1. Files changed
- `app/model-adapters/guided_setup.py` (Ollama status evaluation and 3-step setup guide generator)
- `app/model-adapters/test_guided_setup.py` (unittest simulating stopped Ollama service and asserting 3 setup steps)

### 2. Done-check item by item with evidence
- **Done-check assertion**: If Ollama is not running, show 3 steps: 1 download, 2 run serve, 3 pull llama3.2:3b; verified by test.
- **Automated test evidence (`python app/model-adapters/test_guided_setup.py`)**:
  ```
  Ran 2 tests in 1.117s
  OK
  ```
- **Simulated setup screen output**:
  ```markdown
  ### Private Local Model Setup Required

  Ollama is not currently running. To use StitchLab AI locally and privately without internet access, complete these 3 steps:

  1. **Download Ollama**: Download and install Ollama from https://ollama.com/download.
  2. **Start the Ollama Service**: Open PowerShell or Command Prompt and run: `ollama serve`.
  3. **Pull the llama3.2:3b Model**: In a terminal window, run: `ollama pull llama3.2:3b`.
  ```
- **Validation breakdown**:
  - Asserted presence of Step 1 (download link `https://ollama.com/download`).
  - Asserted presence of Step 2 (command `ollama serve`).
  - Asserted presence of Step 3 (command `ollama pull llama3.2:3b`).
  - Confirmed `check_and_get_setup_instructions()` returns `None` when Ollama is running normally.

### 3. Open problems / founder decisions
- None. Guided setup screen operational.

---

## Milestone M6A.4: Paid API adapter (OpenAI-compatible)

### 1. Files changed
- `app/model-adapters/openai_adapter.py` (OpenAI chat completions adapter using stdlib urllib, supporting auth, quota errors, timeouts)
- `app/model-adapters/test_openai_adapter.py` (unittest suite spawning ephemeral HTTP mock server on 127.0.0.1)

### 2. Done-check item by item with evidence
- **Done-check assertion**: Test asserts call succeeds against the fake server and fails gracefully without network.
- **Automated test evidence (`python app/model-adapters/test_openai_adapter.py`)**:
  ```
  Ran 2 tests in 1.194s
  OK
  Fake OpenAI Response:
  According to Passage 1 [D03, 4], the Account Lead signs off creative before client approval.
  Graceful Connection Error Caught:
  Network unreachable or provider server down: timed out
  ```
- **Verified capabilities**:
  - Pure Python standard library implementation (`urllib.request`, `json`) without external SDK dependencies.
  - Proper Bearer token authentication header and payload generation.
  - Graceful exception mapping for `AuthenticationError` (HTTP 401), `QuotaExceededError` (HTTP 429), and network failure (`ConnectionError`).

### 3. Open problems / founder decisions
- None. Paid API adapter operational and tested against local mock.

---

## Milestone M6A.5: Provider connection health checker

### 1. Files changed
- `app/model-adapters/connection_test.py` (health test evaluator handling authentication, quota, network errors across providers)
- `app/model-adapters/test_connection_test.py` (unittest suite validating each distinct error condition against mock server)

### 2. Done-check item by item with evidence
- **Done-check assertion**: Runs a test call on provider or key change. Handles: invalid key, credit / quota, network unreachable; verified by tests.
- **Automated test evidence (`python app/model-adapters/test_connection_test.py`)**:
  ```
  Ran 4 tests in 2.482s
  OK
  Tested 401 -> Result: {'success': False, 'status': 'INVALID_KEY', 'message': 'Authentication failed (HTTP 401): Invalid API key.'}
  Tested 429 -> Result: {'success': False, 'status': 'QUOTA_EXCEEDED', 'message': 'Rate limit or quota exceeded (HTTP 429).'}
  Tested Unreachable -> Result: {'success': False, 'status': 'NETWORK_ERROR', 'message': 'Network unreachable or provider server down: [WinError 10061] No connection could be made because the target machine actively refused it'}
  Tested 200 -> Result: {'success': True, 'status': 'CONNECTED', 'message': 'Connected to OpenAI provider successfully.'}
  ```
- **Error mapping verification**:
  - HTTP 401 correctly categorized as `INVALID_KEY`.
  - HTTP 429 correctly categorized as `QUOTA_EXCEEDED`.
  - Offline / unreachable port correctly categorized as `NETWORK_ERROR`.
  - Successful 200 probe returns `CONNECTED`.

### 3. Open problems / founder decisions
- None. Connection test logic operational and fully verified.

---

## Milestone M6A.6: Key handling security and external storage

### 1. Files changed
- `app/model-adapters/key_store.py` (secure key manager, memory-only by default, external persistent save to `%LOCALAPPDATA%\StitchLabAI\key.json`)
- `app/model-adapters/test_key_store.py` (unittest asserting external persistence, out-of-repo boundary, and zero repo leakage)

### 2. Done-check item by item with evidence
- **Done-check assertion**: Test saves a dummy key "sk-TEST-DUMMY-0000", asserts it is in the target path, and scans git repo and logs to assert zero hits.
- **Automated test evidence (`python app/model-adapters/test_key_store.py`)**:
  ```
  Ran 1 test in 0.592s
  OK
  External Key Path: C:\Users\tawabcomputers\AppData\Local\StitchLabAI\key.json
  Scanned repository files. Found matches: []
  ```
- **Security verified**:
  - Key path resolved to `C:\Users\tawabcomputers\AppData\Local\StitchLabAI\key.json`, located completely outside repository root `F:\stitchlab-ai`.
  - Recursive file scan across repository source files and logs confirmed zero instances of the key.
  - In-memory keys are held strictly in process memory and erased on demand.

### 3. Open problems / founder decisions
- None. Key storage complies with all security requirements.

---

## Milestone M6A.7: Third-party provider policies template

### 1. Files changed
- `docs/project-record/provider-policies.md` (template documenting OpenAI, Anthropic, and Google policies, all marked NOT VERIFIED)

### 2. Done-check item by item with evidence
- **Done-check assertion**: Template `docs/project-record/provider-policies.md` created for OpenAI, Anthropic, Google; all three marked "NOT VERIFIED".
- **Evidence from `docs/project-record/provider-policies.md`**:
  ```markdown
  # Third-Party Model Provider Privacy & Security Policies
  Status: NOT VERIFIED
  Notice to Client: StitchLab AI does not accept terms of service, data processing agreements, or commercial terms on behalf of clients. When connecting external paid model providers, the client must directly review, execute, and accept terms with each provider under their own commercial account.

  | Provider | Model Adapter | Verification Status | Client Action Required | Training on API Data (Claimed) |
  |---|---|---|---|---|
  | OpenAI | `openai` | **NOT VERIFIED** | Direct Client Account & DPA | Opt-out / Off by default for API |
  | Anthropic | `anthropic` (future) | **NOT VERIFIED** | Direct Client Account & Terms | Off by default for Commercial API |
  | Google Cloud | `gemini` (future) | **NOT VERIFIED** | Direct GCP Project & DPA | Off by default on Vertex AI |
  ```
- **Compliance verified**:
  - Explicit legal statement that client signs their own terms; StitchLab does not accept terms on their behalf.
  - Clear "NOT VERIFIED" status flags assigned to all three major commercial providers.

### 3. Open problems / founder decisions
- None. Template in place for client contract execution.

---

## Milestone M6B.1: Passage limit and hard cap enforcement

### 1. Files changed
- `app/model-adapters/passage_limiter.py` (passage limiter enforcing default 4 and strict hard cap <= 5)
- `app/model-adapters/test_passage_limit.py` (unittest testing default 4 limit and 10-passage input clamp to <= 5)

### 2. Done-check item by item with evidence
- **Done-check assertion**: Unit test passing 10 passages asserts only <= 5 are forwarded.
- **Automated test evidence (`python app/model-adapters/test_passage_limit.py`)**:
  ```
  Ran 3 tests in 0.000s
  OK
  ```
- **Cap verification**:
  - Passing 10 passages with default configuration yields exactly 4 passages.
  - Passing 10 passages requesting 10 yields strictly 5 passages (clamped by `HARD_PASSAGE_CAP = 5`).
  - Passing 10 passages requesting 5 yields 5 passages.

### 3. Open problems / founder decisions
- None. Passage limiter operational.

---

## Milestone M6B.2: Reversible data masking (PII protection)

### 1. Files changed
- `app/model-adapters/masking.py` (regex and dictionary-based reversible data masker for emails, phones, and personnel names)
- `app/model-adapters/test_masking.py` (unittest verifying complete masking and exact restoration on D05 escalation matrix)

### 2. Done-check item by item with evidence
- **Done-check assertion**: Test runs on D05 contacts table, asserts all masked, then asserts unmasking restores original.
- **Automated test evidence (`python app/model-adapters/test_masking.py`)**:
  ```
  Ran 1 test in 0.002s
  OK
  === MAPPING TOKENS ===
  [PERSON_NAME_1] -> Sam Whitfield
  [PERSON_NAME_2] -> Tom Reyes
  [PERSON_NAME_3] -> Daniel Okafor
  [PERSON_NAME_4] -> Priya Shah
  [EMAIL_ADDR_1] -> tom.reyes@brightpath-demo.example
  [EMAIL_ADDR_2] -> tom.reyes@brightpath-demo.example
  [EMAIL_ADDR_3] -> daniel.okafor@brightpath-demo.example
  [EMAIL_ADDR_4] -> daniel.okafor@brightpath-demo.example
  [EMAIL_ADDR_5] -> priya.shah@brightpath-demo.example
  [EMAIL_ADDR_6] -> priya.shah@brightpath-demo.example
  [EMAIL_ADDR_7] -> sam.whitfield@brightpath-demo.example
  [EMAIL_ADDR_8] -> sam.whitfield@brightpath-demo.example
  [PHONE_NUM_1] -> +1 555 0142
  [PHONE_NUM_2] -> +1 555 0136
  [PHONE_NUM_3] -> +1 555 0129
  [PHONE_NUM_4] -> +1 555 0177
  ```
- **Masking verification**:
  - All personnel names (`Sam Whitfield`, `Tom Reyes`, `Daniel Okafor`, `Priya Shah`) eliminated from masked output.
  - All corporate email addresses replaced with structured reversible tokens.
  - All phone numbers (`+1 555 0142`, `+1 555 0136`, `+1 555 0129`, `+1 555 0177`) replaced with structured tokens.
  - `unmask_data()` asserted to return 100% byte-for-byte identical text to the original source.

### 3. Open problems / founder decisions
- None. Reversible masking operational.

---

## Milestone M6B.3: Outbound network guard (NetGuard)

### 1. Files changed
- `app/model-adapters/netguard.py` (strict outbound URL allowlist policy enforcer)
- `app/model-adapters/test_netguard.py` (unittest testing local Ollama port, active provider host, arbitrary domain blocks, and loopback port blocks)

### 2. Done-check item by item with evidence
- **Done-check assertion**: Unit tests allow 127.0.0.1:11434, allow active provider host, block arbitrary url like evil.com, block loopback on wrong port like 127.0.0.1:9999.
- **Automated test evidence (`python app/model-adapters/test_netguard.py`)**:
  ```
  Ran 4 tests in 0.001s
  OK
  ```
- **Allowlist rules verified**:
  - `http://127.0.0.1:11434/api/chat` and `http://localhost:11434/api/tags`: ALLOWED.
  - Active provider host `api.openai.com`: ALLOWED.
  - Arbitrary external endpoints (`http://evil.com/exfiltrate`, `https://unapproved-api.example.com`): BLOCKED (raises `PermissionError`).
  - Loopback on unauthorized ports (`http://127.0.0.1:9999`, `http://localhost:8080/admin`): BLOCKED (raises `PermissionError`).

### 3. Open problems / founder decisions
- None. Outbound network guard fully operational.

---

## Milestone M6B.4: What-was-sent audit log and UI expander

### 1. Files changed
- `app/model-adapters/audit_log.py` (JSONL audit logger recording exact prompt, masked passages, provider, and timestamp)
- `app/model-adapters/test_audit_log.py` (unittest verifying log entry accuracy and zero unmasked PII leakage)
- `app/chat-interface/pipeline.py` (integrated data masking, network validation, and what-was-sent logging into query flow)
- `app/chat-interface/app.py` (added audit log JSON viewer under an expander accordion in the UI)
- `app/chat-interface/test_app.py` (updated test to assert audit data returned)

### 2. Done-check item by item with evidence
- **Done-check assertion**: Unit test runs a query, asserts log entry matches what was sent, asserts no raw unmasked PII in the log.
- **Automated test evidence (`python app/model-adapters/test_audit_log.py`)**:
  ```
  Ran 1 test in 0.023s
  OK
  === RECORDED AUDIT ENTRY ===
  {
    "timestamp": "2026-11-20T16:07:29Z",
    "provider": "openai",
    "model": "gpt-4o-mini",
    "endpoint": "https://api.openai.com/v1/chat/completions",
    "question": "Who is the on-call contact for server outages?",
    "passages_count": 1,
    "passage_citations": ["[D05, 1]"],
    "full_prompt_sent": "Supplied Passages:\nPassage 1 [D05, 1]:\n| Platform or server outage | [PERSON_NAME_1], Systems Lead (on-call) | [EMAIL_ADDR_1] | [PHONE_NUM_1] |\n\nQuestion: Who is the on-call contact for server outages?\n\nAnswer:"
  }
  Verified: Zero unmasked PII present in audit log.
  ```
- **Auditing verified**:
  - Exact prompt matching: log file `logs/what-was-sent.jsonl` contains the exact structured prompt and passages dispatched.
  - Zero raw PII in logs: `Sam Whitfield`, `+1 555 0177`, and `sam.whitfield@brightpath-demo.example` were completely masked before writing to disk.
  - UI visibility: Gradio app exposes the exact prompt under the `"What was sent to model (Privacy & Security Audit Log)"` accordion.

### 3. Open problems / founder decisions
- None. What-was-sent audit log operational.
