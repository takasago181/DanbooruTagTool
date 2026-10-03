# NOW

2026-10-04 — #276 COMPLETE / final optimization and DTT-only cleanup.
[Completion / benchmarks / cleanup / rollback](../issue276/COMPLETE_FINAL_OPTIMIZATION_2026-10-04.md).
[Final production LKG / hashes](../issue276/FINAL_PRODUCTION_LKG.json).

PR #277 merged; production source bf94b3f0. Clean build/regression 469 PASS / 26 opt-in SKIP / 0 FAIL; PR/main CI and actual practical/Regional/LoRA E2E + installed smoke PASS. Search allocation falls from 19–38 MB to a few KB with ordered-result parity; personal rule parsing and atomic persistence are consolidated. No UI or authority/schema change.

UserData 16 files, Library and Forge/Regional settings byte-identical. New final LKG lkg/production-final-optimization-20261004-bf94b3f0; immediate practical rollback lkg/production-practical-20261004-97c4cb74. Pre276 complete/consistent DB recovery and required migration backups retained. Superseded roots/generated files have verified exact local archive recovery; 23 merged task worktrees retired, all refs/history retained. C:/Codex measured logical bytes 45.36 → 18.60 GB (26.77 GB net reclaimed); unrelated directories untouched.

#230/#231/#232/#234/#235/#236/#247/#256/#276 COMPLETE; #237 not planned. No active lane. STOP. #241 UI/UX work is a separately authorized next phase and has not started.
