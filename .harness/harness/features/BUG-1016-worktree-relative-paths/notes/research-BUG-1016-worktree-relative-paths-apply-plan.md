# BUG-1016 — reader findings applied

All three cycle-1 findings are resolved in the pending plan. Required record-panel and check commands exited 0; no implementation, test execution or goal-check occurred. Ready for the once-only plan goalcheck, not for signature until external engineering simplification is routed.

## Findings and evidence

- PF-a04ce645703fce9d4a22de66df1630eb (med substance): BRIEF SC-03/relative predicate and T-01/T-02 preserve explicit empty/whitespace strings and list entries byte-for-byte; only omitted/undefined/null search paths default. This follows grilling Settled's omitted-path ruling. Reader-reported probes were not rerun or independently claimed.
- PF-167168a4fc099a9a415c38a6386db318 (low task proportionality): T-01 removes the redundant node:fs fixture requirement; literal handler-returned effective-input tables and pre/post target assertions retain adapter discrimination.
- PF-0cdd7bb1cf75fbbbe87dd2bd7f5639c2 (low task proportionality): T-01 permits validated-success caching within one governed run, including explicit CLI no-match success, with run/feature/root/runner isolation and boundary invalidation. Errors, ambiguity and inferred roots remain uncached and refuse without fallback; readiness/authorization still run each call. Conditional tests cover caching if selected; no mandatory cache subsystem introduced. T-02 documents actual behavior.

Exact IDs were produced by record-panel from runs/plan-product/panel-c1.md, not assigned here. Controlled set-panel preserves reader severity, kind, summary and task scope and records resolved_by T-01 with reasons. Source issues [1016,1570], both tasks, D-01, mission plan, safety/claim/URI/main-session/Claude-host constraints and DEC-174 direct routing/reason remain unchanged. BRIEF was surgically edited; all plan writes used controlled merge verbs. Approval remains pending and needs_approval true.

## Command stdout receipts

Authoritative CLI: /Users/molchairuangutai/GitHub/harness/.agents/skills/harness/bin/plan-merge.py. All commands target this feature's absolute worktree plan; check uses the supplied feature-tree root. Complete captured apply + record-panel output, including the full old/new REPLACED T-01.intent and T-02.intent scalar values: artifact://498 (read :raw). This is the unabridged task-changing stdout receipt; below are its non-payload result lines verbatim.

```text
APPLIED /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-1016-worktree-relative-paths/.harness/harness/features/BUG-1016-worktree-relative-paths/plan.yaml
ADDED PF-a04ce645703fce9d4a22de66df1630eb
ADDED PF-167168a4fc099a9a415c38a6386db318
ADDED PF-0cdd7bb1cf75fbbbe87dd2bd7f5639c2
PANEL cycle 1 from /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-1016-worktree-relative-paths/.harness/harness/features/BUG-1016-worktree-relative-paths/runs/plan-product/panel-c1.md -> /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-1016-worktree-relative-paths/.harness/harness/features/BUG-1016-worktree-relative-paths/plan.yaml
APPLIED /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-1016-worktree-relative-paths/.harness/harness/features/BUG-1016-worktree-relative-paths/plan.yaml
```

apply exited 0; record-panel exited 0 (the dependent command ran and the combined command exited 0). No APPROVAL-RESET: receipt appeared; gh-sync status was therefore not invoked.

set-panel and check stdout result lines, verbatim:

```text
PANEL cycle 1 -> /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-1016-worktree-relative-paths/.harness/harness/features/BUG-1016-worktree-relative-paths/plan.yaml
APPLIED /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-1016-worktree-relative-paths/.harness/harness/features/BUG-1016-worktree-relative-paths/plan.yaml
OK T-01 2 anchor(s) resolved
OK T-02 2 anchor(s) resolved
CHECK /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-1016-worktree-relative-paths/.harness/harness/features/BUG-1016-worktree-relative-paths/plan.yaml against /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-1016-worktree-relative-paths: 2 task(s), 4 anchor(s) resolved, 0 failure(s)
```

set-panel exited 0; check exited 0. Merge hooks additionally printed pending-BRIEF and INV-37 missing github.build_entry violations plus unrelated legacy STATE notes; these are not erased or claimed green. Full hook output is included in artifact://498; the same diagnostics were emitted by set-panel. No approval or build-entry write was attempted.

## Open handoff requirements

- External eng-squad routing must complete the four-angle simplification before main-session signature. This host lacks engineering-member spawn rights; earlier coordination URI failures are documented in panel-c1.md. Four-angle simplify is **not completed** and is not a panel finding or a mission downgrade.
- Once-only goalcheck belongs to the successor and was explicitly not run here.
- Main session must handle pending approvals and the surfaced missing github.build_entry before execution; no remote status call was authorized by an APPROVAL-RESET receipt.

## 2026-10-04 — accepted simplify application

SF-01, SF-02 and SF-04 are applied; the once-only assigned plan-shape check exited 0. Approval remains pending. This section supersedes the earlier open simplification-routing requirement: `runs/plan-simplify-eng/digest.md` supplies the completed review and `runs/plan-apply-product/state.yaml` supplies this application's acceptance. This is not implementation, another panel or approval.

