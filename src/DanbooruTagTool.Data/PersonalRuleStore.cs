using System.Text.Json;
using System.Text.Json.Serialization;
using DanbooruTagTool.Core;
namespace DanbooruTagTool.Data;
public sealed class PersonalRuleStore(string root)
{
    private string Pathname=>Path.Combine(root,"UserData","PersonalRules","rules.json");
    public static JsonSerializerOptions Options {get;}=new(){WriteIndented=true,Converters={new JsonStringEnumConverter()}};
    public PersonalRules Load() { var rules=File.Exists(Pathname) ? JsonSerializer.Deserialize<PersonalRules>(File.ReadAllText(Pathname),Options) ?? throw new InvalidDataException("空個人ルール") : PersonalRules.Empty; rules.Validate(); return rules; }
    public void Save(PersonalRules rules)
    {
        _=Load(); rules.Validate(); Directory.CreateDirectory(Path.GetDirectoryName(Pathname)!); var temp=Pathname+".tmp";
        try{File.WriteAllText(temp,JsonSerializer.Serialize(rules,Options));if(File.Exists(Pathname))File.Replace(temp,Pathname,Pathname+".bak");else File.Move(temp,Pathname);}
        finally{if(File.Exists(temp))File.Delete(temp);}
    }
}
