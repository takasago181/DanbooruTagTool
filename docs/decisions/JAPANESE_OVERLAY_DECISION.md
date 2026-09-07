# Japanese Overlay Decision

Stage 6.5 keeps Japanese vocabulary beside the authoritative dictionaries. The
overlay adds search/display metadata without changing canonical tags, categories,
post counts, aliases, Special identity, or generation metadata. External values
are imported only when their tag matches the project canonical set under the
existing normalizer. Alias-only records are retained in the audit as evidence and
are never migrated.

The runtime accepts only reviewed or conservative `display`/`search` rows. Source
acquisition is a development-time activity; the builder reads pinned local source
files and normal application loading is fully local, without an API or model.
Stage 7 UI and automatic translation review remain outside this decision.
