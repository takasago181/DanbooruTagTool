# Research and frozen evidence

Research is not accepted production authority. The current compiler reads only
`authority/catalog/current/manifest.json` and its governed projections. Generated
`catalog.db` belongs in a fresh external candidate/artifact directory. UserData is
never a build or evidence output.

`archive/foundation-b.json` indexes exact Git bytes, sizes, SHA256 and the frozen
recovery tag for historical evidence, tools, workflows and retained test oracles.
The tag is on GitHub, not just a local backup. Git history is unchanged; normal
checkout size shrinks, existing clone/history size does not.

```powershell
git fetch origin tag archive/foundation-pre-batch-b-20261003
python -B scripts/maintenance/evidence_archive.py restore "$env:TEMP/DTT-research-replay-new"
python -B scripts/maintenance/evidence_archive.py verify "$env:TEMP/DTT-research-replay-new"
```

Restore creates a full frozen source tree outside checkouts/runtimes/UserData, so
historical Python imports, tests and relative evidence paths remain reproducible.
It verifies every indexed original file and never executes scripts/workflows or
promotes results. Original commands and upstream provenance remain in the frozen
tree. Protected ignored/local-only data is NOT in Git or this archive: retain its
original workspace/recovery copies. Reproduction needing it must supply copies
explicitly. Do not restore evidence over the current product tree.

Current C# regressions retain exact historical fixtures in
`src/DanbooruTagTool.Tests/LegacyCatalogBuild/Inputs`; those are test-only oracles,
not build authority. Some small Issue documents remain useful decision provenance.
KNOWLEDGE #44 and its independent branch are retained. The 207-scenario #213
research corpus/branch remains protected; this batch does not delete research
branches or import new model/feature knowledge.
