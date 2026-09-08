# ARCHITECTURE_POLICY.md

## 拡張性は5境界だけ

1. DataSource
2. TagSearchEngine
3. CooccurrenceEngine
4. Translation / SpecialDictionary
5. PromptFormatter

CoreはGUI非依存。

将来:
- standalone
- Forge
- ComfyUI
- CLI
へ再利用可能にする。

ただしfront-end plugin frameworkは今作らない。

## External / Existing Tool First

新しい機能・補助ツール・自動化を追加する前に、まず既存資産で目的を満たせないか確認する。

優先順:
1. 既に導入済み・利用中の機能/拡張
2. 対象アプリの標準機能
3. 対象環境に対応した既存拡張
4. ローカルで利用できる既存CLI / API / OSSライブラリ
5. それでも残るgapだけを最小限の自作コードで補う

既存資産を使う場合も、互換性・安全性・再現性・保守性・ユーザー操作量を確認する。
既存資産で十分に目的を満たせる機能を、DanbooruTagTool側へ重複実装しない。
自作の方が実装上きれいという理由だけで既存資産を置き換えない。
外部資産の利用はruntime非LLM・ローカル個人利用という既存方針を変更しない。cloud/runtime依存を新たな前提にしない。

## 禁止する過剰設計

- PluginManager
- Event Bus
- Service Locator
- generic DB abstraction
- multiple GUI backend abstraction
- generic API connector framework
- cloud sync
- ranking plugin system
- incremental update framework

## Runtime RAM

ターゲットPC:
32GB RAMでForge Neo / Illustriousを同時利用。

「単体で動く」だけでなく、
生成環境と同時常駐して邪魔にならないことを評価する。

TRIAL v0.2の巨大JSON全展開は最終形式として採用しない。
