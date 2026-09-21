# Issue #179 — Full Character/Copyright Quality Audit Protocol

Status: RESEARCH / AUDIT-ONLY / NO PRODUCTION APPLY

Baseline main: `bea08712eb691ca867e218d211023d7206b6b7dc`

## 1. Population

Audit the original Issue #70 Character/Copyright population:

- Character: 35,890
- Copyright: 8,536
- Total: 44,426
- Artist: excluded completely from audit effort

Current finalized runtime contains 42,894 of those rows after the historical 2D scope pass:

- Character: 35,278
- Copyright: 7,616

The 1,532 excluded rows remain part of this re-audit because the old scope pass itself must be checked.

## 2. Authority correction after #177

The historical Character↔Copyright relation was derived from post co-occurrence. #177 proved that this evidence can create false ownership relations.

Therefore:

- `related_copyright` is supporting evidence only;
- historical Character scope decisions propagated from related Copyright are not independently authoritative;
- historical semantic fixes are audit evidence, not truth;
- relation-only failures belong to #180;
- do not change Character/Copyright identity merely because old relation data is wrong.

The old scope census is still useful as provenance. Keep its decision source visible so relation-derived decisions can be distinguished from manual/direct decisions.

## 3. Stage A — deterministic full census

Run over all 44,426 rows and emit independent signals for:

### Identity / structural
- duplicate canonical identity
- malformed/empty identity fields
- unusual canonical fallback situations
- category-level collisions

### Display
- empty display
- underscore leakage
- broken brackets
- mixed Japanese + raw lowercase ASCII qualifier
- multiple/nested qualifier complexity
- exact display collisions
- canonical-fallback-like display as a review signal only

ASCII/Latin display is never automatically wrong.

### Search / aliases
- duplicate search terms
- exact search collisions across identities
- alias collisions
- high-risk non-identity-looking search terms such as obvious fanart/event markers
- no assumption that blank search_ja is itself an error

### Ranking / UX
- collision size
- post_count impact
- priority within otherwise equivalent exact/strong surfaces

### Product scope provenance
Keep this separate from semantic quality:
- current runtime inclusion/exclusion
- historical media_scope
- historical scope decision source
- whether that scope decision depended on old Character↔Copyright co-occurrence

A relation-derived scope flag must not automatically make the row semantically HIGH_RISK.

## 4. Stage A bands

Semantic quality:
- CLEAR
- CHECK
- HIGH_RISK

Scope authority:
- DIRECT_OR_MANUAL
- LEGACY_RELATION_DERIVED
- UNKNOWN

These are triage labels, not final verdicts.

## 5. Stage B — deterministic pilot

Generate a 500-row pilot with deduplication across:

- known regression cases
- highest semantic risk + post_count
- display/search/alias collisions
- qualifier-heavy and mixed-language rows
- Copyright high-impact rows
- rows touched by historical semantic fixes
- clean stratified controls across Character/Copyright and post_count bands

The pilot must contain both likely failures and clean controls so Stage A false-positive rate can be estimated.

## 6. Stage C — second review

Second review only for:
- proposed field changes
- category/product-scope exclusions
- low-confidence identity decisions
- high-impact collisions
- conflicting evidence

Routine PASS controls are not double-reviewed.

## 7. Stage D — pattern expansion

Only confirmed error families from the pilot may be expanded across the full population. Heuristic flags never write production values directly.

## 8. Output contract

Stage A artifact directory:

`artifacts/issue179-quality-census/`

Required:
- `quality_census.csv`
- `pilot_manifest.csv`
- `clean_control_sample.csv`
- `summary.json`

No accepted Issue #70 source file is modified.

## 9. Future correction contract

If corrections are later accepted, use a new correction ledger/overlay with at least:

- row_id
- canonical_tag
- category
- field
- old_value
- proposed_value
- reason_code
- evidence/provenance
- first_review
- second_review
- final_status

No bulk correction is authorized by Stage A itself.


## 10. Official-identity / fanwork exclusion policy

Product goal: Character/Copyright discovery should represent **official identities and official variants**, not secondary/fan-created community vocabulary.

### Keep

Eligible product/search surfaces:

- OFFICIAL_IDENTITY
  - official Character name
  - official Copyright/work/franchise title
- OFFICIAL_ALIAS
  - official localized name
  - stable official abbreviation
  - verified canonical alias
- OFFICIAL_VARIANT
  - official costume/skin/form/class/ascension/version
  - official anime/game adaptation identity when Danbooru models it distinctly

A term is not excluded merely because it is widely used in fanart. The question is whether the **term itself denotes the official identity**.

### Exclude from product/search

All confirmed fanwork-derived vocabulary is excluded:

- FANWORK_PAIRING
  - pairing/ship/combination names
- FANWORK_HASHTAG
  - fanart posting tags and creator/community hashtags
- FANWORK_EVENT
  - fan-created commemorative/event tags
- FANWORK_MEME
  - meme names / joke variants / unofficial parody labels
- FANWORK_COMMUNITY
  - community-only vocabulary, dream/fujoshi/fandom labels, activity-group tags
- FANWORK_CROSSOVER
  - unofficial crossover/mashup names
- FANWORK_DERIVATIVE
  - fanmade costumes/forms/designs/characters that are not official identities
- NON_IDENTITY_DESCRIPTION
  - descriptive prose or search phrases that do not name an identity

Examples already observed in the pilot include terms such as:
- `ミクの日`
- `初音ミクイラスト`
- `ぼ喜多`
- `おかころ`
- `絵かゆ`
- `腐レイバーン`
- `ス腐ラトゥーン`
- `VOICEROIDドット絵部`
- `コッショリ`
- `ぼっち・ざ・けいおん!`

These examples establish error families; they are not the complete exclusion dictionary.

### Unknowns

Use `UNKNOWN` when official/fanwork status cannot be established reliably.

- UNKNOWN is **not auto-included**.
- UNKNOWN is **not auto-deleted from source data**.
- UNKNOWN stays in review until evidence is sufficient.

### Review field

Add a separate semantic dimension:

`origin_class`

Allowed values:

- OFFICIAL_IDENTITY
- OFFICIAL_ALIAS
- OFFICIAL_VARIANT
- FANWORK_PAIRING
- FANWORK_HASHTAG
- FANWORK_EVENT
- FANWORK_MEME
- FANWORK_COMMUNITY
- FANWORK_CROSSOVER
- FANWORK_DERIVATIVE
- NON_IDENTITY_DESCRIPTION
- UNKNOWN

For a row with several search terms, classify terms independently where necessary. A valid official Character/Copyright row may remain in product while only contaminated `search_ja` terms are removed.

### Safety rule

Do not delete Issue #70 source rows because a search term is fanwork-derived.

Preferred remediation order:

1. preserve official Character/Copyright identity;
2. remove only confirmed fanwork/non-identity search or alias terms;
3. suppress the entire Character/Copyright row only when the **row identity itself** is confirmed fan-created/out of product scope;
4. require second review for whole-row suppression.

This policy is independent of #180 Character↔Copyright ownership reconstruction.
