# TESTING_POLICY.md

pytestをStage 0から使う。

## invariant tests

snapshotが更新されても原則通る:
- layer counts sum == total
- duplicate semantic_idなし
- canonical target存在性
- ambiguous alias silent resolve禁止
- Semantic fake count禁止
- statistics snapshot混在禁止
- true AND result integrity
- raw source schema
- PromptFormatterのみunderscore->space

## snapshot regression tests

特定versionの固定値:
Special v2026-09-02:
- total 2788
- Core 759
- Extended 915
- Alias 778
- Semantic 336
- unique resolved 2443
- ambiguous alias 9

正式辞書更新時はfixture/versionと一緒に更新する。

## Stage別

Stage 0:
source integrity / schema / hash

Stage 3:
knowledge core / alias / semantic

Stage 4:
Japanese/English/mixed search

Stage 5:
AND / Candidate Aggregation / runtime global counts

Stage 6:
statistics / snapshot guard / ranking stability

Stage 7:
UI integration tests where practical

Stage 9:
Prompt / LoRA formatter

Stage 10:
full regression + benchmark + packaging

`python test_file.py`だけのトップレベルassert方式を本番テスト体系にしない。
