# Issue #96 Special expansion promotion prep baseline v1

Status: **PREP / USER-APPROVAL GATE / NO PRODUCTION MUTATION**

## Authority

- live main at branch creation: `9ab7f1cea4678b5c6e550f1c8bd22b136e20e99b`
- prep branch: `prep/issue96-special-expansion`
- source audit: Issue #94, completed
- source audit branch tip: `b505f34956dc60e189e8c749fbe0cb187ad5154e`
- frozen source candidate file: `docs/issue94/special_gap_candidates_v1.csv` at the source audit commit
- source candidate Git blob SHA: `eb9d627e9b774194ec1ff6319374c983f18fb40f`
- input candidates: **195**
- source Danbooru snapshot: `2026-09-02`
- source SHA-256: `9b32d5ac0713ab252e7470ba6af9cb34de56878b6b3b13dfbbf6a4a37d82d95b`

This prep issue does not reopen the 29,021-row gap population and does not add new candidate identities. Issue #94 is the authority for the 195-row product-fit decision.

## Existing Special layer rule

Current Special documentation defines the four layers as:

- `Core`: canonical Danbooru identity with `post_count >= 1000`
- `Extended`: canonical Danbooru identity with `post_count 1..999`
- `Alias`: alias/slang/spelling surface
- `Semantic`: natural-language/descriptive term without a direct numeric canonical identity

All 195 Issue #94 candidates are real Danbooru canonical identities. Therefore the promotion proposal does not need to manufacture Alias or Semantic rows for the candidate identity itself.

Applying the existing layer rule to the frozen Issue #94 post counts gives:

- proposed `Core`: **86**
- proposed `Extended`: **109**
- proposed `Alias`: **0 candidate identities**
- proposed `Semantic`: **0 candidate identities**
- total: **195**

Canonical aliases attached to a candidate remain search metadata for that canonical identity; they do not require a second Special identity unless a separately approved identity-preservation rule says otherwise.

## ID strategy

The current accepted Special IDs are exactly `1..2788` and are already consumed by catalog/runtime and browse evidence. Existing IDs must not move.

Proposed deterministic strategy:

