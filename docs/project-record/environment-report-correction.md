# M0.1 environment report: corrections (20 November 2026)

Replaces the unverified fields in environment-report.md.

| Item | Verified value | How verified |
|---|---|---|
| Windows | Windows 10 Pro, version 1909, build 18363.1556 | winver (founder screenshot) |
| CPU | Intel(R) Core(TM) i5-6300U CPU @ 2.40GHz | wmic cpu get name (founder, Command Prompt) |
| RAM | 8 GB installed (about 7.9 GB usable) | wmic computersystem get totalphysicalmemory (earlier) |
| Graphics | Intel HD Graphics 520, shared memory, no dedicated VRAM | wmic path win32_VideoController (earlier) |
| Disk, C: | About 4.0 GB free at last check | fsutil volume diskfree C: |
| Disk, F: | About 49.8 GB free at last check | fsutil volume diskfree F: |

Earlier entries saying "to record" for Windows version and CPU are now replaced by the verified values above.
