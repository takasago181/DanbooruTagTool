# Provisional Browse HOME overlay

User-authorized addition to Issue #216 after completion commit `9559b4ee54d9bc2a89f23f4c2a7f96210b40429e`. This independent research overlay covers all **10,102** frozen-cohort Characters whose formal HOME is empty, including blocked/conflict rows. It is not production data or accepted authority. The original completed coverage layer remains intact.

## Output and audit

`PROVISIONAL_BROWSE_HOME_V1.csv` contains one row per subject, sorted by descending frozen post count (canonical tag breaks ties). `rank` is within the 13,983 frozen cohort; it is not a rank across all Danbooru Characters. The required character, provisional_home, confidence, reason, evidence_hint and review_state fields are accompanied by rank, post_count and current_state.

- HIGH: recognizable membership in a quick review, or an exact work qualifier / own-wiki introductory membership phrase agreeing with a unique candidate. These are provisional inferences, not verified exact authority.
- MEDIUM: a plausible unique work/ecosystem candidate, or an explicit provisional preference among related titles/brands. Candidate-only mappings are deliberately MEDIUM, never promoted to formal HOME.
- LOW: empty provisional_home and `PROVISIONAL_UNRESOLVED`; retain OC/artist-qualified, real-person, unresolved variant, conflicting identity, generic ecosystem-only and independent multiple-IP cases.

Confidence is a review priority label, not a calibrated probability. HIGH can still be wrong. Company/mascot/ecosystem candidates and guest-context risks need attention during audit; a unique frozen candidate can itself be stale or misleading. Each assigned row is `PENDING_AUDIT`; no row is already accepted. The later separate audit should record ACCEPT / CHANGE / REJECT and inspect the reason and hints before acceptance. Changing this overlay never changes formal authority decisions.

## Fast pass and reproducibility

The pass reused the frozen graph's candidate/family hints, verified alias index for qualifier normalization, frozen post-count snapshot, and 977 available own-character wiki pages from the previously retained review archives. Only cached introductory wiki text supplied additional hints; no new network request, per-character source search or source registry record was required. This intentionally permissive hint use applies only to this overlay.

Artist-category qualifiers, candidate-only variant identity and existing formal conflict/identity findings are held unresolved. Independent multiple-work hints are not silently ranked. A small explicit recognition table handles readily recognizable high-frequency names and brand choices; related-franchise preferences are labeled in the script. All proposed roots must already exist in the frozen Copyright catalog. No fuzzy match is used.

`PROVISIONAL_BROWSE_HOME_INPUTS_V1.csv` is the compact frozen projection used by the builder; the adjacent JSON records hashes of its originals and the normalized projection. It retains the actual candidate set, qualifier, variant status, cached-wiki context, formal state and frequency for each subject so later audit does not need to reconstruct scratch proposals.

Rebuild using `python scripts/issue216/build_provisional_browse_home.py`. The builder writes only this overlay and its six-metric checkpoint. It checks population equality with all empty formal HOME rows, unique identity and root existence. Formal decisions, registry, members, roots and protected input hashes were checked unchanged against the captured base inputs. No authority validator, canonical ledger, production consumer or runtime was modified. No additional test suite was added or run for this fast classification pass.

## First checkpoint

| Metric | Count |
|---|---:|
| inspected | 10,102 |
| provisional HIGH | 308 |
| provisional MEDIUM | 6,703 |
| provisional unresolved | 3,091 |
| Top500 remaining provisional unresolved | 38 |
| Top2000 remaining provisional unresolved | 441 |

The 7,011 assignments await the separate semantic audit. The unresolved population has also been inspected; it is not an unfinished research queue.
