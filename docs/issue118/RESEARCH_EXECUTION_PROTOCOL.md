# Issue #118 research execution protocol

Status: research-only operating protocol. This file is not product/production authority.

## Goals

Prevent two recurring failure modes while #118 remains in research:

1. long reasoning/tool runs stop before leaving a durable checkpoint;
2. repeated GitHub reads/polls trigger `Too Many Requests` or waste request budget.

## Durable-checkpoint rule

Work in bounded passes. A pass should end by committing at least one durable research artifact before starting another expensive analysis step.

Preferred checkpoint boundaries:

- one materializer/script committed;
- one workflow committed;
- one generated summary committed by Actions;
- one independent review artifact committed;
- one counterexample-driven rule refinement committed.

Do not accumulate multiple uncommitted conceptual stages in chat memory.

If a pass is interrupted, the next chat should resume from the latest branch commit + summary/review artifact, not from prose chat history.

## GitHub request-budget rule

Default target: **4-6 external GitHub reads per analysis pass**.

Prefer:

- branch HEAD once;
- Issue comments once, then search the fetched response internally;
- large CSV/inventory once, then search/analyze the fetched content internally;
- generated summary JSON instead of reading many generated files;
- fixed line-range reads for bounded review inventories.

Avoid:

- refetching the same file for each keyword;
- one API call per Issue comment/checkpoint;
- repeatedly listing directories whose summary is already known;
- repeated workflow polling.

## Actions rule

Actions should persist their result back to the research branch as a summary/artifact.

Normal sequence:

1. commit workflow/materializer;
2. do other useful analysis instead of polling;
3. perform at most one run-status check when needed;
4. after success, fetch the committed summary once;
5. on failure, fetch the failed job/log once and repair the cause.

Do not continuously poll an in-progress run.

## Summary-first rule

Every large materialization should emit one compact summary JSON containing at least:

- source artifact/version;
- input population size;
- output/classification counts;
- validation/gate result;
- production authority flag;
- explicit `main/#117/catalog/UserData` mutation flags;
- recommended next gate.

Subsequent chats should read this summary before large CSVs.

## Review provenance rule

Materializers MUST NOT generate semantic human-review verdicts.

Required sequence:

1. materializer creates a review inventory/template with blank verdicts;
2. independent semantic review creates a separate static review artifact;
3. review artifact records the exact source inventory blob SHA when available;
4. promotion/materialization consumes the review artifact as an input;
5. promotion must fail closed if expected provenance/gate values drift.

Fresh-holdout review is validation evidence, not permission for production promotion.

## Counterexample rule

A fresh-holdout counterexample blocks the current bulk candidate set.

Do not return to repeated 1,000-row manual review. Instead:

1. identify the semantic family that produced the counterexample;
2. add a discovery-only boundary/risk rule;
3. remove only that boundary family from the clean candidate set;
4. take a new deterministic fresh holdout with a new salt;
5. repeat until the gate converges or the cluster is declared manual/boundary-only.

Risk rules are candidate discovery/exclusion tools, not semantic authority.

## Stop-loss rule for long reasoning

Before beginning a new large stage, leave a durable checkpoint for the previous stage.

If analysis is becoming broad, split it into separate committed stages instead of attempting one very long reasoning pass. Prefer partial but durable progress over an all-or-nothing pass.

## Production isolation

Until #118 explicitly passes its implementation authorization gate:

- do not mutate `main`;
- do not mutate #117 implementation;
- do not write production sexual-intent authority;
- do not mutate runtime catalog/UserData;
- keep all generated classification data marked `production_authority: NO`.
