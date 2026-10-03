# Issue234 bounded template implementation

Explicit 2026-10-04 user request supersedes the earlier HOLD routing. DTT gap: backend-independent count/preview and freezing literal variants before the existing typed Experiment Lab. Reuses Dynamic Prompts syntax concepts (https://github.com/adieyal/dynamicprompts/blob/main/docs/SYNTAX.md, MIT core); implementation is independent .NET code, no dependency/runtime embedded.

Supports deterministic `{a|b}` and flat named `__name__` txt wildcards, nested alternatives/references. Exact BigInteger count precedes enumeration. Configurable cap 1–256, depth16, parse budget8192, input/output16000 characters, file count256/size256KB. Unsupported/unresolved syntax stays raw; cycles/depth/oversized output fail closed. Experiments additionally retain their existing literal-only, 16-value axis and 64-trial cap.

UserData/Templates/workspace.json version1 and flat Wildcards/*.txt are separate personal files; optional explicit external root. Atomic save retains previous JSON backup. Reopen performs no expansion, model/network call or generation. Explicit selected materialization uses existing undoable PromptWorkspace. Experiment handoff pins existing Model/LoRA/Recipe baseline and creates a literal positive replacement axis, then requires existing Save/Start; no second queue. Existing experiment plan stores exact resolved prompts.

Targeted tests: parser/cap/cycle/raw/persistence/materialization and actual view-model→pinned baseline→stored ExperimentPlan handoff. Production, catalog and existing DB schema unchanged. Issues stay open until combined production acceptance; no promotion in this PR.
