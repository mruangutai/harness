# Goal-check — BUG-1303 drafted plan vs. operator intent (cycle 0)

**Does this plan deliver the operator's stated intent?**

**Not as drafted — one high gap.** The plan's prescribed digest form is correct and I proved it
validates, but the `artifact:` line **inside the very `## Output` block T-02 edits** points outside
`.harness/<repo>/features/<FEAT>/`, and T-02 forbids touching it. A reviewer that follows only its
documented block still settles as `BLOCKED (contract violation)` — the exact B-9 failure
(`ship-review-2026-09-05-ship-final.md:85`). Everything else grades clean: 1 high, 2 med, 1 low.

Measured at working tree `c369fb1f`-equivalent, worktree
`BUG-1303-plan-code-review-digest`, approvals `pending` (`plan.yaml:3-4`, `BRIEF.md:115`).

## 1. Intent coverage — GAP (high)

Positive control, run from the worktree root: the form T-02/T-03 prescribe
(`code_grade: n_a` + `reviewed: plan:.harness/harness/features/BUG-1303.../plan.yaml`) with a
feature-dir artifact returns `digest ok`, rc=0. So the remedy is right, and `_is_plan_review` /
`_pending_plan_review_error` / `_PLAN_REVIEW_PREFIX` / `CODE_GRADE_VALUES`
(`.claude/skills/harness/bin/validate-digest.py:977-1046`) accept it as the plan states.

- **G-1 (high) — `BRIEF.md` REQ-01, `plan.yaml` T-02.** The same digest with the artifact line the
  persona's `## Output` block actually documents —
  `.claude/agents/harness-code-reviewer.md:96` and `.omp/agents/harness-code-reviewer.md:97`,
  `artifact: <HARNESS_CONTROL_PLANE_ROOT>/.harness/notes/review-harness-code-reviewer-<runid>.md` —
  returns `VERDICT: BLOCKED (contract violation)`, rc=1:
  *"artifact ... does not name a `.harness/<repo>/features/<FEAT>/` location"*
  (`validate-digest.py:790` `FEATURE_DIR_IN_ARTIFACT_RE`, `:827-853`). `_resolve_feature_dir` runs
  BEFORE the plan-target check (`:1028-1030`), so this refuses in plan mode and post-pin alike.
  T-02's intent says *"Change nothing else in either file: no other field"* (`plan.yaml:174`), and
  the persona's write-grant prose repeats the same wrong path (`:34` / `:35`).
  **Consequence:** the plan ships and the next plan-phase code reviewer that trusts its own persona
  file over `harness-handoff` still has its correct work thrown away — B-9 unclosed. T-01's guard
  cannot catch it either: `documented_contract_gaps` grades only `SCHEMAS` fields, and `artifact` is
  not one, so REQ-04's "class of defect" closes only over schema fields.
  **Repair:** widen T-02 (and the REQ-01/REQ-02 wording) to correct the `artifact:` line in both
  copies to `.harness/<repo>/features/<FEAT>/notes/review-harness-code-reviewer-<runid>.md`, and add
  a `grep -qF` for it to T-02's verify.

## 2. Scope fidelity — PASS

The sixteen-persona guard (REQ-04 / T-01) is **the intent's own logic, not creep**: it is the
discriminating test for this bug's own defect (SC-02), and I reproduced D-01's measurement — across
all 16 `ALIAS` personas against their documented blocks, exactly one gap exists and it is
`harness-code-reviewer`/`code_grade` in both trees. One fix today, the class closed. No stated defect
is left unaddressed except G-1.

## 3. Traceability — PASS

REQ→task: REQ-01→T-02,T-03 · REQ-02→T-01,T-02 · REQ-03→T-03 · REQ-04→T-01 · REQ-05→T-04. No orphan
REQ; every `traces:` cites a REQ that exists. **REQ-03 is delivered negatively** (no task lists any
path under `.claude/skills/harness/bin/`) — legitimate, and SC-04 is its check.
SC→task: SC-01→T-03 verify · SC-02,03,05→T-01 · SC-04→structural (no task, by design) ·
SC-06→T-04 · SC-07→T-03 · SC-08→T-02 verify. No orphan SC.

## 4. Verifiability — GAP (med ×2)

Spot-checks, all non-mutating: `.agents/skills/harness/bin/gen-decisions-index.py` is `-rwxr-xr-x`
and **does support `--stdout`**; `--stdout | diff -q -` against the index exits 0 today, so T-04's
verify is well-formed and its `grep -qF "documented output block"` target exists.
T-02's python body-compare works: `# Harness: Code Reviewer` is present in both files and the bodies
are byte-identical today. T-01's verify string matches `plan.yaml:120` character for character.
T-03's greps (`reviewed: plan:`, `DEC-207`) both return **zero matches** in
`.claude/skills/harness-code-review/SKILL.md` today, so that verify genuinely discriminates; its
"Red flags" table exists at `:163` and the pinned-SHA section at `:155`. No SC is anchored on a line
number or a file-global count.

