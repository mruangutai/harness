# QA gate — FEAT-03-subissue-mirror — c0

## Verdict: PASS

`unit` runner exits 0, all 3 listed scripts pass, every named `ok` label required by T-03..T-07's
`verify:` blocks is present in the output. Static SC-06/SC-09/SC-10/D-01 grep receipts all confirmed
by direct command, not by digest. `qa_gate: blocking` (`.harness/harness.json:242`) is satisfied.

## Range gated

`4d00dbc..e68ba00` (three commits: `2897b09` T-01, `ae728e8` T-02..T-07, `e68ba00` T-08) —
**not** `HEAD~1`. `git diff --stat e68ba00..HEAD -- .claude/skills/harness/bin docs/harness/DECISIONS.md .harness/harness.json`
is **empty** — no bin/harness.json/DECISIONS.md drift past the pin, so every receipt below is a
pinned receipt, not a working-tree one. The only post-pin dirt is orchestrator bookkeeping
(`STATE.md`, `feature.yaml` — only `phase`/`review_sha`/`cycles_used`/`cost_usd` changed, `github:`
block untouched — and `.harness/logs/2026-07-31.md`), none of it reviewed code.

## Phase 1 (BRIEF+PLAN only, no source read) — expected coverage

Derived before opening any `.py`/`.sh` file: per-terminal-state behavior for open/close-task/abandon/
ship, the parent-origin three-way branch on both terminal states, a feature.yaml round-trip test, an
INV-21 warn-level check, environmental-SKIP coverage for old+new subcommands, and (inspection-only)
the gh_issues.py extraction, no-real-gh, no-retrofit, and DECISIONS/check-docs consistency. This list
matches what was actually built — no gap between Phase 1 and Phase 2 on the automated-evidence SCs.

## SC evidence — 7 SCs with `evidence: unit`, named explicitly

**I counted 7, matching PLAN:149, not the dispatch's "eight."** The dispatch's count is wrong;
neither BRIEF nor PLAN supports eight. Enumerated from BRIEF `## Success Criteria`: SC-01, SC-02,
SC-03, SC-04, SC-05, SC-08, SC-12.

| SC | Test | Anchor |
|---|---|---|
| SC-01 | "parent created and recorded", "three sub-issues attached to the parent", "attach uses internal id not number", "re-run open creates nothing", "recorded-not-attached task is attached on re-run" | test-gh-sync.py:193,217,218,237,318 |
| SC-02 | "close-task closes exactly one issue", "absorbed #12 #14 NOT closed" | test-gh-sync.py:244,245 |
| SC-03 | "abandon closes 3 subs not_planned", "abandon closes the milestone", "abandon leaves an adopted parent open", "abandon closes a created parent not_planned", "abandon leaves a parent with no recorded origin open" | test-gh-sync.py:381,385,391,417,445 |
| SC-04 | "ship closes a created parent completed", "ship leaves an adopted parent open", "ship leaves a parent with no recorded origin open", "ship closes the milestone regardless of parent origin" | test-gh-sync.py:553,578,605,583 |
| SC-05 | "issue numbers recorded in feature.yaml", "pre-existing parent survives per-task saves", "parent_origin survives per-task saves", "created parent records origin created", "adopted parent records origin adopted" | test-gh-sync.py:212,324,328,214,297 |
| SC-08 | "case (a): INV-21 note appears when parent is unrecorded", "case (b): no INV-21 note when parent is recorded", "case (c): no INV-21 note when github.sync is false", "exit code unchanged by INV-21" | test-check-state.py:64,74,84,95 |
| SC-12 | "gh missing", "sync disabled", "repo unpinned", "failed attach is a SKIP...(SC-12)", "abandon with sync disabled" | test-gh-sync.py:168,172,176,353,529 |

## Matrix

`test_matrix`: `logic|bugfix -> unit`, `config|docs -> []`. Tasks: T-01 config, T-02/T-03/T-05/T-06/T-07
logic, T-04 bugfix, T-08 docs. T-01 and T-08 correctly resolve to no automated kind (DEC-163, PLAN
D-06) — **not a coverage defect**, per the closed list. `functional/integration/component/ui/eval/
typecheck` all `cmd: null`; BRIEF `## Verification gaps` states no SC rests on a null kind — confirmed,
none of the 7 unit-evidence SCs needs them. No `ai_behavior` task exists; no eval required, none run.

