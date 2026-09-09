# Plan-panel scope review — BUG-201-depends-on-integrity — c0

**BLUF: clean. No task serves a dead requirement, no requirement is untraced, the DAG among T-01..T-04
is a valid topological order, the shared file surface across T-01/T-04 is intentional sequential
ownership (not a conflict), and T-01/T-02's designed-to-fail `verify:` is the intended TDD red half,
not a plan defect. Zero gating findings from this lens.** Every source claim below was re-verified
directly against `harness_yaml.py`, `plan-merge.py`, `check-plan-routes.py` and `DECISIONS.md` at
`af859ee8` (HEAD in this worktree is exactly that sha; working tree is clean except the new feature
files, so the tracked files ARE the base-sha bytes — confirmed via `git log`/`git status`).

## The five required checks

**1. Every REQ-01..REQ-04 traced by at least one task — MET.**
REQ-01 -> T-01 (`traces: [REQ-01, REQ-02]`), T-03 (`traces: [REQ-01..REQ-04]`).
REQ-02 -> T-01, T-03.
REQ-03 -> T-02 (`traces: [REQ-03]`), T-03.
REQ-04 -> T-03, T-04 (`traces: [REQ-04]`).
No REQ is left untraced.

**2. No `traces:` cites a nonexistent REQ — MET.** Every id referenced (REQ-01..REQ-04) exists in
`BRIEF.md`'s Requirements section; no task cites REQ-05 or higher.

**3. `depends_on` across T-01..T-04 is a valid topological order — MET.** T-01: `[]`, T-02: `[]`,
T-03: `[T-01, T-02]`, T-04: `[T-03]`. Every edge points to a task declared earlier in the list; no
forward reference, no dangling id (all three targets T-01/T-02/T-03 exist among T-01..T-04), no
cycle. (Per the operator's fixed scope, I did not evaluate whether self-dependencies or cycles are
themselves validated — that is explicitly out of order.)

**4. No task's `verify:` asserts something a predecessor deletes or has not yet created — MET, and
T-01/T-02's designed-red verify is the INTENDED TDD shape, not a defect.**
- File-existence order is clean: T-01 creates `tests/unit/test-plan-depends-on.py` (does not exist
  pre-task, confirmed by glob), T-02 appends to `tests/integration/test-plan-merge.py` (pre-existing,
  confirmed present), T-03 (`depends_on: [T-01, T-02]`) is the first to run all four suites and both
  new-file dependencies are already satisfied by then, T-04 (`depends_on: [T-03]`) appends to the file
  T-01 created, transitively after T-03.
- T-01's and T-02's own `verify:` commands, run in isolation at the point each task executes (before
  T-03 lands the rule), WILL exit non-zero by design — the intent explicitly instructs recording the
  "literal FAIL lines observed" as the task's deliverable proof. I checked whether this is
  structurally sound against how `verify:` is actually consumed: `harness-tdd-enforcement/SKILL.md`
  states plainly *"a green suite has never meant a green `verify:`"* and that `task_verify` is
  reported into the B-7 receipt as an **audit trail, not a gate**. This matches the established
  convention elsewhere in this repo's own plan corpus — e.g. BUG-1286's SC-02 ("demonstrated failing
  first... a passing unit run at review time is not evidence for this criterion"), BUG-1290's task
  verify comments ("PASS requires a FAIL marker line from EACH of the six new cases"), BUG-1081's "the
  test-first RED run is the discrimination evidence." This plan's phrasing is plainer (embedded in
  `intent:` rather than the `verify:` command itself checking for a marker) but is the same shape.
  **Verdict: intended TDD red half, not a defect.**

**5. The four `files:` paths are exactly what each task needs — MET, and the T-01/T-04 shared surface
is correct sequential ownership, not a conflict.**
- T-01: `tests/unit/test-plan-depends-on.py` — creates it. Matches intent exactly.
- T-02: `tests/integration/test-plan-merge.py` — appends one case pair. Matches (file pre-exists).
- T-03: `.claude/skills/harness/bin/harness_yaml.py` — the single file touched; intent says "Touch NO
  other file," and I confirmed against source that `validate_plan_doc` (harness_yaml.py:326-344) is
  the sole call point both `load_plan` and `plan-merge.py`'s `_schema_error` (plan-merge.py:462-475)
  already route through — no second file needs editing to reach both routes.
- T-04: `tests/unit/test-plan-depends-on.py` — same file T-01 created. **This is not a conflict**:
  `depends_on: [T-03]` on T-04, and T-03 itself `depends_on: [T-01, T-02]`, so T-04 is transitively
  ordered strictly after T-01 by the DAG. Two tasks owning the same test file in dependency order is
  an established, unremarkable pattern in this repo's own plan corpus (e.g.
  `tests/unit/test-suite-layout.py` is touched by multiple sequential tasks in
  BUG-1302-suite-layout-fail-closed). No path is claimed that a task cannot deliver its intent
  without, and no path goes untouched by the intent that names it.

## Source claims independently re-verified (beyond the five)

