# NOW — いま何をやっているか

最終整理: 2026-10-03 JST — #248 Foundation Audit COMPLETE / REVIEW STOP

## 現在地

#245 production closeoutは完了済み。新LKG・実Forge→Library照合・UserData保護までPASS。

#248 Foundation Auditも完了し、Issueをcloseしました。

最終レポート:
`docs/issue248/FOUNDATION_AUDIT_2026-10-03.md`

## 結論

#249〜#255を全部やる必要はありません。

推奨は次の最小構成です。

1. **P0小修正**
   - mainへ直接pushする古いIssue70 workflow 2本をdisable/archive。

2. **Foundation Batch A**
   - #249 + #253の必要部分だけ統合。
   - Issue履歴依存のcatalog buildをsemantic authority / maintenance compilerへ置換。
   - WPFからcatalog build責務を外す。
   - 現行124,895行と成人向けhard/niche Special・SexualIntent・Unified Browse・HOME/group等をparity保護。
   - current UIから未参照の旧Special-only facet stateだけ削除。

3. **Foundation Batch B**
   - #250 + #251 + #252の有用部分を統合。
   - Batch A後にcold evidence / one-off scripts / obsolete workflows / merged-superseded branchesをactive treeから退避。
   - provenance/recoveryは保持。

## 今やらない

- #253の全面的なCore/App再設計
- #254 performance/storage最適化
- #255 Git history compaction
- Artist除外
- CreateViewModel/MainViewModelの抽象化
- CatalogEntry分割

いずれも現在は実害または測定根拠が不足。

## STOP

Foundation実装はまだ開始しない。

次はユーザーが#248結果を確認してから、選定した最小構成を実装へ進める。
