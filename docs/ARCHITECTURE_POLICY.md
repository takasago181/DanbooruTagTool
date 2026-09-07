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
