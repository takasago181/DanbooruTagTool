using System.Globalization;
using System.Security.Cryptography;
using System.Text;
using System.Text.Json;

namespace DanbooruTagTool.Core;

public sealed record RecipeSnapshot(string Positive, string Negative, GenerationRecipe Recipe);
public sealed record RecipeDerivation(string ParentId, string? ParentImageSha256, string Source,
    RecipeSnapshot Parent, RecipeSnapshot Requested, IReadOnlyList<MetadataDifference> Changes);

/// <summary>One bounded parent edge, not recursive lineage or an execution override.</summary>
public static class GenerationRecipeDerivation
{
    public const string Key = "DTT Recipe derivation v1";
    private const int MaxBytes = 128 * 1024;
    public static bool IsKey(string name) => name.Equals(Key, StringComparison.OrdinalIgnoreCase);
    public static GenerationRecipe Strip(GenerationRecipe r) => r with
    { SourceParameters = (r.SourceParameters ?? []).Where(p => !IsKey(p.Name)).ToArray() };
    public static RecipeSnapshot Snapshot(string positive, string negative, GenerationRecipe r) => new(positive, negative, Strip(r));
    public static string Identity(RecipeSnapshot s) => Convert.ToHexString(SHA256.HashData(Encoding.UTF8.GetBytes(JsonSerializer.Serialize(s)))).ToLowerInvariant();
    public static RecipeDerivation Build(RecipeSnapshot parent, RecipeSnapshot requested, string source, string? imageSha = null)
    {
        var value = new RecipeDerivation(Identity(parent), imageSha, source, parent, requested, Diff(parent, requested));
        Validate(value); return value;
    }
    public static IReadOnlyList<MetadataDifference> Diff(RecipeSnapshot parent, RecipeSnapshot current)
    {
        var rows = new List<MetadataDifference>();
        void Add(string key, string? left, string? right) { if (left != right) rows.Add(new(key, left, right, left is null ? "only right" : right is null ? "only left" : "changed")); }
        static string? N<T>(T? value) where T : struct, IFormattable => value?.ToString(null, CultureInfo.InvariantCulture);
        var p = parent.Recipe; var c = current.Recipe;
        Add("Positive", parent.Positive, current.Positive); Add("Negative", parent.Negative, current.Negative);
        Add("Model", p.Model, c.Model); Add("Model hash", p.ModelHash, c.ModelHash);
        Add("Seed", N(p.Seed), N(c.Seed)); Add("Steps", N(p.Steps), N(c.Steps));
        Add("Sampler", p.Sampler, c.Sampler); Add("Scheduler", p.Scheduler, c.Scheduler); Add("CFG", N(p.Cfg), N(c.Cfg));
        Add("Width", N(p.Width), N(c.Width)); Add("Height", N(p.Height), N(c.Height));
        Add("LoRA", JsonSerializer.Serialize(GenerationLibraryMetadata.Loras(parent.Positive)), JsonSerializer.Serialize(GenerationLibraryMetadata.Loras(current.Positive)));
        Add("Source evidence", JsonSerializer.Serialize(p.SourceParameters ?? []), JsonSerializer.Serialize(c.SourceParameters ?? []));
        // Hires/RNG/etc remain evidence, never executable overrides. Even an
        // unchanged editor cannot claim same conditions when these are omitted.
        if (p.RequiresDerivativeConsent || c.RequiresDerivativeConsent)
            rows.Add(new("Unapplied conditions (not sent)", JsonSerializer.Serialize(p.UnappliedParameters), JsonSerializer.Serialize(c.UnappliedParameters), "not applied"));
        return rows;
    }
    public static GenerationRecipe With(GenerationRecipe recipe, RecipeDerivation edge) => Strip(recipe) with
    { SourceParameters = (Strip(recipe).SourceParameters ?? []).Concat([new GenerationParameter(Key, Serialize(edge))]).ToArray() };
    public static string Serialize(RecipeDerivation edge) { Validate(edge); return JsonSerializer.Serialize(edge); }
    public static RecipeDerivation? Read(IReadOnlyList<GenerationParameter>? parameters)
    {
        var fields = (parameters ?? []).Where(p => IsKey(p.Name)).ToArray();
        if (fields.Length == 0) return null;
        if (fields.Length != 1 || Encoding.UTF8.GetByteCount(fields[0].Value) > MaxBytes) throw new InvalidDataException("Recipe派生記録の重複/上限超過。");
        try { var edge = JsonSerializer.Deserialize<RecipeDerivation>(fields[0].Value) ?? throw new InvalidDataException("空のRecipe派生記録。"); Validate(edge); return edge; }
        catch (JsonException e) { throw new InvalidDataException("不正Recipe派生記録。", e); }
    }
    public static bool IsValid(GenerationParameter p) { try { return Read([p]) is not null; } catch (InvalidDataException) { return false; } }
    private static void Validate(RecipeDerivation edge)
    {
        bool SnapshotValid(RecipeSnapshot? s) => s is { Positive: not null, Negative: not null, Recipe: not null } &&
            !(s.Recipe.SourceParameters ?? []).Any(p => p is null || p.Name is null || p.Value is null || IsKey(p.Name));
        if (!SnapshotValid(edge.Parent) || !SnapshotValid(edge.Requested) || edge.Changes is null || edge.Source is null || edge.Source.Length > 512 ||
            !GenerationLoraProvenance.Hex(edge.ParentId, 64) || edge.ParentImageSha256 is not null && !GenerationLoraProvenance.Hex(edge.ParentImageSha256, 64)) throw new InvalidDataException("不正Recipe parent/snapshot。");
        if (Identity(edge.Parent) != edge.ParentId || !Diff(edge.Parent, edge.Requested).SequenceEqual(edge.Changes)) throw new InvalidDataException("Recipe parent identity / changed fields不一致。");
        if (Encoding.UTF8.GetByteCount(JsonSerializer.Serialize(edge)) > MaxBytes) throw new InvalidDataException("Recipe派生記録の上限超過。");
    }
    public static string Summary(RecipeDerivation? edge) => edge is null ? "派生元記録なし。" :
        $"派生元: {edge.Source}\nRecipe SHA256: {edge.ParentId}" + (edge.ParentImageSha256 is null ? "\n元画像SHA256未記録" : "\n元画像SHA256: " + edge.ParentImageSha256) +
        (edge.Changes.Count == 0 ? "\n元Recipeから対応条件の変更なし（画像の完全一致は保証しません）。" : "\n派生条件: " + string.Join(" / ", edge.Changes.Select(x => x.Field))) +
        string.Concat(edge.Changes.Select(x => $"\n{x.Field}: {x.Left ?? "未指定"} → {x.Right ?? "未指定"}"));
    public static string Summary(IReadOnlyList<GenerationParameter>? parameters)
    { try { return Summary(Read(parameters)); } catch (InvalidDataException e) { return e.Message; } }
    public static GenerationRecipe FromImage(GenerationMetadataSnapshot metadata, string source, Func<string, GenerationMetadataSnapshot>? reader = null)
    {
        var r = Strip(GenerationRecipe.FromMetadata(metadata));
        using var file = new FileStream(metadata.SourcePath, FileMode.Open, FileAccess.Read, FileShare.Read);
        var fresh = (reader ?? ForgePngGenerationMetadata.Read)(metadata.SourcePath);
        if (metadata.RawInfotext != fresh.RawInfotext || JsonSerializer.Serialize(metadata.Parameters) != JsonSerializer.Serialize(fresh.Parameters))
            throw new InvalidDataException("派生元metadataが変更されています。Libraryを再スキャンしてください。");
        var sha = Convert.ToHexString(SHA256.HashData(file)).ToLowerInvariant();
        var s = Snapshot(metadata.Positive, metadata.Negative, r);
        return With(r, Build(s, s, source, sha));
    }
}
