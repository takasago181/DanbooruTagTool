# #245 — baseline native WPF failure diagnosis

2026-10-02 JST。製品UI・既存test・assertionは変更していない。

## 結論 A / B / C / D

- **A: 既存mainにも存在する。** clean main `a96dcd10d77e85d629e0169669ea26028f88c835` と PR旧head `b856279fd0b7aef3893ba62bd13aa49a9024b366` は同じ `src` tree `dc121b5d6d9a9a48988d7f617bdb38499b11106e`。同一session・同一コマンドの元#223 testは両方2 PASS。別の独立native probeで同じ900×560を指定すると両方一覧高さ0、1280×720では両方41.33 DIP。表示環境の小さい時だけ発現する既存product defectである。
- **B: #245 helper起因の証拠なし。** 元testをhelperなし・別processで実行。独立probeもApp startupやUiAuditのcontent detachを使わず、memory store/clipboardで実MainWindowをShowし、元test同様にreviewed groupを選択した。main/PR全caseの寸法・結果数が一致。
- **C: testの暗黙geometry前提あり。** 元testはWidth=1200/1500、Height=900を要求するが、Show後の実寸・DPI・work areaを確認しない。前回はscreen約682.7×512 DIPでactual900×560になった。1200/1500×900のwrap/filter/return acceptanceと小画面UXの判定が同じassertionに混ざった。今回元testの意図と `>80` をそのまま保持し、test修正なし。
- **D: 本物の小画面UX bugあり。** group選択後も17個のgroup候補、説明、header/searchをAuto行に残す。幅が狭いほどwrapして大きくなり、結果のstar行を使い切る。900×560ではAuto行の合計474 DIPがview324.67 DIPを超え、結果行0。1280×720も結果surface48 / list41.33。headerだけの問題でも、データが空の問題でもない（選択group45件）。Phase Cの両案へ反映。局所patchはしない。

前回の小さいdesktopへOS設定を戻すことはしていない。したがって「前回のscreen条件でclean mainの元testを再実行」は未実施。Aは同一sessionのclean-main/PR比較と、actual900×560での独立再現に基づく。display縮小を起こしたOS/RDP等の原因までは未確定であり、今回のproduct/harness原因とは区別する。

## 同一machine/session比較

現在: Session 1、primary/virtual1706.67×960 DIP、work area(0,0,1706.67,912)、144 DPI / 1.5 scale。physical換算2560×1440。WindowState=Normal。両checkoutを順次実行し、native WPF processを重ねていない。

| requested / actual native DIP（両者一致） | list height | DictionaryWorkspace | inner grid | header | tab strip | selected content |
|---|---:|---:|---:|---:|---:|---:|
| 1200×900 / 1200×900 | 221.33 | 664.67 | 646 | 67.33 | 48.67 | 672.67 |
| 1500×900 / 1500×900 | 235.33 | 664.67 | 646 | 67.33 | 48.67 | 672.67 |
| 900×560 / 900×560 | **0** | 324.67 | 474 | 67.33 | 48.67 | 332.67 |
| 1280×720 / 1280×720 | **41.33** | 484.67 | 466 | 67.33 | 48.67 | 492.67 |

inner grid rows [header, search, relation/group, refinement, results]:
1200: [44,38.67,335.33,0,228]; 1500: [44,38.67,321.33,0,242];
900: [44,38.67,391.33,0,0]; 1280: [44,38.67,335.33,0,48]。

親chain、desired/actual、width properties、header/tab位置、screenは [clean main](evidence/geometry-clean-main.json) / [PR](evidence/geometry-pr246.json) の全記録参照。explicit-content caseはWindow ancestorを維持した補助実験でありnative client sizeそのものとは呼ばない。900では補助実験もlist0、1280では72。主結論はnative caseによる。

## 再現手順

各checkoutで同じcommand（results directoryのみ分離）:

```powershell
dotnet test src/DanbooruTagTool.Tests/DanbooruTagTool.Tests.csproj -c Release --disable-build-servers -m:1 --filter FullyQualifiedName~Issue223WpfTests --logger trx --results-directory <new-output>
```

独立probeは `scripts/issue245/README.md`。clean-main project referencesにも同じprobeを適用するが、clean checkoutへhelper/sourceを書き込まない。既存UserData/authorityは不変、表示設定変更なし、通信なし。

## Gateの扱い

元#223 acceptanceは現在の表示環境でgreenになった。これは低解像度UXが修正済みという意味ではない。実装前STOPでは既存defectを持つbaselineとして記録し、将来実装Gateでnative requested/actualを明示し、元のwrap/filter/return/label/no-ellipsisを維持した上で900×560・1280×720の一覧到達性を検証する。新しいskip、threshold変更、MinHeight変更、CI専用hackなし。
