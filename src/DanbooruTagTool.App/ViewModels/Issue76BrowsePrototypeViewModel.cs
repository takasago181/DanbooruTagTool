using System.Collections.ObjectModel;
using System.Globalization;
using DanbooruTagTool.Core;

namespace DanbooruTagTool.App.ViewModels;

public enum Issue76FacetAxis { Kind, BodySite, Theme }

public sealed class Issue76FacetOptionViewModel(
    Issue76FacetAxis axis,
    string id,
    string label) : Observable
{
    public Issue76FacetAxis Axis { get; } = axis;
    public string Id { get; } = id;
    public string Label { get; } = label;
    private bool selected;
    private int count;
    public bool Selected { get => selected; set { if (Set(ref selected, value)) Notify(nameof(Display)); } }
    public int Count { get => count; set { if (Set(ref count, value)) Notify(nameof(Display)); } }
    public string Display => $"{Label}  {Count:N0}";
}

public sealed record Issue76BrowseRowViewModel(CatalogEntry Entry)
{
    public string Label => "◆ " + Entry.Label;
    public string English => Entry.Canonical ?? Entry.English;
    public string Usage => Entry.UsageText;
}

/// <summary>
/// Isolated Issue #76 WPF prototype. This is not the production MainViewModel.
/// </summary>
public sealed class Issue76BrowsePrototypeViewModel : Observable
{
    private static readonly (string Id, string Label)[] KindDefinitions =
    [
        ("ACTION_CONTACT", "行為・接触"),
        ("CLOTHING_EXPOSURE", "衣服・露出"),
        ("TOOL_OBJECT", "道具・物"),
        ("BODY_STATE", "身体・状態"),
        ("FLUID_EXCRETION", "体液・排泄"),
        ("POSE_SCENE", "ポーズ・構図・場面"),
        ("PERSON_RELATION", "人物・関係"),
        ("NONHUMAN_TRANSFORMATION", "異形・変形"),
        ("META_EXPRESSION", "表現・メタ")
    ];

    private static readonly (string Id, string Label)[] BodyDefinitions =
    [
        ("MALE_GENITAL", "男性器"),
        ("BREAST_NIPPLE", "乳房・乳首"),
        ("FEMALE_GENITAL", "女性器"),
        ("MOUTH_ORAL", "口・口内"),
        ("BUTTOCK_ANAL", "尻・肛門"),
        ("URETHRA", "尿道")
    ];

    private static readonly (string Id, string Label)[] ThemeDefinitions =
    [
        ("BDSM_RESTRAINT", "拘束・BDSM"),
        ("INJURY_R18G", "損傷・R18G"),
        ("REPRO_PREGNANCY_LACTATION", "生殖・妊娠・授乳")
    ];

    private readonly ICatalog catalog;
    private readonly SearchEngine search;
    private readonly SpecialBrowseV2Index index;
    private SpecialBrowseV2Filter filter = SpecialBrowseV2Filter.Empty;
    private string query = "";
    private int sortIndex;
    private IReadOnlyList<Issue76BrowseRowViewModel> results = [];

    public ObservableCollection<Issue76FacetOptionViewModel> KindOptions { get; } = [];
    public ObservableCollection<Issue76FacetOptionViewModel> BodyOptions { get; } = [];
    public ObservableCollection<Issue76FacetOptionViewModel> ThemeOptions { get; } = [];
    public IReadOnlyList<NavigationNode> Navigation { get; }
    public IReadOnlyList<Issue76BrowseRowViewModel> Results { get => results; private set => Set(ref results, value); }
    public RelayCommand ToggleFacet { get; }
    public RelayCommand ClearFacets { get; }

    public string Query
    {
        get => query;
        set
        {
            if (Set(ref query, value))
            {
                Notify(nameof(IsSearching));
                Refresh();
            }
        }
    }

    public int SortIndex { get => sortIndex; set { if (Set(ref sortIndex, value)) Refresh(); } }
    public bool IsSearching => !string.IsNullOrWhiteSpace(Query);
    public string ResultSummary => $"{Results.Count:N0}件";
    public bool HasFacets => !filter.IsEmpty;
    public string AppliedSummary
    {
        get
        {
            var labels = new List<string>();
            if (filter.KindId is { } kind) labels.Add(LabelFor(Issue76FacetAxis.Kind, kind));
            labels.AddRange(filter.BodySiteIds.Select(id => LabelFor(Issue76FacetAxis.BodySite, id)));
            labels.AddRange(filter.ThemeIds.Select(id => LabelFor(Issue76FacetAxis.Theme, id)));
            return labels.Count == 0 ? "条件なし" : "適用中: " + string.Join(" × ", labels);
        }
    }