- unit: **satisfied** — cmd `.claude/skills/harness/bin/run-unit-tests.sh`, ran clean, exit 0.
- functional/integration/component/ui/eval/typecheck: **not applicable** (cmd null, no SC depends on them) — soft skip.

`matrix_ok: true`.

## Receipts run myself (not trusted from digests)

- `run-unit-tests.sh` exit 0; all 3 scripts (`test-validate-digest.py`, `test-gh-sync.py`,
  `test-check-state.py`) PASS; every `ok` label above present in the streamed output.
- **Streaming confirmed by reading the script**: `python3 "$BIN_DIR/$s"` with no redirection/capture;
  runner's own PASS/FAIL line prints after.
- **MISCONFIGURED path proven live**: touched `test-orphan.py`, ran the runner with `2>&1` split —
  exit 2, `MISCONFIGURED: .../test-orphan.py is not in run-unit-tests.sh's explicit script list` on
  stderr, stdout empty. Deleted the probe; `git status --porcelain` no longer mentions it.
- **`detect` glob**: resolves to `test-check-state.py`, `test-gh-sync.py`, `test-validate-digest.py` —
  matches (T-07 added a third file after T-01 landed; not a regression of T-01's receipt).
- SC-06 (`wayfind.py`): absence checks all **0** — `"-F", f"sub_issue_id="`, `"-F", f"issue_id="`,
  `"--jq", ".id"`, `/parent"`. Carve-out presence checks both **1** — `sub_issues", "--paginate"` and
  `dependencies/blocked_by",$`. No bare `"gh"` literal. `gh_issues.py` imports cleanly, all five forms
  print correctly.
- D-01 standing guard: `grep -cE 'parent_args|blocked_by_args' gh-sync.py` = **0**.
- **Premise protection checked directly, not assumed**: no `save_recorded` call anywhere in
  `cmd_abandon` or `cmd_ship` (grep over each function body returns empty) — the three absent-
  `parent_origin` fixtures do not pass vacuously.
- **Label placement confirmed**: "ship closes the milestone regardless of parent origin" sits inside
  the `parent_origin: adopted` fixture at `test-gh-sync.py:583`, exactly the placement that catches
  one `if origin == "created":` wrapped around both the parent close and the milestone PATCH.
- **SC-09**: no `sub_issues_summary` reference anywhere in `gh-sync.py`/`test-gh-sync.py`/`wayfind.py`;
  `test-gh-sync.py` fakes `gh` exclusively via `GH_SYNC_GH` env override, no real `gh` invocation.
- **SC-11**: `check-docs.sh` exit 0 ("no stale statements found", 45 patterns / 73 files);
  `amendment 7` present in DECISIONS.md (count 1). `check-state.sh` exits 1 in this repo (see coverage
  gap note below) but carries **no `INV-10` line** and **no `INV-21` line** (sync false here) — matches
  T-08's/T-07's stated contract, which is the specific-invariant + unchanged-exit-code check, not a
  bare exit-0 assertion.
- Read `cmd_abandon`/`cmd_ship` source directly: the reason/body-file comment is unconditional on any
  recorded parent (not gated on origin); only the *close* branches on origin; the milestone PATCH is
  unconditional in both. Matches PLAN D-01 exactly.
- `wayfind.py:270`'s redundant `issue(repo, num, "id")` pre-attempt and the literal `-F sub_issue_id=`
  dry-run print are both still present verbatim.
- **Adequacy check, MF-2 class, read not assumed**: `cmd_close_task` (`gh-sync.py:305-315`) still
  prints the absorbed-numbers line ("left open for the ship briefing") — the PLAN-specified print was
  not silently dropped. The negative assertion at `test-gh-sync.py:245-246` is scoped to `closes`, a
  list filtered from the fake-gh **call log** (`log`) to `issue close` lines only — **not** a stdout
  substring check — so "absorbed #12 #14 NOT closed" passing is not vacuous against the print's own
  `#12`/`#14` text.
- **Adequacy check, MF-1 class, read not assumed**: both `abandon` leave-open fixtures — "abandon
  leaves an adopted parent open" (`test-gh-sync.py:391-394`) and "abandon leaves a parent with no
  recorded origin open" (`:445-450`) — assert absence in **both** close forms, `\bissues/40\b` (the
  PATCH form `cmd_abandon` actually uses for its created-parent close) and `issue close 40`. Not taken
  from STATE.md's claim; read directly.

