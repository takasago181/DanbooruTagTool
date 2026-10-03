using System.Collections.ObjectModel;
using System.IO;
using System.Text.Json;
using DanbooruTagTool.Core;
using DanbooruTagTool.Data;
namespace DanbooruTagTool.App.ViewModels;
public sealed class TemplateViewModel : Observable
{
    private readonly MainViewModel main; private readonly TemplateStore store;
    private string source = "", externalRoot = "", status = "明示Previewで展開します。生成しません。"; private int cap = 64;
    private TemplatePreview? preview;
    public string Source { get => source; set { Set(ref source, value); Invalidate(); } }
    public string ExternalRoot { get => externalRoot; set { Set(ref externalRoot, value); Invalidate(); } }
    public int Cap { get => cap; set { Set(ref cap, value); Invalidate(); } }
    public string Status { get => status; private set => Set(ref status, value); }
    public ObservableCollection<string> Variants { get; } = [];
    private string? selected;
    public string? Selected { get => selected; set { Set(ref selected, value); Materialize.Refresh(); } }
    public RelayCommand Preview { get; } public RelayCommand Save { get; } public RelayCommand Reload { get; } public RelayCommand Materialize { get; } public AsyncRelayCommand ToExperiment { get; }
    public TemplateViewModel(MainViewModel main, PortablePaths paths)
    {
        this.main = main; store = new(paths.Root);
        Preview = new(_ => Guard(() => { var wildcards = store.ReadWildcards(ExternalRoot); preview = PromptTemplates.Preview(Source, wildcards.Values, Cap); Variants.Clear(); foreach (var v in preview.Variants) Variants.Add(v); Selected = Variants.FirstOrDefault(); Status = $"{preview.Count}候補 /上限{Cap}（seed別の生成数は実験側で確認）。" + (preview.Count > Cap ? "上限超過: materialize/実験不可。" : "") + "\n" + string.Join("\n", preview.Warnings); ToExperiment?.Refresh(); }));
        Save = new(_ => Guard(() => { store.Save(new(1, Source, Cap, ExternalRoot)); Status = "UserDataへ保存しました。"; }));
        Reload = new(_ => Guard(Load));
        Materialize = new(_ => { if (Selected is not null && Variants.Contains(Selected)) { main.Workspace.Replace(Selected); main.CreatePageIndex = 0; } }, _ => main.CreateEditingAvailable && Selected is not null && Variants.Contains(Selected));
        ToExperiment = new(async _ => { try { await main.Experiments!.LoadTemplateVariantsAsync(Variants.ToArray()); if (main.Experiments.TemplateDraftReady) main.CreatePageIndex = 4; else Status = main.Experiments.Status; } catch (ArgumentException e) { Status = e.Message; } }, _ => main.CreateEditingAvailable && main.Experiments?.CanEdit == true && Variants.Count is > 0 and <= 16 && Variants.All(v => !v.Contains('\n') && !v.Contains('\r')));
        main.PropertyChanged += (_, _) => { Materialize.Refresh(); ToExperiment?.Refresh(); }; Guard(Load);
    }
    private void Load() { var d = store.Load(); source = d.Source; cap = d.Cap; externalRoot = d.ExternalRoot; Notify(nameof(Source)); Notify(nameof(Cap)); Notify(nameof(ExternalRoot)); Invalidate(); }
    private void Invalidate() { preview = null; Variants.Clear(); Selected = null; Status = "変更済み。Previewを押してください。"; ToExperiment?.Refresh(); }
    private void Guard(Action action) { try { action(); } catch (Exception e) when (e is IOException or UnauthorizedAccessException or ArgumentException or JsonException) { Status = e.Message; } }
}

