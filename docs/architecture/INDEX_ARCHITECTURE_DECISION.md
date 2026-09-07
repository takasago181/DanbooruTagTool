# INDEX_ARCHITECTURE_DECISION

決定日: 2026-09-05  
対象Stage: Stage 2 のみ

## Tested Dataset

- Approved Source: `nyanko-devs/danbooru2026`
- Fixed revision: `ebb02a630201c7b51487e45fb90b3fcf4cbedc20`
- Fixed file: `metadata/posts-snapshot.parquet`
- Stage 1 source hash: `5b6b2671dc0fa966de71af76dfd342f485f76581447cec9e26c313ba9fb1c2fd`
- Statistics population: `is_deleted IS NOT TRUE`（`true`だけ除外。`NULL`は保持）

Stage 1のApproved Sourceを正本として使用した。Dataset候補の再比較・再決定は行っていない。

## Subset and method

同一の最小prototype入力は `1 <= id <= 1,000,000` の連続ID範囲である。採用populationの実post数は879,047、General tag数は34,236だった。Parquetの`id`、`is_deleted`、`tag_string_general`だけをHTTP Range readで読み、General tag文字列をsource fieldとして空白区切りで復元した。これはsource列の構文専用であり、Prompt入力を空白分割する設計ではない。

- 前処理: 67.725 s、peak RSS 153.3 MB、生成subset JSONL 191.2 MB
- 実行環境: Windows 11 / Ryzen 7 9800X3D / 32 GB RAM（ユーザー提示環境）
- 各runtime値: 5回の中央値。ANDと集計はwarm index上、openは別プロセスのcold open。
- `base≈` 条件: 1=`penguin_panties`、100=`chest_of_drawers`、10,018=`rose`、99,358=`school_uniform`。選択tag自体はcandidateから除外し、残る全candidateの`co_count`を集計した。

再実行: `C:\Users\takas\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe tools/stage2_benchmark.py run --extract`。生の測定結果は [results.json](/C:/Codex/DanbooruTagTool/benchmarks/stage2/results.json)、runnerは [stage2_benchmark.py](/C:/Codex/DanbooruTagTool/tools/stage2_benchmark.py) に保存した。

## Compared Architectures

1. **Forward-only sorted postings**: `tag_id -> sorted post ordinal[]`。ANDはposting交差。Candidate Aggregationはbase postのhash setを作り、全tag postingを走査してcandidateを発見し、全`co_count`を厳密に数える。
2. **Bidirectional sorted integer arrays**: 上記に加え `post ordinal -> tag_id[]`。ANDは同一forward postings。Candidate Aggregationはbase postを走査して直接全candidateを発見・加算する。

Roaring Bitmap、mmap binary、SQLiteは今回production品質で実装していない。両方式の差がCandidate AggregationにあるというStage 2の問いに直接答えず、比較対象を増やして結論を曖昧にするためである。採用するのは双方向という**論理構造**であり、このPython pickleをproduction formatとして採用するものではない。

## Benchmark

| Architecture | build | build peak RSS | index size | cold open | resident RSS | AND 1 / 2 / 3 / 5 tags |
|---|---:|---:|---:|---:|---:|---:|
| Forward-only | 3.780 s | 302.8 MB | 70.2 MB | 56.0 ms | 144.1 MB | 0.285 / 62.927 / 95.581 / 134.218 ms |
| Bidirectional | 4.929 s | 468.1 MB | 160.9 MB | 461.2 ms | 486.9 MB | 0.287 / 62.322 / 94.148 / 130.803 ms |

| base posts | achieved base | Forward-only: discover + all co_count | Bidirectional: discover + all co_count | bidirectional speed-up |
|---:|---:|---:|---:|---:|
| ≈1 | 1 | 461.719 ms | 0.004 ms | 115,000× |
| ≈100 | 100 | 496.998 ms | 0.298 ms | 1,669× |
| ≈10,000 | 10,018 | 535.035 ms | 20.102 ms | 26.6× |
| ≈100,000 | 99,358 | 639.908 ms | 176.854 ms | 3.6× |

