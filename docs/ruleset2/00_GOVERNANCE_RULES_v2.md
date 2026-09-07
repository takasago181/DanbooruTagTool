# GOVERNANCE_RULES v2 — DanbooruTagTool

## 1. HARD INVARIANTS — always enforced

1. **Runtime is local and deterministic by default.** Production runtime uses no LLM, no network, no API, and no cloud translation.
2. **Severity is metadata, not a completeness filter.** Hard, niche, explicit, R18G, or unusual terms are not deleted, weakened, or excluded merely because of severity.
3. **No silent semantic rewrite.** Alias, statistics, model form, LoRA, or support data may not silently change the meaning/output ownership of a Special concept.
4. **Role separation is mandatory.** Keep these separate: source Special identity, official alias/history, semantic concept, statistics population, Prompt output form/ownership, model-specific form, Practical Phrase, and LoRA trigger/helper.
5. **Source presence is not model familiarity.** Current e621/Gelbooru/Danbooru presence never by itself upgrades a term to MODEL_OBSERVED or USER_ENV_VERIFIED.
6. **Exact model/version first.** Current checkpoint/version evidence precedes ancestor/base evidence. Unknown remains UNKNOWN.
7. **Audit provenance must be reproducible.** Source/version/date/hash/row-count or equivalent provenance is recorded whenever it affects a frozen conclusion.
8. **Stage boundary changes are explicit.** Stage9/10 remain unstarted until explicitly opened. Dictionary work may not silently mutate Pilot001 acceptance expectations or production relations.
9. **A disproved conclusion is discarded.** Do not preserve a prior decision merely because it was previously frozen or implemented.
10. **Source history is preserved.** A curated migration may change current semantics/output routing, but the prior/source value and migration reason remain traceable.

## 2. CURATED-MUTABLE RULES — change when evidence or product goals justify it

11. **Prompt ownership is not permanently tied to the original Special string.** The current Prompt owner/output form may migrate after explicit review. Runtime alias/statistics/model layers still may not perform silent ownership changes.
12. **General Danbooru may become the preferred output/canonical form when explicitly audited as equivalent or better.** It may not silently absorb a Special concept merely because an alias exists.
13. **Japanese is primarily a human-readable gloss.** It should let the user understand the row at a glance. Japanese search is secondary and must not distort the gloss.
14. **Search index data is derived data.** Search aliases/keywords may be optimized independently from Japanese gloss text.
15. **Curated metadata may be corrected.** Category, related category, gender scope, Danbooru interpretation, semantic routing, canonical/statistics mapping, and similar enrichment fields may change with an audit trail.
16. **Support structure may evolve.** CORE_SUPPORT / OPTIONAL_VARIATION / slots / ranking may be revised when evidence or UX improves, while raw historical evidence remains preserved.
17. **Model forms and LoRA registries may evolve independently.** They never become core semantic truth merely because they are practical.

## 3. AUTOMATION AND UX — distinguish hidden mutation from deterministic assistance

18. **Hidden source/semantic mutation is prohibited.** The tool must not secretly delete, generalize, replace, or rewrite selected concepts.
19. **Deterministic assistance is allowed when explicit and inspectable.** Presets or user-enabled policies may assemble support tags, model forms, weights, ordering, or formatting if the rule is deterministic, reversible, and does not alter source/semantic identity.
20. **Recommendation is not ownership.** A suggested support/model form is allowed without becoming semantic truth.
21. **Existing-tool-first is a preference, not a ban.** Reuse Forge/ComfyUI/extensions when they already solve the problem well; integrate equivalent functionality when doing so materially reduces user operations, improves consistency, or avoids cross-tool friction.
22. **Normal UI hides audit clutter.** Show meaning, useful choices, and Prompt output by default; provenance/risk/debug metadata belongs in details/audit views.

## 4. HISTORICAL FREEZE — preserve snapshots, do not fossilize design

23. **Freeze means immutable historical snapshot + explicit migration path.** Never overwrite a frozen artifact in place. A newer version may supersede its design if the migration is documented and regression-tested.
24. **Stage6 raw evidence is protected.** Raw source snapshot, counts, math inputs, and recorded historical outputs remain reproducible. New derived scores/rankings/UI order may be versioned separately.
25. **Stage8A/8B frozen versions remain historical baselines.** Architecture or semantics may advance in a new version when product goals or evidence justify it; the old snapshot/hash remains intact.
26. **Pilot001 acceptance expectations are a frozen test baseline.** Dictionary/ruleset work does not silently rewrite those counts; a deliberate new pilot version is required.

## 5. SOURCE-SPECIFIC RULES

27. **Danbooru alias is evidence/history, not automatic semantic truth.** Broader/narrower/state/action/body-part/consent/context loss is reviewed explicitly.
28. **e621 final vocabulary audit uses same-date raw tags + tag_aliases with published SHA verification when available.** Thresholded autocomplete is fallback/discovery-only.
29. **Gelbooru frozen source remains a reproducibility baseline.** Current-source checks may be added separately; frozen baseline and current truth are different concepts.
30. **Invalid/deprecated/ambiguous source rows do not become default recommendation merely because they match.**
31. **NoobAI EPS and V-Pred remain separate profiles.**
32. **Anima/Gelbooru forms remain model-specific evidence and do not overwrite source/semantic identity.**

## 6. DATA MODEL CONSEQUENCES

33. `Tag` in the current Special2788 table is treated as a **source term snapshot**, not necessarily the forever Prompt output string.
34. A future schema should expose dedicated fields/records for `prompt_output_form` / `prompt_owner` instead of inferring them from `Tag` or alias sidecars.
35. Alias sidecars must not be the source of truth for Prompt ownership. Legacy `prompt_owner=ORIGINAL_SPECIAL_TERM` fields are compatibility snapshots only.
36. Search keys should not be required to contain the full Japanese gloss verbatim.
37. Validators protect provenance and declared invariants, not arbitrary equality to an older candidate.

38. **Alias semantic relationship and statistics eligibility are orthogonal.** A mapping may be semantically non-equivalent yet useful as related statistics, or semantically equivalent while requiring lexical/context caution. Never collapse both decisions into one `safe/risk` flag.
39. **Authoritative Alias routing is two-axis.** `37_ALIAS_SEMANTIC_RELATIONSHIP_v3.0.csv` owns semantic relationship; `38_ALIAS_STATISTICS_POLICY_v3.0.csv` owns statistics eligibility. Legacy `04/05` files are compatibility/audit views only.

## 7. CURRENT STAGE STATE

- Dictionary audit remains the highest-priority work.
- Codex repo implementation: NOT STARTED.
- Stage8C Phase1 Pilot001 acceptance: NOT COMPLETED.
- Stage9: NOT STARTED.
- Stage10: NOT STARTED.
- Runtime non-LLM/offline invariant: unchanged.
