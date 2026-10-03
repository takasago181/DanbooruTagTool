# Foundation Batch B — preserved checkpoint / external reuse gate

Baseline: main `0193cee41c52050e680767f722efcdcef6de481f`, PR #261 merged.
Branch: `foundation/batch-b`. Production remains #245 LKG; no install or UserData mutation.

## Work preserved before the revised gate

- #250: 2,976 historical evidence files and their exact original Git hashes/bytes
  frozen under remote tag `archive/foundation-pre-batch-b-20261003`. Normal
  checkout removes 259,721,312 bytes across 3,192 archived evidence/tool/workflow
  files. Full source replay restored and verified, without rebuilding authority.
- 59 tracked fixtures relocated into test-only Inputs; 60 oracles indexed including
  existing Issue76 audit. Original Git bytes and accepted test representation have
  separate hashes/sizes. 42 CRLF originals keep the previously accepted LF test
  representation; no CSV semantic values, canonical identity or accepted hash changed.
- #251 already reached archive of 197 historical scripts/test/build helpers before
  the revised instruction. They remain recoverable, not rewritten. Shared health
  uses Maintenance verify instead of old source/queue checks; duplicate manifest
  validation and stale native exit-code handling corrected. Toolchain route added.
- #252: 19 main workflow recipes archived, unique checks retained in semantic CI.
  403 historical workflow registry entries disabled; IDs/prior state/recovery in
  `BATCH_B_GITHUB_LEDGER.json`. Four absent-main recipes have exact YAML retained.
- 73 remote branch refs removed with expected-SHA leases, closed-Issue + exact-main
  ancestry + no-worktree-owner proof. Unique/research/KNOWLEDGE/production and all
  attached branch owners retained. Local branches/history not destroyed.
- Existing 42 worktrees retained; this task adds one (43 total), zero removals.
  Batch A's 65 unsaved research / 5 KNOWLEDGE files and protected ignored assets
  remain in their original workspaces; no repeat ignored inventory/cleanup.
- Task helper now fixes new task `core.autocrlf=false` rather than inheriting legacy
  root config. One App source file has only EOL normalization required by existing
  attributes, verified with an empty ignore-EOL diff; no product execution change.
- Routing/README and closeout ownership/recovery guidance updated.

## Verification

- Targeted .NET: 21 PASS / 1 protected SKIP; relocated facet/taxonomy checks: 6 PASS.
- Final full normal Release: 353 PASS / 22 explicit protected/live/generator SKIP / 0 FAIL.
- Affected protected #118 fixtures and TEMP-only generation: 6 PASS / 0 SKIP / 0 FAIL.
- Maintenance: 22 PASS / 1 production opt-in SKIP; workspace tests: 2 PASS.
- Runtime pipeline disposable manifest/shape/UserData contracts PASS; Forge JS syntax PASS.
- Maintenance accepted manifest verify PASS (124,895 rows); no compiler input/code
  or semantic changes, so Batch A full ordered parity was not repeated.
- Archive replay original hashes: 3,252 PASS; retained oracle representation hashes PASS.
- Read-only workstation health: no failure; warnings are the uncommitted task,
  unchanged older installed source, and absent shortcut in this task checkout.
- Production 19 files including 14 UserData files byte-identical; result in
  `BATCH_B_PROTECTED_RESULT.json`. No publish, installed runtime, Library/LoRA,
  LKG or protected legacy/data-root change. No GUI needed for these changes.
- PR CI pending checkpoint publication; results will be recorded after push.

## Revised mandatory gate (user direction during this task)

P0 + Batch A are not rolled back. Safe results above are retained. Further large
#251 integration/rewrite/deletion, large #253 architecture changes and equivalent
new custom implementations are STOPPED pending actual upstream source inspection
and a DTT-code-mapped KEEP/REUSE/WRAP/PORT/REWRITE/REPLACE/ARCHIVE/REJECT matrix.
#250 separation remains authorized. No additional large tool cleanup has begun
after the revised gate. Research completion must be reported and STOP again;
it does not authorize implementation of proposed replacements/new features.

## Recovery / remaining work

Archive replay: `research/README.md`. Source rollback: revert this Batch B commit
on a separate branch; no history rewrite. Remote branches/workflow enable commands
are individually in `BATCH_B_GITHUB_LEDGER.json`; revert alone does not undo those
external operations. Existing production/LKG need no rollback because unchanged.

History/clone object storage is not compacted. Unmerged and local-only research
remains protected. #213 corpus/branch and KNOWLEDGE #44 are retained. Broad #253,
#254, #255, production promotion/post-Foundation LKG, #230 and #256 feature work
remain outside this checkpoint. Next: external reuse decision research, then STOP.
