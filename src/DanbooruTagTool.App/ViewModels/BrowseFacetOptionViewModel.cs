namespace DanbooruTagTool.App.ViewModels;

public enum BrowseFacetKind { Local, BodySite, Theme }

public sealed class BrowseFacetOptionViewModel(
    BrowseFacetKind kind,
    string id,
    string label) : Observable
{
    public BrowseFacetKind Kind { get; } = kind;
    public string Id { get; } = id;
    public string Label { get; } = label;

    private bool selected;
    private int count;

    public bool Selected
    {
        get => selected;
        set { if (Set(ref selected, value)) Notify(nameof(IsVisible)); }
    }

    public int Count
    {
        get => count;
        set
        {
            if (!Set(ref count, value)) return;
            Notify(nameof(IsVisible));
            Notify(nameof(ToolTip));
        }
    }

    public bool IsVisible => Selected || Count > 0;
    public string ToolTip => $"{Count:N0}件";
}
