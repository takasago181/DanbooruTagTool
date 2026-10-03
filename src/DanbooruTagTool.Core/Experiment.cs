using System.Globalization;
using System.Text.Json;

namespace DanbooruTagTool.Core;

public enum ExperimentVariable { Positive, Negative, TagWeight, Cfg, Steps, Sampler, Scheduler, LoraWeight }
public sealed record ExperimentAxis(ExperimentVariable Kind, string Target, IReadOnlyList<string> Values);
public sealed record ExperimentSetup(string Name, string Hypothesis, RecipeSnapshot Baseline,
    ExperimentAxis X, ExperimentAxis? Y, IReadOnlyList<long> Seeds, int Repetitions = 1, bool AllowUnapplied = false);
public sealed record ExperimentTrial(Guid Id, int X, int Y, long Seed, int Repetition, RecipeSnapshot Requested);
public sealed record ExperimentPlan(Guid Id, DateTime CreatedUtc, string BaselineId, ExperimentSetup Setup, IReadOnlyList<ExperimentTrial> Trials);
public sealed record TrialEvaluation(int? Rating = null, bool? Passed = null, bool Winner = false, string Note = "");
public sealed record ExperimentObservation(string Direction = "", string Exceptions = "");
public sealed record ExperimentAttempt(Guid Id, Guid RunId, Guid TrialId, int RunNumber, string Status,
    DateTime? StartedUtc = null, DateTime? CompletedUtc = null, ForgeApiResult? Receipt = null,
    long? LibraryImageId = null, TrialEvaluation? Evaluation = null);