ANDは両方式で同じforward postingsを用いるため、実質同等だった。一方、Candidate Aggregationはforward-onlyがbase sizeにかかわらず全34,236 tag postingを横断するのに対し、双方向はbase postのtag列だけを読む。この測定では、AND時間だけを性能指標にしていない。

## Correctness

小規模ground truthをpytest化し、両方式で次が完全一致することを検査した。

- true multi-tag ANDのpost ordinal（post IDへの1対1対応）
- `base_count`
- 選択tagを除く全candidateの`co_count`

fixtureでは `a AND b AND c` のbase postは `[10, 14]`、base countは2、candidate `d` のco_countは1である。forward-onlyとbidirectionalの両方が同一結果となる。これは [test_stage2_architectures.py](/C:/Codex/DanbooruTagTool/tests/test_stage2_architectures.py) で恒久テストにした。

## Decision

**Stage 5のfull statistics indexは、`tag_id -> sorted post set` と `post_id/ordinal -> tag_id[]` の双方向indexを採用する。**

実装はpost IDをそのまま配列添字にせず、採用population内の連続ordinalを使う。forward sideはtagごとのsorted integer posting、reverse sideはpacked tag ID列とpost offset列にする。Core Tag Setのselected canonicalからforward ANDを作り、得られたbase ordinalをreverse sideで走査してAuxiliary candidateの発見と全co_count集計を行う。CoreとAuxiliaryの概念をindex内で混在させない。

## Adoption rationale

- Candidate Aggregationが本プロダクトの最重要技術課題であり、base=1から100,000まで全条件で双方向が明確に速い。
- 真のmulti-tag ANDは同じforward postingsで実現でき、pair共起へすり替わらない。
- Forge Neo / Illustrious XLとの同時利用では、prototypeの常駐増分は約343 MB（144.1→486.9 MB）と無視できないが、候補更新の待ち時間を0.46–0.64 sから0.000004–0.177 sへ下げる価値が大きい。
- productionではPython object / pickleを使わず、packed binary arrays（必要ならread-only mmap）へ落とす余地を残す。これにより双方向の論理要件を保ったままRAMをさらに抑える。これはStage 5のfull buildで検証する事項であり、今回production indexは作らない。

## Rejected alternatives

- **Forward-onlyをruntime採用**: size、cold open、resident RAMは小さい。しかし候補集計ごとに全postingを走査するため、Candidate Aggregationの要求を満たさない。
- **Roaring Bitmapを今採用**: ANDの改善候補にはなるが、reverse traversalなしではCandidate Aggregation問題を解かない。bitmap実装・形式比較はfull buildの前に必要性が生じた場合だけ追加検証する。
- **SQLiteをruntime中心にする**: このprototypeで検証していない。row/SQL実行オーバーヘッドと全candidate集計の実装複雑度があり、packed双方向配列より優先する根拠がない。
- **Python pickle / array-of-arraysをproduction採用**: benchmark専用。pickleのcold open 461 msとresident 486.9 MBは、Forge同居の最終目標に対して十分小さくない。

## Risks / Unknowns

- 本測定はID 1..1,000,000の879,047 post subsetであり、11,218,362 postのfull populationへの線形・非線形な拡大率はStage 5で別途測る必要がある。
- candidateごとの除外規則、global count、ranking、role分類は未実装。Stage 6以降の範囲であり、今回の`co_count`集計へ混ぜていない。
- packed binary/mmapの容量・cold open・Forge同居RAMは未測定。双方向構造の採用後、production format選択の残課題である。
- `is_deleted=NULL`を保持するStage 1方針はsubsetにも適用済み。NULLをfalseへ書き換えてはいない。

Stage 3以降の実装には進んでいない。
