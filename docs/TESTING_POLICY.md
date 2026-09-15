# TESTING_POLICY.md

The current product test gate is the clean WPF/.NET solution under `src/`.
The former root Python/Tk suite and runtime-index tests were retired by Issue
#83 after the WPF runtime and current catalog build were proven independent.

Current commands:

```powershell
dotnet test src/DanbooruTagTool.sln -c Release
dotnet test src/DanbooruTagTool.Tests/DanbooruTagTool.Tests.csproj -c Release --filter FullyQualifiedName~Issue76
python scripts/issue70/queue_manager.py bootstrap
python -m unittest discover -s tests/issue70 -v
```

## Current invariants

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

## Historical snapshot evidence

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

The following stage descriptions are historical evidence, not current WPF
completion gates. Issue #70 queue tests remain active because that lane is
still in progress.

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
