namespace DanbooruTagTool.Data;

public enum CatalogBuildProfile
{
    Full,
    Ordinary
}

public static class CatalogBuildProfiles
{
    public static CatalogBuildProfile Parse(string value)
        => value.Trim().ToLowerInvariant() switch
        {
            "full" => CatalogBuildProfile.Full,
            "ordinary" => CatalogBuildProfile.Ordinary,
            _ => throw new ArgumentException($"Unknown catalog build profile: {value}. Expected full or ordinary.", nameof(value))
        };

    public static string Name(this CatalogBuildProfile profile)
        => profile switch
        {
            CatalogBuildProfile.Full => "full",
            CatalogBuildProfile.Ordinary => "ordinary",
            _ => throw new ArgumentOutOfRangeException(nameof(profile))
        };
}
