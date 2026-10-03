# Issue 231 implementation / verified regional adapter

Explicit user authorization reopens the previously deferred scope as a bounded v1.
One implementation Batch reuses Recipe, typed Forge executor, PNG receipts, Library,
PromptParser and Experiment Lab. DTT implements no diffusion/attention engine.

Installed Forge Neo: `97b26fb404314a11dad7cdde2706da57ea53f4f2`, runtime neo-2.29.2.
Existing extension: https://github.com/hako-mikan/sd-webui-regional-prompter,
`b10c496dbcb9c94be0d5d64edda8511460cc9d28`, AGPL-3.0 (installed LICENCE).
No install, update, dependency changes or restart. This installed upstream explicitly
supports Neo; the old jessearodriguez Forge port is a reference, not a replacement.
Installed source `scripts/rp.py` ui return/process and `/script-info` agree on 20 args.
`/extensions` supplies enabled repository/commit/version. The adapter requires the
verified profile and ordered labels; unknown commits/contracts reject before POST.
No eternal generic 20-arg compatibility assumption.

Common + A + B, per-subject/common negative, explicit Horizontal=Columns (left/right),
Vertical=Rows (top/bottom), two positive ratios, lossless raw/weight/LoRA compile.
Reserved backend control words inside blocks reject rather than alter region count.
Optional common adds one BREAK-delimited common segment, with common flags matching.
Full request JSON, config and extension identity are attached in a bounded PNG iTXt
only after scalar/LoRA and RP metadata verification. Original Forge infotext stays intact.
Recipe/preset and Library recover config; unsigned receipts are local observations,
not authentication. Ordinary Recipe serialization/identity remains unchanged when
Regional is absent. Known regional recipes cannot bypass the adapter through bridge.

Composer comparison creates an ordinary baseline from the same blocks and one
RegionalMode axis in the existing Lab. Model/hash, LoRA full-file identity, seed,
steps, CFG, sampler/scheduler and resolution stay fixed. Existing durable attempts,
receipt/Library links, changed fields, metadata/config diff, human evaluation and
reopen/reproduce remain owned by Lab. No automatic leakage/quality ranking.

Evidence under `C:/Codex/DanbooruTagTool/_local/task-artifacts/issue231`:
initial direct horizontal spike PASS; development 3-request ordinary/horizontal/
vertical Lab PASS; exact PNG/Library/Recipe/preset round-trip and ordinary guard PASS.
Targeted tests cover compiler boundaries, malformed ratios/control words, capability
mismatch, zero POST on unavailable extension, applied metadata, old Recipe identity,
controlled comparison/tampering plus existing Recipe/Library/Lab regression.
Final candidate/CI/full-regression and production results recorded in closeout/LKG.

Deferred: grid, masks, additional subjects, regional LoRA guarantees on Neo DiT models,
additional fork/version adapters. v1 preserves LoRA identity and passes tokens to the
extension; it makes no promise of per-region LoRA isolation or visual leakage prevention.

Safety: real UserData never serves as test output. All runtime/DB/settings backup and
hash checks precede promotion. Existing extension source/settings stay intact; RP's
normal lastrun preset write is captured and restored to the initial backed-up bytes.
Old runtime LKG/backup remains. No broad cleanup or historical task restoration.
