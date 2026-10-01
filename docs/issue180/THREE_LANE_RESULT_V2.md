# Issue #180 — Three-lane result checkpoint v2

Source CI: `35627966162` — **success**

## Lane A — Batch A authority worklist

- mechanically ready families: **12**
- authority approved: **0**
- second review required: **12**

This lane remains authority-gated. Exact catalog presence is not sufficient for HOME approval.

## Lane B — next 50 qualifier families

Total: **50 families / 2,227 Character rows**

- P1_EXACT_ROOT: **33 families / 1,299 rows**
- P2_NORMALIZATION: **0 families / 0 rows**
- P3_SEMANTIC_RESEARCH: **17 families / 928 rows**

P1 means the qualifier text already exists as an exact Copyright root; it is still not automatic HOME authority.
P3 has no direct Copyright root and must not be guessed.

P1 examples include `ragnarok_online`, `senran_kagura`, `precure`, `last_origin`, `final_fantasy`, `chainsaw_man`, `overwatch`, `nijisanji`, `dragon_ball`, `street_fighter`, `elden_ring`, `idolmaster`, `marvel`, and `guilty_gear`.

P3 examples include `league`, `mega_man`, `housamo`, `girls'_frontline_2`, `sekaiju`, `splatoon`, `cookie`, `hetalia`, `tales`, `kirby`, `naruto`, `neptunia`, `nanoha`, `sao`, `neural_cloud`, and `tf2`.

## Lane C — unqualified Character control

Deterministic sample: **200 rows**

- MULTI_TOKEN_UNQUALIFIED: **165**
- SINGLE_TOKEN: **35**
- variant-like suffix bucket: **0**
- unexpected trailing qualifier: **0**

This confirms that the unqualified population cannot be reduced by the same final-parenthetical-qualifier rule used by the qualifier lanes. It needs a distinct authority strategy.

## Next split

The CI now materializes three explicit work products:
1. P1 exact-root authority batch — 33 families / 1,299 rows
2. P3 semantic research batch — 17 families / 928 rows
3. unqualified authority worklist — 200 controls

All remain research-only. No accepted relation, main, or production mutation.