/// <summary>Finite explicit axes over existing Recipe snapshots. Never expands templates or changes shared Prompt state.</summary>
public static class ExperimentPlanner
{
    public const int MaxTrials = 64;
    private static readonly CultureInfo Invariant = CultureInfo.InvariantCulture;
    public static int Count(ExperimentSetup s)
    {
        if (s.X is null || s.Seeds is null || s.X.Values is null || s.X.Values.Count is < 1 or > 16 ||
            s.Y is not null && (s.Y.Values is null || s.Y.Values.Count is < 1 or > 16) ||
            s.Seeds.Count is < 1 or > 16 || s.Repetitions is < 1 or > 4)
            throw new ArgumentException("各軸1〜16値、seed1〜16個、反復1〜4回を明示してください。");
        var count = checked(s.X.Values.Count * (s.Y?.Values.Count ?? 1) * s.Seeds.Count * s.Repetitions);
        if (count > MaxTrials) throw new ArgumentException($"{count}生成は上限{MaxTrials}を超えます。");
        return count;
    }
    public static ExperimentPlan Build(ExperimentSetup setup)
    {
        Count(setup);
        if (string.IsNullOrWhiteSpace(setup.Name) || setup.Name.Length > 200 || setup.Hypothesis.Length > 4000 ||
            setup.Baseline is null || setup.Baseline.Positive.Length > 16000 || setup.Baseline.Negative.Length > 16000)
            throw new ArgumentException("実験名、baseline、hypothesisの上限を確認してください。");
        var baseline = GenerationRecipeDerivation.Snapshot(setup.Baseline.Positive, setup.Baseline.Negative, setup.Baseline.Recipe);
        var loras = GenerationLibraryMetadata.Loras(baseline.Positive);
        var identities = GenerationLoraProvenance.Expected(baseline.Recipe.SourceParameters);
        if (loras.Count != identities.Count || loras.Any(l => !identities.Any(i => i.Name == l.Name && i.FileSha256 is not null)))
            throw new ArgumentException("baseline LoRAをForge候補とlocal full-file SHA256で固定してください。");
        if (string.IsNullOrWhiteSpace(baseline.Recipe.Model) || string.IsNullOrWhiteSpace(baseline.Recipe.ModelHash) ||
            baseline.Recipe.Steps is not (>= 1 and <= 150) || baseline.Recipe.Cfg is not (>= 0 and <= 30) ||
            string.IsNullOrWhiteSpace(baseline.Recipe.Sampler) || string.IsNullOrWhiteSpace(baseline.Recipe.Scheduler) ||
            baseline.Recipe.Width is not (>= 64 and <= 2048) || baseline.Recipe.Height is not (>= 64 and <= 2048) ||
            baseline.Recipe.Width % 8 != 0 || baseline.Recipe.Height % 8 != 0)
            throw new ArgumentException("baselineにModel/hash・Steps・CFG・sampler/scheduler・sizeを固定してください。");
        if (setup.Seeds.Any(s => s < 0 || s == long.MaxValue) || setup.Seeds.Distinct().Count() != setup.Seeds.Count)
            throw new ArgumentException("seedは重複のない明示的な非負整数です（random/-1不可）。");
        if (setup.Y?.Kind == setup.X.Kind) throw new ArgumentException("X/Yは別の変数を選んでください。");
        foreach (var a in new[] { setup.X, setup.Y }.OfType<ExperimentAxis>())
        {
            if (!Enum.IsDefined(a.Kind) || a.Target.Length > 2000 || a.Values.Any(v => string.IsNullOrWhiteSpace(v) || v.Length > 4000 || v.Contains('{') || v.Contains('}') || v.Contains("__")))
                throw new ArgumentException("軸値は明示的なliteralです。wildcard/template・空値・上限超過は使えません。");
        }
        setup = setup with { Baseline = baseline, X = setup.X with { Values = setup.X.Values.ToArray() },
            Y = setup.Y is null ? null : setup.Y with { Values = setup.Y.Values.ToArray() }, Seeds = setup.Seeds.ToArray() };
        var id = Guid.NewGuid(); var trials = new List<ExperimentTrial>(); var seen = new HashSet<string>();
        var allowed = new HashSet<string>(StringComparer.Ordinal) { "Seed" };
        foreach (var a in new[] { setup.X, setup.Y }.OfType<ExperimentAxis>())
            foreach (var f in Fields(a.Kind)) allowed.Add(f);
        foreach (var seed in setup.Seeds)
        for (var rep = 0; rep < setup.Repetitions; rep++)
        for (var y = 0; y < (setup.Y?.Values.Count ?? 1); y++)
        for (var x = 0; x < setup.X.Values.Count; x++)
        {
            var s = baseline with { Recipe = baseline.Recipe with { Seed = seed } };
            s = Apply(s, setup.X, setup.X.Values[x]); if (setup.Y is { } axis) s = Apply(s, axis, axis.Values[y]);
            var edge = GenerationRecipeDerivation.Build(baseline, s, "Experiment " + id);
            if (edge.Changes.Any(d => d.State != "not applied" && !allowed.Contains(d.Field)))
                throw new ArgumentException("非対象条件が変わる軸です。固定Model/LoRA/Recipe条件を保持してください。");
            if (!seen.Add(GenerationRecipeDerivation.Identity(s) + "/" + rep)) throw new ArgumentException("同じ条件の重複trialです。軸値を確認してください。");
            trials.Add(new(Guid.NewGuid(), x, y, seed, rep, s with { Recipe = GenerationRecipeDerivation.With(s.Recipe, edge) }));
        }
        return new(id, DateTime.UtcNow, GenerationRecipeDerivation.Identity(baseline), setup, trials);
    }
    public static void Validate(ExperimentPlan p)
    {
        // Recompute solely from stored setup, never current UI defaults; prove every controlled field before execution.
        var expected = Build(p.Setup);
        if (p.Id == Guid.Empty || p.BaselineId != expected.BaselineId || p.Trials.Count != expected.Trials.Count || p.Trials.Select(t => t.Id).Distinct().Count() != p.Trials.Count)
            throw new InvalidDataException("Experiment identity/count不一致。");
        for (var i = 0; i < p.Trials.Count; i++)
        {
            var t = p.Trials[i]; var e = expected.Trials[i]; var edge = GenerationRecipeDerivation.Read(t.Requested.Recipe.SourceParameters);
            if (t.Id == Guid.Empty || t.X != e.X || t.Y != e.Y || t.Seed != e.Seed || t.Repetition != e.Repetition ||
                GenerationRecipeDerivation.Identity(GenerationRecipeDerivation.Snapshot(t.Requested.Positive, t.Requested.Negative, t.Requested.Recipe)) !=
                GenerationRecipeDerivation.Identity(GenerationRecipeDerivation.Snapshot(e.Requested.Positive, e.Requested.Negative, e.Requested.Recipe)) ||
                edge?.ParentId != p.BaselineId || edge.Source != "Experiment " + p.Id ||
                GenerationRecipeDerivation.Identity(edge.Requested) != GenerationRecipeDerivation.Identity(GenerationRecipeDerivation.Snapshot(t.Requested.Positive, t.Requested.Negative, t.Requested.Recipe)))
                throw new InvalidDataException("Trialの非対象条件 / exact Recipe / parent不一致。");
        }
    }
    private static IEnumerable<string> Fields(ExperimentVariable k) => k switch
    {
        ExperimentVariable.Positive or ExperimentVariable.TagWeight => ["Positive"], ExperimentVariable.Negative => ["Negative"],
        ExperimentVariable.LoraWeight => ["Positive", "LoRA"], ExperimentVariable.Cfg => ["CFG"], ExperimentVariable.Steps => ["Steps"],
        ExperimentVariable.Sampler => ["Sampler"], ExperimentVariable.Scheduler => ["Scheduler"], _ => throw new ArgumentException("Unknown variable")
    };
    private static RecipeSnapshot Apply(RecipeSnapshot s, ExperimentAxis a, string value)
    {
        decimal Number(decimal min, decimal max)
        { if (!decimal.TryParse(value, NumberStyles.AllowLeadingSign | NumberStyles.AllowDecimalPoint, Invariant, out var n) || n < min || n > max) throw new ArgumentException($"軸値{value}: {min}〜{max}の数値を指定してください。"); return decimal.Parse(n.ToString("G29", Invariant), Invariant); }
        string Fragment(string text)
        {
            if (a.Target.Length == 0) return text.Length == 0 ? value : text + ", " + value;
            var at = text.IndexOf(a.Target, StringComparison.Ordinal);
            if (at < 0 || text.IndexOf(a.Target, at + a.Target.Length, StringComparison.Ordinal) >= 0) throw new ArgumentException("置換対象はbaseline内に完全一致で1回だけ必要です。");
            return text[..at] + value + text[(at + a.Target.Length)..];
        }
        string Weighted(bool lora)
        {
            if (string.IsNullOrWhiteSpace(a.Target)) throw new ArgumentException("weight軸の対象名を指定してください。");
            var items = new PromptParser(new Catalog([])).Parse(s.Positive);
            var matches = items.Where(i => lora ? i.Kind == PromptItemKind.Lora && i.StructuredName == a.Target :
                i.Kind == PromptItemKind.Weighted && i.StructuredName == a.Target || i.Kind is PromptItemKind.Normal or PromptItemKind.Raw && i.Surface.Trim() == a.Target).ToArray();
            if (matches.Length != 1) throw new ArgumentException("weight対象はbaseline内の単純tag/LoRA tokenに1回だけ必要です。");
            var item = matches[0]; var n = Number(lora ? -2 : -3, lora ? 2 : 3).ToString(Invariant);
            var token = lora ? $"<lora:{a.Target}:{n}>" : $"({a.Target}:{n})";
            var parsed = new PromptParser(new Catalog([])).Parse(token);
            if (parsed.Length != 1 || parsed[0].Kind != (lora ? PromptItemKind.Lora : PromptItemKind.Weighted) || parsed[0].StructuredName != a.Target)
                throw new ArgumentException("weight対象はparserで認識できる単純tokenにしてください。");
            var surface = item.Surface[..(item.Surface.Length - item.Surface.TrimStart().Length)] + token + item.Surface[item.Surface.TrimEnd().Length..];
            return PromptParser.Serialize(items.Select(i => i.Id == item.Id ? i with { Surface = surface } : i));
        }
        return a.Kind switch
        {
            ExperimentVariable.Positive => s with { Positive = Fragment(s.Positive) }, ExperimentVariable.Negative => s with { Negative = Fragment(s.Negative) },
            ExperimentVariable.TagWeight => s with { Positive = Weighted(false) }, ExperimentVariable.LoraWeight => s with { Positive = Weighted(true) },
            ExperimentVariable.Cfg => s with { Recipe = s.Recipe with { Cfg = Number(0, 30) } },
            ExperimentVariable.Steps => s with { Recipe = s.Recipe with { Steps = Number(1, 150) is var n && n == decimal.Truncate(n) ? (int)n : throw new ArgumentException("Stepsは整数です。") } },
            ExperimentVariable.Sampler => s with { Recipe = s.Recipe with { Sampler = value } },
            ExperimentVariable.Scheduler => s with { Recipe = s.Recipe with { Scheduler = value } }, _ => throw new ArgumentException("Unknown variable")
        };
    }
    public static string Json<T>(T value) => JsonSerializer.Serialize(value);
}
