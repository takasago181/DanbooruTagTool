# Issue #30 Phase 2 human review result — 2026-09-10

ユーザーが番号付きcontact sheetの12枚を確認した。所見は「対象が存在するか」と「指定した部位・関係が成立しているか」を分けて記録した。これは今回のWAI17 / Forge Neo profileに限定された結果であり、production AUTOの根拠ではない。

## Pair results

| Experiment | Seed | Human answer | Result | Validity | 要約 |
|---|---:|---|---|---|---|
| P2-001 `vibrator in anus` | 41001 | neither | BOTH_FAIL | TARGET_REALIZATION_FAILED | Aはバイブが膣側、Bは肛門内と判定できない |
| P2-001 `vibrator in anus` | 41002 | neither | BOTH_FAIL | TARGET_REALIZATION_FAILED | Aは肛門に何もなく、Bも肛門内と判定できない |
| P2-002 `holding sex toy` | 41011 | A | A_ONLY_PASS | VALID_FOR_THIS_PAIR | Aだけ手持ち成立 |
| P2-002 `holding sex toy` | 41012 | both | BOTH_PASS | CONTRAST_CONTAMINATED | Bにも手持ちが出現 |
| P2-003 `breast expansion` | 41021 | both | BOTH_PASS | VALID_FOR_TARGET_REALIZATION | A/Bとも成立、Bが大きい |
| P2-003 `breast expansion` | 41022 | both | BOTH_PASS | VALID_FOR_TARGET_REALIZATION | A/Bとも成立、Aが大きい |

## Decision

- P2-001: `HOLD_HUMAN_REVIEW_ONLY`。Taggerが部品を検出しても、device-to-body-site bindingは成立しなかった。
- P2-002: `HOLD_HUMAN_REVIEW_ONLY`。1 seedではA優位、1 seedではB対照が汚染され、AUTO根拠にはならない。
- P2-003: `HOLD`。2 seedともA/Bでtargetは成立し、今回の条件ではNegativeに入れても抑制は観測されなかった。ただしサイズ差は記録するだけで、一般則へ拡張しない。

Artifact gateは12/12 PASS。追加seed・追加実験は実施せず、DEV/ChatGPT reviewへ停止する。

Machine-readable record: `ISSUE30_PHASE2_HUMAN_REVIEW_RESULTS_20260910.json`
