namespace DanbooruTagTool.Core;

/// <summary>
/// A display-only projection of the ordered Prompt sequence. It intentionally
/// does not expose mutation operations or a second serialized Prompt.
/// </summary>
public sealed record PromptCategoryItem(PromptItem Item, int OriginalIndex)
{
    public string Japanese => Item.Display;
    public string English => Item.Canonical ?? (Item.Kind == PromptItemKind.Lora ? Item.Surface.Trim() : Item.StructuredName ?? Item.Surface.Trim());
    public bool HasEnglish => Item.Canonical is not null || Item.StructuredName is not null;
}

public sealed record PromptCategoryGroup(string Key, string Label, IReadOnlyList<PromptCategoryItem> Items)
{
    public int Count => Items.Count;
    public string CountText => $"{Count}件";
}

public static class PromptCategoryProjection
{
    public const string SpecialKey = "special";
    public const string OtherKey = "other";
    public const string SpecialLabel = "◆ Special";
    public const string OtherLabel = "その他・未解決";

    public static IReadOnlyList<PromptCategoryGroup> Build(ICatalog catalog, IEnumerable<PromptItem> items)
    {
        var categoryOrder = catalog.Entries
            .Where(entry => !entry.IsSpecial)
            .SelectMany(entry => entry.Paths)
            .GroupBy(path => path.GenreId, StringComparer.Ordinal)
            .Select(group =>
            {
                var path = group.First();
                return new CategoryDefinition("general:" + path.GenreId, path.Genre);
            })
            .ToList();

        var definitions = categoryOrder.ToDictionary(category => category.Key, StringComparer.Ordinal);
        definitions[SpecialKey] = new(SpecialKey, SpecialLabel);
        definitions[OtherKey] = new(OtherKey, OtherLabel);

        var grouped = definitions.Keys.ToDictionary(key => key, _ => new List<PromptCategoryItem>(), StringComparer.Ordinal);
        var fallbackCategoryOrder = new List<CategoryDefinition>();
        var index = 0;
        foreach (var item in items)
        {
            var key = Classify(catalog, item);
            if (!grouped.TryGetValue(key, out var target))
            {
                // A catalog may contain a future accepted path not present in
                // the initial order. Keep it deterministic without inventing
                // a new category: append the existing path label once.
                var entry = Resolve(catalog, item);
                var path = entry?.Paths.FirstOrDefault();
                if (path is null)
                {
                    key = OtherKey;
                    target = grouped[key];
                }
                else
                {
                    var definition = new CategoryDefinition("general:" + path.GenreId, path.Genre);
                    if (!definitions.ContainsKey(definition.Key))
                    {
                        definitions.Add(definition.Key, definition);
                        fallbackCategoryOrder.Add(definition);
                        grouped.Add(definition.Key, target = []);
                    }
                    else target = grouped[definition.Key];
                }
            }
            target.Add(new(item, index));
            index++;
        }

        var result = new List<PromptCategoryGroup>();
        foreach (var definition in categoryOrder.Concat(fallbackCategoryOrder).Concat([
                     new CategoryDefinition(SpecialKey, SpecialLabel),
                     new CategoryDefinition(OtherKey, OtherLabel)]))
        {
            if (grouped.TryGetValue(definition.Key, out var group) && group.Count > 0)
                result.Add(new(definition.Key, definition.Label, group));
        }
        return result;
    }

    private static string Classify(ICatalog catalog, PromptItem item)
    {
        if (item.Kind is PromptItemKind.Raw or PromptItemKind.Lora or PromptItemKind.Control)
            return OtherKey;

        var entry = Resolve(catalog, item);
        if (entry is null) return OtherKey;
        if (entry.IsSpecial) return SpecialKey;
        var path = entry.Paths.FirstOrDefault();
        return path is null ? OtherKey : "general:" + path.GenreId;
    }

    private static CatalogEntry? Resolve(ICatalog catalog, PromptItem item) =>
        (item.CatalogId is not null
            ? catalog.Entries.FirstOrDefault(entry => entry.Id == item.CatalogId)
            : null)
        ?? catalog.Resolve(item.Canonical ?? item.StructuredName ?? item.Surface.Trim());

    private sealed record CategoryDefinition(string Key, string Label);
}
