using System.Numerics;
namespace DanbooruTagTool.Core;

public sealed record TemplatePreview(string Source, BigInteger Count, IReadOnlyList<string> Variants, IReadOnlyList<string> Warnings);
/// <summary>Deterministic compatible subset of Dynamic Prompts syntax. No generator or background execution.</summary>
public static class PromptTemplates
{
    public const int MaximumCap = 256;
    private sealed record Node(string? Literal, Node[] Children, bool Choice)
    {
        public BigInteger Length => Literal is not null ? Literal.Length : Choice ? Children.Max(c => c.Length) : Children.Aggregate(BigInteger.Zero, (n,c) => n + c.Length);
        public BigInteger Count => Literal is not null ? BigInteger.One : Choice ? Children.Aggregate(BigInteger.Zero, (n,c) => n + c.Count) : Children.Aggregate(BigInteger.One, (n,c) => n * c.Count);
        public IEnumerable<string> Expand()
        {
            if (Literal is not null) return [Literal];
            if (Choice) return Children.SelectMany(c => c.Expand());
            IEnumerable<string> values = [""];
            foreach (var child in Children) values = values.SelectMany(v => child.Expand().Select(c => v + c)).ToArray();
            return values;
        }
    }
    public static TemplatePreview Preview(string source, IReadOnlyDictionary<string, string[]> wildcards, int cap = 64)
    {
        if (cap is < 1 or > MaximumCap) throw new ArgumentException($"上限は1〜{MaximumCap}です。");
        if (source.Length > 16000) throw new ArgumentException("テンプレートは16000文字以内です。");
        var warnings = new List<string>(); var budget = 8192;
        Node Raw(string text) => new(text, [], false);
        Node Parse(string text, HashSet<string> stack, int depth)
        {
            if (depth > 16 || --budget < 0) throw new ArgumentException("テンプレートの深さ/複雑さの上限を超えました。");
            if (text.Length > 16000) throw new ArgumentException("wildcard行は16000文字以内です。");
            var nodes = new List<Node>(); var start = 0;
            for (var i = 0; i < text.Length; i++)
            {
                if (text[i] == '\\') { i++; continue; }
                Node? node = null; var end = i;
                if (text[i] == '{')
                {
                    var level = 1; var parts = new List<string>(); var part = i + 1; var j = part;
                    for (; j < text.Length && level > 0; j++)
                    {
                        if (text[j] == '\\') { j++; continue; }
                        if (text[j] == '{') level++;
                        if (text[j] == '}') level--;
                        if (text[j] == '|' && level == 1) { parts.Add(text[part..j]); part = j + 1; }
                        if (level == 0) parts.Add(text[part..j]);
                    }
                    if (level != 0) { warnings.Add("閉じていない構文をraw保持しました。"); nodes.Add(Raw(text[start..])); return new(null, nodes.ToArray(), false); }
                    end = j - 1; var body = text[(i + 1)..end];
                    if (i > 0 && text[i - 1] == '$' || parts.Count < 2 || body.Contains("$$") || body.Contains("::") || body.Contains('$'))
                    { warnings.Add("未対応構文をraw保持: " + text[i..j]); node = Raw(text[i..j]); }
                    else node = new(null, parts.Select(p => Parse(p, stack, depth + 1)).ToArray(), true);
                }
                else if (text[i..].StartsWith("__", StringComparison.Ordinal))
                {
                    var close = text.IndexOf("__", i + 2, StringComparison.Ordinal);
                    if (close < 0) continue;
                    end = close + 1; var name = text[(i + 2)..close];
                    if (wildcards.TryGetValue(name, out var lines))
                    {
                        if (!stack.Add(name)) throw new ArgumentException("循環wildcard: " + name);
                        if (lines.Length == 0) throw new ArgumentException("空wildcard: " + name);
                        node = new(null, lines.Select(l => Parse(l, stack, depth + 1)).ToArray(), true); stack.Remove(name);
                    }
                    else { node = Raw(text[i..(end + 1)]); warnings.Add("未解決wildcardをraw保持: " + name); }
                }
                if (node is null) continue;
                if (i > start) nodes.Add(Raw(text[start..i])); nodes.Add(node); i = end; start = end + 1;
            }
            if (start < text.Length) nodes.Add(Raw(text[start..]));
            return new(null, nodes.ToArray(), false);
        }
        var root = Parse(source, new(StringComparer.Ordinal), 0); var count = root.Count; if (root.Length > 16000) throw new ArgumentException("展開後Promptは16000文字以内です。");
        return new(source, count, count <= cap ? root.Expand().ToArray() : [], warnings.Distinct().ToArray());
    }
}

