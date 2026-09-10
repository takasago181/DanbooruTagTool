# Issue #30 Phase 2 reuse-only review design — 2026-09-11

## RESULT

既存 Phase 1 画像のみを使い、`CAL-023 double handjob` の2 seed × A/B、計4画像をレビュー対象にする。新規生成・新規 seed・evaluator再実行はゼロ。

## EVIDENCE

- Selected existing Special: ID 21 `double handjob`（現行 protected project data の日本語: 「二人または両手を使う手淫」）。
- Concrete PASS question: **「2人または両手による手淫が2つ同時に成立しているか？」**
- Concrete FAIL condition: **「1つの手淫だけ・立っているだけ・該当行為なし」**
- Still-image judgeability: 2人の参加者と両手/二つの手の動作が同一フレームに見えるかを確認できる。
- Review scope: 2 pairs / 4 images.

## SELECTION RATIONALE

`CAL-023` は current canonical Japanese が count/action を明示し、A/B の既存 prompt-only画像が同じ seed で揃っているため最小レビューに適する。`CAL-022 double footjob` は同系統だが、1 experiment / 4 imagesで十分なため選ばない。`CAL-024 teamwork (sexual)` は役割割当の文脈依存が強い。`CAL-032 anus + after footjob` は `after footjob` を静止画だけで直接判定できず、multi-Special retention とともに DEFER とする。

## NEXT

contact sheetで同 seed の A/B を比較し、`A / B / both / neither / tie / unclear` で人手判定する。判定後はDEV/ChatGPTが exact-count evidence の十分性、multi-Special defer、Phase 2 closeまたは追加の狭い実験を決める。reuse-only passから新規生成へ自動進行しない。