### Dispositions

- **SF-01 — applied:** `plan.yaml` T-01 intent now requires section/MV recognition shared with `extractEditPaths` (one matcher for extraction and rewriting, no prescribed parser abstraction). Valid-section/body-row discrimination, quoting, hashes, CRLF, malformed extraction/advisory and original/revised post behavior remain required. Added the assertion that extraction of revised input equals the effective destinations judged by `preDomain`/`postDomain`.
- **SF-02 — applied:** T-01's relative predicate uses the existing `.omp/extensions/harness-hooks.ts` `URI_SCHEME` for scheme detection, not another regex. The BRIEF predicate and BUG-2003 permission paragraph are unchanged.
- **SF-04 — applied:** T-02 derives DEC-251 contract content from BRIEF SC-07 and the existing named Constraints (DEC-174/250/233, discovery, revised-input channel, relative predicate, silent lexical rewriting, validated-success caching and BUG-2003 URI classification). T-01 references the omitted-versus-blank default rule once instead of repeating it. SC-04/06 references retain resolver-error and non-governed coverage. Origins #1016/#1570, lineage, seven-tool/six-path/edit-MV obligations, execution/pre/post agreement, cache optionality, rejected alternatives, host boundaries, decision-id collision handling, index regeneration and the T-01 receipt pointer remain. Existing constraint lead-ins are stable enough; no BRIEF edit was needed.
- **SF-03/05/06/07/08/09 — not applied:** explicitly excluded by the accepted application dispatch; their recorded skip reasons remain in the simplify digest. No accepted finding was skipped.

### Preservation evidence

Before and after snapshots were read from this worktree, without git validation or executing task verify blocks. These SHA-256 values matched exactly:

| Preserved material | Before = after |
|---|---|
| All loaded plan fields except both task intents (sorted compact JSON) | `c72b1b6042bfa44d97990b69f59002df00aba58c5ebd3fd0b96739efcb1ac780` |
| Complete BRIEF bytes, including SC-01 through SC-07 | `bde42130c8073bad7ae5c8c8b6895ff929ccc2126921098a3ddd78d5c7f24985` |
| T-01 test-first paragraph | `cf74dc4467552c21700a755117bdbec4943842ca189c99a0bcd3c7f8ddb6a305` |
| T-01 final four test/assertion/receipt paragraphs, joined by newline | `d61a6355ba8ba8a661b43f25f81ea41c80ec4ec19a7aedb03a49b0396b4e6e94` |

Thus the task set, traces, verify blocks, D-01, lanes, execution metadata, dependencies, panel, pending approval and `needs_approval: true` are unchanged; every pre-existing named test/assertion paragraph is preserved. Prior sections of this note were retained and only this section appended.

### Command receipts

Control-plane CLI: `/Users/molchairuangutai/GitHub/harness/.agents/skills/harness/bin/plan-merge.py`. Both changes used `amend --key tasks --field intent`, with `--id T-01` / `T-02`, this feature's absolute `--file`, raw temporary `--value-file` payloads, and the `--show` compare-and-swap hashes `37f81da60fcea9252900f8a4e8af5022e1c213268e5353458f402fc2a4676378` / `d6a425ef6be4b6dce1a119c396babb8735b557e84f43edd7ee1ad64dfe9a4350`. Both amend invocations exited 0 and printed:

```text
AMENDED tasks:T-01.intent
APPLIED /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-1016-worktree-relative-paths/.harness/harness/features/BUG-1016-worktree-relative-paths/plan.yaml
AMENDED tasks:T-02.intent
APPLIED /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-1016-worktree-relative-paths/.harness/harness/features/BUG-1016-worktree-relative-paths/plan.yaml
```

No `APPROVAL-RESET:` receipt appeared; no remote gh-sync call was made. Merge-internal hooks also reported the unapproved BRIEF and INV-37 missing `github.build_entry`, plus unrelated legacy STATE notes already disclosed above; these are not claimed green or repaired here.

Exactly once after both amendments, from the assigned worktree:

```text
python3 /Users/molchairuangutai/GitHub/harness/.agents/skills/harness/bin/plan-merge.py check --file /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-1016-worktree-relative-paths/.harness/harness/features/BUG-1016-worktree-relative-paths/plan.yaml --root /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-1016-worktree-relative-paths
OK T-01 2 anchor(s) resolved
OK T-02 2 anchor(s) resolved
CHECK /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-1016-worktree-relative-paths/.harness/harness/features/BUG-1016-worktree-relative-paths/plan.yaml against /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-1016-worktree-relative-paths: 2 task(s), 4 anchor(s) resolved, 0 failure(s)
```

Observed check exit: **0**. No builds, tests, lint, formatters, smoke runs or production task verify commands were executed.

`files_touched`: `plan.yaml` (T-01/T-02 intent only) and `notes/research-BUG-1016-worktree-relative-paths-apply-plan.md` (this append), both under this feature's assigned worktree directory. No run artifacts, implementation, unrelated docs/changelog or Expertise were written.

Open questions: no application blocker. Main session still owns pending approvals and the already surfaced missing GitHub Build entry before implementation; the product lead owns run-state/digest collation.
