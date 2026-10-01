# Final high-frequency Browse review

Base: `e5b6361e52f95b372a8672d2b0fc47d07a433145`.

This completes the requested last high-frequency audit: every one of the 145
remaining Top2000 unresolved subjects received an individual light visual
review of tag identity, qualifiers, frozen candidates and retained own wiki
context. No new external Character searches or deep research were performed.

| Requested result | Count |
| --- | ---: |
| Browse HOME additions | 1 |
| Retained unresolved | 144 |
| Final Top2000 unresolved | 144 |
| Final Top500 unresolved | 10 |

`sasha_(haguhagu) -> sasha-chan_to_classmate_otaku-kun` is the only addition.
Her own page explicitly identifies her as the current heroine of that published
manga. This distinguishes an author-qualified published-work Character from a
standalone OC. The Browse choice does not certify formal authority, and does not
force any unrelated earlier continuity into this manga scope.

## Why the others remain

| Retained reason | Count |
| --- | ---: |
| Creator original | 57 |
| Avatar / persona | 36 |
| Performer / fan representation | 13 |
| Insufficient identity context | 13 |
| Real person / actual animal | 11 |
| Concept / folklore / non-work | 7 |
| Fan OC / multiple identities | 5 |
| Shared company mascot | 1 |
| Multiple IP ambiguity | 1 |

Representative checks:

- Shigure Ui, Dokibird, Sameko Saba and their costumes remain avatar identities;
  another persona, designer, guest game or former affiliation does not establish
  ordinary work membership. Pekomama remains a person/avatar boundary case.
- Sakurai Masahiro, Yagoo, voice actresses and actual racehorses remain real
  subjects, rather than Characters of works they created, voiced or inspired.
- Cookie tags describe performers or fan representations; they do not become
  canonical Touhou cast. Sendai Hakurei no Miko explicitly aggregates multiple
  fan-original identities and is distinct from the canon Satori character.
- Santa Claus, Mishaguji, death personifications and mythological Anubis retain
  the concept/folklore identity instead of a game-specific incarnation.
- Alexiel explicitly covers both Shingeki no Bahamut and Granblue Fantasy.
  Respawn Nessie is a shared company mascot across multiple games. Neither is
  silently assigned an arbitrary single title.
- Empty/absent own text leaves Akama Ichibee, Karen-chan and other insufficiently
  described identities unresolved. Candidate hints alone are not used to rescue
  them. Missing text is not proof of nonmembership or originality.

Every individual disposition and excerpt is in
`BROWSE_TOP2000_FINAL_REVIEW_V1.csv`. Raw exact own-page bodies were projected
from previously retained inputs into `BROWSE_TOP2000_FINAL_CONTEXT_V1.json.gz`:
144 available pages, 12 empty bodies and one absent own page. Original raw
archives and all prior versions remain retained.

The complete independent final overlay is
`REVIEWED_BROWSE_HOME_FINAL_V1.csv`: 7,746 assigned Browse HOME and 2,356
reviewed unresolved, accounting for all 10,102 subjects once.

Reconstruct the overlay and checkpoint without network by running
`python scripts/issue216/apply_final_top2000_browse_review.py`. This replays
frozen individual review dispositions; it does not re-research or infer them.
Input hashes are recorded in `BROWSE_TOP2000_FINAL_CHECKPOINT_V1.json`.

Data checks: 145 exact selected subjects, complete accounting, unique identity,
root existence, deterministic byte reconstruction, unchanged rows outside the
145 subjects, and byte preservation of prior overlays / formal ledgers.
`git diff --check` passed. No local unit tests added or regression suite run for
this data audit. Existing branch CI separately validates the formal layer.

Formal #180/#216 authority remains unchanged. Every row is
`formal_authority_eligible=NO`. No main merge or production apply. The final
high-frequency audit is complete; remaining ambiguity is an explicit reviewed
outcome and does not trigger further source hunting in this task.
