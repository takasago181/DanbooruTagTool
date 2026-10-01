# Issue #180 — Serial Completion Worktree start prompt v1

Use one new Codex-managed Worktree.

Start branch:
`research/issue180-serial-completion`

Paste the following prompt:

```
DanbooruTagTool Issue #180を、このWorktree 1本だけで完走方向へ進めてください。

固定branch:
research/issue180-serial-completion

このチャットでは claim_codex_role_v2.py を実行しないでください。
旧 Forward 0〜3 / QA の5役は停止済みです。旧branchesは証拠/mailboxとしてread-onlyで利用してください。

最初に live GitHub を再取得してください。
最低限:
- origin/main
- research/issue180-single-home-pilot
- research/issue180-serial-completion
- research/issue180-forward-0..3
- research/issue180-qa-integrator
- Issue #180 最新コメント
- Issue #188 最新残件
- docs/issue180/serial/SERIAL_COMPLETION_V1.md
- QA_REVIEW_LEDGER_V2.csv
- SOURCE_REVIEW_LEDGER_V2.csv
- current v3 migration/dispatch summaries

古い件数/HEADよりliveを優先してください。

最優先は既存Forward mailboxの未QA backlog消化です。
未QA proposalが1件でも残る間、新規campaignのweb researchは原則開始しないでください。
proposal_idをcurrent QA_REVIEW_LEDGER_V2.csvと照合し、4 mailboxから未QAだけを取得してください。

QA backlogは小分けしすぎないでください。
目安は1 integration waveあたり:
- 50〜100 proposals
または
- 300〜600 relation instances
の自然なsource/semantic境界です。

ただし FAMILY_HOME / MEMBER_OF / VARIANT_OF / conflict 等でgraphが大きく変わる場合は、そこで早めにfull v3して構いません。
単純DIRECT_HOMEを3〜10 proposal処理するたびにfull v3/CIを回さないでください。

同じWorktree内でも research pass と review pass を分離してください。
候補を見つけたから即acceptせず、review passでsourceを開き直し、
source identity / scope / exact member coverage / current canonical applicability を再確認してください。

既にSOURCE_REVIEW_LEDGER_V2でACCEPTEDの同一source + 同一mapping ruleは再利用可です。
ただしexact Character/member coverageは確認してください。
曖昧名・alias・variant・family/root・conflict・terminal・migration correctionは100% review。
既承認rosterのdeterministic exact-name extractionだけ現行contractの10% sampling（min10/max50）可。不一致1件でもそのbatch全件reviewへ昇格してください。

wave内部ではcheap checks中心:
- parse-back
- git diff --check
- schema/duplicate checks
- targeted tests

integration boundaryでのみ:
- full v3
- campaign rebuild
- tracked dispatch refresh
- all Issue180 tests
- source ledger validation
- #179 freshness
- protected-source checks
- reproducibility

を実施してください。

research/issue180-serial-completionへの通常pushではfull CIを自動起動させないでください。
integration waveのexact commitをpush後、Issue180 Character HOME v3 workflowをworkflow_dispatchでこのserial branchに対して手動起動し、exact SHAがgreenになるまで確認してください。
green exact commitだけを research/issue180-single-home-pilot へ forceなしでfast-forwardしてください。

CI失敗、stale dispatch、duplicate、PARTIAL、safe unresolved、schema/serializer修正ではユーザーに戻らず自律修復・継続してください。

既存未QA backlogが0になったら、そのままSerial Phase Bへ移行してください。
current v3/campaign queueを再構築し、4 slot全体からhighest reusable-yield OPENを1本ずつ処理してください。
OPEN優先、次にOPEN_WITH_PROGRESS。prior_checked_routesは繰り返さない。
source reuseを新規検索より優先し、RESEARCH_STOP_PROTOCOL_V2のroute budgetを守ってください。
一つのsourceで証明できるexact relationsはまとめて回収してください。

PARTIALは進捗だけ記録してcampaignを閉じない。
EXHAUSTIVEはexact scopeを本当に網羅した場合だけ。
HOMEを推測しない。

通常checkpoint後に「続けて」をユーザーへ要求しないでください。
真のpolicy blocker / protected mutation / persist不能 / final completionまで自律継続してください。

#188 telemetryは通常Issue #180 checkpoint commentに混ぜて記録してください。telemetry専用commit禁止。観測不能値はnull。

禁止:
force push
main merge
production apply
#70/#179/#132 protected source変更
HOME semantics変更
git clean -fdx
git clean -fdX

最終完了条件はSERIAL_COMPLETION_V1.mdのFinal gateに従ってください。
```
