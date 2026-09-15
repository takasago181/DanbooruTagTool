namespace DanbooruTagTool.Data;

// Accepted #56 evidence from main dad9d24551cb08f573507101221b934442339ecf (PR #62).
// Unlisted CSVs are ignored. Listed files must match accepted SHA-256 bytes.
public static class Issue56Inputs
{
    public static IReadOnlyDictionary<string, string> MappingHashes { get; } =
        new System.Collections.ObjectModel.ReadOnlyDictionary<string, string>(new Dictionary<string, string>
    {
        ["docs/issue56/pilot/issue56_ui_genre_pilot_v1_classification_map.csv"] = "18edbe3ddb1f31fc0461b2be1912f5f780a4206f62ed76725d8d7ffeb6159ea1",
        ["docs/issue56/rollout/reviewed/issue56_old01_crossaudit_a_v1.csv"] = "46e6469ca1bdfe255f072985a2f3f354d1ad3d2cab946e148eebe9e9ea10aacf",
        ["docs/issue56/rollout/reviewed/issue56_old01_crossaudit_b_v1.csv"] = "6bc81a090e78aeafa511eec1131db486b8c0a2cdada3045d85b34c4125357a96",
        ["docs/issue56/rollout/reviewed/issue56_old02_crossaudit_a_v1.csv"] = "d10fb96337b96eac6fd0c866e54ad34da234ae3181fc1a4620b5001bd55b2e38",
        ["docs/issue56/rollout/reviewed/issue56_old02_crossaudit_b_v1.csv"] = "017ee0a31bbb9f8300cb6d310d5d94773f12b339d8c8a1062131eb7fb227b086",
        ["docs/issue56/rollout/reviewed/issue56_old02_crossaudit_c_v1.csv"] = "372a8a651f4c10f61564e465df9136ea1021bc312f2fc783d791a2c74ceddf49",
        ["docs/issue56/rollout/reviewed/issue56_old03_crossaudit_v1.csv"] = "0a6f86038c3e0d4aa2f4237b4b5ec02b2a9c11f62b36191b83ff3baf84ae8bc2",
        ["docs/issue56/rollout/reviewed/issue56_old04_crossaudit_a_v1.csv"] = "537992bc6120c21acaffed40d879fcedb80f65905782fb96a0aedc5f08487770",
        ["docs/issue56/rollout/reviewed/issue56_old04_crossaudit_b_v1.csv"] = "af77792ee0f3de7b3d7bc0c95ee3bbd499b6581b66ad18043584c9b2356090d0",
        ["docs/issue56/rollout/reviewed/issue56_old04_crossaudit_c_v1.csv"] = "0cc7e31a79b3501396f997f9c7fa3e21355019a2234b6e9decc45b30150356b3",
        ["docs/issue56/rollout/reviewed/issue56_old05_crossaudit_a_v1.csv"] = "0e2de054542f154f2252d90328cfeb177e50df663892548c1638614c9a697a39",
        ["docs/issue56/rollout/reviewed/issue56_old05_crossaudit_b_v1.csv"] = "31cdaec63b6e78db68f2af0b5c3dc0c04770bd99465eb36371e736d4ade38a4d",
        ["docs/issue56/rollout/reviewed/issue56_old06_crossaudit_a_v1.csv"] = "b5afc4d129eb06d41d7836ce7786a8b9ea959404d002a3e129591af794463a1e",
        ["docs/issue56/rollout/reviewed/issue56_old06_crossaudit_b_v1.csv"] = "e0b0409cb13923b8d0d5877acd22485d4c49674266289daa5eca30f9450a0b00",
        ["docs/issue56/rollout/reviewed/issue56_old07_crossaudit_a_v1.csv"] = "e6cf867d7162ff52e3903bd2255f31d64dfd904aa611c92ce1fd9419b943133b",
        ["docs/issue56/rollout/reviewed/issue56_old07_crossaudit_b_v1.csv"] = "a7dfceb08844b709728a79b35ad228c9870bfa3f99b66f225944374b5d1481e6",
        ["docs/issue56/rollout/reviewed/issue56_old08_crossaudit_v1.csv"] = "57aa00dfada273365a839e442390fdde3b45c11c800cc2d63b619dcf55db288f",
        ["docs/issue56/rollout/reviewed/issue56_old09_crossaudit_v1.csv"] = "f90d34f204e53d4f0fb547ba7e068959fbce66577e19e1c69fb8186be00f7254",
        ["docs/issue56/rollout/reviewed/issue56_old10_crossaudit_v1.csv"] = "e0682809f711f6b4d91cea1632e3727fdd180cf51ce0ef17dcff6636cd67dcc6",
        ["docs/issue56/rollout/reviewed/issue56_old11_crossaudit_v1.csv"] = "7599a6360ca94dca48ad80f4dbcaf77f3d4c205a1e0df117e3063112cb76659e",
        ["docs/issue56/rollout/reviewed/issue56_old12_crossaudit_v1.csv"] = "821463923c312878c142734abf524da1e285a6f851b63d3e45b0371dd52a5d6d",
        ["docs/issue56/rollout/reviewed/issue56_old_other_part03a_reviewed_v1.csv"] = "d2bc8548e97fd0ff95c49f84030eef06d80c19fb62545b59b72d4a361ee47c9b",
        ["docs/issue56/rollout/reviewed/issue56_old_other_part03b_reviewed_v1.csv"] = "a542405157eaa132d23b02ff1466885fbb364e871eef4b01a9f36a4e7bd2749d",
        ["docs/issue56/rollout/reviewed/issue56_old_other_part04a_reviewed_v1.csv"] = "9332cd64fa5788ab5c034045dd165c6302b013d224b01abb3f9ab5a35a1d7077",
        ["docs/issue56/rollout/reviewed/issue56_old_other_part04b_reviewed_v1.csv"] = "88259bc1a62e1111649abf7b5412ee7d6e959c446282adc746f16e1db5806c9e",
        ["docs/issue56/rollout/reviewed/issue56_old_other_part05a_reviewed_v1.csv"] = "2831df6f37e6938ab5b885306d216437d12b686c1acc00de5ab1b8730b48a11e",
        ["docs/issue56/rollout/reviewed/issue56_old_other_part05b_reviewed_v1.csv"] = "5136b0c073f79c0cdfa35e75ebfeb6d664710ffaf24d39b56edecfb5b58309a0",
        ["docs/issue56/rollout/reviewed/issue56_old_other_part06a_reviewed_v1.csv"] = "edd36cb439f7306dc47a9bcef3fc1a56b73021752b29cfbae2d51f1063928578",
        ["docs/issue56/rollout/reviewed/issue56_old_other_part06b_reviewed_v1.csv"] = "559b67e566447ee76e34f635cdcf0519913ab9204d4904a62179c16f1d8e71c8",
        ["docs/issue56/rollout/reviewed/issue56_old_other_part07a_reviewed_v1.csv"] = "69e18846f536d679310e52dcbfc42e7602ebddceeddba59cc7563fd69aabb4ae",
        ["docs/issue56/rollout/reviewed/issue56_old_other_part07b_reviewed_v1.csv"] = "e87f9915f283caa043385e7cd26db98ec0240d72d48539ff526ed2b780f57f44",
        ["docs/issue56/rollout/reviewed/issue56_old_other_part08_reviewed_v1.csv"] = "31f943b2dc36b611e009feb7a3a8d8a2c1606d9fa68ca379b56317362bb69cb6",
        ["docs/issue56/rollout/reviewed/old_other_part01_v1.csv"] = "f6bd71db13e7153bdf960aa80dd4965d3a3e4316edbc1fd0b3980bc7d09e196a",
        ["docs/issue56/rollout/reviewed/old_other_part02_v1.csv"] = "3ca1f5ebfbca1098162364d3c4e874a1a04ffdb6ee957be4e99ff120308f2f79",
    });
}
