using System.Text.Json;
using DanbooruTagTool.Core;
using Xunit;
namespace DanbooruTagTool.Tests;
public sealed class RegionComposerTests
{
    private static RegionComposerConfig Config => new("2girls, outdoors", "(red hair:1.2), <lora:sample:0.5>, [unknown:raw]", "blue hair, blue dress", "low quality", "bad hands", "text");
    [Fact] public void CompilerPreservesRawAndExplicitBoundaries()
    {
        var c=RegionComposer.Compile(Config);
        Assert.Equal(Config.Common+" BREAK "+Config.SubjectA+" BREAK "+Config.SubjectB,c.Positive);
        Assert.Equal("low quality BREAK bad hands BREAK text",c.Negative);
        Assert.Equal(c,RegionComposer.Compile(Config));
        Assert.Equal(Config,JsonSerializer.Deserialize<RegionComposerConfig>(JsonSerializer.Serialize(Config)));
        Assert.Equal("Columns",RegionComposer.Args(Config)[3]); Assert.Equal("Rows",RegionComposer.Args(Config with {Layout=RegionLayout.Vertical})[3]);
        Assert.Throws<ArgumentException>(()=>RegionComposer.Compile(Config with {SubjectA="foo BREAK bar"}));
        Assert.Throws<ArgumentException>(()=>RegionComposer.Compile(Config with {Ratios="1,0"}));
        Assert.Throws<ArgumentException>(()=>RegionComposer.Compile(Config with {Ratios="1;1"}));
    }
    [Fact] public void MissingChangedOrDisabledExtensionIsRejected()
    {
        var args=RegionComposer.Labels.Select(label=>new {label,choices=new[]{"Columns","Rows"}}).ToArray();
        using var scripts=JsonDocument.Parse(JsonSerializer.Serialize(new[]{new {name="regional prompter",is_img2img=false,is_alwayson=true,args}}));
        using var extensions=JsonDocument.Parse(JsonSerializer.Serialize(new[]{new {enabled=true,remote=RegionComposer.Repository,commit_hash=RegionComposer.Commit,version="b10c496d"}}));
        Assert.Equal(RegionComposer.Contract,RegionComposer.Detect(scripts.RootElement,extensions.RootElement).Contract);
        using var empty=JsonDocument.Parse("[]"); Assert.Throws<System.IO.InvalidDataException>(()=>RegionComposer.Detect(empty.RootElement,extensions.RootElement));
        using var changed=JsonDocument.Parse(extensions.RootElement.GetRawText().Replace(RegionComposer.Commit,new string('a',40)));
        Assert.Throws<System.IO.InvalidDataException>(()=>RegionComposer.Detect(scripts.RootElement,changed.RootElement));
        using var mismatch=JsonDocument.Parse(scripts.RootElement.GetRawText().Replace("Divide Ratio","Other Ratio"));
        Assert.Throws<System.IO.InvalidDataException>(()=>RegionComposer.Detect(mismatch.RootElement,extensions.RootElement));
    }
    [Fact] public void RegionalClaimsRequireActualMetadata()
    {
        var p=RegionComposer.Compile(Config);
        var ordinary=ForgePngGenerationMetadata.Parse("test.png",p.Positive+"\nNegative prompt: "+p.Negative+"\nSteps: 12, Sampler: Euler, CFG scale: 5, Seed: 1, Size: 512x512");
        Assert.Throws<System.IO.InvalidDataException>(()=>RegionComposer.Verify(Config,ordinary));
        var actual=ordinary with { Parameters=ordinary.Parameters.Concat(new[] {new GenerationParameter("RP Active","True"),new("RP Divide mode","Matrix"),new("RP Matrix submode","Columns"),new("RP Calc Mode","Attention"),new("RP Ratios","1,1"),new("RP Use Base","False"),new("RP Use Common","True"),new("RP Use Ncommon","True"),new("RP Mask submode","Mask"),new("RP Prompt submode","Prompt"),new("RP Base Ratios","0"),new("RP Options","disable convert 'AND' to 'BREAK'"),new("RP LoRA Neg Te Ratios","0"),new("RP LoRA Neg U Ratios","0"),new("RP threshold","0.4"),new("RP LoRA Stop Step","0"),new("RP LoRA Hires Stop Step","0"),new("RP Flip","False")}).ToArray() };
        RegionComposer.Verify(Config,actual);
        Assert.Throws<System.IO.InvalidDataException>(()=>RegionComposer.Verify(Config with {Layout=RegionLayout.Vertical},actual));
    }
    [Fact] public async System.Threading.Tasks.Task MissingCapabilityNeverPostsOrCreatesOutput()
    {
        using var handler=new MissingRegionalHandler();
        var api=new ForgeGenerationApiClient(new System.Net.Http.HttpClient(handler));
        var c=RegionComposer.Compile(Config);
        var result=await api.GenerateAsync("http://127.0.0.1:7860",new(c.Positive,c.Negative,new GenerationRecipe(Regional:Config)),System.IO.Path.Combine(System.IO.Path.GetTempPath(),System.Guid.NewGuid().ToString()));
        Assert.False(result.Success); Assert.Null(result.ImagePath); Assert.Equal(0,handler.Posts); Assert.Contains("送信していません",result.Status);
    }
    private sealed class MissingRegionalHandler : System.Net.Http.HttpMessageHandler
    {
        public int Posts;
        protected override System.Threading.Tasks.Task<System.Net.Http.HttpResponseMessage> SendAsync(System.Net.Http.HttpRequestMessage r,System.Threading.CancellationToken ct)
        {
            if(r.Method==System.Net.Http.HttpMethod.Post) Posts++;
            var properties=new[]{"prompt","negative_prompt","seed","steps","sampler_name","scheduler","cfg_scale","width","height","batch_size","n_iter","override_settings","override_settings_restore_afterwards","send_images","save_images","alwayson_scripts"}.ToDictionary(k=>k,k=>new{});
            var schema=JsonSerializer.Serialize(new { paths=new Dictionary<string,object> { ["/sdapi/v1/txt2img"] = new { post = new { requestBody = new { content = new Dictionary<string,object> { ["application/json"] = new { schema = new Dictionary<string,string> { ["$ref"]="#/components/schemas/Request" } } } } } } }, components = new { schemas = new { Request = new { properties } } } });
            var json=r.RequestUri!.AbsolutePath=="/openapi.json"?schema:"[]";
            return System.Threading.Tasks.Task.FromResult(new System.Net.Http.HttpResponseMessage(System.Net.HttpStatusCode.OK){Content=new System.Net.Http.StringContent(json)});
        }
    }
    [Fact] public void ExistingOrdinaryIdentitySerializationIsPreserved()
    {
        var json=JsonSerializer.Serialize(new GenerationRecipe(Seed:1));
        Assert.DoesNotContain("Regional",json);
        var baseline=new RecipeSnapshot("plain","",new());
        Assert.Empty(GenerationRecipeDerivation.Diff(baseline,baseline));
    }
    [Fact] public void ControlledComparisonPinsAllConditionsAndRejectsTampering()
    {
        var config=Config with {SubjectA="red hair"}; var ordinary=RegionComposer.Ordinary(config);
        var recipe=new GenerationRecipe("model",7,12,"Euler","Normal",5,768,512,"abc");
        var setup=new ExperimentSetup("regional","human evaluation",new(ordinary.Positive,ordinary.Negative,recipe),new(ExperimentVariable.RegionalMode,"",new[]{"Ordinary","Horizontal","Vertical"}),null,new long[]{7},Regional:config);
        var plan=ExperimentPlanner.Build(setup); ExperimentPlanner.Validate(plan);
        Assert.Null(plan.Trials[0].Requested.Recipe.Regional); Assert.Equal(config,plan.Trials[1].Requested.Recipe.Regional);
        Assert.Equal(RegionLayout.Vertical,plan.Trials[2].Requested.Recipe.Regional!.Layout);
        Assert.All(plan.Trials,t=> {Assert.Equal(7,t.Requested.Recipe.Seed);Assert.Equal(recipe.ModelHash,t.Requested.Recipe.ModelHash);Assert.Equal(recipe.Cfg,t.Requested.Recipe.Cfg);});
        var trials=plan.Trials.ToArray(); trials[1]=trials[1] with {Requested=trials[1].Requested with {Recipe=trials[1].Requested.Recipe with {Cfg=9}}};
        Assert.Throws<System.IO.InvalidDataException>(()=>ExperimentPlanner.Validate(plan with {Trials=trials}));
    }
}
