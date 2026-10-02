# BATCH_AG — Anima relation-stress community evidence — 2026-10-02

Owner: Issue #44 `KNOWLEDGE:#44`
Branch: `knowledge/generation-corpus`
Mode: community failure synthesis
Scope: multi-subject pairwise interference, strong-prior leakage, 3+ subject stress, interaction-heavy scenes

## 1. Pairwise interference

Sources:
- https://huggingface.co/circlestone-labs/Anima/discussions/93
- https://huggingface.co/circlestone-labs/Anima/discussions/120

Repeated structure:
- identity A works alone;
- identity B works alone;
- A+B can fail badly;
- adding obvious appearance descriptors can help some pairs and fail others.

This is stronger evidence for:
`pairwise/compositional interference`
than for:
`identity unknown`.

Required diagnostic:
A_ONLY -> B_ONLY -> AB minimal.

Promoted:
- K-COMM-ANIMA-017.

## 2. Strong series/concept leakage

In discussion #93, one user reports that a strong series/concept surface appeared to bleed its learned traits across subjects.
Reducing that surface's weight improved the shown pairing.

Project treatment:
- useful contamination hypothesis;
- not a universal weight threshold;
- exact cause could be text-encoder leakage, training co-occurrence or prompt context.

Promoted:
- K-COMM-ANIMA-018.

## 3. Three-plus subject stress

Discussion #120 contains attempts with:
- 3–4 subjects;
- distinct positions;
- distinct visual attributes;
- distinct clothing;
- distinct held objects.

Users report severe bleed and recommend regional prompting for this level of constraint.

This matches general research:
- K-HARD-009
- CompAlign multi-subject complexity results.

Project consequence:
Anima stress classes should distinguish:
- 2 subjects / simple relation
- 2 subjects / many bound attributes
- 3+ subjects
- 3+ subjects + distinct resources/actions

Promoted:
- K-COMM-ANIMA-019.

## 4. Interaction-heavy adult feedback

Source:
https://huggingface.co/circlestone-labs/Anima/discussions/13

Public feedback reports:
- subject count can be correct while sex/body-linked traits attach to the wrong subject;
- interactions with objects/other subjects remain difficult in some cases;
- unusual/extreme concepts can be weak or unstable.

We do not preserve explicit prompt wording.
We preserve the structural failure:
`correct entities + wrong role/body-site assignment`.

Promoted:
- K-ADULT-007.

## 5. Adult relation evaluation consequence

Do not score only:
- “both subjects present”.

Also score:
- role owner
- body-site owner
- interaction target
- visible relation
- wrong cross-subject trait transfer
- count

## 6. Prompt-vs-control routing

If:
- A_ONLY good
- B_ONLY good
- AB bad

First:
- reduce redundant/high-pressure shared context;
- add stable subject-specific descriptors;
- test pairwise minimal Prompt.

If still bad:
- regional/mask control;
- masked/scheduled LoRA where adapters are involved;
- local reconstruction if global composition is already acceptable.

Do not conclude concept ignorance until isolated tests fail.

## Promotion result

New CANDIDATE:
- K-COMM-ANIMA-017
- K-COMM-ANIMA-018
- K-COMM-ANIMA-019
- K-ADULT-007
