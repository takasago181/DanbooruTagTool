# Issue #36 Relaxed V5 — ChatGPT-led semantic repair

Base evidence commit: `7567c3e681f251582ac508191761ebcea9bd69f1`

This lane exists because V4 is structurally usable but contains clear language/semantic defects. V4 remains immutable evidence and is never overwritten.

## Authority / execution model

- Translation and semantic decisions are made by ChatGPT directly.
- Codex/Luna is not used as translator, challenger, semantic auditor, or repair judge in this lane.
- Runtime remains local/non-LLM; this is development-time artifact repair only.

## Unit of work

The frozen V4 audit set has 30,629 rows in 31 shards.

For each shard:
1. read canonical English and current `display_ja`;
2. keep acceptable Japanese unchanged;
3. record only changed rows in `overrides/audit_shard_NNNN.csv`;
4. re-read the changed set against canonical English;
5. mark the shard complete in `progress.json`.

A later deterministic materialization step applies overrides to the frozen V4 table without changing canonical identity/order.

## Repair criteria

Repair when at least one applies:
- Simplified/Traditional Chinese or other clearly non-Japanese display accepted as Japanese;
- mixed-English machine debris that is not a legitimate proper noun/technical token;
- clear semantic mistranslation;
- polysemy failure (`pupils` -> students, `pussy` -> cat, sexual `fingering` -> musical fingering, etc.);
- broken spatial/relation construction (`on/in/under/over/between/through` relationship reversed or destroyed);
- malformed generated Japanese that changes the represented tag meaning.

Do not churn wording merely for naturalness. Rough but semantically usable Japanese is acceptable under the user-directed relaxed closeout policy.

## Fallback policy

When a proper name, product/code, opaque phrase, meme title, or ambiguous label cannot be translated confidently from the available evidence, use canonical-English fallback rather than inventing a Japanese meaning.

## Invariants

Blocking invariants:
- exactly 30,629 canonical rows after materialization;
- canonical set and order unchanged;
- no duplicate/missing/extra canonical rows;
- every display non-empty;
- canonical English identity/output semantics unchanged;
- no writes to production `data/**` or runtime overlay before a separate promotion gate;
- no V3.1 PASS claim from this relaxed lane.

## Final validation

After all 31 shards are complete:
- apply overrides to a new V5 materialized table;
- deterministic row/order/schema checks;
- language debris scan;
- relation/polysemy regression scan;
- ChatGPT semantic re-audit of all changed rows plus targeted samples of unchanged rows;
- produce a terminal report for a separate promotion decision.
