namespace DanbooruTagTool.Core;

/// <summary>Display-only metadata. Home authority stays on CatalogEntry.</summary>
public sealed record CharacterBrowseGroup(string HomeCopyright, string Id, string Label, int SortOrder);
public sealed record CharacterBrowseGroupCount(string Id, string Label, int Count, int SortOrder);

public static class CharacterBrowseGroups
{
    public const string OtherId = "__other";
}
