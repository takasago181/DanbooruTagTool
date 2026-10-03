using System.Diagnostics;
using System.IO;
using System.Text.Json;
using DanbooruTagTool.Core;
using Xunit;
namespace DanbooruTagTool.Tests;
[Collection("Workstation performance")]
public sealed class PersonalRulePerformanceTests
{
    [Issue254PerformanceFact]
    public void MeasureRepeatedPersonalFiltering()
    {
        var catalog=Fixtures.Catalog(); var evaluator=new PersonalRuleEvaluator(catalog);
        var entries=catalog.Entries.ToArray(); var active=new PersonalModelKey("test","abc");
        var rules=new PersonalRules(1,[],Enumerable.Range(0,256).Select(i=>new PersonalExclusion(Guid.NewGuid(),i==0 ? "azure_locks" : "unmatched_"+i,PersonalSeverity.Hide,new())).ToArray());
        int Filter(){var hidden=0;for(var i=0;i<2000;i++)if(evaluator.Hidden(rules,active,entries[i%entries.Length]))hidden++;return hidden;}
        for(var i=0;i<3;i++)Filter(); var samples=new List<object>();
        for(var i=0;i<11;i++){var before=GC.GetAllocatedBytesForCurrentThread();var timer=Stopwatch.StartNew();var hidden=Filter();timer.Stop();samples.Add(new {ms=timer.Elapsed.TotalMilliseconds,allocatedBytes=GC.GetAllocatedBytesForCurrentThread()-before,hidden});}
        File.WriteAllText(Path.ChangeExtension(Environment.GetEnvironmentVariable("DTT_PERF_REPORT")!,".personal.json"),JsonSerializer.Serialize(samples));
    }
}
