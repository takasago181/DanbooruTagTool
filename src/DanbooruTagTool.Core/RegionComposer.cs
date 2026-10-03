using System.Globalization;
using System.Text.Json;
using System.Text.RegularExpressions;

namespace DanbooruTagTool.Core;

public enum RegionLayout { Horizontal, Vertical }
public sealed record RegionComposerConfig(string Common, string SubjectA, string SubjectB,
    string CommonNegative = "", string NegativeA = "", string NegativeB = "",
    RegionLayout Layout = RegionLayout.Horizontal, string Ratios = "1,1");
public sealed record RegionalCapability(string Repository, string Commit, string Version, string Contract);
public sealed record RegionalReceipt(RegionComposerConfig Config, RegionalCapability Extension, string RequestJson);

/// <summary>Structured blocks only. Diffusion and attention remain wholly in Forge.</summary>
public static class RegionComposer
{
    public const string Key = "DTT Regional receipt v1";
    public const string Repository = "https://github.com/hako-mikan/sd-webui-regional-prompter";
    public const string Commit = "b10c496dbcb9c94be0d5d64edda8511460cc9d28";
    public const string Contract = "hako-mikan-neo-matrix-20-v1";
    public static string MatrixMode(RegionComposerConfig c) => c.Layout == RegionLayout.Horizontal ? "Columns" : "Rows";
    public static void Validate(RegionComposerConfig c)
    {
        if (!Enum.IsDefined(c.Layout) || string.IsNullOrWhiteSpace(c.SubjectA) || string.IsNullOrWhiteSpace(c.SubjectB))
            throw new ArgumentException("Subject A / B とlayoutを指定してください。");
        foreach (var block in new[] { c.Common, c.SubjectA, c.SubjectB, c.CommonNegative, c.NegativeA, c.NegativeB })
        {
            if (block is null || block.Length > 16000 || Regex.IsMatch(block, @"\b(BREAK|AND|ADDCOMM|ADDNCOMM|ADDBASE|ADDROW|ADDCOL|ADDP|ADDMASK)\b"))
                throw new ArgumentException("block内のregional制御語 / ANDは使えません。raw・weight・LoRAは保持します。");
            var parser = new PromptParser(new Catalog([]));
            if (PromptParser.Serialize(parser.Parse(block)) != block) throw new ArgumentException("Prompt raw round-trip不一致。");
        }
        var parts = c.Ratios.Split(',');
        if (parts.Length != 2 || parts.Any(p => !decimal.TryParse(p, NumberStyles.AllowDecimalPoint, CultureInfo.InvariantCulture, out var n) || n <= 0 || n > 10000))
            throw new ArgumentException("ratioは2つの正数です（例 1,1 / 2,1）。");
    }
    public static (string Positive, string Negative) Compile(RegionComposerConfig c)
    {
        Validate(c);
        // Empty common is a real optional block; region boundaries never come from parser rewriting.
        var p = (string.IsNullOrWhiteSpace(c.Common) ? "" : c.Common + " BREAK ") + c.SubjectA + " BREAK " + c.SubjectB;
        var n = c.CommonNegative + " BREAK " + (string.IsNullOrWhiteSpace(c.NegativeA) ? "_" : c.NegativeA) + " BREAK " + (string.IsNullOrWhiteSpace(c.NegativeB) ? "_" : c.NegativeB);
        if (string.IsNullOrWhiteSpace(c.CommonNegative)) n = (string.IsNullOrWhiteSpace(c.NegativeA) ? "_" : c.NegativeA) + " BREAK " + (string.IsNullOrWhiteSpace(c.NegativeB) ? "_" : c.NegativeB);
        return (p, n);
    }
    public static (string Positive, string Negative) Ordinary(RegionComposerConfig c)
    {
        Validate(c);
        return (string.Join(", ", new[] { c.Common, c.SubjectA, c.SubjectB }.Where(s => !string.IsNullOrWhiteSpace(s))),
            string.Join(", ", new[] { c.CommonNegative, c.NegativeA, c.NegativeB }.Where(s => !string.IsNullOrWhiteSpace(s))));
    }
    public static object?[] Args(RegionComposerConfig c)
    {
        Validate(c);
        return [true, false, "Matrix", MatrixMode(c), "Mask", "Prompt", c.Ratios, "0", false,
            !string.IsNullOrWhiteSpace(c.Common), !string.IsNullOrWhiteSpace(c.CommonNegative), "Attention",
            new[] { "disable convert 'AND' to 'BREAK'" }, "0", "0", "0.4", null, "0", "0", false];
    }
    public static readonly string[] Labels = ["Regional Prompter", "", "", "Main Splitting", "Mask mode", "Prompt mode", "Divide Ratio", "Base Ratio", "Use base prompt", "Use common prompt", "Use common negative prompt", "Generation Mode", "Options", "LoRA in negative textencoder", "LoRA in negative U-net", "threshold", "", "LoRA stop step", "LoRA Hires stop step", "flip \",\" and \";\""];
    public static RegionalCapability Detect(JsonElement scripts, JsonElement extensions)
    {
        var candidates = scripts.EnumerateArray().Where(s => s.GetProperty("name").GetString() == "regional prompter" && !s.GetProperty("is_img2img").GetBoolean() && s.GetProperty("is_alwayson").GetBoolean()).ToArray();
        if (candidates.Length != 1) throw new InvalidDataException("Regional Prompter alwayson APIがありません。通常生成へfallbackしません。");
        var args = candidates[0].GetProperty("args").EnumerateArray().ToArray();
        if (args.Length != Labels.Length || args.Where((a,i) => a.GetProperty("label").GetString() != Labels[i]).Any() ||
            !args[3].GetProperty("choices").EnumerateArray().Any(v => v.GetString() == "Columns") ||
            !args[3].GetProperty("choices").EnumerateArray().Any(v => v.GetString() == "Rows"))
            throw new InvalidDataException("Regional Prompter argument contract不一致。");
        var installed = extensions.EnumerateArray().Where(e => e.GetProperty("enabled").GetBoolean() && e.GetProperty("remote").GetString()?.TrimEnd('/').Replace(".git", "") == Repository && e.GetProperty("commit_hash").GetString() == Commit).ToArray();
        if (installed.Length != 1) throw new InvalidDataException("未検証Regional Prompter repository/version。adapter更新が必要です。");
        return new(Repository, Commit, installed[0].GetProperty("version").GetString()!, Contract);
    }
    public static void Verify(RegionComposerConfig c, GenerationMetadataSnapshot m)
    {
        var compiled = Compile(c);
        if (m.Positive != compiled.Positive.Trim() || m.Negative != compiled.Negative.Trim()) throw new InvalidDataException("Regional compiled Prompt不一致。");
        var expected = new Dictionary<string,string> { ["RP Active"]="True", ["RP Divide mode"]="Matrix", ["RP Matrix submode"]=MatrixMode(c), ["RP Calc Mode"]="Attention", ["RP Ratios"]=c.Ratios, ["RP Use Base"]="False", ["RP Use Common"]=(!string.IsNullOrWhiteSpace(c.Common)).ToString(), ["RP Use Ncommon"]=(!string.IsNullOrWhiteSpace(c.CommonNegative)).ToString(), ["RP Mask submode"]="Mask", ["RP Prompt submode"]="Prompt", ["RP Base Ratios"]="0", ["RP Options"]="disable convert 'AND' to 'BREAK'", ["RP LoRA Neg Te Ratios"]="0", ["RP LoRA Neg U Ratios"]="0", ["RP threshold"]="0.4", ["RP LoRA Stop Step"]="0", ["RP LoRA Hires Stop Step"]="0", ["RP Flip"]="False" };
        foreach (var pair in expected)
            if (m.Value(pair.Key)?.Trim('"') != pair.Value) throw new InvalidDataException("Regional適用を確認できません: " + pair.Key);
    }
    public static RegionalReceipt? Read(IReadOnlyList<GenerationParameter>? parameters)
    {
        var fields = (parameters ?? []).Where(p => p.Name == Key).ToArray();
        if (fields.Length == 0) return null;
        if (fields.Length != 1 || fields[0].Value.Length > 100000) throw new InvalidDataException("Regional receipt重複/上限超過。");
        try
        {
            var r = JsonSerializer.Deserialize<RegionalReceipt>(fields[0].Value) ?? throw new InvalidDataException("Empty regional receipt.");
            Validate(r.Config);
            if (r.Extension.Repository != Repository || r.Extension.Commit != Commit || r.Extension.Contract != Contract) throw new InvalidDataException("Regional receipt adapter不一致。");
            using var request = JsonDocument.Parse(r.RequestJson);
            var compiled = Compile(r.Config);
            if (request.RootElement.GetProperty("prompt").GetString() != compiled.Positive || request.RootElement.GetProperty("negative_prompt").GetString() != compiled.Negative || request.RootElement.GetProperty("alwayson_scripts").GetProperty("Regional Prompter").GetProperty("args").GetRawText() != JsonSerializer.Serialize(Args(r.Config))) throw new InvalidDataException("Regional receipt request不一致。");
            return r;
        }
        catch (Exception e) when (e is JsonException or ArgumentException or KeyNotFoundException) { throw new InvalidDataException("不正Regional receipt。",e); }
    }
    public static bool IsValid(GenerationParameter p) { try { return Read([p]) is not null; } catch (InvalidDataException) { return false; } }
}
