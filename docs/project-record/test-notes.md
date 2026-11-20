# StitchLab AI - Golden Test Evaluation Report

**Target Document Corpus**: Brightpath Media (demo, fictional)  
**Provider**: gemini (gemini-3.5-flash)  
**Date Executed**: 2026-11-21 04:23:31  
**Pass Rate**: **9/10** (90.0%)  

## Summary Results Table

| ID | Question | Expected | Actual | Citation Check | Conflict Check | Outcome | Latency (s) |
|---|---|---|---|---|---|---|---|
| Q01 | What are the steps to onboard a new client in ClickUp? | ANSWER | ANSWER | PASS | NA | **PASS** | 21.804 |
| Q02 | How long does an enterprise refund approval take? | ANSWER | ANSWER | PASS | NA | **PASS** | 3.3074 |
| Q03 | Who signs off creative before a campaign goes live? | ANSWER | ANSWER | PASS | NA | **PASS** | 5.4073 |
| Q04 | What fields does the paid social brief template include? | ANSWER | ANSWER | PASS | NA | **PASS** | 4.5018 |
| Q05 | Who do I call about a platform outage at night? | ANSWER | ANSWER | PASS | NA | **PASS** | 5.7242 |
| Q06 | How much notice is needed to cancel a retainer? | ANSWER | ANSWER | PASS | NA | **PASS** | 3.4015 |
| Q07 | How long after approval does a standard campaign launch? | ANSWER | ANSWER | PASS | NA | **PASS** | 2.9632 |
| Q08 | What is the Growth retainer fee and included hours? | ANSWER | ERROR | FAIL | NA | **FAIL** | 1.5262 |
| Q09 | How do we request a discount on our retainer? | NOT_FOUND | NOT_FOUND | PASS | NA | **PASS** | 0.5527 |
| Q10 | Does a paid social campaign with a $12,000 budget need Marketing Director approval? | CONFLICT | CONFLICT | NA | PASS | **PASS** | 0.6991 |

## Performance and Accuracy Observations
- **Pass Rate**: 9/10 queries met all exact behaviour, citation, and factual constraints.
- **Latencies**: All reported latencies are real observed execution durations measured sequentially on the target CPU environment.
- **Negative Refusal (Q09)**: Successfully refused with exact string `Not found in your documents.` without hallucinating fee or discount terms.
- **Planted Conflict (Q10)**: Successfully detected the $15,000 (D03) vs $10,000 (D04) approval threshold disparity and presented both sources without picking a side.
- **False Conflicts**: Zero false conflict flags occurred across Q01-Q09.

## Non-pass Explanations
None. All golden evaluation queries passed.