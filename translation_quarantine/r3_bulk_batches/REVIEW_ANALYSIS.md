# Issue #36 — REVIEW 604原因分析

最新checkpoint `issuecomment-5591125456` と、branch `ui-ja/issue36-r3-bulk-canary` のcommit `94366c0269cd4dd4ff9e6355441090eafc246a12` に固定された625件再評価成果物を読み取り専用で分析した。

## 結論

- 対象: **604 REVIEW**（READY 21は再評価対象外）
- raw reason code:
  - `NO_SAFE_SEARCH_CANDIDATE`: **604**
  - `NO_SUPPORTED_DISPLAY_CANDIDATE`: **604**
  - `HIGH_OR_CRITICAL_MISSING_EXACT_CANONICAL_SCOPE`: **9**
- #32 bridge起因: **0**（604件すべて `READY / NOT_REQUIRED`）
- contradiction: **0**
- 追加bulk再実行: **未実施**
- production promotion: **未実施**

分類は重複しないprimary categoryとして行った。

| Category | 件数 | 概要 |
|---|---:|---|
| wording不足 | 103 | semantic scopeはあるが、独立して採用できるdisplay/search wordingがない |
| semantic scope不足 | 484 | semantic scopeがなく、透明構成probeにも該当しない |
| HIGH/CRITICAL exact evidence不足 | 9 | CRITICALでexact-canonical authoritative scopeがない |
| transparent composition未対応 | 8 | 保守的な広いtoken-shapeでは候補だが、現行規則では未承認 |
| bridge関連 | 0 | #32 bridgeは全件READY/NOT_REQUIRED |
| その他 | 0 | 残余なし |

カテゴリ合計は **604**。

## Risk分布

604 REVIEW全体は LOW **508**、MEDIUM **86**、CRITICAL **10**。HIGH_POSE_ACTION / HIGH_ANATOMY_ADULT は0件。

### wording不足 — 103

semantic scopeは凍結済みだが、wording candidateがない。代表例:

`black_shoes`, `purple_shirt`, `boots`, `cup`, `red_dress`, `green_jacket`, `mask`, `sword`, `bikini`, `girl_on_top`

うち29件はoverlayにtermが存在するが、複数候補・slang・曖昧性・狭義化があるため不採用。例: `green_jacket → 緑ブレザー`、`sword → グレートソード`。残り74件はoverlay wording自体がない。

### semantic scope不足 — 484

代表例:

`angel_wings`, `undressing`, `kneehighs`, `no_bra`, `low_twintails`, `hair_rings`, `floating_hair`, `ear_piercing`, `hand_in_pocket`, `sunglasses`

local Special2788 referenceには、このsemantic-gap集合とexact matchする候補が45件ある。ただし現在のeffective riskはLOWであり、実際にはadult/action/relation-sensitiveな行も含むため、取得しても即READY化せず別監査へ送る。

### HIGH/CRITICAL exact evidence不足 — 9

`hair_over_one_eye`, `eyes_visible_through_hair`, `holding_staff`, `double_bun`, `multiple_tails`, `scar_on_face`, `eyewear_on_head`, `holding_cup`, `hand_on_another's_head`

これらはexact-canonical authoritative semantic evidenceが取れるまで、R3 fail-closedによりREVIEWのままにする。

### transparent composition未対応 — 8

広い構造probeでは候補だが、現行の凍結rule vocabularyにはない:

`open_shirt`, `cloudy_sky`, `blue_sky`, `starry_sky`, `open_coat`, `swimsuit`, `sky`, `black_bodysuit`

これは自動READYではない。`open_*` は状態意味、`sky/background` は意味幅を特に確認する必要がある。既存overlayで単一termがあり、最も近い候補は `blue_sky`。

### bridge関連 / その他

該当なし。bridge contradiction・missing・blockedは0件。

## 自動化可能範囲と残す範囲

安全に自動化できるのは、quarantine内の証拠取得・凍結・分類・再現性検証まで。exact canonical referenceの収集も、alias除外・完全一致・provenance固定を満たす候補生成に限れば自動化できる。

一方、以下は人手または別のauthoritative routeへ残す。

- 9件のCRITICAL exact scope不足
- 484件の一般semantic scope不足
- 103件のdisplay/search wording不足。overlay/search termだけで昇格しない
- 8件のtransparent composition未対応
- subtype narrowing、slang、polysemy、actor/target/relationを含む候補

## 追加evidence acquisitionの見積り

- 保守的に、現時点で最も近い新規候補は **1件**（`blue_sky`）
- semantic scopeだけは既にあるがwording不足の **103件**は、独立した採用可能wordingを取得できればREADY候補になり得る
- transparent composition未対応の **8件**は、ruleとwordingのfocused audit後に候補化できる上限
- よって保守的なREADY候補レンジは **1〜104件**。これは承認数ではなく、追加証拠が揃った場合の上限見積り
- exact local referenceの45件はsemantic scope取得候補としてのみ数え、adult/action/relation riskとwording監査が終わるまでREADY見積りには加えていない

## Integrity / 停止点

- R3 gate: **変更なし**
- production / #32 / #35 / `CURRENT_DEV_TASK.md` / main: **変更なし**
- 追加bulk再実行: **なし**
- blind/self-grade: **なし**
- 既存結果の false READY: **0**
- contradiction: **0**
- replay: **PASS**

この分析をcheckpointとして保存し、ここで停止する。
