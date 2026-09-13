namespace DanbooruTagTool.Data;

public static class CatalogOutputGuard
{
    public static string Validate(string output, params string[] roots)
    {
        var full = Path.TrimEndingDirectorySeparator(Path.GetFullPath(output));
        foreach (var root in roots)
        {
            var protectedRoot = Path.TrimEndingDirectorySeparator(Path.GetFullPath(Path.Combine(root, "data")));
            if (full.Equals(protectedRoot, StringComparison.OrdinalIgnoreCase) ||
                full.StartsWith(protectedRoot + Path.DirectorySeparatorChar, StringComparison.OrdinalIgnoreCase))
                throw new ArgumentException("Catalog output must not equal or be inside protected source data.");
        }
        return full;
    }
}
