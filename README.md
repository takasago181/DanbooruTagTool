# DanbooruTagTool

日本語/英語のタグ理解・発見からPrompt/Negative、Forge生成、Library、LoRAまでを
支える個人用Windows WPFツール。成人向け・fetish・hard/nicheの深いSpecial発見を保護します。

#247 Foundationは完了。PR #261〜#264を受入し、#255はNO ACTION。
新しい未適用Foundation LKGを保持。productionは既存#245 LKGのままです。
次のDEV lane / #256 / #230 / production適用はユーザーの指示待ち。

- Foundation完了記録: [checkpoint](docs/issue247/FOUNDATION_COMPLETE_2026-10-03.md)
- 未適用Foundation LKG: [record](docs/issue247/FOUNDATION_LKG_2026-10-03.json)

- 現在地: [NOW](docs/project/NOW.md) / [routing](docs/project/CURRENT_ROUTING.json)
- 安全境界: [PERMANENT_RULES](docs/project/PERMANENT_RULES.md)
- runtime/rollback: [LKG](docs/project/LAST_KNOWN_GOOD.md) / [pipeline](docs/maintenance/PORTABLE_RUNTIME_PIPELINE.md)
- 現行tool選択: [TOOLCHAIN](docs/maintenance/TOOLCHAIN.md)
- 外部実装調査Gate: [report](docs/foundation/EXTERNAL_REUSE_GATE_2026-10-03.md) / [matrix](docs/foundation/EXTERNAL_REUSE_MATRIX.md)
- accepted authority/compiler: [CATALOG_AUTHORITY](docs/foundation/CATALOG_AUTHORITY.md)
- researchと凍結再現: [research](research/README.md)
- Issue終了時のownership/cleanup: [ISSUE_CLOSEOUT](docs/maintenance/ISSUE_CLOSEOUT.md)
- 過去の現在地: [history](docs/project/CURRENT_STATE_HISTORY.md)

通常Appは`catalog.db`を読みます。compiler入力は`authority/catalog/current`。
旧Issue CSVはtest oracle/researchであり、暗黙runtime authorityではありません。
UserDataはgenerated outputに含めません。live Issueと最新checkpointで次のtaskを選択し、
このREADMEのsnapshotを最新HEADの代わりに使わないでください。
