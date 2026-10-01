# Issue #180 — Codex-managed Worktree common start prompt v2

Status: ACTIVE

All five Codex chats may be launched identically.

## User launch operation

For each of five new Codex chats:

1. choose **Worktree**;
2. choose the same starting branch: `research/issue180-single-home-pilot`;
3. paste the same common prompt below.

Codex-managed worktrees are expected to start detached. Do not treat `HEAD (no branch)` as an error.

## Common prompt

```
DanbooruTagTool Issue #180を開始してください。

このWorktreeはdetached HEADで正常です。現在branch名から役割判定しないでください。
標準の git fetch origin --prune も実行しないでください。

最初に:
python scripts/issue180/claim_codex_role_v2.py

を実行し、そのJSON出力の role / target_branch / slot をこのチャットの固定役割として使用してください。
Forward 0→1→2→3→QA の5役はremote claim refでatomicに排他取得されます。
ユーザーへ番号入力・branch変更・worktree作成・Forward→QAの手動中継を要求しないでください。

今回の初回runだけは、origin/mainのcompact routingとIssue #180/#188のlive stateを確認するcold startにしてください。
以後、同一contractならwarm resumeを使い、大型の不変文書を毎run再読しないでください。

remote freshness確認は git ls-remote を優先してください。
managed worktreeでFETCH_HEAD権限エラーが出るため、通常の git fetch を前提にしないでください。
Git objectが本当に必要な場合だけ git fetch --no-write-fetch-head を試し、それも不可ならGitHub HTTP/APIをread-onlyで使用してください。

roleがFORWARD_Nなら、canonicalの最新 fwd-N.csv をread-onlyで取得し、PARALLEL_EXECUTION_V2 / AUTHORITY_BATCH_SCHEMA_V2 / RESEARCH_STOP_PROTOCOL_V2に従ってauthority/source単位で処理してください。
自分のtarget_branchへは detached HEAD のまま HEAD:refs/heads/<target_branch> としてfast-forward pushして構いません。
proposal以外のcanonical ledger/dispatchは変更しないでください。

roleがQAなら、4 Forward target branchをGitHubから直接確認し、未QA proposalを統合してください。
QAだけがcanonical writerです。full v3、campaign rebuild、dispatch refresh、Source/QA ledger、green CI確認、exact-green canonical fast-forwardを担当してください。

通常のPARTIAL、duplicate、stale、safe unresolved、軽微なschema/serializer修正では停止せず継続してください。
PARTIALはcampaignを閉じず、EXHAUSTIVEはexact scopeを本当に網羅した場合だけです。

#188の次10 actual #180 run telemetryも記録してください。telemetry専用commitは作らず、通常run終了時のIssue #180 commentへlast_run_metricsを残してください。観測不能値はnullで、推測しないでください。

禁止:
force push / main merge / production apply / #70・#179・#132 protected source変更 / HOME semantics変更 / git clean -fdx / git clean -fdX。

真のpolicy blocker、protected mutation要求、persist不能なtechnical blocker、担当仕事の実枯渇、final completion以外ではユーザーへ「続けて」を要求しないでください。
```

## Role allocation

The helper claims these one-shot remote lock refs in order:

- `research/issue180-claim-forward-0`
- `research/issue180-claim-forward-1`
- `research/issue180-claim-forward-2`
- `research/issue180-claim-forward-3`
- `research/issue180-claim-qa`

Each successful lock maps to the existing target branch of the same role. Claim refs are coordination-only and are outside the Issue180 workflow branch pattern.

Do not manually reset/reuse a claim ref while the corresponding Codex chat may still be active.