- **G-2 (med) — `BRIEF.md` SC-04, SC-06, SC-08.** All three declare `verify: automated
  evidence: integration`, but no task adds an assertion for them to `tests/integration/`: SC-04 is a
  `git diff --name-only`, SC-06 is `git show` + the generator, SC-08 lives only in T-02's own verify
  string (`plan.yaml:142`). T-01's intent (`:77-122`) adds nothing for any of them.
  **Consequence:** at ship qa runs the integration kind, and the three SCs have no integration case
  to cite — pm must grade them `not_met` at goal-check for a planning reason no build retry fixes.
  **Repair:** either add the three assertions to T-01's section, or re-declare SC-04/06/08 as
  `verify: inspection` citing the task-verify receipts.
- **G-3 (med) — `plan.yaml` T-01 step (2), `BRIEF.md` SC-05.** `CONTRACT_SOURCES` and the "explicit
  expected floor" are both hand-typed in the same test, so the floor is derived from the artifact it
  grades. A seventeenth persona added to `validate-digest.py:238` `ALIAS`/`SCHEMAS` is absent from
  both and the count still meets the floor. **Consequence:** REQ-04's "reads as a named failure
  rather than a smaller passing count" holds only for today's roster — the exact silence REQ-04
  exists to end. **Repair:** derive the persona set from `validator.ALIAS` keys, as the file's own
  `_reviewer_template_paths` (`tests/integration/test-validate-digest.py:117`) already does, and keep
  `CONTRACT_SOURCES` as the path map only, FAILing on any ALIAS persona it does not cover.

## 5. Dependency shape — PASS (one low)

`T-01 [] → T-02 [T-01] → T-03 [T-01,T-02] → T-04 [T-03]` is a linear topological order. No verify
asserts anything a predecessor deletes. T-01's deliberate red is genuinely survivable: its verify
pipes the suite into `grep -qF`, so the pipeline status is grep's and the section prints its ok line
whatever the other sections do (`plan.yaml:66-67`, `:124-128`); the runners in `main()`
(`test-validate-digest.py:3892-3906`) accumulate counts and none aborts. T-03's full-suite verify
runs only after T-02 has closed the `code_grade` red and T-03 itself closes the three plan-mode
assertions.

- **G-4 (low) — `plan.yaml` T-03 verify, `BRIEF.md` SC-01.** Both gate on the WHOLE
  `tests/integration/test-validate-digest.py` suite going green, and neither the BRIEF nor the plan
  records a baseline that it is green at the branch point (no `observed ... at <sha>` line).
  I did not run it — out of this dispatch's scope. **Consequence:** any pre-existing unrelated FAIL
  reddens T-03 and burns build cycles diagnosing someone else's failure.
  **Repair:** record the measured baseline with its sha in `plan.yaml` before build starts.

## 6. Constraint compliance — PASS

`check-plan-routes.py` on this plan: **0 violations**; the single `DEVIATION` on T-01 is the expected
DEC-174 carve-out output. I re-derived the lanes rather than accepting them: `check-domain.sh
--resolve` returns `NOBODY` for `.claude/agents/harness-code-reviewer.md`,
`.omp/agents/harness-code-reviewer.md` and `.claude/skills/harness-code-review/SKILL.md` — the plan's
claim (`plan.yaml:17-25`) holds. `tests/integration/test-validate-digest.py` resolves to
backend-dev/dev-ops/qa, and DEC-174's ruling covers it — *"each gate's test included"*
(`DECISIONS-INDEX.md:177`) — so `main-session-direct` is correct, not a lane dodge.
`.harness/harness/docs/DECISIONS.md` resolves to `harness-documentor`, matching T-04.
DEC-207 is **not** re-legislated: D-03 (`plan.yaml:43-45`) leaves it unamended, and its index row
already rules plan mode legal (`DECISIONS-INDEX.md:207`). DEC-209/SEC-01/INV-6 are unweakened by
construction — no task's `files:` names anything under `.claude/skills/harness/bin/`.
Approvals are `pending` in both artifacts.

## Open questions

- Q1 (blocking): G-1 — widen T-02 to fix the `artifact:` line, or is correcting the persona's
  documented write path a separate ticket? REQ-01 as written is unmeetable without it.
- Q2 (non-blocking): G-2 — re-declare SC-04/06/08's verify method, or add the three integration
  cases to T-01?
