# Issue132 Current Automation Operation

Current machine-readable authority:

`docs/issue132/parallel/RUNTIME_AUTHORITY.json`

All five automations must read that file first and follow only the role card named there.

Product goal:

> 作りたい画像の見た目・行為・部位・体位・衣装・構図などから、Danbooruタグ名を知らなくても自然に目的タグへ辿り着けること。

Adult/sexual generation is a normal supported workflow. Accuracy wins over guessing.

Current topology:
- Worker 1 / 2 / 3: NEW forward classification
- Repair: historical invalids, promotion-blocking holds, append-only overlays
- Coordinator: QA, CI interpretation, watchdog

25 rows is persistence granularity, not a semantic work limit. Historical staging is immutable. No merge or production apply is authorized.

Do not infer current authority from old filenames, Git history, status caches, or issue comments.
