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
        set
        {
            if (!Set(ref selected, value)) return;
            Notify(nameof(IsVisible));
            Notify(nameof(IsEnabled));
        }
    }

    public int Count
    {
        get => count;
        set
        {
            if (!Set(ref count, value)) return;
            Notify(nameof(IsVisible));
            Notify(nameof(IsEnabled));
            Notify(nameof(ToolTip));
        }
    }

    // Body/theme facets occupy fixed chip slots; hiding zero-count options makes
    // the WrapPanel reflow every remaining chip whenever another facet changes.
    public bool IsVisible => Kind is BrowseFacetKind.BodySite or BrowseFacetKind.Theme || Selected || Count > 0;
    public bool IsEnabled => Selected || Count > 0;
    public string ToolTip => $"{Count:N0}件";
}
