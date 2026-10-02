"""Extract declarative controls without executing UI or touching UserData."""
import csv
from pathlib import Path
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[2]
TARGET = ROOT / "docs/issue245/BASELINE_CONTROLS.csv"
NS_X = "{http://schemas.microsoft.com/winfx/2006/xaml}"
KINDS = {"Button", "ToggleButton", "CheckBox", "RadioButton", "TextBox", "ComboBox", "TabItem", "Expander", "GridSplitter", "MenuItem"}


def collect(path):
    def walk(node, ancestors):
        kind = node.tag.split("}")[-1]
        attrs = node.attrib
        context = ancestors + ([f"{kind}:{attrs.get('Header', '')}"] if kind in {"TabItem", "Expander"} else [])
        if "DataContext" in attrs:
            context += ["DataContext=" + attrs["DataContext"]]
        if kind in KINDS:
            yield {"file": path.relative_to(ROOT).as_posix(), "context": " / ".join(context), "control": kind,
                   "name": attrs.get(NS_X + "Name", ""), "label": attrs.get("Content", attrs.get("Header", "")),
                   "command": attrs.get("Command", ""), "click": attrs.get("Click", ""),
                   "value": attrs.get("Text", attrs.get("IsChecked", attrs.get("SelectedIndex", attrs.get("SelectedValue", "")))),
                   "enabled": attrs.get("IsEnabled", ""), "tooltip": attrs.get("ToolTip", ""),
                   "width": attrs.get("Width", ""), "min_width": attrs.get("MinWidth", ""),
                   "visibility": attrs.get("Visibility", "")}
        for child in node:
            yield from walk(child, context + ([kind] if kind.endswith("Resources") or kind in {"DataTemplate", "ControlTemplate"} else []))
    yield from walk(ET.parse(path).getroot(), [])


if __name__ == "__main__":
    rows = [row for path in sorted((ROOT / "src/DanbooruTagTool.App").rglob("*.xaml")) for row in collect(path)]
    TARGET.parent.mkdir(parents=True, exist_ok=True)
    with TARGET.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0])); writer.writeheader(); writer.writerows(rows)
    print(f"{len(rows)} declarative controls -> {TARGET.relative_to(ROOT)}")
