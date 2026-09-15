using System.Globalization;
using System.Text.RegularExpressions;

namespace DanbooruTagTool.Core;

public enum PromptItemKind { Normal, Weighted, Lora, Control, Raw }
public enum PromptOutputProfile { Canonical, GenerationFriendly }
public sealed record PromptItem(Guid Id, string Surface, string? Canonical, string? Japanese,
    PromptItemKind Kind, string? StructuredName = null, decimal? Weight = null, string? CatalogId = null)
{
    public string Display => Kind switch
    {
        PromptItemKind.Weighted => $"{Japanese ?? StructuredName} {Weight}",
        PromptItemKind.Lora => $"LoRA {StructuredName} {Weight}",
        PromptItemKind.Raw => Surface + " ?",
        _ => Japanese ?? Surface
    };
    public bool CanEditWeight => Kind is PromptItemKind.Weighted or PromptItemKind.Lora;
}

public sealed class PromptParser(ICatalog catalog)
{
    private static readonly Regex Weighted = new(@"^\(((?:[^():\[\]<>\\]|\\[()])+):(-?\d+(?:\.\d+)?)\)$", RegexOptions.CultureInvariant);
    private static readonly Regex Lora = new(@"^<lora:([^:<>\r\n]+):(-?\d+(?:\.\d+)?)>$", RegexOptions.CultureInvariant);
    public PromptItem[] Parse(string text)
    {
        if (text.Length == 0) return [];
        // Only split top-level unescaped commas. Unbalanced/unsupported groups remain untouched.
        var parts = new List<string>();
        var stack = new Stack<char>();
        int start = 0; bool escaped = false;
        for (int i = 0; i < text.Length; i++)
        {
            char c = text[i];
            if (escaped) { escaped = false; continue; }
            if (c == '\\') { escaped = true; continue; }
            if (c is '(' or '[' or '<' or '{') stack.Push(c);
            else if (c is ')' or ']' or '>' or '}')
            {
                if (stack.Count == 0 || !Matches(stack.Peek(), c)) return [Recognize(text) with { Kind = PromptItemKind.Raw, Canonical = null, Japanese = null }];
                stack.Pop();
            }
            else if (c == ',' && stack.Count == 0) { parts.Add(text[start..i]); start = i + 1; }
        }
        parts.Add(text[start..]);
        return parts.Select(Recognize).ToArray();
    }
    private static bool Matches(char a, char b) => (a, b) is ('(', ')') or ('[', ']') or ('<', '>') or ('{', '}');
    private PromptItem Recognize(string surface)
    {
        var t = surface.Trim();
        if (t == "BREAK") return new(Guid.NewGuid(), surface, null, null, PromptItemKind.Control);
        var l = Lora.Match(t);
        if (l.Success && decimal.TryParse(l.Groups[2].Value, CultureInfo.InvariantCulture, out var lw))
            return new(Guid.NewGuid(), surface, null, null, PromptItemKind.Lora, l.Groups[1].Value, lw);
        var w = Weighted.Match(t);
        if (w.Success && decimal.TryParse(w.Groups[2].Value, CultureInfo.InvariantCulture, out var weight))
        {
            var entry = ResolveRecognized(w.Groups[1].Value);
            return new(Guid.NewGuid(), surface, entry?.Canonical, entry?.Japanese, PromptItemKind.Weighted, w.Groups[1].Value, weight, entry?.Id);
        }
        var tag = ResolveRecognized(t);
        return new(Guid.NewGuid(), surface, tag?.Canonical, tag?.Japanese, tag == null ? PromptItemKind.Raw : PromptItemKind.Normal, CatalogId: tag?.Id);
    }
    private CatalogEntry? ResolveRecognized(string value)
    {
        var exact = catalog.Resolve(value);
        if (exact != null) return exact;

        // Generation-friendly output escapes literal parentheses. Only use the
        // unescaped form as a catalog lookup candidate; never rewrite the
        // stored Prompt surface.
        var unescaped = UnescapeLiteralParentheses(value);
        if (unescaped == value) return null;
        return catalog.Resolve(unescaped) ?? catalog.Resolve(unescaped.Replace(' ', '_'));
    }
    private static string UnescapeLiteralParentheses(string value)
    {
        var result = new System.Text.StringBuilder(value.Length);
        for (int i = 0; i < value.Length; i++)
        {
            if (value[i] == '\\' && i + 1 < value.Length && value[i + 1] is '(' or ')') { result.Append(value[++i]); continue; }
            result.Append(value[i]);
        }
        return result.ToString();
    }
    public static string Serialize(IEnumerable<PromptItem> items) => string.Join(",", items.Select(i => i.Surface));
}

public static class PromptOutputFormatter
{
    private static readonly Regex Weighted = new(@"^\(((?:[^():\[\]<>\\]|\\[()])+):-?\d+(?:\.\d+)?\)$", RegexOptions.CultureInvariant);

    public static string Serialize(IEnumerable<PromptItem> items, PromptOutputProfile profile) =>
        string.Join(",", items.Select(item => Format(item, profile)));

