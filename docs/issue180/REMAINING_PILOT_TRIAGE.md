# Issue #180 — Remaining pilot authority triage

Status: RESEARCH / NO PRODUCTION APPLY

The latest artifact for commit `63c2c1adb8c474e3776961607c92c8a8a9f71bfa` contains **45**, not 56, rows still marked `NEEDS_AUTHORITY_REVIEW`. The earlier 56 count was a reporting error and is superseded by the artifact-derived count.

## Final triage

- **BULK_CURATED_LIST: 11**
  - 6 hololive roster cases.
  - 5 Touhou cases that should use the same curated-authority family as already accepted B002 Touhou rows, but still require explicit evidence before confirmation.
- **ROOT_OR_VARIANT_POLICY: 17**
  - 4 Piapro Characters whose official identity is clear but whose canonical HOME root is not represented/approved.
  - 2 Hatsune Miku variant rows that should wait for base-character HOME and A4 variant proof.
  - 11 qualifier/root-normalization cases.
- **INDIVIDUAL_RESEARCH: 17**
  - ambiguous identities, generic/non-Copyright qualifiers, legacy-only cases, or characters whose stable canonical root still needs independent proof.

Total: **45**.

## Evidence notes

The official hololive talent roster explicitly lists Shirakami Fubuki, Mori Calliope, Usada Pekora, Nekomata Okayu, Takanashi Kiara, and Sakura Miko, so these six are suitable for one curated-list authority rule.

Crypton/Piapro officially defines Hatsune Miku, Kagamine Rin, Kagamine Len, Megurine Luka, MEIKO, and KAITO as the Piapro Characters. This proves identity/group membership but does **not** by itself authorize mapping them to `vocaloid`; the product still needs an approved canonical HOME root.

Re:Zero's official character material identifies Rem. That supports the identity side of `rem_(re:zero)`; the remaining task is approval of the qualifier-to-canonical-Copyright root normalization.

## Expansion decision

Do not expand the current 250-row pilot to the full Character population yet. First close the 11 bulk curated-list cases and the reusable root-normalization mappings. The 17 individual cases remain manual/semantic review material. This preserves the rule that a wrong relation is worse than no relation.

No accepted source, main branch, or production runtime is modified by this triage.
