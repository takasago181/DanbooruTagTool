# V1 UI / INTERACTION — FIRST IMPLEMENTATION BASELINE

最終更新: 2026-09-13

> **FIRST IMPLEMENTATION BASELINE / USER-ACCEPTED**
>
> この文書は、Issue #66 の第一実装に使うUI / interaction baselineである。
> `docs/PRODUCT_GOAL_LOCK.md` の製品目的を置き換えない。
> `docs/product/V1_UI_DESIGN_DISCUSSION_DRAFT.md` は設計議論のprovenanceとして保持するが、第一実装では本書を優先する。
> ここから追加設計を広げず、まず実装して実際の画像生成ワークフローで使い、実使用で確認できた不便を後続修正する。

## 1. Product interaction goal

中心体験は以下。

`理解 -> 発見 -> 選択 -> 出力`

DanbooruTagTool は、画像生成中に何度も戻って使える軽量ローカル道具とする。

通常の実用ループ:

`Forge等のPromptをコピー -> DanbooruTagToolで読込 -> 日本語で理解 -> Special / Generalから発見 -> 手動追加 / 整理 -> canonical Englishをコピー -> 生成環境へ戻す`

v1で行わない:
- automatic Prompt optimization
- hidden support insertion
- automatic Negative generation
- automatic model rewrite
- automatic failure diagnosis
- direct Forge / ComfyUI generation control

## 2. Two-workspace structure

同一アプリ内に2つのworkspaceを持つ。

### A. Dictionary / Search workspace

役割:
- 既存Prompt読込
- 日本語理解
- 日本語 / English / mixed検索
- Special deep browse
- General shallow browse
- タグ詳細確認
- Prompt末尾への明示追加
- final English Prompt copy

基本レイアウト:

`左: navigation | 中央: search/list/detail | 右: current Prompt`

### B. Prompt Edit workspace

役割:
- 数十タグを一気に見渡す
- 選択
- 複数選択
- 並べ替え
- 削除
- weight等の限定編集
- actual English Prompt確認 / copy

基本レイアウト:

`左 約70%: 日本語Prompt編集 | 右 約30%: actual English Prompt`

右に日本語Promptを重複表示しない。

## 3. Special / General discovery

### Special

Special Core Dictionaryは製品の主役の一つとして明確に扱う。

- 左navigation最上位に独立した `◆ Special`
- completed #56 taxonomyを利用
- `genre -> subgenre -> Special list`
- 深く掘れる探索経路を持つ
- Specialを単なるbadge付き検索結果へ格下げしない

Special detailで通常表示するもの:
- 日本語名 / 意味
- canonical English
- 使用数
- genre > subgenre
- `Promptへ追加`
- `同じ分類のSpecial` 4〜6件程度

新しいauthoritative related-Special graphはv1のために作らない。
`同じ分類` は #56 taxonomy から作る。

### General

Generalは広く・浅く探す辞書とする。

- #64 accepted taxonomyを使用
- shallow practical genres
- UI側で別taxonomyを発明しない
- #64完了前はprovider/interfaceを先に実装してよい

General detailはSpecialより簡素にする。

### List columns

Special / Generalの通常一覧の基本情報:

- 日本語
- canonical English
- 使用数
- add state (`＋` / `✓ 追加済み`)

Specialだけ控えめな `◆` を付けてよい。

### Usage count

使用数は通常一覧で常時表示する。

- 正確な整数値
- 3桁区切り
- canonical側の件数を表示
- Alias自体に別件数を捏造しない
- 実件数を持たないSemantic入口は `0` にせず `—` 等で扱う

閲覧時の標準順は使用数降順。
必要なsortは第一実装では原則:
- 使用数 ↓
- 日本語名

検索結果はusage countではなくsearch relevanceを優先する。

## 4. Search interaction

検索欄は1本のみ。

対応:
- Japanese
- English
- canonical
- approved Alias
- mixed input

ユーザーへ検索方式の選択を要求しない。

概念上の優先順:
1. exact
2. strong canonical / English / approved Alias
3. strong Japanese intent
4. word-boundary / prefix intent
5. substring
6. fuzzy

既知回帰 `anal -> piano / analog...` のようなincidental substring/fuzzy noiseを抑える。

Special / Generalを別検索へ分断しない。

browse中に検索した場合:
- browse location
- scroll position
- selected item
を保持し、query clearで元位置へ戻れるようにする。

`Back` / `query clear` / `breadcrumb` は別動作として扱う。

## 5. Existing Prompt import contract

Prompt読込は保守的に行う。

原則:

> 読むときは壊さない。追加するときはcanonical。

読込時:
- 元の順番をそのまま保持
- 元表記を勝手に正規化しない
- 認識できたものだけ日本語表示を重ねる
- 未解決はraw surfaceのまま保持
- 自動カテゴリ整理しない
- Noob向け等の自動並べ替えをしない
- 既存重複を勝手に消さない

実装上はPromptを単なるsetではなくordered PromptItem sequenceとして扱う。

## 6. Dictionary add behavior

辞書から新規追加するタグは常にPrompt末尾へ追加する。

