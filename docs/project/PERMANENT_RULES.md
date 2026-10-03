# PERMANENT RULES

This file contains only project-wide invariants. Current lane status, temporary workflow, detailed Stage instructions, and Issue-specific procedure belong in live Issues or task-specific docs.

## 1. Authority and scope

1. GitHub live state is the project authority; chat memory and stale local management files are not.
2. The selected live Issue owns task scope, completion conditions, and task-specific behavior.
3. `docs/PRODUCT_GOAL_LOCK.md` owns product-level intent unless an explicitly approved decision updates it.
4. Historical Issues/docs remain provenance, not automatic current instructions.
5. When sources disagree, resolve ordinary staleness from the higher-authority live source. Stop only if unresolved ambiguity materially affects a write, protected data, accepted semantics, or production.

## 2. Codex autonomy

6. The project should constrain outcomes and safety, not micromanage implementation.
7. Codex may choose implementation order, internal architecture, helper tooling, refactor granularity, and investigation method when the task contract does not fix them.
8. Suggested steps/checklists are guidance unless explicitly identified as a hard gate.
9. Prefer the smallest safe route to the requested outcome; skip obsolete or redundant work when evidence justifies it.
10. Do not preserve historical architecture merely because it already exists, and do not rewrite healthy bounded code merely because a newer pattern exists.

## 3. Protected local/user data

11. Real `UserData` and personal Library/LoRA state are user-owned.
12. Runtime/publish operations must not delete, reset, mirror-overwrite, or silently migrate user-owned state.
13. Any required UserData migration must be explicit, backed up, transactional where practical, version-aware, and rollback/recovery capable.
14. Ignored source/derived/runtime/protected data may exist only locally. GitHub absence is not proof that it is disposable.
15. `git clean -fdx` and `git clean -fdX` are prohibited in the project workspace.
16. Broad delete/recreate, destructive mirror operations, or unknown-content cleanup around protected paths are prohibited without verified recovery.

## 4. Accepted semantic/product authority

17. Canonical identity is not changed for Japanese/UI convenience.
18. Stable Special IDs are preserved unless a separately approved migration explicitly changes the identity contract.
19. Research, candidate, HOLD, local experiment, and external evidence do not silently become accepted production authority.
20. Japanese/search/browse overlays remain distinct from canonical identity unless a task explicitly changes that contract.
21. Existing Prompt/raw user intent is not silently rewritten by cleanup/refactoring.
22. Do not introduce hidden automatic Prompt insertion/rewrite as an incidental implementation choice.

## 5. Production and repository mutation

23. This is a single-user personal repository. Branch/PR review is required for risky or substantial changes, not for every trivial/reversible edit.
24. Production promotion must identify the source commit and preserve rollback/recovery evidence appropriate to the risk. Independent human review is optional when automated/manual verification is sufficient for personal use.
25. A runtime must not be declared current when its provenance/hash evidence materially disagrees with the claimed source.
26. Research/evidence does not become production behavior accidentally; an explicit promotion decision is still required, but it does not need team-style ceremony.
27. Cleanup must prove that a branch/file/data path is obsolete or recoverable before destructive removal.

## 6. External software/data

28. Reuse existing OSS/data when it is safer or better than rebuilding the same commodity capability.
29. Current project assumption is private/local personal use with no planned distribution. Under that assumption, routine external-code/data experiments do not need a formal license/provenance audit. Preserve the upstream source/repository URL when practical and do not knowingly ingest obviously stolen, leaked, private, or malicious material.
30. Before public distribution, publishing a bundled derivative, hosted/shared service use, commercial use, or another materially broader use, perform the license/provenance review appropriate to that release and replace/remove anything that cannot be used safely.
31. Preserve DTT behavior with parity/regression evidence proportional to replacement risk.
32. External/network providers are allowed when useful. They must fail boundedly, must not corrupt local state, and credentials/secrets must not be committed to the repository.
33. Offline operation is useful but not a universal requirement for every feature.
34. Do not add a dependency or framework solely for architectural fashion.

## 7. Quality and evidence

35. Measure performance before optimizing production behavior when the benefit is not obvious.
36. Prefer semantic/regression fixtures at current domain boundaries over repeated historical ceremony.
37. Meaningful durable findings should be recoverable from GitHub Issue/commit/result evidence, not only chat.
38. Reports should be sufficient for review but need not repeat unchanged policy or history.

## 8. Current details live elsewhere

Current routing: `docs/project/CURRENT_ROUTING.json`

Human dashboard: `docs/project/NOW.md`

Execution guidance: `docs/project/EXECUTION_ARCHITECTURE.md`

Task details: selected live GitHub Issue and task-specific docs.

## 9. Closeout ownership

39. Substantial Issue closeout records product/test/tool/workflow/data/branch/worktree disposition and recovery; temporary scaffolding does not silently become permanent architecture.
40. Closed-Issue write automation needs an explicit current owner or must be disabled. Preserve unique regression checks in current semantic CI.
41. Worktree/branch retirement requires owner and recovery proof; closed/old/detached is insufficient. See `docs/maintenance/ISSUE_CLOSEOUT.md` and the guarded Batch A lifecycle tools.

## 10. Start existing local dependencies before skipping validation

User instruction, 2026-10-03: applies to all subsequent development work.

42. A stopped local dependency is not, by itself, a validation blocker. When validation requires an existing local service, app, API or execution environment, Codex must determine its safe existing startup method, attempt startup autonomously and continue the actual validation. Do not finish with only “stopped, therefore SKIP”. This includes Forge Neo, local APIs, development backends, test servers and database services.
43. Prefer existing scripts/CLI, then PowerShell or equivalent, then API, and Computer Use only when necessary. Reuse repository/environment startup methods and existing configuration. Do not silently rebuild the environment, install software, change settings or weaken validation to obtain a PASS. Preserve protected data and applicable backup/rollback boundaries.
44. Stop as a blocker only when required credentials are unavailable; external charges would be incurred; destructive operations are required; new installation or substantial environment changes are necessary; configuration changes require user judgment; or an actual startup attempt fails and reasonable self-recovery cannot resolve it. Report the concrete blocker and attempts, rather than treating a stopped process as evidence of inability to validate.
45. Record startup/readiness, actual validation results and any remaining limitations. Distinguish external startup failure from product failure. Startup authorization does not authorize unrelated feature work, production deployment, protected-data changes or bypassing the task's STOP boundary.

## 11. Proportionate validation / reuse valid results

User instruction, 2026-10-03: applies to all subsequent development work.

46. Select tests from the concrete failure modes of the change. During implementation, prefer the smallest sufficient targeted scope; retain quality, safety and regression detection.
47. Run full regression and final CI once per final candidate by default. Reuse valid PASS results for the same relevant code/artifact and assumptions; do not rerun for reassurance, docs/comments, an unchanged merge, or to repeat completed hash comparisons.
48. Rerun only when relevant code, dependencies, settings, schema/migration, build/publish configuration, Forge paths or artifacts change, assumptions fail, or results are flaky/inconsistent. Start with affected targeted checks; repeat broader checks only when the impact warrants it.
49. Real Forge/GUI/production smoke must match the affected behavior: Forge/Recipe changes need Forge checks, UI interaction changes need UI checks, metadata parsing changes need real metadata checks. Internal refactors/docs/unrelated small changes do not automatically need every smoke.
50. Eliminate duplicate and low-value execution, not necessary verification. Record what each check proves and reuse it until its premise changes; never manually rerun the same CI without a concrete reason.
