# References

参考コードのみ。
データCSVはルート `data/` を正本として参照する。

TRIAL v0.2:
日英検索 / UI / Prompt分離の参考。
最終runtime data形式として採用しない。

Legacy prototype:
2026-05 pair co-occurrenceの歴史的参考。
pair scoreをtrue ANDとして採用しない。

Important:
`references/` 内のtestファイルは過去prototypeの参考資料であり、
正式なproject regression suiteには含めない。
pytest discoveryはルート `tests/` のみに固定する。
