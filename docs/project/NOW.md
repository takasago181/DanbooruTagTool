# NOW — いま何をやっているか

最終整理: 2026-10-03 JST (#245 production closeout complete; Foundation gate open)

## Current focus

### #248 Foundation Audit — READY / ACTIVE NEXT

The production closeout gate is satisfied.

Verified baseline:
- repository main at gate-open: `c75a4795bd082987e8e8348f0432200b20094ff5`
- production runtime source: `b3f48c359a8473c8bbf02347487cba5d8dacf96c`
- new LKG: `docs/project/LAST_KNOWN_GOOD.json`
- #245: CLOSED
- #225: final production checkpoint recorded
- Release tests: 364 PASS / 4 SKIP / 0 FAIL
- focused: 112 PASS / 1 SKIP / 0 FAIL
- real Create -> Forge -> PNG -> Library 10-field + declared model-hash round-trip: PASS
- resumed 5 Prompt items, Recovery, empty Negative, 2 Presets preserved
- existing Library/LoRA/catalog/protected authority preserved

Known limitation:
- native pixel capture still returns a white client area, so final visual appearance is not pixel-verified; actual UI operations/status, WPF render/tree and generation workflow passed.

#248 now audits the promoted baseline and decides the **smallest Foundation work actually worth doing**. It must stop after the audit/recommendation; #249–#255 are not an automatic checklist.

## Operating policy being simplified

Draft PR #259 updates the project for capable Codex + private single-user workstation use:
- project fixes WHAT / WHY / HARD BOUNDARIES / ACCEPTANCE; Codex chooses HOW;
- completed Issue-era worker procedure is removed from global startup rules;
- distribution-only gates are demoted;
- trivial personal-repo changes do not require PR ceremony;
- external OSS/data reuse is encouraged when useful; formal license/provenance review is not a routine blocker for private local experiments;
- UserData, rollback/recovery, destructive-cleanup, canonical/stable-ID and secret-safety protections remain.

Product priority is explicit: general use remains supported, but **adult / sexual / fetish / hard-niche 2D generation support is a first-class priority**. Foundation/OSS reuse must not genericize away deep Special discovery or difficult relation/body-site/count/visibility/device/topology workflows.

## Production baseline

User-facing runtime:
`C:\Codex\DanbooruTagTool-App`

Current LKG source:
`b3f48c359a8473c8bbf02347487cba5d8dacf96c`

Current runtime hashes and exact UserData/Library evidence:
- `docs/project/LAST_KNOWN_GOOD.json`
- `docs/issue245/PRODUCTION_CHECKPOINT_2026-10-03.json`

Do not reopen completed #132/#180/#216/#223/#245 work unless a concrete regression or #248 dependency requires it.

## Next

1. merge/apply the rule simplification after review of #259;
2. run #248 against the promoted baseline;
3. publish dispositions KEEP / WRAP / REWRITE / DELETE / ARCHIVE;
4. recommend only the Foundation work that materially helps;
5. STOP before implementation.
