# Environment report (M0.1)

Date: 20 November 2026
Owner: Arslan Khan

| Item | Result |
|---|---|
| Computer | Windows PC, user account tawabcomputers |
| Windows version | To record (run `winver`) |
| CPU | To record (run `wmic cpu get name` if available, or Task Manager, Performance) |
| RAM | 8 GB installed (about 7.9 GB usable) |
| Graphics | Intel HD Graphics 520, shared memory, no dedicated VRAM |
| Disk, C: | About 1.8 GB free (Windows system drive, tight) |
| Disk, F: | About 57 GB free (used for models and project files) |
| Ollama program | F:\Ollama\ollama.exe |
| Model folder | F:\Ollama_Models (set with OLLAMA_MODELS) |
| Model installed | llama3.2:3b, 2.0 GB, shown by `ollama list` |
| Test prompt | "Say hello in one sentence" returned "Hello!" |
| Response time | 0.83 seconds for that short prompt only |

## Conclusions
- The model runs on this PC.
- Retrieval prompts with 3 to 5 document passages will take longer. Re-measure in M5.2 and record the real time. Do not quote this 0.83 s figure as the speed of the assistant.
- Keep C: at 5 GB or more free before installing Python packages, which may need space.
- Keep heavy programs closed while the assistant runs (8 GB RAM, no dedicated GPU).
