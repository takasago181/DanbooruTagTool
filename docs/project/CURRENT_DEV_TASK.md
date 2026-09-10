# CURRENT DEV TASK

最終同期: 2026-09-10

## Mirror Metadata

- Source Issue: #43 `[NAMING][RESERVED] Replace Special2788 as product concept name before final Stage10 freeze handoff`
- State: active
- Activation reason: Issue #49 production promotion completed, independently audited, and merged to `main`.
- Current production main: `490f5653460804c8a40cb48d093b91d5d8dd5d9c`
- Purpose: final naming/freeze gate for the Special dictionary concept before downstream Stage10 preparation handoff.

## Current decision direction

- Preferred formal concept name: `Special Core Dictionary`
- Historical/snapshot label `Special2788` remains valid for the original 2,788-entry corpus and historical evidence.
- User-selected one-or-more Special entries remain `Core Tag Set`.
- Relationship: `Special Core Dictionary -> Core Tag Set -> Auxiliary/support -> Prompt`.

## Required work

1. Re-read Issue #43 body and latest comments.
2. Inventory active `Special2788` references and classify each as:
   - rename now
   - compatibility alias / keep internally
   - historical reference / never rewrite
3. Decide exact definitions of:
   - Special Core Dictionary
   - Special Core Entry / Special
   - Core Tag Set
4. Prefer low-risk staged naming migration. Do not perform blind global replace.
5. Do not rename protected physical paths, schemas, serialized keys, manifests, hashes, or historical evidence unless a separate compatibility review explicitly approves it.
6. Prove dictionary content, canonical identity, protected hashes/authority, and Stage9 behavior are unchanged by naming-only changes.
7. Publish/freeze the final Special dictionary snapshot terminology for KNOWLEDGE / PROMPT / #30 / #42 handoff.

## Hard boundaries

- no Stage10 production A/B
- no #36 Japanese overlay production promotion
- no dictionary content change as part of naming-only work
- no rewrite of historical Issues/commits/evidence
- no count-dependent permanent replacement name
- no protected-data path/schema change without explicit compatibility review

## Start Gate

Codex may begin only after confirming:
- `docs/project/CURRENT_STATE.md` current DEV = #43
- this file Source Issue = #43 / State active
- Issue #49 is completed/closed and main contains audited promotion HEAD `490f5653460804c8a40cb48d093b91d5d8dd5d9c`

If any mismatch exists, STOP and repair management synchronization first.
