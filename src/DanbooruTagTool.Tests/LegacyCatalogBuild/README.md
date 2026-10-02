# Historical catalog build oracle

These former Data build owners and resources compile **only into the tests**.
They preserve the exact pre-Foundation behavior and allow same-input migration
parity. They are not production compiler steps and must not be referenced by App,
Data or Maintenance. See `docs/foundation/CATALOG_AUTHORITY.md`.

Code is unchanged except explicit `System.IO` imports needed by the WPF test
project's implicit-using set. Existing evidence/hash/population checks remain.
