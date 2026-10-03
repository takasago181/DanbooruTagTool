# Frozen test oracle inputs

These frozen historical fixtures protect legacy contracts and recovery. They are
compiled/read only by Tests; App/Data/Maintenance must not use them. Production
authority is `authority/catalog/current`. Original locations, SHA256, sizes and
recovery commit are in `research/archive/foundation-b.json`. Original Git bytes
and accepted test checkout bytes have separate SHA256/size fields: 42 historical
CRLF blobs use the already accepted LF representation, without changing any CSV
value or legacy accepted hash. Attributes preserve these frozen representations.

The old importer accepts the repository root but now resolves retained tracked
fixtures here. Protected external source files still require `DTT_SOURCE_ROOT`.
Historical #118 generators emit disposable TEMP outputs, never rewrite these
fixtures. The opt-in exporter remains a historical migration tool; normal tests cannot
regenerate accepted authority. Full historical script replay uses the frozen
external tree, with its original paths (see `research/README.md`).
