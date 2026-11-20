# StitchLab AI - Golden Test Evaluation Report

**Target Document Corpus**: Brightpath Media (demo, fictional)  
**Date Executed**: 2026-11-20 20:51:03  
**Pass Rate**: **10/10** (100.0%)  

## Summary Results Table

| ID | Question | Expected | Actual | Citation Check | Conflict Check | Outcome | Latency (s) |
|---|---|---|---|---|---|---|---|
| Q01 | What are the steps to onboard a new client in ClickUp? | ANSWER | ANSWER | PASS | NA | **PASS** | 44.7069 |
| Q02 | How long does an enterprise refund approval take? | ANSWER | ANSWER | PASS | NA | **PASS** | 22.7577 |
| Q03 | Who signs off creative before a campaign goes live? | ANSWER | ANSWER | PASS | NA | **PASS** | 26.8884 |
| Q04 | What fields does the paid social brief template include? | ANSWER | ANSWER | PASS | NA | **PASS** | 39.35 |
| Q05 | Who do I call about a platform outage at night? | ANSWER | ANSWER | PASS | NA | **PASS** | 45.2942 |
| Q06 | How much notice is needed to cancel a retainer? | ANSWER | ANSWER | PASS | NA | **PASS** | 30.887 |
| Q07 | How long after approval does a standard campaign launch? | ANSWER | ANSWER | PASS | NA | **PASS** | 31.4562 |
| Q08 | What is the Growth retainer fee and included hours? | ANSWER | ANSWER | PASS | NA | **PASS** | 26.514 |
| Q09 | How do we request a discount on our retainer? | NOT_FOUND | NOT_FOUND | PASS | NA | **PASS** | 0.7972 |
| Q10 | Does a paid social campaign with a $12,000 budget need Marketing Director approval? | CONFLICT | CONFLICT | NA | PASS | **PASS** | 0.8872 |

## Performance and Accuracy Observations
- **Pass Rate**: 10/10 queries met all exact behaviour, citation, and factual constraints.
- **Latencies**: All reported latencies are real observed execution durations measured sequentially on the target CPU environment.
- **Negative Refusal (Q09)**: Successfully refused with exact string `Not found in your documents.` without hallucinating fee or discount terms.
- **Planted Conflict (Q10)**: Successfully detected the $15,000 (D03) vs $10,000 (D04) approval threshold disparity and presented both sources without picking a side.
- **False Conflicts**: Zero false conflict flags occurred across Q01-Q09.

## Non-pass Explanations
None. All 10 golden evaluation queries passed.