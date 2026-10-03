using System.Collections.ObjectModel;
using System.IO;
using System.Text.Json;
using DanbooruTagTool.Core;
using DanbooruTagTool.Data;

namespace DanbooruTagTool.App.ViewModels;

public sealed class RegionComposerViewModel : Observable
{
    private readonly MainViewModel main;
    private readonly string presetsPath;
    private bool busy;
    private string common="", subjectA="", subjectB="", commonNegative="", negativeA="", negativeB="", ratios="1,1", status="生成条件はCreateの「生成条件 / Preset」を使用します。";
    private RegionLayout layout;
    public RegionComposerConfig? RestoredRegional { get; private set; }
    public string Common { get=>common; set { Set(ref common,value); Changed(); } }
    public string SubjectA { get=>subjectA; set { Set(ref subjectA,value); Changed(); } }
    public string SubjectB { get=>subjectB; set { Set(ref subjectB,value); Changed(); } }
    public string CommonNegative { get=>commonNegative; set { Set(ref commonNegative,value); Changed(); } }
    public string NegativeA { get=>negativeA; set { Set(ref negativeA,value); Changed(); } }
    public string NegativeB { get=>negativeB; set { Set(ref negativeB,value); Changed(); } }
    public string Ratios { get=>ratios; set { Set(ref ratios,value); Changed(); } }
    public RegionLayout Layout { get=>layout; set { Set(ref layout,value); Changed(); } }
    public IReadOnlyList<RegionLayout> Layouts { get; } = Enum.GetValues<RegionLayout>();
    public string Status { get=>status; private set=>Set(ref status,value); }
    public bool CanEdit => !busy && main.CreateEditingAvailable;
    public string Name { get; set; } = "";
    public ObservableCollection<RegionPreset> Presets { get; } = [];
    private RegionPreset? selectedPreset;
    public RegionPreset? SelectedPreset { get=>selectedPreset; set { Set(ref selectedPreset,value); Load?.Refresh(); } }
    public RegionComposerConfig Config => new(Common,SubjectA,SubjectB,CommonNegative,NegativeA,NegativeB,Layout,Ratios);
    public string Preview { get { try { var c=RegionComposer.Compile(Config); return $"{RegionComposer.MatrixMode(Config)} /ratio {Ratios}\nP: {c.Positive}\nN: {c.Negative}"; } catch(ArgumentException e) { return e.Message; } } }
    public RelayCommand Save { get; }
    public RelayCommand Load { get; }
    public RelayCommand ReturnToOrdinary { get; }
    public AsyncRelayCommand Detect { get; }
    public AsyncRelayCommand Generate { get; }
    public AsyncRelayCommand Compare { get; }
    public RegionComposerViewModel(MainViewModel main, PortablePaths paths)
    {
        this.main=main; presetsPath=Path.Combine(paths.Root,"UserData","region-composer-presets.json");
        Save=new(_=>Guard(()=>
        {
            RegionComposer.Validate(Config);
            if(string.IsNullOrWhiteSpace(Name)) throw new ArgumentException("preset名を指定してください。");
            Directory.CreateDirectory(Path.GetDirectoryName(presetsPath)!);
            var fresh=ReadPresets().Append(new RegionPreset(Guid.NewGuid(),Name.Trim(),Config)).ToArray();
            var temp=presetsPath+"."+Guid.NewGuid().ToString("N")+".tmp";
            File.WriteAllText(temp,JsonSerializer.Serialize(fresh)); File.Move(temp,presetsPath,true);
            Reload(); Status="新しいcomposer presetを保存しました。";
        }),_=>CanEdit);
        Load=new(_=>Guard(()=> { if(SelectedPreset is { } p) { Restore(p.Config); Status="composer presetを復元しました。生成条件は現在のCreate条件です。"; } }),_=>CanEdit && SelectedPreset is not null);
        ReturnToOrdinary=new(_=> { RestoredRegional=null; main.Create.ReleaseRegionalEvidence(); main.CreatePageIndex=0; main.Create.Refresh(); Status="通常modeへ戻しました。元のregional条件は未適用の証拠として保持します。"; },_=>CanEdit);
        Detect=new(async _=>await Run(async()=> { var capability=await main.Forge.ReadRegionalCapabilitiesAsync(); Status=$"確認済み: {capability.Repository}\n{capability.Commit} / {capability.Contract}。生成時も再確認します。"; }),_=>CanEdit);
        Generate=new(async _=>await Run(async()=>
        {
            var config=Config; var compiled=RegionComposer.Compile(config);
            if(!main.Create.TryRecipe(out var r,out var error)) throw new ArgumentException(error);
            if(r is not {Model:not null,ModelHash:not null,Seed:>=0,Steps:not null,Sampler:not null,Scheduler:not null,Cfg:not null,Width:not null,Height:not null}) throw new ArgumentException("Create生成条件の全項目とModel hashを指定してください。");
            var parent=GenerationRecipeDerivation.Read(r.SourceParameters);
            r=GenerationRecipeDerivation.Strip(r) with { Regional=config };
            if(parent is not null) r=GenerationRecipeDerivation.With(r,GenerationRecipeDerivation.Build(parent.Parent,new(compiled.Positive,compiled.Negative,r),parent.Source,parent.ParentImageSha256));
            await main.Forge.GenerateRecipeAsync(new(Guid.NewGuid(),"Region Composer","verified regional",compiled.Positive,compiled.Negative,r),allowDerivative:main.Create.AllowDerivative);
            Status=main.Forge.RecipeStatus;
        }),_=>CanEdit);
        Compare=new(async _=>await Run(async()=> { await main.Experiments!.LoadRegionalComparisonAsync(Config); main.CreatePageIndex=4; Status=main.Experiments.Status; }),_=>CanEdit);
        try { Reload(); } catch(Exception e) when(e is IOException or JsonException or InvalidDataException) { Status="presetを読めません: "+e.Message; }
        main.Forge.PropertyChanged+=(_,_)=>Changed();
    }
    public void Restore(RegionComposerConfig? c)
    {
        RestoredRegional=c;
        if(c is not null) { RegionComposer.Validate(c); Common=c.Common; SubjectA=c.SubjectA; SubjectB=c.SubjectB; CommonNegative=c.CommonNegative; NegativeA=c.NegativeA; NegativeB=c.NegativeB; Layout=c.Layout; Ratios=c.Ratios; }
        main.Create.Refresh(); Changed();
    }
    private RegionPreset[] ReadPresets()
    {
        if(!File.Exists(presetsPath)) return [];
        if(new FileInfo(presetsPath).Length>4*1024*1024) throw new InvalidDataException("preset上限超過。");
        var list=JsonSerializer.Deserialize<RegionPreset[]>(File.ReadAllText(presetsPath)) ?? throw new InvalidDataException("preset不正。");
        foreach(var p in list) RegionComposer.Validate(p.Config);
        return list;
    }
    private void Reload() { Presets.Clear(); foreach(var p in ReadPresets()) Presets.Add(p); }
    private void Changed() { Notify(nameof(Preview)); Notify(nameof(CanEdit)); Save?.Refresh(); Load?.Refresh(); Detect?.Refresh(); Generate?.Refresh(); Compare?.Refresh(); ReturnToOrdinary?.Refresh(); }
    private void Guard(Action action) { try { action(); } catch(Exception e) when(e is IOException or ArgumentException or InvalidDataException or JsonException) { Status=e.Message; } }
    private async Task Run(Func<Task> action)
    {
        busy=true; Changed();
        try { await action(); }
        catch(Exception e) when(e is IOException or ArgumentException or InvalidDataException or JsonException or System.Net.Http.HttpRequestException or InvalidOperationException or OperationCanceledException or KeyNotFoundException) { Status=e.Message; }
        finally { busy=false; Changed(); }
    }
}
public sealed record RegionPreset(Guid Id,string Name,RegionComposerConfig Config);

