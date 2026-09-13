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

Completed sequential rows: 1-10,900 / 30,629 (35.59%)

- PROPOSED: 10,378
- UNRESOLVED: 522
- HIGH: 9,309
- MEDIUM: 1,069
- LOW: 522
- remaining: 19,729

Batches:

- 1-500: 484 proposed / 16 unresolved
- 501-1,300: 783 proposed / 17 unresolved
- 1,301-2,300: 974 proposed / 26 unresolved
- 2,301-3,300: 982 proposed / 18 unresolved
- 3,301-4,300: 967 proposed / 33 unresolved
- 4,301-5,300: 963 proposed / 37 unresolved
- 5,301-5,500: 196 proposed / 4 unresolved
- 5,501-5,700: 190 proposed / 10 unresolved
- 5,701-5,900: 181 proposed / 19 unresolved
- 5,901-6,900: 939 proposed / 61 unresolved
- 6,901-7,900: 931 proposed / 69 unresolved
- 7,901-8,900: 929 proposed / 71 unresolved
- 8,901-9,900: 953 proposed / 47 unresolved
- 9,901-10,900: 906 proposed / 94 unresolved

Batch 14 audit重点:
- `futa_with_female`〜`green_necktie` の1,000件をpopulation正本から再構築・再監査し、前回の未永続draftは正式成果として再利用していない
- accepted pilot-v2 taxonomy と protected/canonical boundaries を維持
- `ghost / giraffe / goat / gold / golden / gradient / grass / green` 系を語幹だけで一括分類せず、対象identityと初心者向け実用発見経路で個別に再監査
- `goosebumps` を生物ではなく身体状態、`golf_course` を行為ではなく場所、`grasshopper` を植物ではなく生物、`green_lightsaber` を色ではなく武器として修正するなど、部分一致由来の誤分類を除去
- hair ornament は衣装アクセサリ、`*_print` は柄、gogglesの着用位置は着脱・露出として境界を再確認
- 固有作品内概念・イベント・ミームおよび名称だけでは安全に確定できない94件はUNRESOLVED
- direct binary blob経由で通常形式の単一 `.csv.xz` ledgerを保存し、前回のconnector fragment write障害を回避
- canonical/Japanese overlay/Special/#66 UI/search/mainは変更しないcandidate-buildのみ

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
- past checkpointed batch files are not overwritten; corrections are recorded as later review/correction artifacts
- PROGRESS.md records the current sequential stop point
- Issue #64 records major checkpoints and review gates
- main is not updated until the full 30,629 candidate and audit are accepted

Recovery order for a new chat:

1. `docs/project/CURRENT_STATE.md`
2. Issue #64 latest comments
3. `docs/issue64/full_rollout/PROTOCOL.md`
4. `docs/issue64/full_rollout/MANIFEST.json`
5. this `PROGRESS.md`

Next unprocessed global row: **10,901**.
