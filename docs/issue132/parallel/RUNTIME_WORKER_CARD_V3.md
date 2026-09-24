# Issue132 Runtime Worker Card V3

Purpose: keep normal worker runs short, deterministic, and semantic-first.

## Hot-path authority
Normal run reads only:
1. this card;
2. WORKER_EXECUTION_CARD_V1.md for semantic rules;
3. own lane status;
4. exact shard + shard manifest needed for the forward frontier.

Do NOT read CURRENT_AUTOMATION_OPERATION.md, coordinator history, quality_flags, old CI logs, or unrelated staging during a normal forward run unless this card or the semantic card cannot resolve a concrete conflict.

## Scope
Each worker owns one lane only. Never edit another lane, main, production, UserData, #64/#76/#118.

Old invalid staging debt is NOT a normal worker responsibility. The repair automation owns pre-existing invalid windows. Normal workers move the forward frontier only.

## Run algorithm
At run start, read own status and determine the forward next_new frontier. Set a fixed target of exactly 12 consecutive 25-identity windows = 300 NEW identities, bounded only by lane end.

For window 1 through window 12:
1. Load the authoritative 25 source tuples from the validated shard: (lane_local_index, review_seq, identity_key).
2. Finalize each identity once under WORKER_EXECUTION_CARD_V1.md.
3. A genuine unresolved identity may become a hold only after bounded identity-specific research; continue later tuples without shifting positions.
4. Before write, require exact 1:1 tuple coverage: no gaps, duplicates, extras, shifted rows, wrong review_seq, or wrong identity_key; finalized + holds must equal window size.
5. Write the staging/checkpoint using create for NEW path or current SHA for EXISTING path.
6. Re-fetch the exact written file and repeat the tuple gate. If it fails, repair/delete that window before continuing; count zero progress until fixed.
7. Immediately begin the next window. Do not decide whether to continue.

Every fourth completed window, perform the required cumulative 100-row QA from the semantic card, persist definite fixes, then immediately continue.

## Semantic speed rules
Prefer one strong CORE route. Add route2 only if it is an independent realistic browse axis, not merely true.
- color/pattern adjective alone != COLOR_PATTERN_SHAPE;
- object/clothing placement alone != POSE_POSITION;
- animal/plant motif or print alone != LIVING;
- object presence alone != SCENE_BACKGROUND;
- body/theme/local refinements must be intrinsic/entailed.
Research only material ambiguity.

## Stop
Normal terminal states:
- 12 windows / 300 NEW completed;
- lane complete;
- evidenced hard tool/contract conflict preventing safe write and fallback;
- actual platform-forced interruption.

Never self-stop because one 25-row save succeeded, QA completed, elapsed effort feels high, or a report would be convenient. Do not retry old blocking holds at run start; repair/coordinator handles old debt.

## End
Write status once at terminal/end boundary. Keep report compact: start, end, NEW count, finalized/holds, next_new, blocker if any.