    public Issue76BrowsePrototypeViewModel(ICatalog catalog, SpecialBrowseV2Index index)
    {
        this.catalog = catalog;
        this.index = index;
        search = new SearchEngine(catalog);

        foreach (var (id, label) in KindDefinitions) KindOptions.Add(new(Issue76FacetAxis.Kind, id, label));
        foreach (var (id, label) in BodyDefinitions) BodyOptions.Add(new(Issue76FacetAxis.BodySite, id, label));
        foreach (var (id, label) in ThemeDefinitions) ThemeOptions.Add(new(Issue76FacetAxis.Theme, id, label));

        Navigation =
        [
            new("v2:kinds", "種類から探す", KindDefinitions.Select(item => new NavigationNode("v2:kind:" + item.Id, item.Label, [])).ToArray()),
            new("v2:body", "部位から探す", BodyDefinitions.Select(item => new NavigationNode("v2:body:" + item.Id, item.Label, [])).ToArray()),
            new("v2:themes", "テーマから探す", ThemeDefinitions.Select(item => new NavigationNode("v2:theme:" + item.Id, item.Label, [])).ToArray())
        ];

        ToggleFacet = new(parameter =>
        {
            if (parameter is not Issue76FacetOptionViewModel option) return;
            filter = option.Axis switch
            {
                Issue76FacetAxis.Kind => filter.WithKind(filter.KindId == option.Id ? null : option.Id),
                Issue76FacetAxis.BodySite => filter.ToggleBodySite(option.Id),
                Issue76FacetAxis.Theme => filter.ToggleTheme(option.Id),
                _ => filter
            };
            Refresh();
        });
        ClearFacets = new(_ => { filter = filter.Clear(); Refresh(); }, _ => !filter.IsEmpty);
        Refresh();
    }

    public void StartFromTree(string key)
    {
        var parts = key.Split(':', 3);
        if (parts.Length != 3 || parts[0] != "v2") return;
        query = "";
        Notify(nameof(Query));
        Notify(nameof(IsSearching));
        filter = parts[1] switch
        {
            "kind" => SpecialBrowseV2Filter.Empty.WithKind(parts[2]),
            "body" => SpecialBrowseV2Filter.Empty.ToggleBodySite(parts[2]),
            "theme" => SpecialBrowseV2Filter.Empty.ToggleTheme(parts[2]),
            _ => SpecialBrowseV2Filter.Empty
        };
        Refresh();
    }

    private void Refresh()
    {
        IEnumerable<CatalogEntry> source;
        if (IsSearching)
        {
            source = search.Search(Query).Select(hit => hit.Entry);
            source = index.IntersectInInputOrder(source, filter);
        }
        else
        {
            source = index.IntersectInInputOrder(catalog.Entries.Where(entry => entry.IsSpecial), filter);
            source = SortIndex == 1
                ? source.OrderBy(entry => entry.Label, StringComparer.Create(CultureInfo.GetCultureInfo("ja-JP"), false))
                : source.OrderByDescending(entry => entry.Usage);
        }

        // The accepted catalog can contain multiple Special rows that resolve to the
        // same canonical prompt identity (for example a canonical row plus an alias
        // row). Browse must show one discovery result per canonical identity, just as
        // SearchEngine already does, while semantic-only rows remain distinct by ID.
        source = DistinctPromptIdentities(source);

        Results = source.Select(entry => new Issue76BrowseRowViewModel(entry)).ToArray();
        RefreshOptions();
        Notify(nameof(ResultSummary));
        Notify(nameof(HasFacets));
        Notify(nameof(AppliedSummary));
        ClearFacets.Refresh();
    }

    private void RefreshOptions()
    {
        foreach (var option in KindOptions)
        {
            option.Selected = filter.KindId == option.Id;
            option.Count = VisibleCount(filter.WithKind(option.Id));
        }
        foreach (var option in BodyOptions)
        {
            option.Selected = filter.BodySiteIds.Contains(option.Id);
            var next = option.Selected ? filter : filter.ToggleBodySite(option.Id);
            option.Count = VisibleCount(next);
        }
        foreach (var option in ThemeOptions)
        {
            option.Selected = filter.ThemeIds.Contains(option.Id);
            var next = option.Selected ? filter : filter.ToggleTheme(option.Id);
            option.Count = VisibleCount(next);
        }
    }

    private int VisibleCount(SpecialBrowseV2Filter candidate)
        => DistinctPromptIdentities(index.IntersectInInputOrder(
            catalog.Entries.Where(entry => entry.IsSpecial), candidate)).Count();

    private static IReadOnlyList<CatalogEntry> DistinctPromptIdentities(IEnumerable<CatalogEntry> entries)
    {
        var seen = new HashSet<string>(StringComparer.Ordinal);
        var output = new List<CatalogEntry>();
        foreach (var entry in entries)
        {
            var key = entry.Canonical is { Length: > 0 } canonical ? "C:" + canonical : "S:" + entry.Id;
            if (seen.Add(key)) output.Add(entry);
        }
        return output;
    }

    private static string LabelFor(Issue76FacetAxis axis, string id)
    {
        var source = axis switch
        {
            Issue76FacetAxis.Kind => KindDefinitions,
            Issue76FacetAxis.BodySite => BodyDefinitions,
            Issue76FacetAxis.Theme => ThemeDefinitions,
            _ => []
        };
        return source.FirstOrDefault(item => item.Id == id).Label ?? id;
    }
}
