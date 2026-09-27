# NOW — いま何をやっているか

最終整理: 2026-09-27 JST

このファイルは、GitHubを開いたときに**現在の主作業・進捗・次の行動**を人間がすぐ把握するためのdashboardです。

正本の優先順位:

`live GitHub -> immutable checkpoint/result -> CURRENT_ROUTING.json -> CURRENT_STATE.md -> Issue / task-specific contract`

固定件数・固定HEADはsnapshotです。実作業前にはliveを再取得してください。

---

## 1. COMPLETE — #132 Tag classification usability / discoverability

2026-09-27 production promotion completed from live main f229ee4d2c3f5ea03dc964634a6d39d7f730710e.

- Pass A reviewed all **31,003 ordinary identities**; Pass B/C reconciliation and semantic QA are complete.
- PR **#197** merged the static secondary-route overlay into main.
- Clean self-contained win-x64 publish and isolated plus installed-catalog checks passed.
- Actual delta: **274 route pairs / 273 identities**, unexpected changes **0**, removals **0**, non-route catalog metadata changes **0**.
- Runtime: C:\Codex\DanbooruTagTool-App; runtime-manifest.json source main f229ee4d2c3f5ea03dc964634a6d39d7f730710e.
  - EXE SHA256: 4199BE55CF1E0A79600DDC6632756C3436F34DCA9E45DAF965A769E4288EA554
  - catalog SHA256: 24665D7C92B9DE9B22D92C7713F4E9876DC9C15B98E02324BBE670448BEA7FF9
  - manifest SHA256: 238809EA281AC938FFF832FF2F57F0D8363E56E9AE1231F8A8970FCC20C882F6
- Production process smoke passed: the actual EXE reached DanbooruTagTool v1, was responsive, and produced no matching crash event. Visual UI inspection was unavailable.
- UserData was excluded from deployment; README.txt and user.db hashes remained unchanged.

Keep the following as separate follow-ups under their existing owners:
- #64 color/pattern taxonomy;
- #64/#76 LIVING/NONHUMAN boundary;
- unreproduced routes and local refinements;
- Unified facet architecture.

## 2. ACTIVE PARALLEL RESEARCH — #180 Character -> HOME Copyright

目的:
- Characterから**single canonical HOME Copyright**をhigh-precision authorityで再構築
- unreliableな旧relation authorityを置き換えるためのresearch

状態:
- Issue: **#180**
- branch: `research/issue180-single-home-pilot`
- Draft PR: **#182**
- research active
- main merge / production applyは未承認

直近の基盤改善:
- Issue180 CIの `push + pull_request` 二重発火を解消
- 直近24hで 91 runs / 46 unique SHAs だった重複を整理
- PR #194で redundant PR trigger削除 + concurrency追加

次:
- live branch / PR #182 の最新checkpointからresearch継続
- production applyは別Gate

---

## 3. INFRA ACTIVE — #188 Execution efficiency / repository structure

目的:
- semantic精度を落とさず、AIの周辺事務処理・重複CI・巨大入力・重複routingを削る

Issue:
- **#188**

mainへ反映済み:
- PR #189: execution architecture / compact routing / overhead lint
- PR #190: #132 incremental CI と full audit を分離
- PR #191: CURRENT_STATE current/history分離
- PR #192: deterministic compact CSV transport
- PR #193: execution telemetry
- PR #194: #180 duplicate CI trigger解消

現在の原則:
- cold start と warm resume を分ける
- immutable evidenceがauthority、statusはcache
- 大規模sourceは必要rangeだけmodelへ渡す
- structured outputは real serializer + parse-back
- checkpoint CI / boundary QA / final full auditを分離
- semantic判断そのものを雑にして速度を稼がない

残り:
- telemetryを実運用で観測して、真のbottleneckを特定
- state/progress/cacheの二重authorityが残る箇所を順次整理
- project-wide overhead lintを継続改善

---

## 4. STANDBY / DRAFT — #179 Character/Copyright quality audit

目的:
- Character/Copyright identity
- 日本語display/search
- ranking
- 2D scope品質

状態:
- Issue: **#179**
- branch: `research/issue179-character-quality-audit`
- Draft PR: **#181**
- branch / research evidenceは保持
- 現在の主Automation対象ではない
- Artist auditは対象外

次:
- #179を再開する場合はlive Issue / PR #181 / branchを正本にする
- #132 / #180とdata/semantic decisionsを混ぜない

---

## 5. 完了済み / default next taskではない

以下は「今やっている主作業」として復活させない:

- Performance / Runtime Load Audit
- portable/runtime hardening
- #117 implementation baseline
- #118 sexual intent baseline

現行runtime:
- user-facing: `C:\Codex\DanbooruTagTool-App`
- self-contained `win-x64`
- real `UserData` はuser-owned protected state

---

## 6. 作業開始時にどこを読むか

### 新しいchat / lane変更 / contract不明

1. `docs/project/CURRENT_ROUTING.json`
2. この `NOW.md`
3. `docs/project/CURRENT_STATE.md`
4. target live Issue / PR / checkpoint
5. `docs/project/PERMANENT_RULES.md`
6. 必要なtask-specific contract

### 同じlaneのwarm resume

1. compact routing / contract fingerprint
2. immutable progress listing
3. changed state
4. next bounded input

変更されていないhistoryや巨大specを毎run全文再読しない。

---

## 7. やってはいけないこと

- unrelated active laneを混ぜる
- research branchからproduction apply
- valid immutable checkpointをstale statusで巻き戻す
- real UserDataをpublish output扱いする
- broad cleanup / `git clean -fdx` / `git clean -fdX`
- semantic uncertaintyを速度のためにCHECKED扱いする
- CSV/JSONのdelimiter整形をmodelの目視だけに任せる
