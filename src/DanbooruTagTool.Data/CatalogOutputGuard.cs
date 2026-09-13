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
        // The second root is the authority root in the catalog build contract.
        // Keep the accepted #56 evidence tree immutable alongside protected data.
        if (roots.Length > 1)
        {
            var acceptedIssue56 = Path.TrimEndingDirectorySeparator(Path.GetFullPath(Path.Combine(roots[1], "docs", "issue56")));
            if (full.Equals(acceptedIssue56, StringComparison.OrdinalIgnoreCase) ||
                full.StartsWith(acceptedIssue56 + Path.DirectorySeparatorChar, StringComparison.OrdinalIgnoreCase))
                throw new ArgumentException("Catalog output must not equal or be inside authority docs/issue56.");
        }
        return full;
    }
}
