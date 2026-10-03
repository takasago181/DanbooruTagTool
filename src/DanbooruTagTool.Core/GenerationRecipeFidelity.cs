namespace DanbooruTagTool.Core;

/// <summary>Conservative projection boundary, not a backend/profile compatibility claim.</summary>
public static class GenerationRecipeFidelity
{
    private static readonly HashSet<string> Applied = new(StringComparer.OrdinalIgnoreCase)
    { "Model", "Model hash", "Seed", "Steps", "Sampler", "Schedule type", "Scheduler", "CFG scale", "Size", GenerationLoraProvenance.HashesKey, GenerationLoraProvenance.ReceiptKey, GenerationRecipeDerivation.Key, RegionComposer.Key };
    private static readonly HashSet<string> Informational = new(StringComparer.OrdinalIgnoreCase)
    { "Version", "User", "Time taken" };

    public static IReadOnlyList<GenerationParameter> Unapplied(GenerationRecipe recipe)
    {
        var source = recipe.SourceParameters ?? [];
        // Aliases share one owner: conflicting/duplicate scheduler evidence is not
        // silently reduced to the last occurrence, even if values happen to agree.
        static string Key(string name) => name.Equals("Schedule type", StringComparison.OrdinalIgnoreCase) ? "Scheduler" : name;
        var duplicates = source.GroupBy(p => Key(p.Name), StringComparer.OrdinalIgnoreCase)
            .Where(g => g.Count() > 1).Select(g => g.Key).ToHashSet(StringComparer.OrdinalIgnoreCase);
        var regionalApplied = recipe.Regional is not null && RegionComposer.Read(source)?.Config == recipe.Regional;
        return source.Where(p => !Informational.Contains(p.Name) &&
            (duplicates.Contains(Key(p.Name)) ||
             !(p.Name.StartsWith("RP ", StringComparison.Ordinal) && regionalApplied || Applied.Contains(p.Name) && Projected(p.Name, recipe)))).ToArray();
    }

    private static bool Projected(string name, GenerationRecipe r) => name.ToLowerInvariant() switch
    {
        "model" => !string.IsNullOrWhiteSpace(r.Model),
        "model hash" => !string.IsNullOrWhiteSpace(r.ModelHash),
        "seed" => r.Seed is >= 0,
        "steps" => r.Steps is >= 1 and <= 150,
        "sampler" => !string.IsNullOrWhiteSpace(r.Sampler),
        "schedule type" or "scheduler" => !string.IsNullOrWhiteSpace(r.Scheduler),
        "cfg scale" => r.Cfg is >= 0 and <= 30,
        "size" => r.Width is >= 64 and <= 2048 && r.Height is >= 64 and <= 2048 && r.Width % 8 == 0 && r.Height % 8 == 0,
        "lora hashes" or "dtt lora provenance v1" => GenerationLoraProvenance.IsValid(r.SourceParameters!.Single(p => p.Name.Equals(name, StringComparison.OrdinalIgnoreCase))),
        "dtt regional receipt v1" => RegionComposer.IsValid(r.SourceParameters!.Single(p => p.Name == RegionComposer.Key)),
        "dtt recipe derivation v1" => GenerationRecipeDerivation.IsValid(r.SourceParameters!.Single(p => GenerationRecipeDerivation.IsKey(p.Name))),
        _ => false
    };
}
