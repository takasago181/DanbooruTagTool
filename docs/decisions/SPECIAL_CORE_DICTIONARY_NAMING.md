# Special Core Dictionary — Final Naming Decision

Date: 2026-09-10 JST
Status: **FINAL / durable naming decision**
Source: Issue #43, final user decision checkpoint `5611921195`

## Decision

The formal, count-independent product and dictionary concept name is exactly:

`Special Core Dictionary`

This name is final. It is not provisional, a preferred alias, or a request to
rename protected storage identifiers.

## Exact definitions

| Term | Fixed meaning |
|---|---|
| **Special Core Dictionary** | The stable product concept containing the Special entries used as the image-generation nucleus source. Its name does not encode a mutable row count. |
| **Special / Special Core Entry** | One per-entry object. Existing `Special` wording remains valid where unambiguous; new explanatory prose may use `Special Core Entry`. |
| **Core Tag Set** | The user-selected one-or-more Special entries that form the generation nucleus. This is distinct from the dictionary. |
| **Special2788** | Historical/snapshot corpus identity for the original 2,788-entry population. It also remains in protected paths, technical identifiers, schemas, serialized keys, manifests, and immutable evidence where compatibility requires it. |

The fixed relationship is:

`Special Core Dictionary -> Core Tag Set -> Auxiliary/support -> Prompt`

## Migration policy

- Rename only current user-facing wording and current architecture/spec or
  downstream terminology where the change is semantic naming only.
- Keep existing code identifiers, class/function names, internal keys, paths,
  schemas, serialized keys, manifests, and hash authorities when changing them
  would add compatibility or protected-integrity risk.
- Never rewrite historical Issues, commits, checkpoints, audit evidence,
  reports, immutable snapshot labels, or the factual statement that the
  historical corpus contained 2,788 entries.
- Do not change dictionary rows, canonical identity, aliases, search/ranking,
  Prompt semantics, Japanese overlay status, or Stage9 behavior as part of this
  naming decision.

The complete baseline reference inventory and per-path action are recorded in
`docs/issue43/SPECIAL_CORE_DICTIONARY_REFERENCE_INVENTORY.md`.

## Downstream terminology

KNOWLEDGE #44, PROMPT #5, #30, and #42 may use `Special Core Dictionary` for
the formal concept. When referring to the concrete current production data,
they must retain the physical path and snapshot identifier
`Special2788` as required for reproducibility.
