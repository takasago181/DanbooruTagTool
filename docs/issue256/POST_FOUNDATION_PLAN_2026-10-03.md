# #256 after Foundation — workflow first, one Batch

User authorization selects #256 after the separately authorized Foundation production promotion. Baseline clean main `ad14d45f8d20a16cb340f1cf41433f645c5b27a6`. #247 and #249–#255 remain closed. #230/#231 and Batch 2 are not started. Old frozen implementation packs are research inputs, not binding implementation order.

## Recovered inputs / current overlap

Reused all 35 live Issue comments, the Oct 1–2 main/KNOWLEDGE snapshots in [recovery ledger](../foundation/EXTERNAL_REUSE_RECOVERY.json), and the 142-row [adoption matrix](../foundation/EXTERNAL_REUSE_MATRIX.json). No new repository audit or broad OSS search. The final Anima VAE correction excludes that local Forge installation problem from this scope. [Checkpoint index](RECONCILIATION_2026-10-03.json) links the recovered comments; their original evidence remains immutable.

| Capability / candidate | Current disposition | Reason / next boundary |
|---|---|---|
| Prompt parser, canonical/JP search, explicit workspace/Undo | KEEP / already implemented | Lossless authored surface and accepted deterministic ranking; no external cleaner replacement. |
| Forge API, 1 request/1 result, PNG verification, Library ingestion | KEEP / already implemented | Existing #228/#245 workflow already generates, checks and imports. Agent Scheduler/another generator would duplicate the backend. |
| Library → Create / P-N / eight Recipe conditions; Preset save/load | REUSE / already implemented | No new restoration workflow; Batch 1 repairs the missing identity constraint along this existing route. |
| PNG/EXIF envelope, raw infotext, Core/Data parser boundary | KEEP / Foundation complete | #253 makes another boundary rewrite unnecessary. Keep current file safety and fidelity. |
| Model identity / Recipe evolution | REUSE + native extension **Batch 1** | Preserve imported Model hash through Create/Presets/restart and enforce it before generation and in actual PNG. |
| ComfyUI / multi-generator adapters | PORT later | sd-parsers/media-metadata remain useful. Graph ambiguity/raw fragments and Library migration are a separate reviewable Batch; not prerequisites for today's Forge workflow. |
| Full Model Profiles / dialect / cutoff evidence | KEEP evidence / defer | Integrate existing Knowledge; no parallel truth DB or family-wide guidance. Batch 1 hash is execution identity, not a claim about model responsiveness. |
| LoRA local inventory, SHA, overrides, explicit add | KEEP / implemented | Remote exact-hash provider would be optional WRAP; structured trigger provenance and cache schema are deferred. |
| Intent bridge / inline autocomplete | PORT conventions / defer | Current deterministic search remains authoritative. Requires its own reviewed language/interaction acceptance, independent of Recipe identity. |
| Immutable snapshots / lineage / typed diff | REUSE framework candidates / defer | DiffPlex may help text presentation; domain identity/parent persistence remains DTT work. No second live Prompt owner or #230 trial manager. |
| Fast review / XMP | PORT UX / defer | Existing ratings/favorites/notes suffice for this Batch; sidecars must not become annotation authority. |
| Reference mining / character core | WRAP/KEEP candidates / defer | Useful later, but provider/actor ownership boundaries would expand this PR. |
| LLM/RAG/embedding/compiler, regional/ref-image generation | WRAP external tools / defer | Not needed to fix exact reproducible model selection. No mandatory Python/Node/runtime LLM stack. |
| Source updater / broad I/O/index rewrite | REUSE maintenance boundary / no action now | #251 tooling and #254 measured work already cover current need. No repeated audit/rebuild at startup. |
| Copied AGPL heuristic conflict table; unlicensed tag-assistant code | Reference only / reject direct copy | Canonical semantics, evidence and known license restrictions prevent silent code/data import. |

