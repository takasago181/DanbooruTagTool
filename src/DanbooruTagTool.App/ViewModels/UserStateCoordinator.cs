using DanbooruTagTool.Core;
using DanbooruTagTool.Data;

namespace DanbooruTagTool.App.ViewModels;

/// <summary>
/// The single App-side owner of UserState load/snapshot/save wiring. It does
/// not change save timing; callers still invoke Persist at the same UI events.
/// </summary>
public sealed class UserStateCoordinator(IUserStateStore store) : Observable
{
    public UiState Ui { get; private set; } = new();
    public UserState? Load()
    {
        var state = store.Load();
        if (state != null) Ui = state.Ui;
        return state;
    }
    public void SaveUi(UiState value) => Ui = value;
    public void Persist(PromptWorkspace workspace, DictionaryWorkspaceViewModel dictionary, PromptEditorViewModel prompt,
        GenerationPresetsViewModel presets, ForgeViewModel forge)
    {
        Ui = Ui with
        {
            Workspace = prompt.WorkspaceIndex,
            Browse = dictionary.BrowseKey,
            Query = dictionary.Query,
            SelectedEntry = dictionary.SelectedEntry?.Entry.Id,
            BrowseScroll = dictionary.Query.Length == 0 ? dictionary.BrowseScroll : dictionary.RestoreScroll,
            BrowseScope = dictionary.Scope.ToString(),
            BrowsePrimaryRoute = dictionary.PrimaryRouteId,
            BrowseLocalSubroute = dictionary.LocalSubrouteId,
            BrowseBodySites = dictionary.BodySiteIds.OrderBy(value => value, StringComparer.Ordinal).ToArray(),
            BrowseThemes = dictionary.ThemeIds.OrderBy(value => value, StringComparer.Ordinal).ToArray(),
            BrowseDeepOnly = dictionary.DeepOnly,
            ContentIntent = dictionary.ContentIntent.ToString(),
            EnglishChips = prompt.EnglishChips,
            OutputProfile = prompt.OutputProfile,
            ForgeUrl = forge.ForgeUrl,
            ForgeExtensionPath = forge.ForgeExtensionPath
        };
        store.Save(new(workspace.Snapshot(), Ui, presets.Presets.ToArray()));
    }
}
