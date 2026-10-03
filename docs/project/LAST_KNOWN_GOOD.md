# Last Known Good deployed runtime snapshot

Foundation promoted 2026-10-03 from clean main/source `ad14d45f8d20a16cb340f1cf41433f645c5b27a6`.
Production `C:\Codex\DanbooruTagTool-App`; LKG copy `C:\Codex\DanbooruTagTool-Production-LKG-20261003-ad14d45f`.
Tag `lkg/production-foundation-20261003-ad14d45f`.

EXE SHA256 `FCAAF7BB0F59A38F523F22B0683561E035F4740AD7ADDCD8B415677780CCB24F`.
Catalog SHA256 `F0BEC5AEDBBB4B1D26010EFFE582C2E0C26D33748DC19CC7C90206097697AC29`.
Manifest SHA256 `707F1E6479F77E7600646D4F84CF90ECFFF2C1DE7720B2685E807782A4950F9B`.

Canonical publish / bounded installed Windows start / isolated EXE Library-LoRA-metadata hooks / installed catalog search-Browse tests PASS. All 124,895 ordered semantic payloads match previous production, including HOME. Actual UserData14/14 byte-identical; schema2 unchanged. Foundation full regression/CI reused.
Forge currently stopped: new live generation SKIPPED. Interactive GUI navigation/appearance not certified; installed catalog/ViewModel tests and actual EXE WPF fixture checks passed. Exact limitations are preserved, not converted into a live-generation PASS.

[Current machine snapshot](LAST_KNOWN_GOOD.json) / [promotion report](../issue256/FOUNDATION_PRODUCTION_2026-10-03.md).
[Previous #245 LKG](../issue256/PREVIOUS_PRODUCTION_LKG_2026-10-03.json) and old backup retained.
Rollback: graceful stop, restore only five managed payloads from `C:\Codex\DanbooruTagTool-PreFoundation-Backup-20261003-ad14d45f`; keep live UserData. Batch1 schema3 is development only; if deployed later, rollback to a schema2 client requires its pre-migration data backup or a matching schema3 runtime.

The uninstalled Foundation LKG `76269b8c` remains separate. #256 Batch1 is not this deployed artifact.