No wholesale REWRITE/REPLACE is justified. Already implemented capabilities are consolidated, not implemented again. The full 142-row matrix retains rejected and unresolved candidates; this table selects a workflow slice, rather than overturning that research.

## Batch 1 — pin restored Recipe checkpoint identity

Concrete gap: imported PNG `Model hash` is already stored in Library metadata, but `GenerationRecipe.FromMetadata` discarded it. A renamed/replaced checkpoint with the same name could be selected later and pass verification against its *new* API hash. Keep the historical hash as an explicit Recipe constraint.

User value: Library image → Create → save Preset → reopen → regenerate refuses a different checkpoint instead of claiming a faithful recipe. A matching name/hash can resolve an otherwise ambiguous basename. No hash prefix/fuzzy fallback or automatic clearing on Model edits. Users can explicitly change/remove the optional hash for a derivative. Missing hashes in old recipes retain current behavior. The short hash is the exact backend-declared fingerprint; it is not a full-file SHA256 guarantee or proof of bit-identical image reproduction.

Scope: optional `ModelHash`, metadata mapping, existing two editors, existing API validation/readback, backed-up transactional UserData schema/payload 2→3. Existing JSON bytes, P/N/Undo/recovery, IDs and eight scalar conditions remain intact during migration. Foundation/old version-2 clients refuse newer data rather than erase the new field. Migration occurs only on isolated fixtures in this task; **Batch 1 is not deployed**.

## Reuse decision for this feature

- [.NET / Microsoft.Data.Sqlite](../../src/DanbooruTagTool.Data/Storage.cs): REUSE existing serializer, nullable record compatibility, SQLite `BackupDatabase` and transaction; no new dependency.
- [sd-parsers Model](https://github.com/d3x-at/sd-parsers/blob/0949676c24a5bbaf26ef0aa8c362132b7b27cb5b/src/sd_parsers/data/model.py): MIT, pinned source hash `8CAFC5BE3659BE66D15925A4A0439A6E08A78D9683ED160BF6CAEFAFDFA5379C`, last inspected change April 2025, not archived. Separate optional model name/hash is a useful **design reference**, implemented in the existing .NET record. No upstream code copied. Direct WRAP would add Python/Pillow to a WPF runtime just for a scalar already parsed by DTT; rejected for compatibility/dependency/maintenance cost. Graph/generator parsing is deferred, not falsely called implemented.
- media-metadata MIT / TypeScript matrix evidence: KEEP future format/AIR candidate; Node stack does not help the selected scalar constraint. No repeated library survey or download.
- Existing DTT API capability matching and PNG parser: REUSE; only the historical constraint is missing. No new identity provider, model downloads, Forge options mutation, retry, or architectural rewrite.

For subsequent development: choose desired behavior → examine existing tool/library/implementation → check license/maintenance/compatibility/dependencies → decide adoption → implement only the gap.

## Validation / stop

Clean Release build: 0 warnings / 0 errors. Targeted: **80 PASS / 0 FAIL**. One local final full regression: **372 PASS / 25 SKIP / 0 FAIL**. Added 12 cases cover imported/saved hash, ambiguity, mismatch-before-POST, actual-PNG mismatch/output retention/no retry, UI-independent state round-trip/Undo, schema2 JSON and backup parity, migration failure rollback. Existing old-recipe/API/metadata tests remain passing.

Actual development executable isolated WPF hook: schema3 persistence and editable Model hash binding/layout PASS at 900×600 / 1400×900; renders inspected. Real production all 19 files remain identical to the post-promotion snapshot, including 14/14 UserData files. No semantic authority, research/data/legacy path move/delete. CI result is recorded in PR checks and the immutable Issue checkpoint, avoiding a second CI run merely to stamp this document.

STOP at Batch 1 PR. #256 stays OPEN for remaining decisions; no Batch 2 implementation or Batch 1 production apply. Before later deployment, preserve version2 backup; rollback from migrated version3 data requires a matching runtime or explicit restoration of its pre-migration backup.
