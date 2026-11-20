# StitchLab AI Build Notes

## Ingestion and Citations (M2.1)
Source documents are Markdown, so page number is null; citations use [DocID, Section].
No manual fixes were required during extraction; all 8 source documents parsed cleanly with identical headings, preserved lists, intact tables, and exact numerical strings.


## Not-found Relevance Threshold (M3.3)
- **Chosen Threshold**: `0.0` (Cross-Encoder logit scale).
- **Rule**:
  1. Retrieve top 10 candidates via Hybrid search (FTS5 + Vector merged with RRF k=60).
  2. Rerank candidates with `cross-encoder/ms-marco-MiniLM-L-6-v2`.
  3. If the top candidate's reranker score is `< 0.0`, the system halts retrieval and returns exactly `"Not found in your documents."`
  4. If top candidate score is `>= 0.0`, all candidates with score `>= 0.0` (capped at the configured passage limit) are retained as context.
- **Observed Scores Across All 10 Golden Questions**:
  | Question ID | Expected Behaviour | Top Reranker Score | Top Chunk ID | Threshold Outcome |
  |---|---|---|---|---|
  | Q01 | ANSWER | 8.3122 | D01_3 | FOUND (2 passages retained) |
  | Q02 | ANSWER | 3.7900 | D02_5 | FOUND (3 passages retained) |
  | Q03 | ANSWER | 8.7571 | D03_4 | FOUND (2 passages retained) |
  | Q04 | ANSWER | 8.8434 | D04_1 | FOUND (1 passage retained) |
  | Q05 | ANSWER | 4.2299 | D05_2 | FOUND (1 passage retained) |
  | Q06 | ANSWER | 7.0984 | D06_4 | FOUND (2 passages retained) |
  | Q07 | ANSWER | 8.9683 | D03_5 | FOUND (2 passages retained) |
  | Q08 | ANSWER | 7.9239 | D07_4 | FOUND (3 passages retained) |
  | Q09 | NOT_FOUND | -3.1991 | D02_1 | Not found in your documents. (0 passages) |
  | Q10 | CONFLICT | 3.8807 | D04_2 | FOUND (2 passages retained: D04_2, D03_2) |
- **Margin Analysis**:
  - Lowest answerable top score: `3.7900` (Q02)
  - Unanswerable top score (Q09): `-3.1991`
  - Separation margin: `6.9891` points
- **Test Set Size & Overfitting Risk**:
  The evaluation suite contains exactly 10 questions with only 1 planted negative question (Q09). A threshold of `0.0` naturally leverages the logit decision boundary of the pre-trained MS-MARCO model (positive logits imply relevance, negative logits imply non-relevance). However, evaluating against a single negative query carries a significant risk of overfitting. While effective for the Brightpath demonstration, production deployments must calibrate against a broader distribution of out-of-domain and borderline queries.

## Conflict Detection Rules and Known Limits (M4.3)
- **Algorithm**: Pure deterministic rule-based detection without LLM calls (`app/conflict-checks/conflicts.py`).
- **Conflict Types Supported**:
  1. **Type 1 (Conflicting quantities/amounts)**: Detects differing numbers/amounts with matching units or currencies (`$` amounts, `working days`, `calendar days`, etc.) across sentences of DIFFERENT documents where non-numerical lexical token overlap is high (Jaccard similarity >= 0.25).
  2. **Type 2 (Opposite polarity)**: Detects contrasting instructions (`must` vs `must not`, `required` vs `not required`, `allowed` vs `not allowed`, `can` vs `cannot`, `permitted` vs `prohibited`) across sentences of DIFFERENT documents where remaining lexical token overlap is high (Jaccard similarity >= 0.50).
- **Known Limitations**:
  1. *Lexical overlap dependency*: The detector relies on shared vocabulary/stems between sentences. Paraphrased conflicts expressing identical concepts with completely disjoint synonyms will be missed.
  2. *Cross-document scope only*: Intentionally ignores intra-document number differences (e.g. D02 section 4.2's 5 working days for approval vs section 5.1's 10 working days for payment), which prevents false alarms on staged multi-step workflows in a single document, but means intra-document inconsistencies are not flagged.
  3. *Unit/Pattern regex bounds*: Only recognizes pre-configured numerical units (currency `$`, duration patterns). Arbitrary non-standard units or unstructured numerical metrics without patterns are not compared.
  4. *Sentence-level granularity*: Cannot synthesize multi-sentence conditionality (e.g. an exception clause located three paragraphs later).

## Offline Startup Guarantee and Model Pre-downloading (M5.1)
- **Environment variables**: `HF_HUB_OFFLINE=1` and `TRANSFORMERS_OFFLINE=1` are exported in `activate-env.ps1` and initialized in `app/paths.py`. Telemetry is disabled everywhere (`ANONYMIZED_TELEMETRY=False`, `GRADIO_ANALYTICS_ENABLED=False`).
- **Pre-downloading during setup**: During initial setup, `python app/ingestion/download_models.py` caches the approved models (`sentence-transformers/all-MiniLM-L6-v2` and `cross-encoder/ms-marco-MiniLM-L-6-v2`) into `F:\stitchlab-cache\hf\hub`.
- **Startup behavior**: When the app launches, HuggingFace and Transformers operate strictly offline against cached model weights. Zero network requests or model downloads occur at startup.
- **Verification**: An automated test (`app/chat-interface/test_offline_app.py`) starts the Gradio app with all external network traffic intercepted and blocked at the socket level (`getaddrinfo` and `connect`), confirms zero external requests succeed, and verifies the app answers queries and detects conflicts using local models and indexes.

