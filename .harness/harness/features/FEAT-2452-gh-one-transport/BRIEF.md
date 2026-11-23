# BRIEF — FEAT-2452 One GitHub transport, caller failure policy kept

## Problem

Harness operators maintain several independent gh runners. A binary override can leave telemetry or board calls reaching real GitHub during an offline test; failed dependency reads can expose blocked wayfinding tickets; unchecked label creation and untyped launch/JSON failures obscure what happened. Maintainers cannot distinguish accidental divergence from intentional mirror, factory and reconcile policies without tracing every caller.

## Done when — by perspective

**operator** — I can trust dependency-read failures not to make work eligible, receive actionable failures instead of parser or launch crashes, and keep the existing mirror and lifecycle outcomes. I can see a separately filed ticket for the enforcement problems this change deliberately does not repair.

**code maintainer** — I can change the operator/library GitHub execution boundary once, test it offline through one binary override, and find each caller's intended failure and partial-write behavior in one reference.

## Success criteria

- SC-01 (code maintainer): All operator/library gh launches in factory_gh, gh-sync, wayfind, board_lifecycle and gh_cost_log use factory_gh's shared binary-resolution/launch boundary; the counter uses its non-measured primitive without recursive measurement or import-time cycles. The raising and typed non-raising forms preserve status, both streams and typed launch/strict-JSON errors. QA demonstrates a failing state before the new transport assertions pass.
  verify: automated evidence: unit
- SC-02 (code maintainer): FACTORY_GH is the only operator/library binary override. GH_SYNC_GH and the D-11 dual-pin doctrine are absent from the scoped production modules, test support, test headers and manual-probe comments; offline mirror, board and factory integration paths use the same fake, including telemetry. QA demonstrates a failing caller-level single-override regression first: with only FACTORY_GH set and an offline default-gh sentinel first on PATH, the real mirror caller's fake transcript and telemetry are asserted and any default-binary dispatch fails the test without reaching GitHub, before and after the fix.
  verify: automated evidence: integration
- SC-03 (operator): Wayfinding blockers and parent reads treat only a completed nonzero gh process with an explicit HTTP 404 in typed stderr as absence; auth, network, other HTTP and launch failures stop the operation without an eligible frontier or subsequent resolve writes, and a status-zero malformed-JSON response raises GhError even when its stderr mentions HTTP 404. Invalid JSON raises GhError rather than becoming raw text; the successful issue-create URL remains a text result, dry-run remains non-mutating, and gist stdin is preserved. QA demonstrates each changed failure first.
  verify: automated evidence: unit
- SC-04 (operator): Mirror and lifecycle label-create failures are checked before dependent writes, preserving each caller's colors and force behavior; typed mirror launch errors follow the existing caller policy. Ordinary milestone creation looks up an existing milestone only when the failure's captured output contains both 422 and already exists. Each of divergences (c), (d) and (e) has a failing-first regression; milestone precision is retained only as that inline conjunction with one lookup and one no-lookup regression, and is cut under the settled first-to-cut lever if it needs more.
  verify: automated evidence: integration
