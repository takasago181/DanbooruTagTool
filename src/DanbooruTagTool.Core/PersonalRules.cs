namespace DanbooruTagTool.Core;
public enum PersonalSeverity { Hide, Warn, BlockAdd }
public sealed record PersonalModelKey(string Name="",string Hash="",string Family="")
{
    public bool Matches(PersonalModelKey active) => Hash.Length>0 ? string.Equals(Hash,active.Hash,StringComparison.OrdinalIgnoreCase) : Name.Length>0 ? string.Equals(Name,active.Name,StringComparison.OrdinalIgnoreCase) : Family.Length>0 ? string.Equals(Family,active.Family,StringComparison.OrdinalIgnoreCase) : true;
}
public sealed record PersonalHint(Guid Id,PersonalModelKey Model,string Trigger="",string Positive="",string Negative="",string PreferredPreset="",string Warning="",string Note="");
public sealed record PersonalExclusion(Guid Id,string Token,PersonalSeverity Severity,PersonalModelKey Model,string Replacement="",string Note="");
public sealed record PersonalRules(int Version,IReadOnlyList<PersonalHint> Hints,IReadOnlyList<PersonalExclusion> Exclusions)
{
    public static PersonalRules Empty => new(1,[],[]);
    public void Validate()
    {
        if (Hints is null || Exclusions is null || Hints.Any(h => h is null) || Exclusions.Any(r => r is null)) throw new InvalidDataException("個人ルール配列がありません。");
        static bool KeyValid(PersonalModelKey? key) => key is not null && new[] {key.Name,key.Hash,key.Family}.All(s => s is {Length: <= 600});
        if(Version!=1 || Hints.Count>256 || Exclusions.Count>2048 || Hints.Select(h=>h.Id).Concat(Exclusions.Select(r=>r.Id)).Distinct().Count()!=Hints.Count+Exclusions.Count ||
            Hints.Any(h=>h.Id==Guid.Empty || !KeyValid(h.Model) || new[]{h.Trigger,h.Positive,h.Negative,h.PreferredPreset,h.Warning,h.Note}.Any(s=>s is null || s.Length>4000)) ||
            Exclusions.Any(r=>r.Id==Guid.Empty || !KeyValid(r.Model) || string.IsNullOrWhiteSpace(r.Token) || r.Token.Length>200 || r.Note is null || r.Note.Length>4000 || r.Replacement is null || r.Replacement.Length>4000 || !Enum.IsDefined(r.Severity))) throw new InvalidDataException("個人ルールversion/件数/値が不正です。");
    }
}
public sealed class PersonalRuleEvaluator(ICatalog catalog)
{
    private readonly PromptParser parser=new(catalog);
    public bool Matches(PersonalExclusion rule,PromptItem item)
    {
        var parsed=parser.Parse(rule.Token);
        if(parsed.Length==1 && parsed[0].Canonical is { } canonical && item.Canonical is not null) return canonical==item.Canonical;
        static string Normalize(string s)=>s.Trim().Replace(' ','_');
        return string.Equals(Normalize(rule.Token),Normalize(item.Canonical ?? item.StructuredName ?? item.Surface),StringComparison.OrdinalIgnoreCase);
    }
    public IReadOnlyList<PersonalExclusion> Matching(PersonalRules rules,PersonalModelKey active,PromptItem item) => rules.Exclusions.Where(r=>r.Model.Matches(active) && Matches(r,item)).ToArray();
    public PromptWarning[] Warnings(PersonalRules rules,PersonalModelKey active,PromptWorkspace positive,PromptWorkspace negative)
    {
        var warnings=rules.Hints.Where(h=>h.Model.Matches(active) && h.Warning.Length>0).Select(h=>new PromptWarning("Model","personal-hint",h.Warning+" / "+h.Note)).ToList();
        foreach(var (side,workspace) in new[]{("Positive",positive),("Negative",negative)})
            foreach(var item in workspace.Items) foreach(var rule in Matching(rules,active,item).Where(r=>r.Severity is PersonalSeverity.Warn or PersonalSeverity.BlockAdd))
                warnings.Add(new(side,"personal-"+rule.Severity,$"{side}: {rule.Token} [{rule.Severity}] {rule.Note} /置換案 {rule.Replacement}（既存Promptは保持）"));
        return warnings.ToArray();
    }
    public bool Hidden(PersonalRules rules,PersonalModelKey active,CatalogEntry entry) => Matching(rules,active,new PromptItem(Guid.Empty,entry.English,entry.EffectivePromptToken,entry.Japanese,PromptItemKind.Normal)).Any(r=>r.Severity==PersonalSeverity.Hide);
}
