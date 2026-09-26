# Issue #180 — Codex research stop protocol v2

Status: **ACTIVE**

Purpose: prevent one obscure Character or one unproductive search path from consuming disproportionate Codex quota while preserving Issue #180's rule that missing relation is preferable to a wrong relation.

This protocol does **not** lower the evidence bar. It only defines when a Forward worker stops searching and records a safe unresolved research outcome.

## 1. Reuse before search

Before opening a new web search:

1. inspect the current lane dispatch row;
2. use any `source_hint_urls` first;
3. inspect already approved Issue #180 evidence/decision rows relevant to the same root or authority;
4. only then search for a new authority source.

An accepted source hint means QA already approved the source identity/scope/mapping rule. Forward still checks that the exact Character/member is actually named or otherwise explicitly covered by the page.

## 2. Search routes, not query permutations

A **route** is a distinct authoritative path, for example:

- official work/character/roster page;
- official publisher/developer announcement or cast page;
- official product/store page published by the rights holder/developer/publisher;
- an already accepted source family recorded in `SOURCE_REVIEW_LEDGER_V2.csv`.

Changing search wording against the same site/page lineage is not a new route.

Search-engine results, snippets, mirrors, wikis, fandom pages, Reddit and community lists may help discover an allowed source but are not promoted into HOME evidence unless the existing Issue #180 policy explicitly permits that source class.

## 3. Route budgets

These are ceilings for routine Forward research, not evidence thresholds.

- `FAMILY_ROSTER_HIGH_YIELD`: up to **4** distinct safe authority routes.
- `VARIANT_BASE_READY`: up to **3** distinct safe authority routes.
- `DIRECT_AUTHORITY_RESEARCH`: up to **3** distinct safe authority routes.
- `AMBIGUOUS_LOW_YIELD`: up to **2** distinct safe authority routes.

If the final checked route exposes one concrete, clearly more authoritative follow-up link, one additional follow-up is allowed.

Do not spend quota on repeated generic searches after the route budget is exhausted.

## 4. Outcomes

When safe positive evidence is found:
- exhaust all exact Issue #180 relations safely proved by that source;
- write one `AUTHORITY_BATCH`.

When only the exact whole current Research Unit has truly been reviewed and the v3 terminal contract is satisfied:
- `TERMINAL_BATCH` may be used.

Otherwise, after the route budget is exhausted without a safe positive relation:
- write `RESEARCH_OUTCOME`;
- include `checked_routes`;
- state why each route did not safely establish the relation;
- move to the next OPEN campaign.

`RESEARCH_OUTCOME` is research accounting, not negative evidence and not a canonical terminal decision.

## 5. Do not stop early when

Continue within the budget when:
- an official source clearly points to a more precise roster/profile;
- an exact alias/localization needs one authoritative identity check;
- a high-yield source could safely resolve multiple current Characters.

Do not continue merely because a HOME guess feels plausible.

## 6. True escalation

Forward escalates only when the current policy/harness cannot represent the evidence safely, protected data would need mutation, or a reproducible technical failure prevents normal proposal output.

Ordinary missing evidence, inaccessible pages, ambiguous identity, exhausted routes and safe unresolved outcomes are not user blockers.