- `validate_plan_doc` calls `_validate_station_only` then `_validate_plan_tasks(tasks, path)` then
  returns `doc` (harness_yaml.py:341-345) — T-03's instruction to insert the new helper call
  "IMMEDIATELY AFTER `_validate_plan_tasks(tasks, path)`" targets a real, exact call site.
- `REQUIRED_TASK_FIELDS = ("id", "title", "change_type", "execution_mode", "files", "verify",
  "intent")` (harness_yaml.py:288-289) — matches T-01's case-1 field list verbatim.
- `_validate_plan_tasks` already does `tid = str(t["id"])` (harness_yaml.py:361) — T-01 case 6's claim
  that numeric ids are already str-coerced is accurate.
- `plan-merge.py`'s `_schema_error` (plan-merge.py:462-475) wraps `harness_yaml.validate_plan_doc`,
  and `_verify_spliced` (plan-merge.py:506-514) raises `MergeRefusal(5, ["ILLEGAL PLAN: ..."])` on a
  legal-base/illegal-result splice — T-02's claim of exit 5 + `ILLEGAL PLAN` text on the write route
  is exactly what the source produces.
- `check-plan-routes.py:365-370` calls `harness_yaml.load_plan(path)` and reports a `PlanSchemaError`
  as exit 2 ("does not load"), never as a routing violation — matches the goal-check's clause-3
  reading exactly.
- The 67-file corpus baseline: `git ls-tree -r --name-only HEAD | grep -c
  '.harness/harness/features/[^/]*/plan\.yaml$'` returns **67** at the pinned commit (the working-tree
  `find` returns 68 only because this feature's own untracked `plan.yaml` is now present in the
  worktree — irrelevant to the committed baseline the BRIEF cites, and T-04's assertion is `>= 67`,
  never `== 67`, so this is not a defect).
- `tests/unit/test-harness-yaml-corpus.py:64` resolves the root via
  `HARNESS_PROJECT_DIR or CLAUDE_PROJECT_DIR or os.getcwd()` — matches T-04's claimed resolution order
  verbatim.

## Existing goal-check finding independently reached: D-03 / Q1 — CONFIRM, defensible/low

I read DEC-174 in full (`DECISIONS.md:4302-4403`) rather than trust the plan's paraphrase. Two facts
hold independently: (a) the enumerated enforcement layer is `check-domain.sh`, `bash-write-guard.sh`,
`validate-digest.py`, `check-state.sh`, `check-plan-routes.py`, `dispatch-guard.sh`, and each one's
test file — `harness_yaml.py` and the two touched test files are in none of those; (b) this feature
performs no **cutover** — both `plan-merge.py` and `check-plan-routes.py` already called through
`validate_plan_doc`/`load_plan` at `af859ee8`, so the paragraph's specific "the cutover that makes a
gate use it is main-session-direct" clause has no cutover to bind to here. The riskier unquoted
sentence right after it — "the gate's behaviour changes only by a hand the carve-out governs" — is
read more naturally as bound to that same cutover context than as an unconditional bar on any
squad-executed library edit that changes gate output; under either reading, D-03's corpus proof (0
dangling refs, all 67 files, before and after) satisfies the paragraph's own stated discriminator
("the gate's violation set is identical before and after"). I reach the same place goal-check did:
**defensible, `low`, non-blocking.** CONFIRM, not raised as new.

## What this feature actually needs to ship (the scope question)

All four tasks are load-bearing and none is scope creep: T-01 proves the read-route rejection rule
red-then-green (REQ-01/02), T-02 proves the write-route refusal red-then-green (REQ-03), T-03 is the
one production change all four REQs ultimately rest on, T-04 is the non-regression proof REQ-04
requires with a paired discriminator so the walk itself can't have silently stopped checking. Nothing
in the plan validates self-dependencies, cycles, or ordering (T-01 forbids those cases explicitly at
`:115-116`, T-03 adds no cycle detection at `:197-198`) — correctly inside the operator's ruling in
both directions.

## Findings

None. Empty findings list — every one of the five required checks resolved clean under direct source
re-verification, and the one existing finding I independently re-derived (D-03/Q1) is a CONFIRM of the
goal-check's own `low`/defensible rating, not a new item.

## Open questions

None from this lens. Q-A and Q-B (both already raised by goal-check, operator/main-session-scoped) are
outside my checks; I did not independently re-derive them and take no position beyond noting I did not
dispute them.

```yaml
VERDICT: PASS
DIGEST:
  headline: All five required checks resolve clean under direct source re-verification; zero gating findings; D-03/Q1 independently re-confirmed defensible/low.
  severity_max: none
  findings: 0
  must_fix: []
  spec_violations: []
  code_grade: n_a
  reviewed: "plan:/Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-201-depends-on-integrity/.harness/harness/features/BUG-201-depends-on-integrity/plan.yaml"
  human_commits_in_scope: []
  open_questions: []
  files_touched: []
  expertise_update: []
artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-201-depends-on-integrity/.harness/harness/features/BUG-201-depends-on-integrity/notes/review-harness-code-reviewer-planpanel-c0.md
```
