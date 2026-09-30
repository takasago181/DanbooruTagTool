# KNOWLEDGE Current HOLD / CONFLICT Register

Current verdict authority: `CLAIM_REGISTRY.csv`.

This file centralizes unresolved knowledge so it cannot disappear inside category prose. It does not itself promote a claim.

## Open HOLDs

| HOLD ID | Related Claim IDs | What is unknown | Why unresolved | Resolution required | Intended downstream owner | Stage10? |
|---|---|---|---|---|---|---|
| H-K-001 | K-SEM-004 | canonical vs Alias vs historical/model trigger activation by exact checkpoint | semantic equivalence does not prove model response | pinned-version controlled A/B; preserve exact prompt surfaces | KNOWLEDGE -> PROMPT when authorized | YES |
| H-K-002 | K-SUPPORT-004 | broad+specific help/harm on rare WAI17 Specials | possible reinforcement or dilution | specific/broad/combined paired seeds | PROMPT / Stage10 | YES |
| H-K-003 | K-HARD-007 | WAI17 actor-target/body-site binding ceiling | exact project-family evidence missing | representative relation cases, multi-seed | PROMPT / Stage10 | YES |
| H-K-004 | K-HARD-007 | WAI17 restraint topology ceiling | object presence != topology | topology-scored controlled cases | PROMPT / Stage10 | YES |
| H-K-005 | K-HARD-007 | WAI17 machine/device functional relation ceiling | device presence can false-pass | functional-contact/body-site scoring | PROMPT / Stage10 | YES |
| H-K-006 | K-HARD-007 | WAI17 tentacle source/ownership relation ceiling | source/ownership ambiguity | source-owner-target relation cases | PROMPT / Stage10 | YES |
| H-K-007 | K-HARD-007 | simultaneous Special/count breakpoint | semantic workload not raw count | 1->2->3+ representative complexity ladder | PROMPT / Stage10 | YES |
| H-K-008 | K-NEG-002 | unusual anatomy/count Negative ON/OFF effects | Negative can suppress intended target | family-specific Negative OFF/ON pairs | PROMPT / Stage10 | YES |
| H-K-009 | K-LORA-002 | LoRA × Special/support interaction | adapter can import context/prior/interference | base/A/B/A+B under pinned LoRA/checkpoint | PROMPT / Stage10 follow-up | CONDITIONAL |
| H-K-010 | K-MODEL-NOOB-004 | NoobAI EPS camera/visibility placement and hard relation behavior | author caption order known, exact benefit not | exact-version controlled tests | PROMPT / Stage10 | YES |
| H-K-011 | K-MODEL-NOOB-004 | NoobAI canonical/historical/e621 trigger response | training surface may differ from current canonical | historical surface audit + pinned A/B | KNOWLEDGE -> PROMPT | YES |
| H-K-012 | K-MODEL-ANIMA-004 | Anima tag-only vs concise-hybrid relation delta | community/controlled examples do not establish general rule | profile-specific paired tests | PROMPT / Stage10 | YES |
| H-K-013 | K-MODEL-ANIMA-004 | Anima multi-character/hard-relation ceiling by Base/Aesthetic/Turbo | profiles differ and community evidence is limited | profile-pinned representative tests | PROMPT / Stage10 | YES |
| H-K-014 | K-EVAL-004 | Special2788/final-dictionary coverage across WD EVA02/Kagami/CL Tagger | final dictionary not frozen; evaluator semantic capability differs | after final freeze: vocabulary/mapping/calibration/OOD coverage comparison | KNOWLEDGE, then PROMPT/#30 when authorized | YES |
| H-K-015 | K-EVAL-002; K-EVAL-003 | rare-tail evaluator reliability and relation suitability | wide vocabulary != accuracy or relation ground truth | human-labeled representative calibration | KNOWLEDGE / AUDIT / Stage10 | YES |
| H-K-016 | K-TOOL-004 | Prompt-only -> Forge Couple/ControlNet escalation threshold | assisted tools can rescue but exact stop point unknown | bounded prompt ladder then assisted comparison | PROMPT / Stage10 | YES |
| H-K-017 | K-MODEL-WAI-004; K-MODEL-WAI-005 | exact local WAI17 checkpoint hash and runtime commit identity | current baseline records names/settings, not immutable hashes | record local checkpoint hash + Forge Neo git remote/commit before promotion-critical evidence | KNOWLEDGE / local environment | BEFORE TEST |
| H-K-018 | K-QUALITY-001 | exact family-specific quality/meta effect on target reliability | practical evidence shows composition/style changes, not universal reliability effect | controlled target-level comparisons | PROMPT / Stage10 | CONDITIONAL |

## Active CONFLICTs

No unresolved global conflict is currently promoted as a current rule. Credible disagreements that become irreducible after version/scope separation must receive:
- a Registry row with `STATUS=CONFLICT`;
- a row here;
- both evidence chains;
- an explicit resolution test/source recheck.

Historical disagreements already resolved by scoping/rejection remain in `LEGACY_MAP.md` / `K-REJECT-*` rather than being kept as fake active conflicts.

## HOLD closure rule

A HOLD closes only when:
1. its related Claim row is updated;
2. evidence identity and exact scope are recorded;
3. required validation state is satisfied or explicitly changed with rationale;
4. this register records the closure/removal in the same management change;
5. downstream handoff is performed only when authorized.

Do not close HOLD merely because a community post, another model family, or one seed appears persuasive.