- SC-05 (operator): Malformed ordinary parent/task create URLs produce an actionable typed/mirror diagnostic rather than uncaught integer conversion (#1542), and a failing abandon API call is reported while later per-item work and local abandoned recording continue (#13). Regression controls also preserve mirror SKIP/0, board-station exit 0 on board failure, factory exit 2, reconcile continuation/residual exit 1, issue-type compatibility downgrade and uncertain replacement-create receipt rules. QA demonstrates the new URL/abandon assertions failing first.
  verify: automated evidence: integration
- SC-06 (code maintainer): At git show <review_sha>:.claude/skills/harness/references/github-mirror.md, a caller-to-failure-policy table covers mirror gh/gh_try and specialized recovery/PR/type paths, wayfind, board-station, board_lifecycle, factory and telemetry, including partial writes and the explicit absence of subprocess deadlines. At git show <review_sha>:.claude/skills/harness/bin/factory_cli.py, the opening exit-2 contract no longer promises that nothing mutated. No enforcement executor or GH_BIN setting is changed in the pinned diff.
  verify: inspection
- SC-07 (operator): At git show <review_sha>:.harness/harness/features/FEAT-2452-gh-one-transport/notes/enforcement-backlog.json, a real filed mruangutai/harness ticket titled Enforcement GitHub reads must not trust unverified state is recorded with its issue number, URL, OPEN readback and body. Its body names branch-create-gate's trust of nonempty stdout without checking return code and merge-gate's local-branch fallback after failed head reads, without repairing either executor in this feature.
  verify: inspection

## Verification gaps

- No active kind covering this Python transport surface has a null runner. unit and integration are active. functional is excluded under DEC-187; the unit and executable-fake integration suites carry SC-01–SC-05 instead. component/ui are unresolved but this feature has no browser/component surface; no SC rests on them.
- issue_types_live is locally_run and requires authenticated gh on the pinned repository. Before ship, Main records the registered default read-only probe's stdout at notes/issue-types-live-probe.txt; only CAPABILITY PRESENT or CAPABILITY ABSENT for the pinned github.repo counts, and a SKIP (missing gh, auth, disabled sync or failed query, all exit 0) is not live evidence. Offline compatibility tests do not establish live repository capabilities. No live mutations, deadline behavior, or enforcement repairs are proven by these SCs. No SC requires user-run UAT.

## Constraints

- DEC-138 and DEC-146 SUPPLY the intentional best-effort mirror/board policies; local signed artifacts remain authoritative. DEC-200 and DEC-203 BLOCK changes to PR-readback, lifecycle, abandonment and receipt/recovery ownership while transport moves. DEC-220 BLOCKS changes to pending-create intent and Build-entry receipt semantics. DEC-166 SUPPLIES tracker ownership and dry-run mutation behavior; DEC-167 SUPPLIES resolve's parent discovery and mandatory gist write.
- DEC-174 BLOCKS team execution: every future implementation task is main-session-direct because factory_gh is in check-state's dependency chain. DEC-100 and DEC-144 BLOCK migrating or changing branch-create-gate, merge-gate, check_state/ctx auth and their GH_BIN/private deadline semantics. DEC-234 BLOCKS bootstrap extraction.
- factory_gh is the sole operator/library transport; binary resolution and launch-error typing are shared, and gh_cost_log uses only the non-measured primitive. No retries, compatibility aliases, label-color unification or gh-sync command-flow rewrite. FACTORY_GH is the sole retained override.
- issue:// and pr:// are rejected for code: rendered cached Markdown is not strict typed JSON. run_watch has no Python/ExtensionAPI entry point and no current CI polling caller. No instruction changes.
- Fold #893, #1542 and #13 into the transport/override, URL-validation and abandon-regression tasks respectively; their closure evidence belongs in the ship record, not the policy reference. source_issues remains [2452]. One DEC amendment is required, ruled at signature (signoff ruling §2, condition C1): DEC-138's "Shared code, and migration scope" implementation sentences — that gh_bin() lives in gh_issues.py and that each caller keeps its own runner — become literally false after this cutover, so T-05, after T-04, rewrites only them to name factory_gh as the shared transport with failure policy kept at each caller. The write-only regression guard sentence and every DEC-138 policy clause stay untouched; DEC-146 and the other governing decisions are kept.
- Product is the assigned Harness feature worktree. AGENTS.md maps specification and decisions to .harness/harness/docs/SPEC.md and DECISIONS.md. docs/spec.md, docs/decisions.md and docs/architecture.md do not exist; SPEC §3.3 and module contracts supply applicable architecture guidance, not invented substitute documents.

## Out of scope

- **Subprocess deadlines.** The consolidated seam inherits run_gh's lack of a timeout, so a hung gh hangs every operator path. This already holds on every path. It is a **conscious non-goal**, recorded in the policy table, so the consolidation does not grow timeouts while it is there.
- **The enforcement executors and their divergences** go to the separate ticket: #588 (the INV-26 auth skip) and #846 (wayfind's nested close bypassing the Bash gate) stay open.
- **#2406** (batching and perf), #1545, #607 and the other related backlog.
- **Further DEC amendments.** Only the DEC-138 shared-code amendment above is in scope. The policy table describes DEC-138/146 rather than amending their policy clauses.
- The manual issue-type probe's unchecked cleanup remains outside this transport change; only its retired-override prose is migrated.

## Approval

status: approved
approved-by: Mike Ruangutai (delegated to fable-advisor)
date: 2026-11-23
