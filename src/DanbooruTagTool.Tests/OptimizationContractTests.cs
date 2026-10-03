using System.IO;
using System.Text.Json;
using DanbooruTagTool.Core;
using DanbooruTagTool.Data;
using Xunit;
namespace DanbooruTagTool.Tests;
public sealed class OptimizationContractTests
{
    [Fact]
    public void ReplacedPersonalRuleUsesNewTokenAndScopeWithoutChangingRawPrompt()
    {
        var evaluator=new PersonalRuleEvaluator(Fixtures.Catalog());var p=Fixtures.Workspace();p.Replace("(blue_hair:1.2), raw token");
        var original=new PersonalExclusion(Guid.NewGuid(),"azure_locks",PersonalSeverity.Hide,new());
        Assert.True(evaluator.Matches(original,p.Items[0]));
        var replaced=original with {Token="raw_token",Model=new("same","abc")};
        Assert.False(evaluator.Matches(replaced,p.Items[0]));Assert.True(evaluator.Matches(replaced,p.Items[1]));
        var rules=new PersonalRules(1,[],[replaced]);Assert.Empty(evaluator.Matching(rules,new("same","different"),p.Items[1]));
        Assert.Single(evaluator.Matching(rules,new("renamed","ABC"),p.Items[1]));Assert.Equal("(blue_hair:1.2), raw token",p.English);
    }
    [Fact]
    public void SharedAtomicWriterRetainsDomainBackupAndRefusesInvalidReplacement()
    {
        using var directory=new TempDirectory();var store=new TemplateStore(directory.Path);var original=new TemplateDocument(Source:"{red|blue}");store.Save(original);store.Save(original with {Source="{green|blue}"});
        var path=Path.Combine(directory.Path,"UserData","Templates","workspace.json");Assert.Equal(original,JsonSerializer.Deserialize<TemplateDocument>(File.ReadAllText(path+".bak")));
        var bytes=File.ReadAllBytes(path);Assert.Throws<ArgumentException>(()=>store.Save(original with {Cap=999}));Assert.Equal(bytes,File.ReadAllBytes(path));Assert.Empty(Directory.GetFiles(Path.GetDirectoryName(path)!,"*.tmp"));
        var personal=new PersonalRuleStore(directory.Path);personal.Save(PersonalRules.Empty);personal.Save(new(1,[new(Guid.NewGuid(),new(),Warning:"personal")],[]));
        var personalPath=Path.Combine(directory.Path,"UserData","PersonalRules","rules.json");Assert.Empty(JsonSerializer.Deserialize<PersonalRules>(File.ReadAllText(personalPath+".bak"),PersonalRuleStore.Options)!.Hints);
    }
}