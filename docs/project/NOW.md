# NOW

2026-10-03 — Foundation production昇格、新production LKG保持。
source main `ad14d45f`; 実UserData14/14 byte一致、semantic変更なし。
Forge停止中のため実生成はSKIP。詳細: `docs/issue256/FOUNDATION_PRODUCTION_2026-10-03.md`。

#256 Batch1: Library/PNGから復元したRecipeのModel hashを保持・保存し、API capabilityと実PNGで完全一致を確認。
開発専用schema3 migrationはbackup/transaction付き。production schema2は未変更。
既存35 checkpoint /142行matrix再利用。計画: `docs/issue256/POST_FOUNDATION_PLAN_2026-10-03.md`。

STOPはBatch1 PR。Batch2/#230/#231/Batch1 production適用は未開始。
#247/#249–#255はCLOSEDのまま。旧LKG / backup / protected data保持。
