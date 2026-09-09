# Prompt user-burden minimization policy

Date: 2026-09-10
Status: ACTIVE PROJECT POLICY

## Purpose

For DanbooruTagTool development, validation, and Stage10 evaluation, do not add unnecessary restrictions or manual work to test Prompt workflows merely as a precaution or convenience for the implementation side.

This policy does not remove safety or platform boundaries. Within the supported scope, however, the project must minimize the amount of Prompt reconstruction, Special lookup, tag replacement, and repetitive trial-and-error pushed back to the user.

## Fixed policy

1. Do not introduce Prompt restrictions that are unrelated to the actual test objective, model constraint, evidence requirement, or applicable safety boundary.
2. Do not weaken, generalize, euphemize, or make vague a supported user-specified Special/intent merely to make a test Prompt easier to produce.
3. PROMPT / Stage10 preparation should assemble the completed Prompt as far as possible before presenting it to the user.
4. Where a direct completed Prompt cannot be produced, localize only the minimum unresolved portion instead of turning the whole Prompt into placeholders.
5. Do not require the user to manually search the Special Core Dictionary / historical Special2788 corpus when the project can deterministically produce candidate(s).
6. Candidate selection should normally be reduced to a small set with a recommended first choice and Japanese explanation where useful.
7. Camera, pose, visibility, quality, negative, support structure, model-family handling, and other supported surrounding Prompt construction should be handled by the project rather than returned to the user as unnecessary manual editing.
8. For Stage10 A/B evaluation, design the workflow so that the user's normal responsibility is as close as practical to:
   - generate/receive the prepared A/B pair;
   - inspect the images;
   - choose which result is closer to the intended goal or mark REVIEW/UNKNOWN when necessary.
9. Prompt assembly, candidate expansion, traceability, fixed-seed setup, metadata capture, and repeatable comparison should be automated wherever practical and reliable.
10. Do not make the user repeatedly rebuild Prompts between A/B cases when the tool or evaluation harness can do so deterministically.
11. Minimum-sufficient Prompt remains the design target. More tags or more manual switches are not considered higher quality by themselves.
12. If evidence is insufficient, use HOLD / REVIEW / IMAGE_TEST_REQUIRED rather than compensating by adding broad manual restrictions to every test.
13. Safety or platform boundaries remain applicable and are not traded away as compensation for project defects or development incidents.

## Stage10 quality target

The preferred Stage10 interaction is:

`prepared deterministic A/B -> user inspects -> user chooses A/B/REVIEW`

The project should treat any additional repetitive user operation as implementation debt and remove or automate it when this can be done without weakening traceability, evidence quality, model-family separation, or safety boundaries.

## Relationship to existing rules

This policy strengthens the existing `PERMANENT_RULES.md` Prompt-support rules that already require:
- minimizing manual Special exploration and Prompt reconstruction;
- minimizing the number and scope of unresolved slots;
- preserving supported Special identity/strength instead of diluting it;
- keeping final Prompt payload canonical and traceable.

If a future Prompt, Stage10, TEMP automation, or evaluator design conflicts with this policy, the conflict must be explicitly documented and justified rather than silently shifting work back to the user.