理由:
- 挿入先を毎回考えなくてよい
- 隠れたselection stateで意図しない位置へ入らない
- 既存Prompt中間を勝手に触らない
- Special / Generalで挙動が統一される

新規追加はcanonical Englishを使用する。

同じcanonical identityがすでにPrompt内にある場合:
- `＋` を `✓ 追加済み` にする
- 新規重複追加を防ぐ

ただし既存Prompt内の重複は保持する。
`blue_hair` と `(blue_hair:1.2)` 等も勝手に統合しない。

新規追加後は末尾チップを短時間だけ軽く強調してよい。

## 7. Dictionary workspace — Current Prompt pane

右側current Promptは「今何を生成しようとしているかを日本語で一瞬で読む」ための領域とする。

表示:
- Prompt item count
- `日本語 / EN` 切替
- ordered wrapping chips
- `未解決 N` は必要時のみ
- fixed bottom actions:
  - `Prompt編集を開く`
  - `英語Promptをコピー`

### Japanese-full invariant

**日本語は表示都合で省略しない。**

- ellipsis `…` による意味切断をしない
- 長い日本語は必要な横幅を使う
- 右pane幅を超える場合は自然に折り返して全文表示
- tooltipへ全文確認を押し込まない
- pane境界はユーザーがdrag resize可能

### Current Prompt chip examples

- normal: `青い髪`
- weighted: `青い髪 1.2`
- LoRA: `LoRA Rella 0.6`
- control: `BREAK`
- unresolved raw: `custom_trigger ?`

辞書workspaceではPrompt chipにdelete `×` を常設しない。
クリックは中央辞書詳細をinspectする操作。
本格編集はPrompt Edit workspaceで行う。

## 8. Prompt Edit workspace

Promptは一本のordered sequenceとして扱う。
画面上でwrapしても、順番は左→右 / 上→下として明確にする。

### Japanese display

- 日本語全文表示
- ellipsis禁止
- 長い項目は自然にwrap
- category / role / Special / General badgeを常時並べない
- English tag列を常設しない

### Selection

対応:
- click: single select
- Ctrl+click: toggle multi-select
- Shift+click: range select
- Ctrl+A: select all
- Esc: clear selection

初心者向けに visible `複数選択` mode/buttonも持つ。
そのmode中は普通のclickでtoggle selectionできる。

### Multi-drag

- selected itemをdrag: selection全体を一塊としてmove
- relative orderを保持
- selected itemsが非連続でもdestinationでは一つのcontiguous blockとして集約してよい
- unselected itemをdrag: 既存selectionを解除し、その1件だけmove
- insertion markerを明示
- top/bottom edgeでauto-scroll

### Delete

- Delete key
- multi-delete action
- hover時だけ小さい `×`

通常削除でconfirmation dialogを出さない。
Undoで戻せるようにする。

### Undo / Redo

最低限以下を対象:
- add
- delete
- multi-delete
- reorder
- multi-move
- weight change
- direct English edit / reparse
- Prompt replace直後の復旧可能範囲

Keyboard:
- Ctrl+Z Undo
- Ctrl+Y Redo

### Prompt-local find

Ctrl+F等でPrompt内検索。

- filterしない
- reorderしない
- 該当chipをhighlight / scroll-toする
- Enter / Shift+Enter等でnext / previousを辿れる構成を許容

## 9. Weight / LoRA / special syntax

通常UIをweight editorやLoRA managerにしない。

### Weight

安全に理解できる単純な `(tag:1.2)` 等のみ限定GUI編集対象。

通常chipではweightがある時だけ `日本語名 1.2` と表示。
選択時だけ小さいweight editorを出す。

複雑構文を無理に解釈・再構成しない。

### LoRA

標準的に認識できるLoRA構文は:
- display name
- weight
程度を軽く見せる。

安全に認識できる場合だけweight編集を許容。
DanbooruTagToolをLoRA管理アプリにしない。

### BREAK / control notation

`BREAK` 等は無理に日本語化しない。
軽く識別できればよい。

## 10. Raw / unresolved handling

辞書にない要素は原文保持。

表示例:
`custom_trigger ?`

禁止:
- automatic delete
- guessed replacement
- silent translation rewrite
- nearest-tag auto-conversion

未解決がある場合だけ小さく `未解決 N` を表示。
必要なら順にinspectできる。

詳細候補:
- original raw surface
- `辞書で検索`
- `辞書候補として登録`

辞書候補登録を行う場合、user-side review queueへ軽量保存する。
巨大な未解決管理画面は作らない。

## 11. Direct English edit escape hatch

Prompt Edit workspace右側には、actual serialized English Promptを表示する。
通常はread-only。

`英語Promptを直接編集` を用意し、特殊Forge構文・新規trigger・未対応syntaxへの逃げ道を残す。

適用時:
- whole Promptを再解析
- safely recognized itemsだけstructured representationへ戻す
- unknown partsはraw保持

GUIの表現能力にユーザーを閉じ込めない。

## 12. Autosave / recovery

通常操作からmanual save dialogをほぼ消す。

