# Build

必要: Python 3.11+、reportlab、pypdf、pdfplumber、Pillow、日本語TrueTypeフォント。
QA画像生成はPopplerのpdftoppmを使用する。ネットワークアクセス・モデル実行は不要。
フォントはWindowsのBIZ UDGothicを参照し、PDFには埋め込む。font fileはcommitしない。

repository rootから:

```powershell
python -X utf8 docs/knowledge/textbook/build.py
```

この環境のbundled Pythonでの確実なコマンド:

```powershell
& 'C:\Users\takas\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -X utf8 docs/knowledge/textbook/build.py
```

別環境では `--font /path/regular.ttf --bold-font /path/bold.ttf` を指定する。
フォントは日本語glyphとTrueType outlineが必要。builderは自動downloadを行わない。
PDF、figures/*.svg、references/COVERAGE.jsonを再生成する。
buildに使う固定CSVは同梱するためKnowledge branchのcheckoutは不要。

全ページQA:

```powershell
python -X utf8 docs/knowledge/textbook/validate.py --render
```

QA画像は `tmp/pdfs/issue44-smartphone/`。全ページを幅1080pxでrenderし、
1080×2400pxの画面へfitしたphone画像と20ページ単位のcontact sheetを生成。
原稿・文字サイズ・figureが変わったら再生成して最新の画像を確認する。
PDFリンクは解析でpage destinationを検証する。実機タップ試験は別途必要。

## Knowledge更新時のみ

`references/snapshot.py` のSHA、build.pyのcorpus/main SHAを変更する前にlive gateを実施。
snapshot.pyを実行し、inventoryの差、Registry verdict、HOLD、ledgerを原稿と照合する。
原文Claimを自動翻訳して判定を統合する処理はない。
再生成可能性は同じ内容・レイアウトの再生成を意味し、PDF作成日時によるbyte一致は要件にしない。
