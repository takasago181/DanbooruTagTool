# R3 translation automation test engine

This directory is quarantine-only. It implements Issue #39 and the frozen
`R3_TEST_IMPLEMENTATION_SPEC.md`; it does not promote Japanese wording,
rewrite `data/**`, edit #32/#35 assets, or process the remaining P0 queue.

The normal dry-run is:

```text
python translation_quarantine/r3/r3_run.py --output translation_quarantine/r3
python translation_quarantine/r3/r3_build_blind_audit.py --output translation_quarantine/r3
python translation_quarantine/r3/r3_verify.py --output translation_quarantine/r3 --rerun
```

Use `--evidence PATH` only with a frozen `evidence_manifest.jsonl`. The engine
never fetches live evidence during a rerun. Use `--issue32 PATH` for a frozen
#32 snapshot; generation-only metadata is excluded from the meaning
fingerprint.

The first run creates identity-only evidence when no frozen manifest is
provided. That intentionally leaves wording in `REVIEW`; a reviewer may later
add frozen semantic-scope and wording evidence without changing the selection
or inventing a fresh-pilot override table.

`blind30_input.jsonl` is reviewer-facing and excludes automation states,
reason codes, risk classes, and prior Phase1A verdict fields. The separate
`blind30_key.json` contains the deterministic selection key.

When no frozen #32 snapshot overlaps the selected canonicals, `bridge32_state`
is `REVIEW`; this dry-run condition is not bridge verification. `READY` is
reserved for canonicals covered by the supplied frozen snapshot.
