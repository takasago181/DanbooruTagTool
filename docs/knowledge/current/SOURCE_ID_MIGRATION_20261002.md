# Source ID Migration — 2026-10-02

Owner: Issue #44 `KNOWLEDGE:#44`

## 目的

`GENERATION_KNOWLEDGE_SOURCES.md` で発生していたSource ID衝突を、既存の先行entryを維持したまま修復した記録。

方針:
- 最初に存在したentryは旧IDを維持
- 後から同じIDを再利用したentryだけ新IDへ変更
- Source本文・URL・意味は変更しない
- Claim Registryのstatus/内容は変更しない
- research原本はrename/deleteしない

監査時、Claim Registryから衝突IDへの直接参照は0件だった。
関連する2026-10-02 research/current文書でも衝突IDの直接参照は検出されなかった。

## Research

| 旧IDの後発entry | 新ID |
|---|---|
| S-RESEARCH-019 #2 | S-RESEARCH-029 |
| S-RESEARCH-020 #2 | S-RESEARCH-030 |
| S-RESEARCH-021 #2 | S-RESEARCH-031 |
| S-RESEARCH-022 #2 | S-RESEARCH-032 |
| S-RESEARCH-023 #2 | S-RESEARCH-033 |
| S-RESEARCH-024 #2 | S-RESEARCH-034 |

## Tool

| 旧IDの後発entry | 新ID |
|---|---|
| S-TOOL-011 #2 | S-TOOL-018 |
| S-TOOL-012 #2 | S-TOOL-019 |
| S-TOOL-012 #3 | S-TOOL-020 |
| S-TOOL-013 #2 | S-TOOL-021 |
| S-TOOL-013 #3 | S-TOOL-022 |
| S-TOOL-014 #2 | S-TOOL-023 |
| S-TOOL-014 #3 | S-TOOL-024 |
| S-TOOL-015 #2 | S-TOOL-025 |
| S-TOOL-016 #2 | S-TOOL-026 |

## Practical

| 旧IDの後発entry | 新ID |
|---|---|
| S-PRACTICAL-004 #2 | S-PRACTICAL-008 |
| S-PRACTICAL-005 #2 | S-PRACTICAL-009 |
| S-PRACTICAL-006 #2 | S-PRACTICAL-010 |

## Community

| 旧IDの後発entry | 新ID |
|---|---|
| S-COMM-068 #2 | S-COMM-085 |
| S-COMM-069 #2 | S-COMM-086 |
| S-COMM-070 #2 | S-COMM-087 |
| S-COMM-071 #2 | S-COMM-088 |
| S-COMM-072 #2 | S-COMM-089 |
| S-COMM-073 #2 | S-COMM-090 |
| S-COMM-074 #2 | S-COMM-091 |
| S-COMM-075 #2 | S-COMM-092 |
| S-COMM-076 #2 | S-COMM-093 |
| S-COMM-077 #2 | S-COMM-094 |
| S-COMM-078 #2 | S-COMM-095 |
| S-COMM-079 #2 | S-COMM-096 |
| S-COMM-080 #2 | S-COMM-097 |
| S-COMM-081 #2 | S-COMM-098 |
| S-COMM-082 #2 | S-COMM-099 |

## 修復後Gate

- Source Registry ID total: 256
- duplicate Source IDs: 0
- Source本文削除: 0
- Claim status変更: 0

今後は新しいSourceを追加する前に、Source ID一意性を確認する。
