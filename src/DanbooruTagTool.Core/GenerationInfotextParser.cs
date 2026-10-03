using System.Text.Json;

namespace DanbooruTagTool.Core;

/// <summary>Pure Forge/A1111 infotext adapter. Raw text and ordered, duplicate/unknown parameters remain authoritative.</summary>
public static class GenerationInfotextParser
{
    private const int MaxInfotextChars = 1_000_000;

    public static GenerationMetadataSnapshot Parse(string sourcePath, string infotext)
    {
        if (string.IsNullOrWhiteSpace(infotext))
            throw new GenerationMetadataException("生成情報が空です");
        if (infotext.Length > MaxInfotextChars)
            throw new GenerationMetadataException("PNGの生成情報が大きすぎます");

        var normalized = infotext.Replace("\r\n", "\n", StringComparison.Ordinal).Replace('\r', '\n').Trim();
        var allLines = normalized.Split('\n');
        var parameterLine = "";
        var promptLines = allLines.AsEnumerable();

        if (allLines.Length > 0)
        {
            var candidate = allLines[^1].Trim();
            var candidateParameters = ParseParameterLine(candidate);
            if (candidateParameters.Count >= 3)
            {
                parameterLine = candidate;
                promptLines = allLines.Take(allLines.Length - 1);
            }
        }

        var positive = new List<string>();
        var negative = new List<string>();
        var inNegative = false;
        foreach (var rawLine in promptLines)
        {
            var line = rawLine.Trim();
            if (line.StartsWith("Negative prompt:", StringComparison.Ordinal))
            {
                inNegative = true;
                line = line["Negative prompt:".Length..].Trim();
            }

            if (inNegative) negative.Add(line);
            else positive.Add(line);
        }

        var positiveText = string.Join("\n", positive).Trim();
        var negativeText = string.Join("\n", negative).Trim();
        var parameters = ParseParameterLine(parameterLine);

        if (positiveText.Length == 0 && parameters.Count == 0)
            throw new GenerationMetadataException("Forge形式の生成情報を解析できません");

        return new(sourcePath, infotext, positiveText, negativeText, parameters);
    }

    private static IReadOnlyList<GenerationParameter> ParseParameterLine(string line)
    {
        if (string.IsNullOrWhiteSpace(line)) return [];
        var parts = new List<string>();
        var start = 0;
        var quoted = false;
        var escaped = false;

        for (var i = 0; i < line.Length; i++)
        {
            var c = line[i];
            if (escaped) { escaped = false; continue; }
            if (quoted && c == '\\') { escaped = true; continue; }
            if (c == '"') { quoted = !quoted; continue; }
            if (c == ',' && !quoted)
            {
                parts.Add(line[start..i]);
                start = i + 1;
            }
        }
        parts.Add(line[start..]);

        var result = new List<GenerationParameter>();
        foreach (var part in parts)
        {
            var colon = part.IndexOf(':');
            if (colon <= 0) continue;
            var name = part[..colon].Trim();
            var value = part[(colon + 1)..].Trim();
            if (name.Length == 0) continue;
            if (value.Length >= 2 && value[0] == '"' && value[^1] == '"')
            {
                try { value = JsonSerializer.Deserialize<string>(value) ?? value; }
                catch (JsonException) { value = value[1..^1]; }
            }
            result.Add(new(name, value));
        }
        return result;
    }

}
