# Issue #76 WPF prototype run guide v0.9

Status: **ISOLATED PROTOTYPE ONLY / DEFAULT APP UNCHANGED**

## Purpose

Run the Special v2 browse/filter UI without replacing the production MainWindow behavior.

The prototype is activated only by an explicit command-line flag and generated Issue #76 sidecar.

## 1. Generate the full v0.8 sidecar

From repository root:

```powershell
python tools/issue76_build_v2_integrated.py
```

Expected generated file:

```text
docs/issue76/generated/issue76_v2_candidate_mapping_v0_8.csv
```

The builder validates:
- exact Special IDs 1..2788;
- valid v2 kind/body/theme/status values;
- no browse-visible row without a route;
- no stale buttock/anal review note;
- no duplicate reason token.

Reference SHA-256 from the accepted local v0.8 materialization:

`de5ef4cb712c31425b77fcc8bf2d8f56917356d79b3720845c81d46d8142d5d0`

If a regenerated file differs, inspect the upstream evidence delta before treating it as the same candidate.

## 2. Run tests

```powershell
cd src
dotnet test DanbooruTagTool.sln -c Release
```

Issue #76 prototype tests are in:

`DanbooruTagTool.Tests/Issue76PrototypeTests.cs`

Do not report PASS until this command actually succeeds in a real checkout.

## 3. Build/run the app

Use the normal catalog already expected by the portable app.

Run the app with:

```powershell
DanbooruTagTool.App.exe --issue76-v2-prototype "<repo>\docs\issue76\generated\issue76_v2_candidate_mapping_v0_8.csv"
```

The explicit flag launches:

`Issue76BrowsePrototypeWindow`

without replacing the normal `MainWindow` route.

No flag = existing application behavior.

## 4. Prototype behavior

- left tree starts a fresh Special browse context;
- center chips add required facets;
- kind is single-select;
- multiple body facets are AND;
- multiple themes are AND;
- cross-axis conditions are AND;
- current SearchEngine remains the search authority;
- active facets only filter surviving search hits, preserving their relative order;
- `すべて解除` clears facets but not the query;
- selecting a new tree leaf clears the previous facet state and query.

## 5. Acceptance run

Use:

`docs/issue76/ISSUE76_KNOWLEDGE_FIRST_TASK_MATRIX_v0_9.csv`

Priority order:
1. all P0 tasks;
2. then P1 tasks;
3. record any task that requires knowing the old taxonomy to succeed;
4. record any intersection that produces an unexpectedly broad/empty set;
5. do not fix usability problems by reflexively restoring old visible subgenres.

## 6. Boundary

This prototype does not authorize:
- production v1 taxonomy replacement;
- canonical data edits;
- General taxonomy edits;
- search-ranking changes;
- Issue #75 visual-polish scope changes.

Only after build/test + task-matrix review should the Issue #76 candidate be considered for production migration.