    public static string Format(PromptItem item, PromptOutputProfile profile)
    {
        if (profile == PromptOutputProfile.Canonical || item.Canonical == null || item.Kind is not (PromptItemKind.Normal or PromptItemKind.Weighted))
            return item.Surface;

        var surface = item.Surface;
        var start = 0;
        while (start < surface.Length && char.IsWhiteSpace(surface[start])) start++;
        var end = surface.Length;
        while (end > start && char.IsWhiteSpace(surface[end - 1])) end--;
        var leading = surface[..start];
        var trailing = surface[end..];
        var core = FormatCanonicalCore(item.Canonical);

        if (item.Kind == PromptItemKind.Weighted)
        {
            var trimmed = surface[start..end];
            if (Weighted.IsMatch(trimmed))
            {
                var colon = trimmed.LastIndexOf(':');
                return leading + "(" + core + trimmed[colon..] + trailing;
            }
            return surface;
        }
        return leading + core + trailing;
    }

    private static string FormatCanonicalCore(string canonical) => canonical.Replace("(", "\\(").Replace(")", "\\)").Replace('_', ' ');
}

public sealed record WorkspaceSnapshot(PromptItem[] Items, PromptItem[]? Recovery);
public sealed class PromptWorkspace(PromptParser parser)
{
    private PromptItem[] items = [];
    private PromptItem[]? recovery;
    private readonly Stack<WorkspaceSnapshot> undo = new(), redo = new();
    public IReadOnlyList<PromptItem> Items => Array.AsReadOnly(items);
    public string English => PromptParser.Serialize(items);
    public string ClipboardPayload => English;
    public bool CanUndo => undo.Count > 0;
    public bool CanRedo => redo.Count > 0;
    public bool HasRecovery => recovery != null;
    public event Action? Changed;
    public WorkspaceSnapshot Snapshot() => new(items.ToArray(), recovery?.ToArray());
    public void Restore(WorkspaceSnapshot snapshot) { items = snapshot.Items.ToArray(); recovery = snapshot.Recovery?.ToArray(); undo.Clear(); redo.Clear(); Changed?.Invoke(); }
    private void Change(Action action) { undo.Push(Snapshot()); redo.Clear(); action(); Changed?.Invoke(); }
    public void Replace(string text) => Change(() => { recovery = items.ToArray(); items = parser.Parse(text); });
    public void DirectEdit(string text) => Change(() => items = parser.Parse(text));
    public void Recover() { if (recovery != null) Change(() => (items, recovery) = (recovery!, items)); }
    public bool Contains(string canonical) => items.Any(i => i.Canonical == canonical);
    public IReadOnlyList<PromptItem> FindByCanonical(string canonical) => items.Where(i => i.Canonical == canonical).ToArray();
    public bool Add(CatalogEntry entry)
    {
        if (!entry.CanAdd || Contains(entry.Canonical!)) return false;
        Change(() => items = [..items, new(Guid.NewGuid(), (items.Length == 0 ? "" : " ") + entry.Canonical, entry.Canonical, entry.Japanese, PromptItemKind.Normal)]);
        return true;
    }
    public void Delete(IEnumerable<Guid> ids)
    {
        var set = ids.ToHashSet();
        if (items.Any(i => set.Contains(i.Id))) Change(() => items = items.Where(i => !set.Contains(i.Id)).ToArray());
    }
    // destination is a gap in the original sequence, 0..Count (before removal).
    public void Move(IEnumerable<Guid> ids, int destination)
    {
        if (destination < 0 || destination > items.Length) throw new ArgumentOutOfRangeException(nameof(destination));
        var set = ids.ToHashSet(); var block = items.Where(i => set.Contains(i.Id)).ToArray();
        if (block.Length == 0) return;
        int gap = destination - items.Take(destination).Count(i => set.Contains(i.Id));
        var rest = items.Where(i => !set.Contains(i.Id)).ToList(); rest.InsertRange(gap, block);
        if (!items.SequenceEqual(rest)) Change(() => items = rest.ToArray());
    }
    public void EditWeight(Guid id, decimal weight)
    {
        int index = Array.FindIndex(items, i => i.Id == id);
        if (index < 0 || !items[index].CanEditWeight) return;
        var item = items[index]; var number = weight.ToString(CultureInfo.InvariantCulture);
        var prefix = item.Surface[..(item.Surface.Length - item.Surface.TrimStart().Length)];
        var suffix = item.Surface[(item.Surface.TrimEnd().Length)..];
        var surface = item.Kind == PromptItemKind.Lora ? $"<lora:{item.StructuredName}:{number}>" : $"({item.StructuredName}:{number})";
        Change(() => items[index] = item with { Surface = prefix + surface + suffix, Weight = weight });
    }
    public void Undo() { if (undo.TryPop(out var s)) { redo.Push(Snapshot()); items = s.Items.ToArray(); recovery = s.Recovery?.ToArray(); Changed?.Invoke(); } }
    public void Redo() { if (redo.TryPop(out var s)) { undo.Push(Snapshot()); items = s.Items.ToArray(); recovery = s.Recovery?.ToArray(); Changed?.Invoke(); } }
}
