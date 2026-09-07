# STATISTICS_POLICY.md

## 2種類の件数を混ぜない

### current_post_count
source:
2026-09-02 tag dictionary

用途:
- autocomplete
- 現在使用数表示

### runtime_global_count
source:
Approved post-level statistics dataset

用途:
- global_rate
- relative multiplier
- recommendation ranking

## Raw display

ユーザーへ見せる生データ:
- base_count
- co_count
- together_rate = co_count / base_count
- current_post_count
- relative_multiplier

raw値をshrinkして表示しない。

例:
21 / 29 = 72.4%
はそのまま表示。

## Ranking reliability

1/1=100%等の少数標本暴走はranking内部で抑える。

Stage 6で比較:
- minimum support
- Wilson lower bound
- Beta/Bayesian shrinkage

方式をStage 1で固定しない。

## Generic tags

固定大規模blacklistだけに依存しない。

評価:
- global frequency
- conditional frequency
- relative multiplier
- small manual noise list

## Snapshot

relative multiplier計算に使う:
base_count
co_count
runtime_global_count
total_posts

はすべて同一statistics dataset snapshot由来。

異なるsnapshotなら計算拒否。
