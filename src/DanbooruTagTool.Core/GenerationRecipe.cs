using System.Globalization;

namespace DanbooruTagTool.Core;

public sealed record GenerationRecipe(
    string? Model = null,
    long? Seed = null,
    int? Steps = null,
    string? Sampler = null,
    string? Scheduler = null,
    decimal? Cfg = null,
    int? Width = null,
    int? Height = null)
{
    public bool HasAny =>
        !string.IsNullOrWhiteSpace(Model) || Seed.HasValue || Steps.HasValue ||
        !string.IsNullOrWhiteSpace(Sampler) || !string.IsNullOrWhiteSpace(Scheduler) ||
        Cfg.HasValue || Width.HasValue || Height.HasValue;

    public string Summary
    {
        get
        {
            var parts = new List<string>();
            if (!string.IsNullOrWhiteSpace(Model)) parts.Add(Model!);
            if (Steps is { } steps) parts.Add($"{steps} steps");
            if (!string.IsNullOrWhiteSpace(Sampler)) parts.Add(Sampler!);
            if (!string.IsNullOrWhiteSpace(Scheduler) && !Scheduler.Equals("Automatic", StringComparison.OrdinalIgnoreCase)) parts.Add(Scheduler!);
            if (Cfg is { } cfg) parts.Add($"CFG {cfg.ToString(CultureInfo.InvariantCulture)}");
            if (Width is { } width && Height is { } height) parts.Add($"{width}×{height}");
            if (Seed is { } seed) parts.Add($"Seed {seed}");
            return string.Join(" · ", parts);
        }
    }

    public static GenerationRecipe FromMetadata(GenerationMetadataSnapshot snapshot)
    {
        static string? Clean(string? value) => string.IsNullOrWhiteSpace(value) ? null : value.Trim();
        static long? Long(string? value) => long.TryParse(value, NumberStyles.Integer, CultureInfo.InvariantCulture, out var parsed) ? parsed : null;
        static int? Int(string? value) => int.TryParse(value, NumberStyles.Integer, CultureInfo.InvariantCulture, out var parsed) ? parsed : null;
        static decimal? Decimal(string? value) => decimal.TryParse(value, NumberStyles.Number, CultureInfo.InvariantCulture, out var parsed) ? parsed : null;

        return new(
            Clean(snapshot.Value("Model")),
            Long(snapshot.Value("Seed")),
            Int(snapshot.Value("Steps")),
            Clean(snapshot.Value("Sampler")),
            Clean(snapshot.Value("Schedule type") ?? snapshot.Value("Scheduler")),
            Decimal(snapshot.Value("CFG scale")),
            snapshot.Width,
            snapshot.Height);
    }
}
