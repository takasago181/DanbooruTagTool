# Issue #118 research sidecar contract v1

Research evidence only. This file is not production authority.

## Identity

Exactly one row per normalized unified Tag identity. Current expected population: 31,752.

## Fields

- `identity_key`: normalized identity key.
- `is_general`: current General membership.
- `is_special`: current Special membership.
- `sexual_intent`: `SEXUAL`, `NON_SEXUAL`, `CONTEXTUAL`, or empty when unclassified.
- `review_status`: `HUMAN_REVIEWED`, `AUTO_HIGH_CONF`, or `UNCLASSIFIED`.
- `rule_id`: populated only for automatic candidate evidence.
- `evidence`: review/rule provenance.

## Semantics

`CONTEXTUAL` is a semantic verdict: the concept itself has substantial natural sexual and non-sexual use. It is not uncertainty.

Empty `sexual_intent` + `UNCLASSIFIED` is epistemic uncertainty and MUST NOT silently map to `NON_SEXUAL`.

## Precedence

Human-reviewed evidence overrides automatic candidate rules. Automatic rules may classify only rows not already human-reviewed. Everything else stays explicitly unclassified.

## Runtime boundary

This research sidecar is not a runtime dependency and is not yet wired into Issue #117. A later accepted production sidecar may be baked into compact catalog metadata at build time.
