#!/usr/bin/env python3
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]
subprocess.run(["python", str(ROOT / "tools/issue76_refine_browse_controls.py")], check=True)

xaml = ROOT / "src/DanbooruTagTool.App/MainWindow.xaml"
text = xaml.read_text(encoding="utf-8")
old = 'SelectedItemChanged="NavigationChanged" Expanded="NavigationNodeExpanded" Collapsed="NavigationNodeCollapsed" Background="Transparent"'
new = 'SelectedItemChanged="NavigationChanged" TreeViewItem.Expanded="NavigationNodeExpanded" TreeViewItem.Collapsed="NavigationNodeCollapsed" Background="Transparent"'
if text.count(old) != 1:
    raise RuntimeError(f"expected one TreeView routed-event marker, found {text.count(old)}")
xaml.write_text(text.replace(old, new), encoding="utf-8")
print("Issue #76 routed-event retry fix applied")
