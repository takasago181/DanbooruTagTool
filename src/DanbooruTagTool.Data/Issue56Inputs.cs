namespace DanbooruTagTool.Data;

// Accepted #56 evidence from main dad9d24551cb08f573507101221b934442339ecf (PR #62).
// Unlisted CSVs are ignored. Listed files must match accepted SHA-256 bytes.
public static class Issue56Inputs
{
    public static IReadOnlyDictionary<string, string> MappingHashes { get; } =
        new System.Collections.ObjectModel.ReadOnlyDictionary<string, string>(new Dictionary<string, string>
    {
        ["docs/issue56/pilot/issue56_ui_genre_pilot_v1_classification_map.csv"] = "b96afa412a03838e11fba6888ed062b87870442f022bd97f8b623b0811d6f7a1",
        ["docs/issue56/rollout/reviewed/issue56_old01_crossaudit_a_v1.csv"] = "b3397d9024d5cdd47616121ca562d8d0075da9eb98afadf70d08d731d83cf3c6",
        ["docs/issue56/rollout/reviewed/issue56_old01_crossaudit_b_v1.csv"] = "6f293f5f20615ae59193fb328fcb810eb10196b5053647756dae3ca9a82c94d9",
        ["docs/issue56/rollout/reviewed/issue56_old02_crossaudit_a_v1.csv"] = "40dea79b56062b48e83201d6729ad1f35450ff049005a0ee122c2fca35e0341a",
        ["docs/issue56/rollout/reviewed/issue56_old02_crossaudit_b_v1.csv"] = "df1b044f4d8dfd54004bf9b4781f88e72ddc1eb0036b550e0e7f580f831141a4",
        ["docs/issue56/rollout/reviewed/issue56_old02_crossaudit_c_v1.csv"] = "93693c3e96df1b1f41b0b07610a064773b2255d14d956476336770e9f18cac0a",
        ["docs/issue56/rollout/reviewed/issue56_old03_crossaudit_v1.csv"] = "832007852fc53544f7c3fadd15a772b2ef9bca6af49eedb8d1d740353ea32773",
        ["docs/issue56/rollout/reviewed/issue56_old04_crossaudit_a_v1.csv"] = "46388b8b99a6d6e129ed647ea9ee4dbe59be9272d9c4d5e8935fe850e64decc6",
        ["docs/issue56/rollout/reviewed/issue56_old04_crossaudit_b_v1.csv"] = "2d01ff8bc15db323b44b30feb1780c779a6bd8a0e4e19561c1c7598b717f004c",
        ["docs/issue56/rollout/reviewed/issue56_old04_crossaudit_c_v1.csv"] = "1fd78c9af622bbf3af312b1329144c8f85fa2fe2c989f50c58a1f3f95642f2f5",
        ["docs/issue56/rollout/reviewed/issue56_old05_crossaudit_a_v1.csv"] = "396f4766a0bf870187501e76f122eb1bfd4e2bbfde62e2941d108cac18cf22eb",
        ["docs/issue56/rollout/reviewed/issue56_old05_crossaudit_b_v1.csv"] = "a5266f226c932e5e04e63f6790f548b185318c27f9b02fa2dc150f568e071194",
        ["docs/issue56/rollout/reviewed/issue56_old06_crossaudit_a_v1.csv"] = "2e6e3c24e461ea712aed7661fc54b040d3d6c7aae1bcd7f72e0cebc871663b7d",
        ["docs/issue56/rollout/reviewed/issue56_old06_crossaudit_b_v1.csv"] = "88909c50f2e51a6785dfb4f04265251c12da953e16df540ea39ea2531a6d6947",
        ["docs/issue56/rollout/reviewed/issue56_old07_crossaudit_a_v1.csv"] = "de9743eb8c7ca2fa25cbe0ca1f6b122249a37b09ea163587efd38f7911243667",
        ["docs/issue56/rollout/reviewed/issue56_old07_crossaudit_b_v1.csv"] = "bfae5d64d4966e066c7a5feb345184b20d24d96fad99191c5ef0b95d533a7abd",
        ["docs/issue56/rollout/reviewed/issue56_old08_crossaudit_v1.csv"] = "55cdc17f471315a4fa6cef7da5e938e39f963618e2c86d37342eae878309b8de",
        ["docs/issue56/rollout/reviewed/issue56_old09_crossaudit_v1.csv"] = "1a684190b486050f3a5e73c7bf87fcc83fbeacf0f77c71770550704a1b5e259f",
        ["docs/issue56/rollout/reviewed/issue56_old10_crossaudit_v1.csv"] = "f7ddb0820185fc68229c1cabc948e8106fe308341d79f8f70bb45cf441d65432",
        ["docs/issue56/rollout/reviewed/issue56_old11_crossaudit_v1.csv"] = "dee2e994bc365b61e5a99281a8325bc57d4efd7bf8d61a10897adb974294e382",
        ["docs/issue56/rollout/reviewed/issue56_old12_crossaudit_v1.csv"] = "5349ed0f024233d4f22066ee32459e7d9701e1f92817b2b5e5c75fc457a856a9",
        ["docs/issue56/rollout/reviewed/issue56_old_other_part03a_reviewed_v1.csv"] = "3f1cbede54e46d0e07387b63f3649aea5ea7e92109573f72c41f0651b9c91100",
        ["docs/issue56/rollout/reviewed/issue56_old_other_part03b_reviewed_v1.csv"] = "a6be87a9a3653755c9c5d7c861a39d13b52977455e07075fcb685294fb2f213f",
        ["docs/issue56/rollout/reviewed/issue56_old_other_part04a_reviewed_v1.csv"] = "4d5ae47ba95070b6e86557c0f36d739ed799fb5df387caa635cec2db399e42b5",
        ["docs/issue56/rollout/reviewed/issue56_old_other_part04b_reviewed_v1.csv"] = "6454bb5ae6a0d4a323483eac5e05f3b7fab522fe4f20bf32b57e9240f37a76fd",
        ["docs/issue56/rollout/reviewed/issue56_old_other_part05a_reviewed_v1.csv"] = "b20ec4931a36a2d2750fe7aeba077b08145e3fd6e6739259227a05a8be36c2ab",
        ["docs/issue56/rollout/reviewed/issue56_old_other_part05b_reviewed_v1.csv"] = "c080f3b06c6e2ff92c1d2729d9e4ca64fd005ede7d68ff1d3577975eea22c936",
        ["docs/issue56/rollout/reviewed/issue56_old_other_part06a_reviewed_v1.csv"] = "632fbc5a5ed4c08b70f863d9fdf3dd6a8ac7cf0fb7377b5bf17f1f73639d4510",
        ["docs/issue56/rollout/reviewed/issue56_old_other_part06b_reviewed_v1.csv"] = "3598182fb4a9cf595fcba5a74a61a1aaa6bb76732ef9179dc71b5579b893bdd6",
        ["docs/issue56/rollout/reviewed/issue56_old_other_part07a_reviewed_v1.csv"] = "f7563366a7ade0b437016ac0d57e1dcb8629a11f9c5bef6bae5e576225f667d1",
        ["docs/issue56/rollout/reviewed/issue56_old_other_part07b_reviewed_v1.csv"] = "382296a71b71318dadbd81bb0ebd1773dabe02cf62a907f3a71970f27cea0ba9",
        ["docs/issue56/rollout/reviewed/issue56_old_other_part08_reviewed_v1.csv"] = "d4078c24fdf2b1e5bff9450d3394b9d2763708001fecb344af487a2c5052a201",
        ["docs/issue56/rollout/reviewed/old_other_part01_v1.csv"] = "93be5b64f4d30c0c404f2e11b8ca7ed7fede0c7599c0fb12a07dad9fa2a989a8",
        ["docs/issue56/rollout/reviewed/old_other_part02_v1.csv"] = "1c7b8857fea034d31f91eae0687e5819e9a27244fd5cdcdd9a4a6b2b68416358",
    });
}
