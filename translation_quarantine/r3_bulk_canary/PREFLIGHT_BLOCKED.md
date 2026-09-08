# Issue #36 post-#41 bulk canary preflight

Status: `HOLD_SOURCE_DRIFT`

The GitHub checkpoint and `BULK_AUTOMATION_CONTRACT.md` authorize one 200-row
canary on `ui-ja/issue36-r3-bulk-canary`, but the contract requires stopping if
the current protected P0 queue differs from the queue used by the validated R3
baseline. The runner failed closed before selecting or processing any canary
row.

## Source-of-truth recovery

- GitHub Issue: #36, latest checkpoint `Post-#41 activation — controlled R3 bulk automation canary`
- Execution branch: `ui-ja/issue36-r3-bulk-canary`
- Contract commit: `e1b5783bc0f6b9847723f937225c4d5727dbae27`
- Restored branch HEAD: `e1b5783bc0f6b9847723f937225c4d5727dbae27`
- Validated R3 base/head from contract: `53f02d9b3419db8fd9099b38204c29eed289ee8e` / `1c5a2cba7f8a0c5cd7c15ad510317c75d07d8851`
- Active DEV mirror remains Issue #35; `CURRENT_DEV_TASK.md` was not changed.

## Drift evidence

| Input | Validated hash | Current protected hash |
|---|---|---|
| `translation_quarantine/missing_candidates.csv` | `29a29ed4d6ce124566be5648a3926a76b84ea9301d90fc95043f148054b1f4fc` | `cbb280869707576cbac80a472f372a0becd80d80fbbd99a8d59220f74d331be7` |
| `translation_quarantine/phase1a_review.csv` | `9a273066047579bc4896c013db9d953509a5da6727a4a211f9c47dff7c17ab71` | `d1efbc511fe7ddb35f29a15c26a143fc763168f599094a6b1337b92853070aaf` |

The current queue contains 30,629 data rows and the validated R3 selection
records a 925-row eligible pool. The source is therefore not safely
interchangeable. No queue was restored, overwritten, regenerated, or silently
substituted.

## Execution boundary

- `python -m translation_quarantine.r3.r3_bulk_run --root . --output translation_quarantine/r3_bulk_canary`
  - Result: exit 1, fail-closed with `P0 queue hash differs from the validated R3 source; refusing to switch queues`.
- No 200-row canary was selected or processed.
- No deterministic replay was run.
- No `masked_audit20_input.jsonl` or `masked_audit20_key.json` was generated.
- No blind20 self-grading was performed.
- The generic bulk layer focused tests passed: `3 passed`.

The implementation is ready to resume once DEV supplies or restores the exact
frozen #36/R3 P0 queue and Phase1A exclusion inputs. Until then, proceeding
would violate the contract's source-drift stop condition.
