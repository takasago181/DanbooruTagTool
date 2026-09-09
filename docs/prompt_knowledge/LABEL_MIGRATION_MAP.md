# PROMPT Knowledge Label Migration Map

Owner: PROMPT / Issue #5
Purpose: 旧資料のlabel表記を新しい2軸規格へ読み替える。
Last normalized: 2026-09-09

## 重要

旧 `docs/stages/STAGE_10_PROMPT_*.md` のlabelは履歴として保持する。
今後のcurrent verdictは `00_KNOWLEDGE_GOVERNANCE.md` と `CLAIM_REGISTRY.md` の2軸を使う。

### New axes

- `SOURCE_CLASS` — 根拠の種類
- `STATUS` — 現在の採用状態

---

## Common migration

| Legacy label | New SOURCE_CLASS | New STATUS | Notes |
|---|---|---|---|
| `OFFICIAL_FACT` | `OFFICIAL_MODEL` or domain-specific official | `ACCEPTED` | claim内容が公式記述そのものの場合 |
| `AUTHOR_GUIDE` | `AUTHOR_GUIDE` | `ACCEPTED` | 作者推奨そのもの。最適化解釈は別claim |
| `AUTHOR_MIRROR` | `AUTHOR_GUIDE` | `ACCEPTED` or `HOLD` | mirrorであることをversion/freshnessへ残す |
| `OFFICIAL_RUNTIME_FACT` | `OFFICIAL_RUNTIME` | `ACCEPTED` | local applicabilityは別validation |
| `SEMANTIC_AUTHORITY` | `SEMANTIC_AUTHORITY` | `ACCEPTED` | semantic claimのみ |
| `RESEARCH_BACKGROUND` | `RESEARCH` | `ACCEPTED` | mechanism/taxonomy。exact model behaviorには昇格しない |
| `PROJECT_FACT` | `PROJECT_FACT` | `ACCEPTED` | exact project scopeのみ |
| `CONTROLLED_PRACTICAL` | `CONTROLLED_PRACTICAL` | `ACCEPTED` or `CANDIDATE` | sample/seed/scope次第 |
| `COMMUNITY_JA_STRONG` | `COMMUNITY` | `CANDIDATE` | exact reproductionなしにFACT化しない |
| `COMMUNITY_VALIDATED` | `COMMUNITY` | `CANDIDATE` | official方向整合でもproductionには別検証 |
| `COMMUNITY_CANDIDATE` | `COMMUNITY` | `CANDIDATE` | same meaning |
| `COMMUNITY_JA` / `COMMUNITY_OTHER` | `COMMUNITY` | `CANDIDATE` | localeはsource noteへ |
| `MODEL_LOCAL_OBSERVATION` | `CONTROLLED_PRACTICAL` or `COMMUNITY` | `CANDIDATE` | exact environmentをscopeに保持 |
| `PROJECT_HYPOTHESIS` | `PROJECT_FACT` or source-derived | `CANDIDATE` | source typeは仮説の根拠側を選ぶ。statusはcandidate |
| `ADOPT_CANDIDATE` | source-specific | `CANDIDATE` | “採用候補”はstatusへ統合 |
| `HOLD` | source-specific | `HOLD` | reason/validationを別欄に持つ |
| `CONFLICT` | source-specific | `CONFLICT` | conflicting claims/sourcesを保存 |
| `CONTRADICTED_BY_OFFICIAL` | usually `COMMUNITY` | `REJECTED` | officialと衝突した旧claim |
| `RATIONALE_INCORRECT` | source-specific | `REJECTED` | 結論と理由を分離できる場合は別claim化 |
| `HISTORICAL_ONLY` | `LEGACY` | `HISTORICAL` | current defaultにしない |
| `TIME_SENSITIVE_TOOL_NOTE` | `COMMUNITY` or `OFFICIAL_RUNTIME` | `CANDIDATE` | freshness registry必須 |
| `DATED_RANKING` | `LEGACY` or `COMMUNITY` | `HISTORICAL` | current rankingへ流用しない |
| `ENV_SPECIFIC_HOLD` | source-specific | `HOLD` | scope=`RUNTIME:exact`; validation=`LOCAL_RECHECK` |
| `DO_NOT_PROMOTE_GLOBAL` | source-specific | usually `CANDIDATE/HOLD` | exact scopeへ狭める |

---

## Important examples

### Example 1 — WAI17 long Negative warning

Old:
`AUTHOR_GUIDE`

New:
- SOURCE_CLASS: `AUTHOR_GUIDE`
- STATUS: `ACCEPTED`
- SCOPE: `MODEL_VERSION:WAI-v17`
- VALIDATION: `NOT_REQUIRED`

別claim:
「short Negativeがhard-target最適」
- SOURCE_CLASS: author guidance + project hypothesis
- STATUS: `CANDIDATE`
- VALIDATION: `STAGE10_REQUIRED`

### Example 2 — Anima short relation sentence

Old:
`COMMUNITY_CANDIDATE_WITH_OFFICIAL_DIRECTIONAL_SUPPORT`

New:
- official claim: Anima supports tags + natural language -> `OFFICIAL_MODEL / ACCEPTED`
- optimization claim: one short relation sentence improves binding -> `PROJECT_HYPOTHESIS / CANDIDATE / STAGE10_REQUIRED`

### Example 3 — WAI generic Illustrious Negative inheritance

Old:
`CONTRADICTED_FOR_WAI_V17`

New:
- old generic inheritance claim -> `LEGACY / REJECTED / MODEL_VERSION:WAI-v17`
- WAI author warning -> `AUTHOR_GUIDE / ACCEPTED`

---

## Migration completion rule

Legacy docs do not need destructive bulk rewrite.
A legacy label is considered normalized when:

1. the active claim exists in `CLAIM_REGISTRY.md`, or
2. the topic is explicitly mapped in a categorized `0X_*.md`, and
3. any uncertainty is present in `09_HOLD_CONFLICT_AND_REVALIDATION.md`.

If a future reader sees a legacy label not represented in the active registry, treat it as **evidence/provenance only**, not current verdict.
