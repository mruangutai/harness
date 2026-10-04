# T-02b — current receipt paths

The authorized receipt-path amendment is complete; the single plan check exited 1 on the existing two T-04 anchors. Approval renewal remains main-only and pending: plan.yaml still records approved / main-session / 2026-09-29; BRIEF.md records pending with empty approved-by and date. No approval was changed here.

## Exact scope

- T-02 verify changed only the single --verify-receipt argument from .harness/harness/features/FEAT-1928-digest-object-contract/notes/live-digest-object-probe.md to .harness/harness/features/FEAT-1928-digest-object-contract/notes/live-digest-object-probe-current.md. The remaining literal command, including all ten Harness suites and four absolute OMP suites, was supplied unchanged.
- T-02 files retains every original entry in original order. Immediately after notes/live-digest-object-probe.md, added the full feature-local notes/live-digest-object-probe-current.md and notes/live-digest-object-probe-current.transcript.jsonl paths, in that order.
- T-02 intent explicitly placed fresh evidence “in live-digest-object-probe.md.”; changed only that phrase to “in live-digest-object-probe-current.md.”
- BRIEF SC-05 says “feature-local live-probe receipt” and Verification gaps does not name the old filename; both remain unchanged, including historical receipt preservation wording. SC-03, runtime provenance, all other plan fields, historical receipt/transcript, and prior research are untouched. No lead-owned runs artifact was written.
- No T-02 verify, suite, probe, build, lint, or formatter ran. This amendment does not discharge SC-05.

## Actual commands and outcomes

Control-plane amend --help exited 0; feature-root exited 0 and returned the assigned worktree. The first chained amend --show invocation printed verify hash then exited 4 at files because --yaml-value was omitted; intent in that chain did not run. Retried files --show with --yaml-value and intent --show: exit 0.

Three separate CAS amendments used this exact command prefix:

```sh
python3 /Users/molchairuangutai/GitHub/harness/.agents/skills/harness/bin/plan-merge.py amend --file /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-1928-digest-object-contract/.harness/harness/features/FEAT-1928-digest-object-contract/plan.yaml --key tasks --id T-02
```

Suffixes, in execution order (replacement values supplied on stdin):

```text
--field verify --expect-sha256 4c707a58fd2c26ed3e03d6a28c084a9de67e14f3fa097f121a8ef67c64cb939c --value-file /dev/stdin
--field files --expect-sha256 579182e90165213f6fa03e6f66409f4751fb36f15e4ab5f57d12b7e34c793e54 --value-file /dev/stdin --yaml-value
--field intent --expect-sha256 bc6b22cbac22c56b17b4ec7bd710593ddb29c072f773b3a90e4de3c70d10f493 --value-file /dev/stdin
```

Each exited 0, printing AMENDED tasks:T-02.<field> and APPLIED with the absolute plan path. Captured stdout contained no APPROVAL-RESET:, so no gh-sync call ran. The temporary orchestration script removed itself after success; it only called plan-merge for plan writes. Automatic check-state diagnostics included, on all three calls:

```text
VIOLATION  .harness/harness/features/FEAT-1928-digest-object-contract/BRIEF.md is NOT approved — halt that flow and surface to the user.
```

INV-40 also reported unsigned T-02 drift versus signed 1a292e26304a… without a judgements[] amendment: successive hashes d730d30ca5a7…, 4fc7eef25da1…, 3495b9ffc667…. Ancillary notes concerned resolved INV-32 findings, absent referenced run directories, and existing other-feature INV-23 notes; none was changed. Approval state was read directly after amendment and remains approved; renewed signature is still pending operator authorization and main action.

## Single mandated check — verbatim outcome

```sh
python3 /Users/molchairuangutai/GitHub/harness/.agents/skills/harness/bin/plan-merge.py check --file /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-1928-digest-object-contract/.harness/harness/features/FEAT-1928-digest-object-contract/plan.yaml --root /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-1928-digest-object-contract
```

Executed exactly once; exit 1:

```text
OK T-01 22 anchor(s) resolved
OK T-02 38 anchor(s) resolved
OK T-03 6 anchor(s) resolved
FAIL T-04 files: .claude/skills/harness/bin/plan_merge/panel.py#_digest_mapping: no definition or token '_digest_mapping' in .claude/skills/harness/bin/plan_merge/panel.py
FAIL T-04 files: .claude/skills/harness/bin/plan_merge/panel.py#_fenced_blocks: no definition or token '_fenced_blocks' in .claude/skills/harness/bin/plan_merge/panel.py
OVERLAP tests/integration/canonical-reader-classification.json: T-01, T-04
CHECK /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-1928-digest-object-contract/.harness/harness/features/FEAT-1928-digest-object-contract/plan.yaml against /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-1928-digest-object-contract: 4 task(s), 76 anchor(s) resolved, 2 failure(s)
```

The check did not emit missing-current-receipt failures; it reported all 38 T-02 anchors resolved. This is not proof the fresh receipt/transcript exists or is valid. PM created neither; main owns their later creation. No failure was suppressed or check retried.

## Main-session approval commands — copied unchanged, not executed

From notes/research-plan-reconcile-T02.md. Revoke first; sign only after operator approval of the amended plan and BRIEF. Main also owns the BRIEF signature.

```sh
python3 /Users/molchairuangutai/GitHub/harness/.agents/skills/harness/bin/plan-merge.py revoke-approval --file /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-1928-digest-object-contract/.harness/harness/features/FEAT-1928-digest-object-contract/plan.yaml --by main-session --reason 'Reconcile T-02 bundled-runtime provenance and strengthened SC-05'
python3 /Users/molchairuangutai/GitHub/harness/.agents/skills/harness/bin/plan-merge.py sign-approval --file /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-1928-digest-object-contract/.harness/harness/features/FEAT-1928-digest-object-contract/plan.yaml --by main-session --date 2026-10-03
```

## Open questions

1. Main: renew approvals and disposition INV-40 through the authorized main-session route; this run grants no signature.
2. Main/lead: resolve the two existing T-04 anchor failures and T-01/T-04 overlap outside this narrow assignment.
3. Main: create and verify fresh current receipt/transcript; the historical artifacts remain unchanged and are not fresh proof.
