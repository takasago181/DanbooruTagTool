# Issue #30 Phase 2 Machine Triage / Evaluator Provenance Audit — 2026-09-11

## RESULT

既存 Generation Batch 12画像を対象に、画像生成・新規seed・evaluator再実行なしで provenance と machine-first routing を監査した。

- New images: **0**
- Planned evaluator runs: **36**
- Actual successful evaluator runs: **36**（WD14 12 / Kagami 12 / CL 12）
- Failed/missing evaluator runs: **0**
- Raw artifact image binding: **PASS**
- Reported reference integrity: **FAIL**（33件の誤参照）
- A/B marker integrity: **PASS**

## MACHINE-FIRST ROUTING

- Machine-handled candidates: **0 images / 0 pairs**
- Human review required: **12 images / 6 pairs**
- Blocked: **0 images**
- Human-review reduction: **0.0%**

`HUMAN_REVIEW_REDUCTION = 0 for this batch design`。GB-001/GB-002はrelation・binding・body-site保護、GB-003はlow-confidence等により、全12画像を安全に機械処理済み扱いにはできない。これはユーザーではなく、バッチ選定/設計の省力化失敗である。

## PROVENANCE DEFECT

raw artifactは12画像×3 evaluatorで全36件が画像ID別に存在し、読み取り可能でerror objectもなかった。一方、既存 `calibration_results.json` の `raw_output_artifact` 欄は最終画像以外を中心に誤っており、実測で33件が期待参照と不一致だった。これはreporting defectとして記録し、正しい期待参照をmachine-readable audit JSONに再構成した。evaluatorの再実行はしていない。

## DECISION / NEXT

`HOLD_FOR_DEV_REVIEW`。Phase 2の次batchやStage10 production A/Bへ進めない。DEV/ChatGPTがこのauditを受け入れた後、必要ならmachine-judgeable direct/simple-unaryを意図的に含む4–5実験の別batchを判断する。

Existing local artifact root: `C:\Users\takas\Downloads\StabilityMatrix-win-x64\Data\Models\Issue30Evaluators\issue30_phase2_generation_batch_20260911`
