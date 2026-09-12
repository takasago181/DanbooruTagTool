# STATISTICS_POLICY.md

## Status

This policy governs the optional statistics/co-occurrence subsystem.
It is **not a v1 runtime requirement** under the current beginner-first product scope.

If statistics are surfaced, the correctness rules below remain mandatory.

## 2種類の件数を混ぜない

### current_post_count
source:
current tag dictionary snapshot

用途:
- optional usage-count display
- search/autocomplete assistance where adopted

This is usage evidence, not model-recognition or generation-success evidence.

### runtime_global_count
source:
Approved post-level statistics dataset

用途:
- global_rate
- relative multiplier
- optional recommendation ranking

## Raw display

If raw statistics are shown, keep the raw values distinct:
- base_count
- co_count
- together_rate = co_count / base_count
- current_post_count
- relative_multiplier

Do not present any of them as generation success probability.
Do not shrink/transform a displayed raw fraction without labeling the transformed metric.

## Ranking reliability

1/1=100%等の少数標本をranking上で過大評価しない。
Existing ranking/reliability machinery may remain for the optional recommendation subsystem.

It must not become a reason to require the full statistics index for normal v1 use.

## Generic tags

If recommendation is enabled, do not rely only on a large fixed blacklist.
Possible signals:
- global frequency
- conditional frequency
- relative multiplier
- small manual noise list

## Snapshot integrity

Any relative-multiplier calculation must use:
- base_count
- co_count
- runtime_global_count
- total_posts

from the same statistics dataset snapshot.
Mixed snapshots => reject the calculation.

## v1 boundary

The following are optional/hidden for v1:
- raw co-occurrence dashboard
- rare/Lift main tabs
- aggregate recommendation score explanation UI
- full ~3GB statistics index as a normal-use dependency

The core `understand -> discover -> choose -> copy` path must work without them.
