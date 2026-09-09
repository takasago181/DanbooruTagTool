# PROMPT Version and Freshness Registry

Owner: PROMPT / Issue #5
Purpose: model/runtime/sourceの版・確認日・local applicabilityを一箇所で追跡する。
Last normalized: 2026-09-09

## 読み方

`CLAIM_REGISTRY.md` が「何を信じるか」の正本。
このファイルは「**どの版について、いつ確認したか**」の正本。

`last_checked` が古いだけでclaimを自動無効化しない。
ただし upstream更新が速いmodel/runtimeは、production promotion前に再確認する。

---

## 1. Local primary environment

### WAI Illustrious v17

- profile: `WAI17_LOCAL_FIRST_20260909`
- checkpoint path observed: `sd\\waiIllustriousSDXL_v170.safetensors`
- SHA-256: `f116b0c78ff441467b0cdc8f1936e1ed18ea31e9997c7b132b1b8db533f0bd04`
- local runtime family: Forge Neo
- pipeline: Issue #30 `PASS_PIPELINE`
- last project evidence check: 2026-09-09
- freshness status: `CURRENT_PROJECT_BASELINE`

Known but not frozen here:
- exact Forge Neo runtime commit/version must be taken from Issue #30/current local metadata when Stage10 production runs
- installed extension versions/commits must be captured per experiment, not assumed from this summary

Rule:
**checkpoint hash mismatch or runtime update = same profile name must not be silently reused.**
Create/update profile identity or record exact changed environment.

---

## 2. Model-author / official sources

| Target | Current source role | Last checked | Freshness treatment | Notes |
|---|---|---:|---|---|
| WAI Illustrious v17 | author guide / trusted mirror + author-linked source lane | 2026-09-09 | `RECHECK_BEFORE_PRODUCTION_PROMOTION` | exact author primary desired before final promotion |
| NoobAI XL 1.1 | official Hugging Face model card | 2026-09-09 | `VERSION_PINNED` | native caption order/settings claims scope to 1.1 |
| Illustrious XL v1.1 | official Hugging Face model card | 2026-09-09 | `VERSION_PINNED` | later Illustrious must not overwrite v1.1 claims |
| Illustrious official platform | official current platform | 2026-09-09 | `TIME_SENSITIVE` | useful for family direction, not exact WAI behavior |
| Anima | official Hugging Face model card | 2026-09-09 | `PROFILE_SPLIT_REQUIRED` | Base/Aesthetic/Turbo/derivatives separate |
| WD EVA02 Large Tagger v3 | official model card | 2026-09-09 | `VERSION_PINNED` | vocabulary/training cutoff claims scope to v3 |

---

## 3. Runtime / extension sources

| Runtime/extension | Source role | Last checked | Local status | Rule |
|---|---|---:|---|---|
| Forge Neo | local runtime + upstream project | 2026-09-09 | active | exact runtime build/commit must be captured for production experiment |
| Forge Couple | official GitHub | 2026-09-09 | installed/relevant | exact mode/version local verification required |
| Dynamic Prompts | official GitHub | 2026-09-09 | installed/relevant | save SOURCE_TEMPLATE + RESOLVED_PROMPT |
| ADetailer Neo / ADetailer behavior | official repo + local extension | 2026-09-09 | installed/relevant | pre/post output separated |
| ControlNet | official GitHub capability | 2026-09-09 | candidate lane | compatible control model/version must be exact |
| Regional Prompter | official GitHub capability | 2026-09-09 | compatibility HOLD | Forge Neo exact compatibility must be local-verified |

Do not interpret “official source checked” as “current local extension version exactly equals latest upstream”.

---

## 4. Semantic sources

### Danbooru
- role: `SEMANTIC_AUTHORITY`
- last broad audit: 2026-09-09
- use: canonical meaning / alias / implication / broad-specific relation
- freshness: tag taxonomy can change; exact target used in production should be looked up against current/frozen project dictionary evidence

### e621
- role: supplemental non-human taxonomy only
- last broad audit: 2026-09-09
- freshness: active taxonomy disputes/cleanup can occur
- never silently replace Danbooru canonical identity

---

## 5. Community sources

| Source | Last broad audit | Current role | Recheck trigger |
|---|---:|---|---|
| AIArtRecipe | 2026-09-09 | `COMMUNITY` candidate/failure reservoir | new model/version-specific claim or major site update |
| としあきdiffusion Wiki | 2026-09-09 | `COMMUNITY` practical/runtime knowledge | model/runtime version change; official contradiction |
| Note / Reddit | per-claim | `COMMUNITY` | only when exact claim is used |

Community article publish/update date does not prove technical freshness.
Always prefer exact model/runtime version metadata.

---

## 6. Research sources

Research papers are freshness-sensitive differently from model docs.
They establish general failure mechanisms, not current exact checkpoint behavior.

Current anchors:
- Attend-and-Excite
- T2I-CompBench
- Object-Attribute Binding in T2I
- MultiDiffusion
- Concept Conductor
- multi-LoRA interference research in legacy supplement

Recheck when:
- adopting a new evaluator architecture
- changing failure taxonomy
- introducing a new automated decision rule justified primarily by research

No need to re-search papers before every WAI17 prompt test.

---

## 7. Freshness states

Use these terms:

- `CURRENT_PROJECT_BASELINE` — current local project profile
- `VERSION_PINNED` — claim is exact-version scoped and stable unless that version/source changes
- `TIME_SENSITIVE` — current service/platform/upstream state may change materially
- `RECHECK_BEFORE_PRODUCTION_PROMOTION` — sufficient for current candidate design, but final promotion requires refresh
- `LOCAL_RECHECK_REQUIRED` — upstream capability known; current local behavior/version not yet exact-verified
- `HISTORICAL_REFERENCE` — keep for provenance, not current default

---

## 8. Update triggers

Update this registry if any of these occurs:

1. checkpoint file/hash changes
2. Forge Neo updates before a controlled test
3. extension version changes and behavior may affect results
4. official model card changes a recommendation
5. a later model version is added to scope
6. community source is promoted into an active claim
7. source disappears and a mirror/archive becomes necessary
8. dictionary freeze changes exact semantic surface used by tests

Material changes should also update `CLAIM_REGISTRY.md` if claim validity/status changed.
