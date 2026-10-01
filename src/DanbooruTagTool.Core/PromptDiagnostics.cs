namespace DanbooruTagTool.Core;

public sealed record PromptWarning(string Side, string Code, string Message);
public sealed record PromptBoundary(string Side, int Node, string Kind);
public static class PromptDiagnostics
{
    public static PromptWarning[] Warnings(PromptWorkspace positive, PromptWorkspace negative)
    {
        var warnings = new List<PromptWarning>();
        foreach (var (side, workspace) in new[] { ("Positive", positive), ("Negative", negative) })
        {
            foreach (var group in workspace.Items.Where(i => i.Canonical is not null).GroupBy(i => i.Canonical).Where(g => g.Count() > 1))
                warnings.Add(new(side, "duplicate", $"{side}: {group.Key} は同じcanonicalへ解決される {group.Count()} 件です（alias/weightを含む）。"));
            foreach (var item in workspace.Items.Where(i => i.Kind == PromptItemKind.Raw && !string.IsNullOrWhiteSpace(i.Surface)))
                warnings.Add(new(side, "raw", $"{side}: raw/unknownを保持: {item.Surface.Trim()}"));
        }
        var negativeTags = negative.Items.Where(i => i.Canonical is not null).Select(i => i.Canonical).ToHashSet(StringComparer.Ordinal);
        foreach (var canonical in positive.Items.Where(i => i.Canonical is not null && negativeTags.Contains(i.Canonical)).Select(i => i.Canonical).Distinct())
            warnings.Add(new("Positive / Negative", "conflict", $"両側に {canonical} があります。自動削除/移動はしません。"));
        return warnings.ToArray();
    }
    public static PromptBoundary[] Boundaries(PromptWorkspace workspace, string side) => workspace.Items.Select((item, index) => new { item, index })
        .Where(x => x.item.Kind == PromptItemKind.Control).Select(x => new PromptBoundary(side, x.index + 1, x.item.StructuredName ?? x.item.Surface.Trim())).ToArray();
}
