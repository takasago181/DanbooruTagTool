using DanbooruTagTool.Core;
using Xunit;

namespace DanbooruTagTool.Tests;
public class PromptTests
{
    [Theory]
    [InlineData("blue_hair, blue_hair, (blue_hair:1.2), <lora:Rella:0.6>, BREAK, custom_trigger")]
    [InlineData(" blue hair ,\r\n(red_hair:1.20) , unknown\\,comma,,")]
    [InlineData("[blue_hair:red_hair:0.5], ((smile)), {custom|thing}, <lora:unknown:complex:1>, tail")]
    [InlineData("blue_hair, (broken, raw, blue_hair")]
    [InlineData("a), blue_hair, b")]
    [InlineData("  ")]
    [InlineData("")]
    public void RawRoundTripIsByteForByte(string text)
    { var p = new PromptParser(Fixtures.Catalog()); Assert.Equal(text, PromptParser.Serialize(p.Parse(text))); }

    [Fact] public void EightyItemsLoadAndEdit()
    {
        var w = Fixtures.Workspace(); w.Replace(string.Join(", ", Enumerable.Range(0, 80).Select(i => "trigger_" + i)));
        Assert.Equal(80, w.Items.Count); w.Delete([w.Items[20].Id]); Assert.Equal(79, w.Items.Count); w.Undo(); Assert.Equal(80, w.Items.Count);
    }
    [Fact] public void ImportPreservesOrderSurfaceAndDuplicates()
    {
        var w = Fixtures.Workspace(); w.Replace("blue_hair, blue_hair,(blue_hair:1.2), red hair");
        Assert.Equal(new[] { "blue_hair", " blue_hair", "(blue_hair:1.2)", " red hair" }, w.Items.Select(i => i.Surface));
        Assert.Equal(3, w.Items.Count(i => i.Canonical == "blue_hair"));
    }
    [Fact] public void DictionaryAppendUsesCanonicalAndBlocksNewDuplicate()
    {
        var w = Fixtures.Workspace(); w.Replace("raw"); var e = Fixtures.Catalog().Resolve("azure_locks")!;
        Assert.True(w.Add(e)); Assert.Equal("raw, blue_hair", w.English); Assert.False(w.Add(e)); Assert.Equal(2, w.Items.Count);
    }
    [Fact] public void WeightedExistingBlocksDictionaryDuplicate()
    { var w = Fixtures.Workspace(); w.Replace("(blue_hair:1.2)"); Assert.False(w.Add(Fixtures.Catalog().Resolve("blue_hair")!)); }
    [Fact] public void MixedKindsCoexist()
    {
        var w = Fixtures.Workspace(); w.Replace("blue_hair,(blue_hair:1.2),<lora:Rella:0.6>,BREAK,custom_trigger");
        Assert.Equal(new[] { PromptItemKind.Normal, PromptItemKind.Weighted, PromptItemKind.Lora, PromptItemKind.Control, PromptItemKind.Raw }, w.Items.Select(i => i.Kind));
        Assert.Equal("LoRA Rella 0.6", w.Items[2].Display);
    }
    [Fact] public void DeleteMultipleAndUndoRedo()
    {
        var w = Fixtures.Workspace(); w.Replace("a,b,c,d,e"); w.Delete([w.Items[1].Id, w.Items[3].Id]); Assert.Equal("a,c,e", w.English);
        w.Undo(); Assert.Equal("a,b,c,d,e", w.English); w.Redo(); Assert.Equal("a,c,e", w.English);
    }
    [Fact] public void MovePreservesRawSurfaces()
    {
        var w = Fixtures.Workspace(); w.Replace(" blue hair , (smile:1.20) ,raw"); var raw = w.Items[1].Surface;
        w.Move([w.Items[1].Id], 0); Assert.Equal(raw, w.Items[0].Surface); Assert.Equal(" (smile:1.20) , blue hair ,raw", w.English);
    }
    [Theory] [InlineData(0,"b,d,a,c,e")] [InlineData(3,"a,c,b,d,e")] [InlineData(5,"a,c,e,b,d")]
    public void NonContiguousMultiMoveIsStable(int gap, string expected)
    { var w = Fixtures.Workspace(); w.Replace("a,b,c,d,e"); w.Move([w.Items[3].Id,w.Items[1].Id],gap); Assert.Equal(expected,w.English); w.Undo(); Assert.Equal("a,b,c,d,e",w.English); }
    [Fact] public void WeightEditOnlyRebuildsEditedItem()
    {
        var w = Fixtures.Workspace(); w.Replace("  (blue hair:1.20) , <lora:Rella:0.6>,raw"); w.EditWeight(w.Items[0].Id, 1.5m);
        Assert.Equal("  (blue hair:1.5) , <lora:Rella:0.6>,raw", w.English); w.Undo(); Assert.Equal("  (blue hair:1.20) , <lora:Rella:0.6>,raw",w.English);
        w.EditWeight(w.Items[1].Id,.8m); Assert.Equal(" <lora:Rella:0.8>",w.Items[1].Surface);
    }
    [Fact] public void UnsupportedCannotBeWeightReconstructed()
    { var w = Fixtures.Workspace(); w.Replace("((blue_hair:1.2):1.3)"); w.EditWeight(w.Items[0].Id,2); Assert.Equal("((blue_hair:1.2):1.3)",w.English); }
    [Fact] public void DirectEditReparsesAndIsUndoable()
    { var w = Fixtures.Workspace(); w.Replace("smile"); w.DirectEdit("blue_hair, [a:b:0.3], <lora:X:complex:1>"); Assert.Equal(PromptItemKind.Raw,w.Items[1].Kind); Assert.Equal("blue_hair, [a:b:0.3], <lora:X:complex:1>",w.English); w.Undo(); Assert.Equal("smile",w.English); }
    [Fact] public void ReplaceHasOneGenerationRecovery()
    { var w = Fixtures.Workspace(); w.Replace("a"); w.Replace("b"); w.Replace("c"); w.Recover(); Assert.Equal("b",w.English); w.Undo(); Assert.Equal("c",w.English); }
    [Fact] public void PreviewAndClipboardUseExactlyVisibleSequence()
    { var w = Fixtures.Workspace(); w.Replace("raw,blue_hair,(smile:1.2)"); w.Move([w.Items[2].Id],0); Assert.Equal(PromptParser.Serialize(w.Items),w.English); Assert.Equal(w.English,w.ClipboardPayload); }
    [Fact] public void NewMutationInvalidatesRedo()
    { var w = Fixtures.Workspace(); w.Replace("a,b"); w.Delete([w.Items[0].Id]); w.Undo(); w.DirectEdit("c"); Assert.False(w.CanRedo); }
}
