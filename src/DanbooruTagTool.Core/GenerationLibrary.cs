using System.Globalization;
using System.Text.RegularExpressions;

namespace DanbooruTagTool.Core;

public sealed record LibraryRoot(long Id, string Path, bool Enabled, bool Recursive);
public sealed record ImageAnnotation(bool Favorite = false, int? Rating = null, string Note = "");
public sealed record GenerationLora(string Name, decimal Weight, string RawToken);
public sealed record LibraryImage(long Id, long RootId, string RelativePath, string NormalizedPath,
    string Extension, long FileSize, long MtimeUtcTicks, int? Width, int? Height,
    string Availability, string MetadataStatus, string? MetadataFormat, ImageAnnotation Annotation);
public enum LibrarySort { Newest, Oldest, Filename, Favorite, Rating }
public sealed record LibraryQuery(string Text = "", long? RootId = null, string Positive = "", string Negative = "",
    string Model = "", long? Seed = null, string Sampler = "", string Scheduler = "", decimal? CfgMin = null,
    decimal? CfgMax = null, int? Width = null, int? Height = null, string Lora = "", bool FavoriteOnly = false,
    int? RatingMin = null, string Note = "", bool? HasMetadata = null, LibrarySort Sort = LibrarySort.Newest,
    int Offset = 0, int Limit = 60);
public sealed record LibraryPage(IReadOnlyList<LibraryImage> Images, long Total);
public sealed record MetadataReadResult(string Status, string? Format = null,
    GenerationMetadataSnapshot? Metadata = null, int? Width = null, int? Height = null, string? Error = null, bool Retryable = false);
public interface IGenerationMetadataReader { bool CanRead(string extension); MetadataReadResult Read(string path); }
public sealed record LibraryScanResult(int Added, int Refreshed, int Unchanged, int Missing, int Errors, bool Complete);

public static partial class GenerationLibraryMetadata
{
    // Only the unambiguous simple numeric <lora:name:weight> form is indexed.
    [GeneratedRegex(@"<lora:([^<>:\r\n]+):([+-]?(?:\d+(?:\.\d*)?|\.\d+))>", RegexOptions.IgnoreCase)]
    private static partial Regex LoraPattern();
    public static IReadOnlyList<GenerationLora> Loras(GenerationMetadataSnapshot metadata)
        => Loras(metadata.Positive);
    public static IReadOnlyList<GenerationLora> Loras(string prompt)
    {
        var result = new List<GenerationLora>();
        foreach (Match m in LoraPattern().Matches(prompt))
            if (decimal.TryParse(m.Groups[2].Value, NumberStyles.Number, CultureInfo.InvariantCulture, out var weight))
                result.Add(new(m.Groups[1].Value, weight, m.Value));
        return result;
    }
}

public sealed record MetadataDifference(string Field, string? Left, string? Right, string State);
public static class GenerationMetadataDiff
{
    public static IReadOnlyList<MetadataDifference> Compare(GenerationMetadataSnapshot left, GenerationMetadataSnapshot right)
    {
        var result = new List<MetadataDifference>();
        void Add(string field, string? l, string? r) => result.Add(new(field, l, r,
            l == r ? "same" : l is null ? "only right" : r is null ? "only left" : "changed"));
        Add("Positive", left.Positive, right.Positive); Add("Negative", left.Negative, right.Negative);
        foreach (var name in new[] { "Model", "Model hash", "Seed", "Steps", "Sampler", "Scheduler", "CFG", "Size" })
        {
            string? Value(GenerationMetadataSnapshot m) => name switch
            {
                "Scheduler" => m.Value("Schedule type") ?? m.Value("Scheduler"),
                "CFG" => m.Value("CFG scale"), _ => m.Value(name)
            };
            Add(name, Value(left), Value(right));
        }
        Add("LoRA", string.Join("\n", GenerationLibraryMetadata.Loras(left).Select(x => x.RawToken)),
            string.Join("\n", GenerationLibraryMetadata.Loras(right).Select(x => x.RawToken)));
        var common = new HashSet<string>(["Model", "Model hash", "Seed", "Steps", "Sampler", "Scheduler", "Schedule type", "CFG scale", "Size"], StringComparer.OrdinalIgnoreCase);
        foreach (var name in left.Parameters.Concat(right.Parameters).Select(x => x.Name).Distinct(StringComparer.OrdinalIgnoreCase).Where(x => !common.Contains(x)))
        {
            string? Values(GenerationMetadataSnapshot m) => m.Parameters.Any(x => x.Name.Equals(name, StringComparison.OrdinalIgnoreCase))
                ? string.Join("\n", m.Parameters.Where(x => x.Name.Equals(name, StringComparison.OrdinalIgnoreCase)).Select(x => x.Value)) : null;
            Add(name, Values(left), Values(right));
        }
        return result;
    }
}
