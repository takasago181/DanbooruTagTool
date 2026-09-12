# Issue #64 full rollout progress

Status: IN PROGRESS / candidate build only / not production accepted.

Worker: ChatGPT (development-time classification/review). Codex paused after pilot revision 2.

Accepted basis: Issue #64 pilot revision 2, commit `5064429018123c80c32ac41af715668fb67fb74e`, DEV/AUDIT `PILOT_ACCEPTED`.

## Working set

- exact General population: 30,629 rows
- local working CSV: `issue64_general_30629.csv`
- columns: canonical / display_ja / search_ja / post_count
- SHA-256: `58f9ff128a7ca21a17de4345c36c7891b8169a66fbe3d1de5c190cf48f17d51c`
- 7GB post/runtime index not used for this pass
- runtime LLM dependency: none

## Checkpoint 2026-09-13 JST

Completed sequential rows: 1-5,300 / 30,629 (17.30%)

- PROPOSED: 5,153
- UNRESOLVED: 147
- HIGH: 4,675
- MEDIUM: 478
- LOW: 147
- remaining: 25,329

Batches:

- 1-500: 484 proposed / 16 unresolved
- 501-1,300: 783 proposed / 17 unresolved
- 1,301-2,300: 974 proposed / 26 unresolved
- 2,301-3,300: 982 proposed / 18 unresolved
- 3,301-4,300: 967 proposed / 33 unresolved
- 4,301-5,300: 963 proposed / 37 unresolved

Batch 6 audit重点:
- `car/card`, `bra`, `ring`, `cat`, `chain`, `chest`, `chin`, `clean/clear` 周辺の部分一致誤爆を重点監査
- 対象物identityを修飾語より優先し、`champagne_*`, `cereal_box`, `cleaning_*`, `*_print`, `caterpillar_tracks` 等を用途別に分離
- `card_between_*`, `card_in_*`, `caressing_testicles` 等の関係・行為タグは、内包する物体/身体語よりACTION_CONTACTを優先
- `cbj-ms`, `chilla_(arms)`, `cerise_bouquet`, `clear_marine_calm_(idolmaster)` 等は必要箇所だけ外部定義で境界確認
- 企業名・ブランド・固有イベント・抽象概念など37件は無理に分類せずUNRESOLVEDを維持

## Rules

- accepted 17 top-level genres
- max path depth 2
- no visible catch-all
- beginner practical discovery path takes precedence over substring matching
- object identity takes precedence over modifier fragments
- keep pilot-v2 boundaries for role/clothing, sky/light, screen/composition, body/exposure
- ambiguous proper names/events/projects remain UNRESOLVED when evidence is insufficient
- canonical/Japanese overlay/Special data are not mutated during candidate build

## Persistence

Detailed row-level results are persisted directly in this GitHub work branch.

- branch: `chatgpt/issue64-full-rollout`
- manifest: `docs/issue64/full_rollout/MANIFEST.json`
- immutable detailed ledgers: `docs/issue64/full_rollout/batches/`
- normal batches may use `.csv.xz`; connector-limited batches may use ordered `.xz.b64.partNNN` text fragments with exact reconstruction hashes in MANIFEST
- batch 5+ summary JSON: `docs/issue64/full_rollout/batches/batchNNN_summary.json`
- past batch files are not overwritten; corrections are recorded as later review/correction artifacts
- PROGRESS.md records the current sequential stop point
- Issue #64 records major checkpoints and review gates
- main is not updated until the full 30,629 candidate and audit are accepted

Recovery order for a new chat:

1. `docs/project/CURRENT_STATE.md`
2. Issue #64 latest comments
3. `docs/issue64/full_rollout/PROTOCOL.md`
4. `docs/issue64/full_rollout/MANIFEST.json`
5. this `PROGRESS.md`

Next unprocessed global row: **5,301**.
