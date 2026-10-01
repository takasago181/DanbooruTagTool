# No-obvious-classification Browse review

Base: `96c70ad822ef1db319c1639aebff98c77978e68d`.

All 1,278 previously unresolved subjects with
`NO_OBVIOUS_ADDITIONAL_CLASSIFICATION` were sorted together. Classification
describes a likely subject class for this Browse pass, not formal identity or
authority certification. Candidate roots are routing hints, not proof.

| Requested result | Count |
| --- | ---: |
| Work Character-like | 220 |
| Of those, Browse HOME added | 194 |
| Avatar / creator OC / concept / non-work | 754 |
| Other / ambiguous | 304 |
| Whole overlay unresolved | 2,357 |
| Top2000 unresolved | 145 |

The 220/754/304 classification accounts for all 1,278 subjects. All 194
assignments are additions from the work-like class; 26 work-like subjects remain
unresolved. The other two classes remain unresolved. Prior unresolved was
2,551; Top2000 was 148, so three high-value subjects were added. Top500 remains
ten. The whole overlay now has 7,745 assignments and 2,357 unresolved, accounting
for all 10,102 subjects once.

## Shared review patterns

- Named forms, costumes and versions: own-page explicit base identity plus
  frozen confirmed/reviewed base Browse context. Recognizable short/empty-page
  forms were reviewed as a named group, without claiming validated VARIANT_OF.
- Explicit unique work descriptions: actual character membership phrases and
  exact canonical work context, with human light-review choices for clear
  rootless Characters. No arbitrary first-link choice.
- Named voicebank versions: explicitly described software ecosystem, rather
  than blindly inheriting a different engine from the base. Yuzuki Yukari
  Vocaloid/AI Voice/CeVIO variants and Hanakuma Chifuyu SV are kept distinct.
- Origin versus guest/event: Hyper Roll uses Mega Man, Shiranui Mai's SF6 costume
  uses Fatal Fury, Sangonomiya Kokomi's Sushiro costume uses Genshin, and Miku
  Symphony designs use Vocaloid. Monika's explicit first appearance selects
  Shingeki no Bahamut rather than a later guest title.
- Independent/agency avatars, artist/commissioner OCs, real persons, streamer
  fan mascots and general concepts remain outside the work-class acceptance
  pass. Known avatar-base context also prevents misclassifying a costume whose
  own description omits the word VTuber. Agency avatars are not being declared
  independent; they are simply handled separately from fictional work cast.
- Multiple shared IP contexts, uncertain original identity and missing/empty
  descriptions stay unresolved. Patches, Alexiel and broad shared mascots are
  not silently routed to one associated game. Candidate-only skins are not
  automatically accepted.

## Retained inputs and output

Reused 47 own wiki pages; 16 exact-title bulk API requests returned 1,075 more.
Raw 1,122 pages, the 156 absent exact titles, source URLs, fetch timestamps and
page versions are frozen in `BROWSE_RESIDUAL_REVIEW_WIKI_INPUTS_V1.json.gz`.
Absence and empty text are not evidence of nonmembership or originality.
No individual Character search/deep research or full wiki recrawl was performed.

- `BROWSE_RESIDUAL_THREE_WAY_REVIEW_V1.csv`: all selected subjects, their class,
  light-review result, saved base context and own-page excerpt.
- `BROWSE_RESIDUAL_REVIEW_GROUPS_V1.csv`: shared class/pattern/root counts.
- `REVIEWED_BROWSE_HOME_V3.csv`: complete independent overlay after this pass.
- `BROWSE_RESIDUAL_REVIEW_CHECKPOINT_V1.json`: accounting and input fingerprints.

Rebuild with `python scripts/issue216/review_no_obvious_browse.py`, using only
tracked frozen inputs and no network. Human named judgments and shared review
conditions are retained in that script.

Data checks: unique identities, complete accounting, assigned-root existence,
deterministic output byte equality, unchanged subjects outside the selected
population, and byte preservation of previous overlays/formal ledgers.
`git diff --check` passed. No local unit tests were added or regression suite
run for this data audit; existing formal-authority CI is separately reported.

Formal #180/#216 authority remains unchanged. Every row retains
`formal_authority_eligible=NO`. No main merge or production apply.
