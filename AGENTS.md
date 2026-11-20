# Rules for the coding agent (read before every task)

## Source of truth
- Follow docs/project-record/StitchLab_File1_Milestone_Plan_v1.2.pdf and StitchLab_File2_Project_Record_v1.1.pdf exactly.
- Milestone IDs (M0.1, M2.3 and so on) and their done-checks come from File 1.
- If a task conflicts with these files, stop and ask. Do not improvise.

## How to work
- Work on ONE milestone at a time.
- Stop after its done-check. Report the evidence for each done-check item.
- Wait for the founder to approve before starting the next milestone.
- After each approved milestone, commit with the milestone ID in the message, for example "M2.1 parse documents".

## Non-negotiable rules
- No paid API. The default model is local Ollama, using llama3.2:3b on this PC.
- Ollama on this PC is at F:\Ollama\ollama.exe and models are in F:\Ollama_Models.
- Never write, store, print, or commit API keys. Never commit .env, key files, logs, local-index/, or models.
- Use only the fictional Brightpath documents in documents/fictional-brightpath/. Never use real client data.
- Label all demo content "Brightpath Media (demo), fictional."
- Passages sent to any external model: at most 3 to 5, masked as [NAME], [EMAIL], [PHONE], [ID].
- Conflict detection covers exactly two types: different numbers for the same item, and opposite yes/no answers.
- Answers must cite sources. When evidence is weak, answer "Not found in your documents."
- Ask before adding any new library, and record its exact version.

## Hardware limits
- 8 GB RAM, Intel HD Graphics 520 (no dedicated GPU). Run heavy steps one at a time.
- C: drive is nearly full (about 1.8 GB free). Put project data and caches on F: where possible.

## Reporting format
After each milestone, write a short report:
1. What changed (file list).
2. Done-check result, item by item, with evidence.
3. Open problems and what needs the founder's decision.