# CURRENT DEV TASK

最終同期: 2026-09-08

## Mirror Metadata

- Source Issue: #35 `[UI][DEV] Japanese-first desktop UI pass (dictionary frozen)`
- Parent: #34 `[UI-JA][CROSS] Tool UI / Japanese translation quality improvement`
- State: active
- Branch: `ui-ja/issue35-ui-only`
- Implementation model: Luna
- Purpose: Codexがprivate GitHub Issue APIへ追加認証せず、現行DEV作業内容をrepository内から読むための同期ミラー。

## User decision

辞書本体は別の自動改善処理が進行中。このIssueでは辞書内容を変更しない。

このpassは、現在ロード済みの日本語データを使ってデスクトップUIを一貫した日本語優先表示にするだけ。

## Start gate

編集前に必ず:

1. `ui-ja/issue35-ui-only` をcheckoutする。
2. `docs/project/CURRENT_STATE.md` のactive DEV Issueが #35 であることを確認する。
3. このファイルが Source Issue #35 / State active / Branch `ui-ja/issue35-ui-only` であることを確認する。
4. 不一致があればSTOPして報告する。

branchはIssue #35 active化後のcurrent mainへ再同期済み。古いローカルbranch状態から作業しない。

## Files allowed in this pass

原則として変更対象は:

- `danbooru_tag_tool/ui.py`
- `tests/test_stage7a_ui.py`

必要性が明確でない新規module/abstractionは作らない。

## Forbidden

- `data/**` の変更
- `data/runtime/japanese_overlay.json` の変更
- Special2788 content変更
- canonical / alias / semantic / generation-profile content変更
- search ranking / fuzzy matching / recommendation scoring・ordering変更
- Stage9C/9D composition/session semantics変更
- protected hash/integrity弱体化
- `anal -> piano/analog...` 検索ノイズ修正（これは #34 の別項目）

## Deterministic implementation steps

### Step 1 — `ui.py` にpure display helperを1個だけ追加

以下と同等の挙動:

```python
def bilingual_tag_label(japanese, english_tag):
    ja = (japanese or "").strip() or "日本語未登録"
    return f"{ja} / {english_tag}"
```

`english_tag` を翻訳・normalizeしない。これは表示上のtraceability用でありPrompt整形ではない。

### Step 2 — visible tag/candidate identityをhelperへ統一

既存methodのpresentation文字列だけ変更:

- `_run_search`
  - Special: `item.japanese` + `item.original_term`
  - General: `item.display_japanese` + `item.canonical`
- `_candidate_headline`
  - Japanese overlay display + `candidate.canonical`
  - 日本語なしなら `日本語未登録 / canonical`
- `_render_semantic_support`
  - candidate identity: Japanese overlay display + canonical
  - relation owner Specialも、そのSpecialの `japanese` + `term` でbilingual表示
- `_refresh_state`
  - selected Specialをbilingual表示
  - manually added auxiliaryをbilingual表示しcanonicalを常時表示

これらのtag/candidate identity rowでは英語だけへのsilent fallbackを禁止。

### Step 3 — selected item sourceを明示

新しいstateを作らず文字prefix/badgeだけ使う:

- selected Special: `[選択Special] 日本語 / english_tag`
- manual auxiliary: `[手動追加] 日本語 / canonical`

`Stage9ComposerSession.automatic_injections` は現在empty。fake automatic group/UIを追加しない。現在sessionから表面化していない自動項目は表示しない。

### Step 4 — Japanese-first UI chrome

exact changes:

- window title: `DanbooruTagTool`
- `Prompt preview` -> `完成Prompt`
- `Promptをコピー` -> `完成Promptをコピー`
- `Special2788` -> `Specialタグ候補`
- `選んだSpecial` -> `選択したSpecialタグ`
- `その他のDanbooruタグ`, `関連候補`, `よく使われる`, `珍しい関連`, `意味から補助` は既存日本語を維持

final Prompt payloadそのものは翻訳しない。

### Step 5 — recommendation readabilityはpresentation順だけ変更

`_render_candidate_rows` でscoring/orderを変えず、表示順だけ:

1. bilingual tag identity
2. generation hint / evidence note（あれば）
3. raw statistics (`件数 / 割合 / Lift`) を最後
4. `＋追加` button維持

ranking/filtering/scoring変更禁止。

### Step 6 — Luna passではwindowを再設計しない

existing single-window / panes / resize systemを維持。新規window/dialog/tab構成への変更や大規模geometry/layout rewriteは禁止。

より大きなvisual-layout改善は、このpass後のreal screenshot reviewで必要なら別Issueにする。

## Acceptance tests

1. `bilingual_tag_label("日本語", "sample_tag") == "日本語 / sample_tag"`。
2. missing/blank Japanese -> `日本語未登録 / sample_tag`。
3. Special search rowにJapanese + original Special term。
4. General resultにJapanese + canonical、missing Japaneseはexplicit fallback。
5. selected manual auxiliaryはJapanese/fallback + canonicalを常時表示。
6. related candidateはJapanese/fallback + canonicalを常時表示。
7. semantic-support candidateとowner Special identityがbilingual。
8. final Prompt preview / clipboard payloadはcanonical English Prompt syntaxのまま。
9. `data/**` changed files = 0。
10. search/recommendation/session semantics unchanged。
11. protected integrity tests unchanged and PASS。

## Required test order

```text
python -m pytest -q tests/test_stage7a_ui.py
python -m pytest -q tests/test_stage9c_session.py tests/test_stage0_integrity.py
python -m pytest -q tests/test_e2e_functional.py tests/test_e2e_verdict.py
python -m pytest -q
```

環境/Tk制約で実行不可なら、exact command / error / 未検証項目を報告する。未実行をPASSと表現しない。

## Manual inspection gate

code/tests完了だけでUI完成宣言しない。real Windows Tk screenshot/manual inspectionはUI-JA班が別途実施する。

## Completion report required

- remote branch
- commit SHA
- changed files
- focused/regression/full-suite results
- `data/**` unchanged確認
- search/recommendation/Stage9 semantics unchanged確認
- unverified items
- screenshot/manual inspection status

## Codex Gate

Issue #35 / `CURRENT_STATE.md` / this file are synchronized. Codex may implement **only Issue #35** on branch `ui-ja/issue35-ui-only`.

Do not begin unrelated Stage10 production work from this mirror.
