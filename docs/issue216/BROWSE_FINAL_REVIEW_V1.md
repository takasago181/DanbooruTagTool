# Issue #216 Browse HOME final review

Base: `2c23f513bab43d04f87a020daf39ef8a79b251bc`.

## Disposition

All 10,102 subjects of the independent provisional overlay have a bounded
Browse review disposition. These results are product browsing judgments, not
formal authority certification. An unresolved outcome is deliberate.

| Result | Count |
| --- | ---: |
| Reviewed Browse HOME | 7,495 |
| Reviewed unresolved | 2,607 |
| Added from prior unresolved | 244 |
| Existing Browse HOME changed | 2 |
| Existing Browse HOME removed | 7 |
| Top500 unresolved | 10 |
| Top2000 unresolved | 157 |

The prior review contained 7,258 assignments and 2,844 unresolved subjects.
The net gain is 237 assignments. Top2000 unresolved decreased from 211 to 157.
These ranks refer to the original frozen 13,983 cohort, not a reranked overlay.

## Review coverage

- All original Top500 open ten were checked against actual own-page bodies.
  Nine bodies were retained locally; Yorick was covered by one new bulk wiki
  request. Yorick belongs in Hololive through Shiori Novella. The other nine
  remain independent avatars without a specific catalog root, an OC, or an
  ambiguous fan-character collection. Their individual notes are in
  `BROWSE_FINAL_TOP500_CHECKS_V1.csv`.
- The 211 originally open Top2000 subjects have a focused disposition table in
  `BROWSE_FINAL_TOP2000_CHECKS_V1.csv`. Named work characters, mascots, origin
  rather than guest IP, voice-synthesis ecosystems, and costume/form families
  were reviewed together. OC, performer, independent-avatar and identity
  ambiguity groups remain unresolved. This table covers the original 211;
  removals from previously classified subjects are also present in the full
  output.
- The complete residual population was reviewed by subject class and shared
  family. Explicit Characters sections of named creator works can distinguish
  published characters from standalone OCs. Nested author qualifiers do not
  justify blanket acceptance: unclear creator identities stay unresolved.
- Only named, reviewed costume/form families and explicit coherent costume
  context were added. This does not validate VARIANT_OF for formal authority.
  Honkai variants use the broader franchise Browse context. Arknights collab
  forms of BanG Dream characters retain BanG Dream HOME.

## Corrections and unresolved classes

Seven removals: Pekomama, Mafia Kajita, Uzuki/Kanna/Sananana/Taisa (Cookie),
and Bao the Whale. Person versus avatar/performer representation is unresolved
for the first six. Bao's own page identifies an independent streamer avatar;
the prior Kakkou no Iinazuke assignment was a related-context error.

Pekomama is a new Top500 unresolved subject. Bao adds a Top2000 unresolved
subject. Accordingly, Top500 remains ten despite resolving Yorick.

Symphony Meiko and Symphony Kaito were changed from the event root to Vocaloid.
Event outfits do not make the event the character's natural Browse HOME.
Voice providers mentioned in a fictional character page were not treated as
proof that the character itself is a real person. Cottontail's VTuber avatar is
explicitly distinct from the voice actor, but still lacks a clear catalog HOME.

Residual pattern counts are in the checkpoint. The largest classes are
1,278 without an obvious single destination, 1,092 artist-qualified original
or derivative identities, and 167 real-person/performer contexts. These are
reviewed unresolved, not silently assigned generic `original`/VTuber roots.

## Inputs and reconstruction

`BROWSE_FINAL_REVIEW_CONTEXT_V1.csv` freezes exact own-page introductions and
page IDs from the retained Issue #216 wiki archives, supplemented by
`BROWSE_FINAL_LIGHT_REVIEW_INPUTS_V1.json`. Full previously retained bodies are
in the existing curated/high-value review archives; the supplemental raw JSON
preserves all eleven returned pages from one exact-title API batch. Empty or
absent pages were not used as negative membership proof. No broad wiki recrawl
or character-specific deep research was performed.

Run `python scripts/issue216/finalize_browse_home_review.py` to reconstruct the
five output CSV/JSON artifacts from tracked inputs, without network access.
Input hashes are recorded in `BROWSE_FINAL_REVIEW_CHECKPOINT_V1.json`.

Data checks performed: deterministic reconstruction byte equality, 10,102
unique subjects, accounting, all assigned roots exist, and byte equality of
formal ledgers and previous overlays against the base. `git diff --check`
passed. No new unit tests or local regression suite were run for this data audit.

Formal #180/#216 decisions, source registry and source members are unchanged.
No main merge or production apply. Every output row has
`formal_authority_eligible=NO`; promotion requires a separate explicit task.
