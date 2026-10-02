using DanbooruTagTool.Data;

try
{
    if (args.Length == 2 && args[0] == "verify")
    {
        var authority = CatalogAuthorityReader.Read(args[1]);
        Console.WriteLine($"PASS {authority.Manifest.Snapshot}: {authority.Entries.Length} accepted rows");
    }
    else if (args.Length is 3 or 5 && args[0] == "compile")
    {
        if (args.Length == 5 && args[3] != "--profile") throw new ArgumentException("Expected --profile full|ordinary");
        var authority = CatalogCompiler.Compile(args[1], args[2], args.Length == 5 ? CatalogBuildProfiles.Parse(args[4]) : CatalogBuildProfile.Full);
        Console.WriteLine($"PASS compiled {authority.Entries.Length} accepted rows to {Path.GetFullPath(args[2])}");
    }
    else throw new ArgumentException("Usage: verify <manifest.json> | compile <manifest.json> <new-empty-output> [--profile full|ordinary]");
    return 0;
}
catch (Exception ex) { Console.Error.WriteLine(ex.Message); return 1; }
