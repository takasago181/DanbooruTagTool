#!/usr/bin/env python3
from pathlib import Path

path = Path(__file__).resolve().parents[1] / "src/DanbooruTagTool.Tests/Issue76MainUiIntegrationTests.cs"
text = path.read_text(encoding="utf-8")
old = 'var special = Assert.Single(vm.Navigation.Where(node => node.Key == "special"));'
new = 'var special = Assert.Single(vm.Navigation, node => node.Key == "special");'
if text.count(old) != 1:
    raise RuntimeError("expected one xUnit2031 pattern")
path.write_text(text.replace(old, new), encoding="utf-8")
print("Issue #76 analyzer fix applied")
