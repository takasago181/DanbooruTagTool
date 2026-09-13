using DanbooruTagTool.Core;
using Xunit;

namespace DanbooruTagTool.Tests;
public class SearchTests
{
    [Theory]
    [InlineData("青い髪","blue_hair",1)] [InlineData("blue_hair","blue_hair",0)]
    [InlineData("blue hair","blue_hair",0)] [InlineData("azure_locks","blue_hair",0)]
    [InlineData("青い hair","blue_hair",3)] [InlineData("blu","blue_hair",4)]
    [InlineData("lue","blue_hair",5)] [InlineData("blie hair","blue_hair",6)]
    public void UnifiedSearchCoversAcceptedMatchKinds(string query, string expected, int rank)
    { var hit = new SearchEngine(Fixtures.Catalog()).Search(query).First(); Assert.Equal(expected,hit.Entry.Canonical); Assert.Equal(rank,hit.Rank); }
    [Fact] public void AnalRegressionSuppressesIncidentalNoise()
    { var hits = new SearchEngine(Fixtures.Catalog()).Search("anal"); Assert.Equal("anal",hits[0].Entry.Canonical); Assert.Contains(hits,h=>h.Entry.Canonical=="anal_focus"); Assert.DoesNotContain(hits,h=>h.Entry.Canonical is "piano" or "analog_clock"); }
    [Fact] public void ExactOutranksUsageAndFuzzy()
    { var c = new Catalog([Fixtures.Entry("smile","笑顔",1),Fixtures.Entry("smiles","笑う",900000),Fixtures.Entry("smile_face","笑顔の顔",4000)]); var h=new SearchEngine(c).Search("smile"); Assert.Equal("smile",h[0].Entry.Canonical); Assert.DoesNotContain(h,x=>x.Entry.Canonical=="smiles"); }
    [Fact] public void ExcludedProductFitIsNotSearchableOrAddable()
    { var c=Fixtures.Catalog(); Assert.Empty(new SearchEngine(c).Search("forbidden")); Assert.False(c.Entries.Single(e=>e.Canonical=="forbidden").CanAdd); }
    [Fact] public void SemanticUsageIsUnknownNotFakeZero()
    { var e=Fixtures.Catalog().Entries.Single(e=>e.Canonical==null); Assert.Equal("—",e.UsageText); Assert.False(e.CanAdd); }
    [Fact] public void AmbiguousAliasDoesNotResolvePromptByGuessing()
    { var c=new Catalog([Fixtures.Entry("a","一",aliases:["ambiguous"]),Fixtures.Entry("b","二",aliases:["ambiguous"])]); Assert.Null(c.Resolve("ambiguous")); Assert.Equal(2,new SearchEngine(c).Search("ambiguous").Count); }
    [Fact] public void EnglishSearchHelpersCannotBecomeStrongJapaneseSubstringIntent()
    { var c=new Catalog([Fixtures.Entry("blue_hair","青い髪",100), Fixtures.Entry("analog_clock","時計",99999) with { JapaneseSearch=["analog clock"] }]); var hits=new SearchEngine(c).Search("log"); Assert.Equal(5,Assert.Single(hits).Rank); }
}
