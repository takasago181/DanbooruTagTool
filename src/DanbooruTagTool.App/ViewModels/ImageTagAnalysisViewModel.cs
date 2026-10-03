using System.Collections.ObjectModel;
using System.IO;
using System.Text.Json;
using DanbooruTagTool.Core;
using DanbooruTagTool.Data;
namespace DanbooruTagTool.App.ViewModels;
public sealed class PredictedTagRow(TagComparison value) : Observable
{
    public TagComparison Value => value; public string Label => $"{value.Tag}  {value.Confidence:P1}  {value.Observation}";
    private bool selected; public bool Selected { get => selected; set => Set(ref selected,value); }
}
public sealed class ImageTagAnalysisViewModel : Observable
{
    private readonly MainViewModel main; private readonly ImageTagAnalysisStore store; private readonly LocalTaggerClient client;
    private TaggerProfile? profile; private TagAnalysis? result; private bool busy; private double threshold=.35; private string filter="", status="明示Setup/解析のみ。起動時にモデルを読み込み/ダウンロードしません。";
    public string ForgeRoot { get; set; } = "";
    public bool Busy { get => busy; private set { Set(ref busy,value); Setup.Refresh(); Analyze.Refresh(); AddSelected.Refresh(); Reopen.Refresh(); } }
    public double Threshold { get => threshold; set { Set(ref threshold,value); RefreshRows(); } }
    public string Filter { get => filter; set { Set(ref filter,value); RefreshRows(); } }
    public string Status { get => status; private set => Set(ref status,value); }
    public string Provenance => result is null ? profile is null ? "未設定" : $"{profile.ModelName} / {profile.Revision} / {profile.ModelSha256}" : $"Library {result.LibraryImageId} / image {result.ImageSha256}\n{result.AnalyzedUtc:O}\n{result.Model.ModelSource} @ {result.Model.Revision}\nmodel {result.Model.ModelSha256}\nlabels {result.Model.TagsSha256}\n{result.Model.Implementation} @ {result.Model.ImplementationCommit}\n{result.Model.License}";
    public ObservableCollection<PredictedTagRow> Rows { get; } = [];
    public AsyncRelayCommand Setup { get; } public AsyncRelayCommand Analyze { get; } public AsyncRelayCommand Reopen { get; } public RelayCommand AddSelected { get; }
    public ImageTagAnalysisViewModel(MainViewModel main,PortablePaths paths,LocalTaggerClient? client=null)
    {
        this.main=main; store=new(paths.Root); this.client=client ?? new();
        Setup=new(_ => Run(async () => { profile=await ImageTagAnalysisStore.DiscoverMoatAsync(ForgeRoot); store.SaveProfile(profile); Notify(nameof(Provenance)); Status="既存MOAT v2 cacheを設定しました。モデル取得/生成なし。"; }),_=>!Busy);
        Analyze=new(_ => Run(async () => { var image=main.GenerationLibrary!.Selected!.Image; result=null; RefreshRows(); var analyzed=await this.client.AnalyzeAsync(main.Forge.ForgeUrl,image.Id,image.NormalizedPath,profile!); store.SaveResult(analyzed); if(main.GenerationLibrary.Selected?.Image.Id==image.Id) { result=analyzed; RefreshRows(); Status="解析証拠を保存。選択して追加するまでPromptは変わりません。"; } }),_=>!Busy && profile is not null && main.GenerationLibrary?.Selected is not null && !main.Forge.RecipeBusy);
        Reopen=new(_=>Run(async()=> { var path=main.GenerationLibrary!.SelectedPath; result=store.Latest(await LocalTaggerClient.HashAsync(path)); RefreshRows(); Status=result is null ? "保存結果なし" : "同じ画像SHA256の保存証拠を開きました。推論なし。"; }),_=>!Busy && main.GenerationLibrary?.Selected is not null);
        AddSelected=new(_ => { var tags=Rows.Where(r=>r.Selected && r.Value.Confidence is not null).Select(r=>r.Value.Tag).ToArray(); if(tags.Length==0)return; main.Workspace.AppendText(string.Join(", ",tags)); Status="選択したタグだけをPositiveへ追加しました。Undo可能。"; },_=>!Busy && main.CreateEditingAvailable && result is not null);
        main.GenerationLibrary!.PropertyChanged += (_,e)=> { if(e.PropertyName==nameof(GenerationLibraryViewModel.Selected)) { result=null; RefreshRows(); Analyze.Refresh(); Reopen.Refresh(); } };
        main.Workspace.Changed+=RefreshRows; main.Forge.PropertyChanged+=(_,_)=>Analyze.Refresh(); main.PropertyChanged+=(_,_)=>AddSelected.Refresh();
        try { profile=store.LoadProfile(); } catch(Exception e) when(e is IOException or JsonException) {Status=e.Message;}
    }
    private void RefreshRows() { Rows.Clear(); if(result is not null) foreach(var row in ImageTagDiagnostics.Compare(result,main.Workspace,Threshold,Filter)) Rows.Add(new(row)); Notify(nameof(Provenance)); }
    private async Task Run(Func<Task> action) { Busy=true; try { await action(); } catch(Exception e) when(e is IOException or UnauthorizedAccessException or ArgumentException or InvalidOperationException or JsonException or System.Net.Http.HttpRequestException or OperationCanceledException or KeyNotFoundException) { Status="解析/設定失敗: "+e.Message; } finally {Busy=false;} }
}