- append only;
- reserve new IDs `2789..2983` for the 195 candidates;
- assign in the frozen candidate-file order (`post_count` descending with the source materializer's deterministic tie/order behavior);
- never renumber existing `1..2788`;
- do not give semantic meaning to the numeric ID beyond stable identity/order.

This remains a PREP proposal until the 195-row materialization is validated.

## Accepted Special browse v2 target

New rows must use the already accepted Issue #76 taxonomy, not create a new taxonomy.

### Kind / 種類

- `ACTION_CONTACT` — 行為・接触
- `CLOTHING_EXPOSURE` — 衣服・露出
- `TOOL_OBJECT` — 道具・物
- `BODY_STATE` — 身体・状態
- `FLUID_EXCRETION` — 体液・排泄
- `POSE_SCENE` — ポーズ・構図・場面
- `PERSON_RELATION` — 人物・関係
- `NONHUMAN_TRANSFORMATION` — 異形・変形
- `META_EXPRESSION` — 表現・メタ

### Body-site / 部位

- `MALE_GENITAL` — 男性器
- `BREAST_NIPPLE` — 乳房・乳首
- `FEMALE_GENITAL` — 女性器
- `MOUTH_ORAL` — 口・口内
- `BUTTOCK_ANAL` — 尻・肛門
- `URETHRA` — 尿道

### Theme / テーマ

- `BDSM_RESTRAINT` — 拘束・BDSM
- `INJURY_R18G` — 損傷・R18G
- `REPRO_PREGNANCY_LACTATION` — 生殖・妊娠・授乳

Classification must stay coarse and shallow. Do not create a new visible subcategory merely because a semantic distinction exists.

## Current production/runtime constraints discovered in preflight

The current application is deliberately built around the accepted 2,788-row snapshot. A future approved implementation cannot be a data-only append.

Current hard checks include:

1. `AcceptedAssetImporter.Read`
   - requires `source.Count == 2788`;
   - requires exact equality with Issue #56 mapping and #63 product-fit keys.
2. `SpecialBrowseV2Overlay.Load`
   - requires exactly 2,788 Special rows;
   - requires catalog IDs `S:1..S:2788`;
   - validates the frozen Issue #76 status distribution (`2745 / 15 / 6 / 1 / 21`).
3. production tests
   - assert exactly 2,788 Special rows.
4. `catalog.db`
   - stores `CatalogEntry` payloads with stable string IDs such as `S:<id>`;
   - normal runtime reads the already baked `SpecialBrowseV2` classification;
   - taxonomy/evidence parsing belongs only to explicit catalog build, never normal startup.

Therefore a later implementation must update source/accepted-sidecar coverage, explicit catalog-build validation and tests together. It must not weaken these assertions to unchecked dynamic counts.

## Proposed promotion-row schema

The reviewable 195-row proposal should contain at least:

- `proposed_special_id`
- `canonical_tag`
- `post_count`
- `proposed_layer` (`Core` or `Extended`)
- `canonical_aliases`
- `display_ja`
- `search_ja`
- `kind_id`
- `body_site_ids`
- `theme_ids`
- `browse_status`
- `nearest_existing_special`
- `duplicate_guard`
- `source_issue94_commit`
- `source_candidate_blob`
- `validation_status`
- `notes`

## Japanese-label strategy

The candidates originate from current General canonical identities, so the preferred first source for Japanese display/search text is the accepted production General Japanese overlay when the identity exists there. Reuse accepted text instead of retranslating it.

For any candidate absent from the 30,629 production overlay, or whose existing General wording is too shallow/ambiguous for Special discovery, produce an explicit Japanese review row rather than silently inventing a final label.

Japanese wording is display/search metadata; canonical English identity remains authoritative.

## Duplicate/identity strategy

Before promotion approval, every proposed row must prove:

- canonical identity still equals the frozen #94 candidate;
- it does not collide with an existing Special canonical identity after NFKC/case/underscore-space normalization;
- it does not collapse through current alias closure onto an existing Special identity that would make a new identity redundant;
- its proposed Special ID is unique and append-only;
- aliases do not collide ambiguously with another canonical identity without being surfaced;
- no #94 excluded row is accidentally imported.

## Integration plan after user approval only

A future implementation issue should, in one reviewed change set:

1. add the accepted 195 identities to the protected/accepted Special source path;
2. add Japanese display/search metadata;
3. add product-fit coverage for the new IDs;
4. add accepted browse-v2 classification for the new IDs;
5. extend generation/profile metadata without rewriting old 2,788 IDs;
6. update importer/browse validators from the frozen 2,788 population to the new approved population while preserving fail-closed exact coverage;
7. rebuild a **new** `catalog.db` through the explicit build path;
8. leave `UserData/user.db` untouched;
9. run identity/search/browse/prompt-output regression tests;
10. verify Issue #70 inputs/state/hashes were not changed.

## Rollback plan

Because `catalog.db` is rebuildable knowledge and `UserData/user.db` is separate user state, rollback should be source/version based:

- keep the pre-expansion accepted Special inputs intact in git/protected-data provenance;
- if expansion validation fails, discard the new catalog build and rebuild from the prior accepted Special source set;
- never roll back by editing/deleting `UserData/user.db`;
- never reuse/reassign IDs `2789..2983` to different identities after an accepted promotion without an explicit migration decision.

## Current unresolved prep work

1. Materialize all 195 rows with proposed IDs/layers.
2. Map each row to accepted Issue #76 kind/body/theme facets.
3. Reuse or review Japanese display/search metadata.
4. Run duplicate/canonical/alias checks against current accepted Special authority.
5. Produce exact proposed layer/taxonomy counts and blocked-row count.
6. Stop for user approval before any production mutation.

## Protection flags

- `CONTENT_FILTER_USED=NO`
- `PRODUCTION_FILES_CHANGED=NO`
- `ISSUE70_MUTATED=NO`
