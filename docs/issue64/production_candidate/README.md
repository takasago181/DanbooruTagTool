# Issue #64 production integration candidate

This directory contains the clean, reviewable General taxonomy candidate prepared from live `main` `3f4e47d7331809b2e6a234824799fb3bc179bae8`. It carries the accepted pilot-v2 taxonomy and final effective 30,629-row sidecar, with compact provenance and a standard-library validator. Historical batch ledgers and the larger rework tree remain on `codex/issue64-bounded-rework`.

The final bounded review verdict is `ACCEPT_FOR_PRODUCTION_INTEGRATION`, recorded against [the latest DEV review](https://github.com/takasago181/DanbooruTagTool/issues/64#issuecomment-5660957158). The source rework branch is `codex/issue64-bounded-rework` at `7e10185d2cf43ab683a1c8b377f0d48bb24d4f41`. Issue #64 remains open, and this candidate is not merged.

## Files

- `general_taxonomy.json` is the unchanged accepted pilot-v2 taxonomy.
- `effective_sidecar.csv` is the deterministic effective sidecar. Its canonical sequence is exactly the fixed 30,629-entry target population. Rows marked `UNRESOLVED` have no path and must not appear under a browse genre. Only rows marked `PROPOSED` are browseable.
- `manifest.json` records source commits, population/source hashes, candidate hashes, bounded-review evidence, final totals, and the runtime boundary.
- `../../../tools/issue64_production_candidate_validate.py` checks hashes, exact population count/order, statuses, confidence, and every primary/secondary taxonomy path.

The effective sidecar SHA-256 is `a118f5f904c38cee5b63f0c83b06a56f50ee8afdb623c52eb354731bc0b846d9`. The canonical sequence hash is `ca5cc065c92aa38f9daa6b6c8a1f1c13db135057ebfabca076479dfa96872e2b`. The taxonomy SHA-256 is `7311fa1bf1523fcd83134c975b579289d7dbc8aa4cdb1313952d906fc2beb70f`.

## Validation

From the repository root:

```powershell
python tools/issue64_production_candidate_validate.py
python -m pytest -q tests/test_issue64_production_candidate.py
```

No #66 code or catalog database is changed in this candidate. After DEV review accepts this clean delta, #66 can consume the CSV through its existing General browse provider/catalog import boundary. Canonical identity, Japanese overlay, Special assets, and protected local inputs remain unchanged.
