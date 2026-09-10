# CURRENT DEV TASK

最終同期: 2026-09-10

## Mirror Metadata

- Source Issue: #43 `[NAMING][ACTIVE] Finalize Special Core Dictionary naming and freeze handoff`
- State: completed
- Activation reason: Issue #49 production promotion completed, independently audited, and merged to `main`.
- Current production main: `490f5653460804c8a40cb48d093b91d5d8dd5d9c`
- Purpose: final naming/freeze gate for the Special dictionary concept before downstream Stage10 preparation handoff.

## Final user naming decision

- Formal concept name: **`Special Core Dictionary`** — FINAL.
- `Special2788` remains only where it is a historical snapshot/corpus identifier, compatibility identifier, protected path/schema key, or immutable evidence reference.
- User-selected one-or-more Special entries remain `Core Tag Set`.
- Per-entry concept may remain `Special` where unambiguous; new prose may use `Special Core Entry` when clarity is needed.
- Relationship: `Special Core Dictionary -> Core Tag Set -> Auxiliary/support -> Prompt`.
- Do not invent a count-dependent permanent replacement name.

## Required work

1. Re-read Issue #43 body and latest comments.
2. Inventory active `Special2788` references and classify each as:
   - rename now
   - compatibility alias / keep internally
   - historical reference / never rewrite
3. Apply the final formal concept name `Special Core Dictionary` to current user-facing/current architecture documentation where safe and useful.
4. Prefer low-risk staged naming migration. Do not perform blind global replace.
5. Do not rename protected physical paths, schemas, serialized keys, manifests, hashes, or historical evidence unless a separate compatibility review explicitly approves it.
6. Prove dictionary content, canonical identity, protected hashes/authority, and Stage9 behavior are unchanged by naming-only changes.
7. Publish/freeze the final Special dictionary snapshot terminology for KNOWLEDGE / PROMPT / #30 / #42 handoff. **Completed.**
8. Produce a durable Decision/freeze record containing the exact concept definitions, reference classification, snapshot identity/count/hash, and downstream handoff rules. **Completed; root-cause audit recorded in `docs/issue43/ISSUE43_HOLD_ROOT_CAUSE_AUDIT_20260910.md`.**

## Hard boundaries

- no Stage10 production A/B
- no #36 Japanese overlay production promotion
- no dictionary content change as part of naming-only work
- no rewrite of historical Issues/commits/evidence
- no blind global search-and-replace
- no protected-data path/schema change without explicit compatibility review
- no count-dependent permanent replacement name

## Start Gate

Codex may begin only after confirming:
- `docs/project/CURRENT_STATE.md` current DEV = #43
- this file Source Issue = #43 / State completed
- Issue #49 is completed/closed and main contains audited promotion HEAD `490f5653460804c8a40cb48d093b91d5d8dd5d9c`
- Issue #43 latest checkpoint records `Special Core Dictionary` as the final user-approved formal concept name

If any mismatch exists, STOP and repair management synchronization first.
