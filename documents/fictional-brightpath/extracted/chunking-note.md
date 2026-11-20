# Brightpath Media (demo) Chunking Note

**Document ID**: chunking-note.md  
**Milestone**: M2.2  
**Rule**: Split extracted documents D01..D07 by `##` section heading. Company profile is excluded from searchable knowledge base.  

## Chunking Rules
- **Boundary**: Each section beginning with `## <number>. <title>` forms exactly one chunk.
- **Tables**: Kept intact within their respective section (e.g. D05 escalation matrix, D06 pricing tiers).
- **Metadata fields**: `doc_id`, `section_id`, `section_title`, `page` (`null` for Markdown source), `version`, `last_reviewed`, `citation`.
- **Citation form**: `[DocID, Section]` (e.g. `[D03, 2]`). Normalized from any paragraph citations (e.g. 2.2 -> 2).
- **Short section merge fallback**: Evaluated. All sections are coherent policy blocks (>95 chars); no sections required merging.

## Summary Statistics
- Total searchable documents: 7
- Total chunks generated: 29

| Document ID | Title / Topic | Chunks | Version | Last Reviewed |
|---|---|---|---|---|
| D01 | Client Onboarding SOP | 5 | 2.1 | 2026-03-01 |
| D02 | Enterprise Refund Process | 5 | 1.4 | 2026-02-15 |
| D03 | Campaign Approval Rules | 5 | 3.0 | 2026-04-10 |
| D04 | Paid Social Brief Template | 3 | 1.2 | 2026-01-20 |
| D05 | Escalation Contacts | 3 | 1.6 | 2026-03-20 |
| D06 | Retainer Pricing & Cancellation | 4 | 2.0 | 2026-02-01 |
| D07 | Client FAQ | 4 | 1.1 | 2026-04-02 |

## Sample Chunks

### Chunk `D01_3` ([D01, 3])
```json
{
  "chunk_id": "D01_3",
  "doc_id": "D01",
  "section_id": "3",
  "section_title": "Setting up the client in ClickUp",
  "page": null,
  "version": "2.1",
  "last_reviewed": "2026-03-01",
  "citation": "[D01, 3]"
}
```
Text content:
> ## 3. Setting up the client in ClickUp
> 
> 3.1 Create a new Space named with the client's legal name.
> 
> 3.2 Add the standard folders: Briefs, Creative, Reporting, and Contracts.
> 
> 3.3 Create the onboarding task list. Each task must be completed in order:
> 
> 1. Create the Space and folders.
> 2. Upload the signed contract to Contracts.
> 3. Add the client contacts with their role and approval rights.
> 4. Complete the paid social brief (see D04).
> 5. Set up reporting access for the client.
> 6. Schedule the kickoff call.
> 
> 3.4 The Systems Lead grants ad account access only after step 3 is complete.

### Chunk `D03_2` ([D03, 2])
```json
{
  "chunk_id": "D03_2",
  "doc_id": "D03",
  "section_id": "2",
  "section_title": "Who approves",
  "page": null,
  "version": "3.0",
  "last_reviewed": "2026-04-10",
  "citation": "[D03, 2]"
}
```
Text content:
> ## 2. Who approves
> 
> 2.1 The Account Lead prepares every campaign brief.
> 
> 2.2 The Marketing Director approves campaign budgets above $15,000 per month.
> 
> 2.3 Campaigns at or below $15,000 per month are approved by the Account Lead.

### Chunk `D05_1` ([D05, 1])
```json
{
  "chunk_id": "D05_1",
  "doc_id": "D05",
  "section_id": "1",
  "section_title": "Who to contact",
  "page": null,
  "version": "1.6",
  "last_reviewed": "2026-03-20",
  "citation": "[D05, 1]"
}
```
Text content:
> ## 1. Who to contact
> 
> | Issue                     | Contact                               | Email                                                                                 | Phone              |
> |---------------------------|---------------------------------------|---------------------------------------------------------------------------------------|--------------------|
> | Account questions         | Account Lead on the client's Space    | (named in ClickUp)                                                                    | (named in ClickUp) |
> | Billing dispute           | Tom Reyes, Finance Lead               | [tom.reyes@brightpath-demo.example](mailto:tom.reyes@brightpath-demo.example)         | +1 555 0142        |
> | Creative or approvals     | Daniel Okafor, Marketing Director     | [daniel.okafor@brightpath-demo.example](mailto:daniel.okafor@brightpath-demo.example) | +1 555 0136        |
> | Client services concerns  | Priya Shah, Head of Client Services   | [priya.shah@brightpath-demo.example](mailto:priya.shah@brightpath-demo.example)       | +1 555 0129        |
> | Platform or server outage | Sam Whitfield, Systems Lead (on-call) | [sam.whitfield@brightpath-demo.example](mailto:sam.whitfield@brightpath-demo.example) | +1 555 0177        |

### Chunk `D06_1` ([D06, 1])
```json
{
  "chunk_id": "D06_1",
  "doc_id": "D06",
  "section_id": "1",
  "section_title": "Retainer tiers",
  "page": null,
  "version": "2.0",
  "last_reviewed": "2026-02-01",
  "citation": "[D06, 1]"
}
```
Text content:
> ## 1. Retainer tiers
> 
> | Tier       | Monthly fee   |   Included hours |
> |------------|---------------|------------------|
> | Essentials | $2,500        |               20 |
> | Growth     | $4,800        |               45 |
> | Enterprise | $9,500        |              100 |