## Deliberate decisions assessed and dismissed (not re-litigated, not `must_fix`)

Inverted `absorbs` assertions (D-02), absent/unrecognised-origin leave-open default (SC-03/04),
SC-06 payload/lookup-form scoping with carve-out list GETs retained, D-01 standing regression guard,
`wayfind.py:270` redundant pre-attempt, verbatim `ticket` dry-run print, unconditional comment step,
SC-10's `github:`-block-only scoping (feature.yaml's own bookkeeping churn is not a violation) — all
confirmed present and correct by direct check above, none changed my verdict.

## Coverage gaps (real findings, not must_fix given the closed list)

1. **`wayfind.py` has zero test coverage in the `unit` runner** — no `test-wayfind.py` exists, and T-02
   made `wayfind.py` import-dependent on `gh_issues.py`. SC-06 is `verify: inspection` (structural
   grep only); nothing in the runner exercises `wayfind.py`'s three converted call sites
   (`parent_of`, the `ticket` attach, the `block` edge) at runtime. If `gh_issues.py`'s argv builders
   were subtly wrong in a way that only manifests through `wayfind.py`'s calling convention (arg
   order, kwarg vs positional), no automated test catches it before a live invocation. This is
   eng-lead's already-raised non-blocking Q3 — assessed here as a genuine, moderate-severity gap, not
   dismissed. Scenario: a future edit to `gh_issues.py` changes `attach_sub_issue_args`'s parameter
   order; `test-gh-sync.py` (which calls it the same way `gh-sync.py` does) stays green, `wayfind.py`
   silently breaks at its next live `ticket` invocation.
2. **Test-first ordering cannot be confirmed from git history at task granularity.** Each PLAN task's
   source and test edits land in the same per-run commit (`2897b09`, `ae728e8`, `e68ba00`), so there is
   no commit-level evidence of which was written first. Not a violation — a limitation of the commit
   granularity chosen for this build — but noted since `harness-verification-rules` asks for the audit.
3. **`check-state.sh` exits 1 here for a reason that changed since the plan's baseline receipt.**
   PLAN's `observed @f929d44` baseline was `BRIEF.md is NOT approved` + an orphaned run dir. Today's
   exit 1 is a **different** VIOLATION (`phase is 'validate' but notes/handoff-build.md is missing`)
   plus a note about an orphaned `2026-07-31-12-validator` run dir. The exit **code** is unchanged (1),
   which is literally what T-07/T-08's verify asks for, and no `INV-10`/`INV-21` line appears — so
   SC-11 and SC-08's own receipts hold. But the underlying cause is orchestrator process state
   (missing build→validate handoff artifact), not this feature's code — flagged as an open question
   for the orchestrator/validator-lead, not a QA finding against FEAT-03's diff.

## Open questions

- Q1 (non-blocking): `wayfind.py`'s new dependency on `gh_issues.py` is untested — see coverage gap 1.
- Q2 (non-blocking, informational): `check-state.sh`'s exit-1 baseline moved to a new VIOLATION
  (missing `notes/handoff-build.md`) unrelated to FEAT-03 — worth the orchestrator's attention before
  the validate→ship handoff, not a gate on this feature.

## Not my call

SC-06, SC-07, SC-09, SC-10, SC-11, SC-13 are `verify: inspection` — I supplied grep/read receipts
above for SC-06/09/10/11 as direct evidence; SC-07 (the gate proving itself) and SC-13 (main-session
SKILL.md edit, explicitly out of scope for every agent domain) are unchanged from PLAN's framing and
carried no automated evidence to gate.

`git status --porcelain` at close: only pre-existing dirt (`STATE.md`, `feature.yaml` bookkeeping
fields, `.harness/logs/2026-07-31.md`) — none staged, committed, reverted or stashed by this run.
