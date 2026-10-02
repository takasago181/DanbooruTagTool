using DanbooruTagTool.Core;

namespace DanbooruTagTool.Data;

/// <summary>Runtime adapter: reads accepted classifications, never builds them.</summary>
public static class SpecialBrowseCatalogReader
{
    public static SpecialBrowseV2Index FromCatalog(ICatalog catalog)
    {
        var specials = catalog.Entries.Where(entry => entry.IsSpecial).ToArray();
        if (specials.Any(entry => entry.SpecialBrowseV2 is null))
            throw new InvalidDataException("Catalog is missing accepted Special browse classifications; compile the accepted authority snapshot.");
        return new SpecialBrowseV2Index(specials.Select(entry => new SpecialBrowseV2Entry(
            entry.Id, entry.SpecialBrowseV2!.KindId,
            entry.SpecialBrowseV2.BodySiteIds.ToHashSet(StringComparer.Ordinal),
            entry.SpecialBrowseV2.ThemeIds.ToHashSet(StringComparer.Ordinal),
            entry.SpecialBrowseV2.Status, entry.Canonical)));
    }
}
