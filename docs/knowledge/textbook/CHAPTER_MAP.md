# Knowledge → chapter map

本書は #44 の読書用projection。catalog/00–10 の正本分類を変更しない。
基準 corpus: `9142071e6b10a456a89cb8594ae62d95a07a50b2`。
棚卸し全件は `references/CORPUS_INVENTORY.json`。原資料は移動・変更しない。

| 本書章 | 主な原資料 | 統合・判定上の注意 |
|---|---|---|
| 0 読み方 | catalog/00, Governance, Registry | ACCEPTEDと実画像の検証を分離 |
| 1 モデル | catalog/01, Batch I/L/M, ledger | EPS/V-Pred、Anima各profileを分離 |
| 2 タグ | catalog/06, Batch E/F/G/H | canonical、runtime、unknownを分離 |
| 3 Special/Support | catalog/02, Batch A/B | 現行6役割。自動挿入を提案しない |
| 4 Prompt | catalog/02, Batch E/F/N | 人間の計画順とモデル順を分離 |
| 5 Weight | Batch D, K-TOOL-006/007 | parser説明と効能を分離 |
| 6 Negative | catalog/03, Batch I/J | K-NEG-002はHOLDのまま |
| 7 Pose/Viewpoint | catalog/02, Batch F | frame/orientation/visibilityを分離 |
| 8 複数人物 | catalog/02/03, Batch L/N | A_ONLY/B_ONLY/AB。非性的な例 |
| 9 成人向け用語と構造監査 | catalog/05, HARD_*研究 | 臨床的用語・意味・評価構造。露骨な画像生成レシピは収録対象外 |
| 10 LoRA | catalog/04, Batch L/M | strengthとPrompt weight、補助とbaseを分離 |
| 11 失敗 | catalog/03, Batch C/D | F1–F10とE0–E3を維持 |
| 12 実践 | Practical guide, catalog/02/03/04 | 1実験1問。単発から一般化しない |
| 13 ツール活用 | main PRODUCT_GOAL_LOCK, Batch G/H/J | 現行product優先、古いbranch-local目的は歴史 |
| 付録 | Registry, HOLD, ledger, source registry, Legacy Map | 全Claimの判定・scope・validation・日付を保持 |

## 棚卸し方針

直接利用可能: Registry、current metadata、catalogの現行説明。
統合必要: researchのモデル別調査、Prompt意味役割、scene planning、source audits。
HOLD: 未確定の効果は未確定欄へ。CONFLICTは0件であり架空の対立を作らない。
HISTORICAL: WAIを比較レーンとして扱うが、WAIのACCEPTED ClaimをHISTORICALへ変更しない。
重複: Index/File map/handoffを本文へ貼らず追跡台帳で保持。
収録対象外: 個別の露骨な性行為画像の生成・最適化レシピ、監査用巨大CSVの全文。
不足: KNOWLEDGE_GAPS.mdに記録。空白を推測で埋めない。
