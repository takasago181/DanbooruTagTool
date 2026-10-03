using System.IO;
using System.Net;
using System.Net.Http;
using System.Text.Json;
using DanbooruTagTool.Core;
using DanbooruTagTool.Data;
using DanbooruTagTool.App.ViewModels;
using Xunit;
namespace DanbooruTagTool.Tests;
public sealed class Issue235ImageTagTests
{
    [Fact] public async Task AdapterRecordsSortedConfidenceAndRejectsRemoteOrChangedModel()
    {
        using var d=new TempDirectory(); var profile=await Profile(d.Path); var image=Path.Combine(d.Path,"image.png"); File.WriteAllBytes(image,[1,2,3]); var handler=new Handler(); var client=new LocalTaggerClient(new HttpClient(handler));
        var result=await client.AnalyzeAsync("http://127.0.0.1:7860",42,image,profile);
        Assert.Equal(42,result.LibraryImageId); Assert.Equal("blue_hair",result.Tags[0].Tag); Assert.Equal(.9,result.Tags[0].Confidence); Assert.Equal(profile,result.Model); Assert.Equal(64,result.ImageSha256.Length); Assert.Equal(1,handler.Posts);
        await Assert.ThrowsAsync<ArgumentException>(()=>client.AnalyzeAsync("https://example.com",42,image,profile));
        File.AppendAllText(profile.ModelPath,"changed"); await Assert.ThrowsAsync<InvalidDataException>(()=>client.AnalyzeAsync("http://localhost:7860",42,image,profile)); Assert.Equal(1,handler.Posts);
    }
    [Fact] public async Task ModelAndImageChangeDuringInferenceRejectsEvidence()
    {
        using var d=new TempDirectory(); var profile=await Profile(d.Path); var image=Path.Combine(d.Path,"image.png"); File.WriteAllBytes(image,[1]);
        var handler=new Handler { OnPost=()=>File.AppendAllText(image,"changed") }; var client=new LocalTaggerClient(new HttpClient(handler));
        await Assert.ThrowsAsync<IOException>(()=>client.AnalyzeAsync("http://127.0.0.1:7860",1,image,profile));
    }
    [Fact] public void ThresholdFilterAndComparisonNeverMutatePrompt()
    {
        var p=Fixtures.Workspace(); p.Replace("blue_hair, smile"); var result=new TagAnalysis(1,1,"image","hash",DateTime.UtcNow,"local",null!,[new("blue_hair",.9),new("red_hair",.8),new("lowres",.1)]);
        var rows=ImageTagDiagnostics.Compare(result,p,.35); Assert.Equal(3,rows.Count); Assert.Contains(rows,r=>r.Tag=="smile" && r.Confidence is null); Assert.Contains(rows,r=>r.Tag=="red_hair" && r.Observation.Contains("追加候補")); Assert.Single(ImageTagDiagnostics.Compare(result,p,.35,"red")); Assert.Equal("blue_hair, smile",p.English);
    }
    [Fact] public async Task LibrarySelectionAndExplicitSelectedTagAddReopenWithoutAuthorityMutation()
    {
        using var d=new TempDirectory(); var profile=await Profile(d.Path); var store=new ImageTagAnalysisStore(d.Path); store.SaveProfile(profile);
        var image=Path.Combine(d.Path,"image.png"); File.WriteAllBytes(image,[1,2,3]); var main=new MainViewModel(Fixtures.Catalog(),new MemoryStore(),new MemoryClipboard(),paths:new(d.Path));
        var vm=new ImageTagAnalysisViewModel(main,new(d.Path),new LocalTaggerClient(new HttpClient(new Handler())));
        main.GenerationLibrary!.Selected=new(new(1,1,"image.png",image,".png",3,1,null,null,"Available","None",null,new())); main.Workspace.Replace("smile"); await vm.Analyze.ExecuteAsync(null);
        Assert.Equal("smile",main.English); Assert.Equal(2,vm.Rows.Count(r=>r.Value.Confidence is not null)); vm.Rows.Single(r=>r.Value.Tag=="blue_hair").Selected=true; vm.AddSelected.Execute(null); Assert.Equal("smile, blue_hair",main.English); Assert.True(main.Workspace.Contains("blue_hair")); main.Workspace.Undo(); Assert.Equal("smile",main.English);
        var saved=store.Latest(await LocalTaggerClient.HashAsync(image)); Assert.Equal(profile,saved!.Model); await vm.Reopen.ExecuteAsync(null); Assert.Equal(2,vm.Rows.Count(r=>r.Value.Confidence is not null)); Assert.Equal("smile",main.English);
    }
    private static async Task<TaggerProfile> Profile(string root)
    {
        var model=Path.Combine(root,"model.onnx"); var tags=Path.Combine(root,"tags.csv"); var manifest=Path.Combine(root,"model.json"); File.WriteAllText(model,"fixture"); File.WriteAllText(tags,"tags"); File.WriteAllText(manifest,JsonSerializer.Serialize(new[]{new {name="test",model_path=model,tags_path=tags}}));
        return new("test","test","source","revision",model,await LocalTaggerClient.HashAsync(model),tags,await LocalTaggerClient.HashAsync(tags),manifest,"implementation",new string('a',40),"license");
    }
    private sealed class Handler : HttpMessageHandler
    {
        public int Posts; public Action? OnPost;
        protected override Task<HttpResponseMessage> SendAsync(HttpRequestMessage request,CancellationToken ct) { Posts++; OnPost?.Invoke(); return Task.FromResult(new HttpResponseMessage(HttpStatusCode.OK){ Content=new StringContent("{\"caption\":{\"tag\":{\"red_hair\":0.8,\"blue_hair\":0.9},\"rating\":{}}}")}); }
    }
}