自動保存対象候補:
- current Prompt
- item order
- workspace
- browse position
- splitter widths
- window size / position
- small UI state

次回起動時は作業状態をそのまま復元。

`保存しますか？` confirmationを通常フローで出さない。

### New / clipboard import

`新規Prompt` / `クリップボードから読込` はcurrent Promptを置換する。
自動mergeしない。

直前Promptを1世代だけrecovery snapshotとして保持し、必要なら `直前のPromptを復元` を用意する。

v1では大規模な:
- saved Prompt library
- favorites
- Prompt history manager
を作らない。

## 13. Clipboard / copy interaction

生成中の往復を短くする。

主要操作:
- `クリップボードから読込`
- `英語Promptをコピー`

コピー時にdialogを出さず、短い `✓ コピーしました` 等のtransient feedbackのみ。

タグ単体でもcanonical Englishを軽くコピーできる導線を持ってよい。

## 14. Visible-state = copied-Prompt invariant

絶対条件:

> ユーザーが見ているPrompt状態と、実際にcopyされるPromptを一致させる。

禁止:
- hidden support insertion
- hidden Prompt completion
- automatic unseen reorder
- automatic unseen replacement
- category-based silent insertion

既存import itemは、そのitemをユーザーが明示編集しない限り元表記を維持する。

- moveだけで再serializeし直さない
- weight editはそのitemだけ再構成
- direct English edit時だけwhole Prompt reparse

## 15. Lightweight runtime / architecture baseline

第一候補:
- C#
- .NET
- WPF
- SQLite
- CommunityToolkit.Mvvm等の軽量MVVM補助

概念分離:

`View -> ViewModel -> Application Service -> Repository / SQLite`

候補DB:
- `catalog.db`: rebuildable catalog knowledge
- `user.db`: persistent user/workspace state

通常起動時に行わない:
- CSV rebuild
- taxonomy generation
- dictionary audit
- large statistics preprocessing

通常起動は概ね:
`catalog open -> user state restore -> UI`

Performance baseline:
- search debounce: 約100〜200ms程度
- 30,629 General listはUI virtualization
- rich detailはselected itemについてのみload
- optional large indexesが無くてもcore app startup可能

## 16. Data / authority boundaries

### Special
Use:
- frozen Special 2,788 identities
- completed #56 taxonomy
- existing Japanese presentation assets
- canonical usage counts where available
- #63 product-fit sidecar as current eligibility authority

Do not restart whole Special curation for this UI.

### General
- production Japanese overlay exact 30,629 population
- #64 alone owns practical taxonomy classification
- #66 consumes accepted #64 output
- #66 does not fork or rewrite #64 taxonomy

### Search helpers
Alias / Semantic / other assets may assist discovery but do not change canonical identity.

## 17. First implementation acceptance checks

At minimum verify:

1. 80-item Prompt can be loaded and edited.
2. very long Japanese labels are never ellipsized.
3. imported order is preserved.
4. imported raw surface is preserved unless explicitly edited.
5. dictionary addition always goes to end.
6. duplicate canonical addition is blocked while imported duplicates are preserved.
7. normal / weighted / LoRA / BREAK / unresolved raw can coexist without destructive rewrite.
8. multi-select / multi-drag / delete / Undo work.
9. direct English edit -> reparse preserves unsupported raw text.
10. clipboard import / copy round-trip works.
11. app restart restores current workspace.
12. copied Prompt matches visible explicit state.
13. Japanese / English / mixed search works.
14. exact / strong intent beats incidental substring/fuzzy noise.
15. representative `anal -> piano / analog...` regression is covered.
16. Special deep browse works from #56 assets.
17. General provider boundary exists before #64 acceptance.
18. accepted #64 output can later plug in without UI taxonomy rewrite.
19. ordinary startup does not require optional huge indexes.
20. real Windows usability is checked before v1 acceptance.

## 18. Implementation route

Current owner: **Issue #66**.

First implementation route:

`WPF foundation -> Prompt workspace -> Prompt import/preservation -> Special browse -> bilingual search -> add/edit/reorder -> actual English preview/copy -> General provider boundary`

In parallel:
- Issue #64 continues General 30,629 taxonomy rollout independently.

After #64 acceptance:

`#66 consumes #64 -> product-facing General browse/search checks -> final reconciliation -> real Windows acceptance -> practical v1 baseline`

Codex implementation rules:
- start from latest live main
- dedicated #66 branch
- do not work on #64 rollout branch
- do not delete old Tk implementation first
- reuse useful code/data assets where practical
- do not self-merge
- return branch / commit / changed files / tests / validation
- DEV reviews against this baseline before merge

## 19. Freeze policy

第一実装までは、このbaselineへ便利そうな機能を追加し続けない。

HOLD until real-use evidence:
- favorites
- full Prompt library/history UI
- recommendation/co-occurrence main UI
- model-specific auto optimization
- direct generator integration
- image preview
- Generation Profile dashboard
- automatic support / Negative / conflict resolution
- new semantic related-Special graph

まず実装し、実際の生成で使い、不便が実証された箇所を後続revisionで直す。
