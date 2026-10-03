using System.Collections.ObjectModel;
using System.IO;
using System.Text.Json;
using DanbooruTagTool.Core;
using DanbooruTagTool.Data;
namespace DanbooruTagTool.App.ViewModels;
public sealed class PersonalRulesViewModel : Observable
{
    private readonly MainViewModel main; private readonly PersonalRuleStore store; private readonly PersonalRuleEvaluator evaluator; private PersonalRules rules=PersonalRules.Empty;
    private string status="UserDataの個人設定です。モデル変更でPromptを書き換えません。";
    public string Status {get=>status;private set=>Set(ref status,value);}
    public string ModelName {get;set;}=""; public string ModelHash {get;set;}=""; public string Family {get;set;}="";
    public bool Global {get;set;}=true; public string Trigger {get;set;}=""; public string Positive {get;set;}=""; public string Negative {get;set;}=""; public string PreferredPreset {get;set;}=""; public string Warning {get;set;}=""; public string Note {get;set;}="";
    public string Token {get;set;}=""; public PersonalSeverity Severity {get;set;}=PersonalSeverity.Warn; public IReadOnlyList<PersonalSeverity> Severities=>Enum.GetValues<PersonalSeverity>(); public string Replacement {get;set;}="";
    public PersonalModelKey Active=>new(main.Create.Model,main.Create.ModelHash);
    public string ActiveIdentity=>$"現在Model: {Active.Name} [{Active.Hash}]。hashがあるルールはhash完全一致のみ。";
    public ObservableCollection<PersonalHint> Hints {get;}=[]; public ObservableCollection<PersonalExclusion> Exclusions {get;}=[];
    public PersonalHint? SelectedHint {get;set;} public PersonalExclusion? SelectedRule {get;set;}
    public RelayCommand CaptureModel {get;} public RelayCommand AddHint {get;} public RelayCommand AddRule {get;} public RelayCommand DeleteHint {get;} public RelayCommand DeleteRule {get;} public RelayCommand Reload {get;} public RelayCommand ApplyPositive {get;} public RelayCommand ApplyNegative {get;} public RelayCommand ApplyPreset {get;}
    private PersonalModelKey DraftKey=>Global ? new() : new(ModelName.Trim(),ModelHash.Trim(),Family.Trim());
    public PersonalRulesViewModel(MainViewModel main,ICatalog catalog,PortablePaths paths)
    {
        this.main=main; store=new(paths.Root); evaluator=new(catalog);
        CaptureModel=new(_=> {ModelName=main.Create.Model;ModelHash=main.Create.ModelHash;Global=false;Notify(nameof(ModelName));Notify(nameof(ModelHash));Notify(nameof(Global));});
        AddHint=new(_=>Guard(()=>{var key=DraftKey; ValidateScope(key); Save(rules with {Hints=rules.Hints.Append(new PersonalHint(Guid.NewGuid(),key,Trigger,Positive,Negative,PreferredPreset,Warning,Note)).ToArray()});}));
        AddRule=new(_=>Guard(()=>{var key=DraftKey; ValidateScope(key); Save(rules with {Exclusions=rules.Exclusions.Append(new PersonalExclusion(Guid.NewGuid(),Token.Trim(),Severity,key,Replacement,Note)).ToArray()});}));
        DeleteHint=new(_=>Guard(()=>{if(SelectedHint is {} h)Save(rules with {Hints=rules.Hints.Where(x=>x.Id!=h.Id).ToArray()});}));
        DeleteRule=new(_=>Guard(()=>{if(SelectedRule is {} r)Save(rules with {Exclusions=rules.Exclusions.Where(x=>x.Id!=r.Id).ToArray()});}));
        Reload=new(_=>Guard(()=>{rules=store.Load();Refresh();}));
        ApplyPositive=new(_=>{if(SelectedHint is {} h && h.Model.Matches(Active))main.Workspace.AppendText(string.Join(", ",new[]{h.Trigger,h.Positive}.Where(s=>!string.IsNullOrWhiteSpace(s))));},_=>main.CreateEditingAvailable);
        ApplyNegative=new(_=>{if(SelectedHint is {} h && h.Model.Matches(Active))main.NegativeWorkspace.AppendText(h.Negative);},_=>main.CreateEditingAvailable);
        ApplyPreset=new(_=>{if(SelectedHint is {} h && h.Model.Matches(Active)){var matches=main.Presets.Where(p=>p.Name==h.PreferredPreset).ToArray(); if(matches.Length==1)main.Create.Load(matches[0],"個人設定から明示Preset適用");else Status="推奨Preset名に完全一致する保存Presetを1つ用意してください。";}},_=>main.CreateEditingAvailable);
        main.Workspace.CanAddItem=CanAdd;main.NegativeWorkspace.CanAddItem=CanAdd; main.Dictionary.PersonalVisible=e=>!evaluator.Hidden(rules,Active,e);
        main.Intelligence.PersonalWarnings=()=>evaluator.Warnings(rules,Active,main.Workspace,main.NegativeWorkspace);
        main.Create.PropertyChanged+=(_,e)=>{if(e.PropertyName is nameof(CreateViewModel.Model) or nameof(CreateViewModel.ModelHash))Refresh();};
        main.PropertyChanged+=(_,_)=>{ApplyPositive.Refresh();ApplyNegative.Refresh();ApplyPreset.Refresh();}; Guard(()=>{rules=store.Load();Refresh();});
    }
    private void ValidateScope(PersonalModelKey key){if(!Global && key.Name.Length==0 && key.Hash.Length==0)throw new ArgumentException("モデル固有ルールは名前またはhashを指定してください。familyのみは未解決なので適用しません。");}
    private bool CanAdd(PromptItem item)
    {
        var matches=evaluator.Matching(rules,Active,item); if(matches.Any(r=>r.Severity==PersonalSeverity.BlockAdd)){main.Status=Status="個人block-add: "+string.Join(" / ",matches.Where(r=>r.Severity==PersonalSeverity.BlockAdd).Select(r=>r.Token+" → "+r.Replacement+" "+r.Note));return false;}
        if(matches.Any(r=>r.Severity==PersonalSeverity.Warn))main.Status=Status="個人warn: "+string.Join(" / ",matches.Select(r=>r.Token+" "+r.Note));return true;
    }
    private void Save(PersonalRules next){store.Save(next);rules=next;Refresh();Status="個人ルールを保存しました。Prompt/catalogは書き換えていません。";}
    private void Refresh(){Hints.Clear();foreach(var h in rules.Hints.Where(h=>h.Model.Matches(Active)))Hints.Add(h);Exclusions.Clear();foreach(var r in rules.Exclusions)Exclusions.Add(r);Notify(nameof(ActiveIdentity));main.Intelligence.Refresh();main.Dictionary.RefreshResults();}
    private void Guard(Action action){try{action();}catch(Exception e)when(e is IOException or ArgumentException or UnauthorizedAccessException or JsonException){Status=e.Message;}}
}
