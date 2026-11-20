# Environment report (M0.1)

Date: 20 November 2026
Owner: Arslan Khan

| Item | Result |
|---|---|
| Computer | Windows PC, user account tawabcomputers |
| Windows version | Microsoft Windows 10 Pro (Version 10.0.18363 Build 18363) |
| CPU | Intel(R) Core(TM) i5-6300U CPU @ 2.40GHz (2 cores, 4 logical processors) |
| RAM | 8 GB installed (about 7.9 GB usable) |
| Graphics | Intel HD Graphics 520, shared memory, no dedicated VRAM |
| Disk, C: | 4.05 GB free (4,351,418,368 bytes, system drive) |
| Disk, F: | 52.24 GB free (56,092,684,288 bytes, used for models, caches, and project files) |
| Ollama program | F:\Ollama\ollama.exe |
| Model folder | F:\Ollama_Models (set with OLLAMA_MODELS) |
| Model installed | llama3.2:3b, 2.0 GB (ID: a80c4f17acd5), shown by `ollama list` |
| Test prompt (standalone) | "Say hello in one sentence" returned "Hello!" |
| Response time (standalone) | 0.83 seconds for that short prompt only |
| Memory test: RAM before Ollama | 2004.17 MB available physical RAM |
| Memory test prompt | "Reply with one short sentence about document assistants." |
| Memory test output | "Document assistants are typically administrative professionals who provide support with tasks such as data entry, document management, and document preparation." |
| Memory test elapsed time | 21.74 seconds (model weight loading + cold execution) |
| Memory test: RAM after Ollama | 538.41 MB available physical RAM (RAM delta: 1465.76 MB) |
| Memory test: Out-of-memory error | None (False) |

## Conclusions
- The model runs on this PC without out-of-memory errors.
- Retrieval prompts with 3 to 5 document passages will take longer. Re-measure in M5.2 and record the real time. Do not quote the short prompt figures as the speed of the assistant.
- Cache directories set to `F:\stitchlab-cache\{hf,pip,tmp}` via `activate-env.ps1` to prevent writes to C:.
- Keep heavy programs closed while the assistant runs (8 GB RAM, no dedicated GPU). Run heavy steps sequentially.
