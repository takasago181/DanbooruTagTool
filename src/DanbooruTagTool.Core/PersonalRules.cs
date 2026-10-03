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
    private readonly PromptParser parser = new(catalog);
    // Exclusion records are immutable. Weak keys keep deleted/reloaded rules from
    // becoming a second retained settings store; catalog identity is read-only.
    private readonly System.Runtime.CompilerServices.ConditionalWeakTable<PersonalExclusion, MatchToken> tokens = new();
    private sealed record MatchToken(string? Canonical, string Surface);
    private static string Normalize(string value) => value.Trim().Replace(' ', '_');
    private MatchToken Token(PersonalExclusion rule)
    {
        if (tokens.TryGetValue(rule, out var cached)) return cached;
        return tokens.GetValue(rule, r =>
        {
            var parsed = parser.Parse(r.Token);
            return new(parsed.Length == 1 ? parsed[0].Canonical : null, Normalize(r.Token));
        });
    }
    private bool Matches(PersonalExclusion rule, string? canonical, string surface)
    {
        var token = Token(rule);
        return token.Canonical is not null && canonical is not null
            ? token.Canonical == canonical
            : string.Equals(token.Surface, surface, StringComparison.OrdinalIgnoreCase);
    }
    public bool Matches(PersonalExclusion rule, PromptItem item) =>
        Matches(rule, item.Canonical, Normalize(item.Canonical ?? item.StructuredName ?? item.Surface));
    public IReadOnlyList<PersonalExclusion> Matching(PersonalRules rules, PersonalModelKey active, PromptItem item)
    {
        var surface = Normalize(item.Canonical ?? item.StructuredName ?? item.Surface);
        var result = new List<PersonalExclusion>();
        foreach (var rule in rules.Exclusions)
            if (rule.Model.Matches(active) && Matches(rule, item.Canonical, surface)) result.Add(rule);
        return result;
    }
    public PromptWarning[] Warnings(PersonalRules rules,PersonalModelKey active,PromptWorkspace positive,PromptWorkspace negative)
    {
        var warnings=rules.Hints.Where(h=>h.Model.Matches(active) && h.Warning.Length>0).Select(h=>new PromptWarning("Model","personal-hint",h.Warning+" / "+h.Note)).ToList();
        foreach(var (side,workspace) in new[]{("Positive",positive),("Negative",negative)})
            foreach(var item in workspace.Items) foreach(var rule in Matching(rules,active,item).Where(r=>r.Severity is PersonalSeverity.Warn or PersonalSeverity.BlockAdd))
                warnings.Add(new(side,"personal-"+rule.Severity,$"{side}: {rule.Token} [{rule.Severity}] {rule.Note} /置換案 {rule.Replacement}（既存Promptは保持）"));
        return warnings.ToArray();
    }
    public bool Hidden(PersonalRules rules, PersonalModelKey active, CatalogEntry entry)
    {
        var surface = Normalize(entry.EffectivePromptToken ?? entry.English);
        foreach (var rule in rules.Exclusions)
            if (rule.Severity == PersonalSeverity.Hide && rule.Model.Matches(active) && Matches(rule, entry.EffectivePromptToken, surface)) return true;
        return false;
    }
}
