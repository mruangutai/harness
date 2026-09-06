# Code review — FEAT-55-issue-types-created-work — cycle 1

reviewed: `eb9d044e13383db77414f94b0e24409a15c7bbc0..cd6a3c0dee795ca9261d0ecf2e67df09d2e47b86`

## Stage 1 — spec compliance: PASS

Walked BRIEF.md's REQ-01..REQ-11 and plan.yaml's D-01..D-22 against the diff. Every changed
production line traces to a decision (D-01/02/03/04/05/06/12/14/18/20 govern the mapping and
provenance model; D-11 the single shared module `gh_issue_types.py`; D-13 the net-new
`backlog-issues.json`; D-21 the schema addition; D-22 the capability-call fix). No scope creep
found: `CHORE_TYPES` sets in both `gh-sync.py` and `factory_decompose.py` are untouched (D-06),
`github.issue_types` was not added to the shipped template (D-16), and no per-change_type override
key exists (D-12).

SC-04 (inspection): every `type_id` passed to `apply_issue_type`/`apply_type_args` on both routes
is `declared[type_name]`, and `declared` is built only from `node["id"]` in
`gh_issue_types.classify_capability`'s parse of the live GraphQL response
(`gh_issue_types.py:126-134`). No identifier is hard-coded. CONFIRMED.

SC-11 (inspection): `DECISIONS.md:6103` and `github-mirror.md:19` carry the identical eighth-purpose
row (verified character-for-character via the same regex the standing pin guard uses); the guard
itself (`tests/unit/test-issue-types-pin.py`) uses `re.DOTALL`, so the wrapping risk PF-bad4d5185
warned about does not apply to this pinned text (both rows sit on one physical line anyway).
CONFIRMED — SC-11 satisfied.

## Stage 2 — code quality: FAIL (one high, gated by the mechanical grader)

### The four leads

**1. Four-state provenance is read BY VALUE at every site — CONFIRMED.**
Swept every consumer of `typed`/`factory["typed"]` in both production files; every read compares
`== "created"` or `is True` (never bare membership/presence):
- `gh-sync.py:996,1003,1049-1060,1083` (`_parent_needs_type`, `_task_needs_type`,
  `_open_ensure_parent`, `_open_create_task`, `_backfill_issue_types`)
- `gh-sync.py:1639,1701` (backlog route — a boolean scheme since `backlog-issues.json` is a
  net-new receipt with no pre-existing legacy rows to protect against; still value-checked,
  `is True`, never key-presence)
- `factory_decompose.py:155-159` (`load_factory`'s load filter drops any value that is not
  exactly `True`/`"created"`/`"adopted"` — stricter than gh-sync.py's copy-through, see the info
  note below), `:400,404,437,444` (`_required_issue_types`, `_backfill_issue_types`)

Live-proved by `tests/integration/test-gh-issue-types.py` CASE J and
`tests/integration/test-factory-issue-types.py` CASE H: a fixture seeding a legacy
`feature.json`/`factory.yaml` with a recorded parent/task number and **no `typed` key at all**
(the exact 41-pre-existing-file shape) asserts zero `updateIssue` calls carry that issue's derived
node id, on the first run **and** on a rerun. These run the real binaries via subprocess against a
fake `gh`, not mocks.

**2. Pre-creation refusal precedes every create, backfill included — CONFIRMED.**
- `cmd_open` (gh-sync.py:1114-1128): `_refuse_undeclared_issue_types` runs before
  `_open_ensure_milestone`, `_open_ensure_parent`, the task loop, and `_backfill_issue_types`.
- `cmd_backlog` (gh-sync.py:1727-1740): `_refuse_undeclared_backlog_types` runs before both the
  create-or-skip loop and the `_backlog_apply_type` loop.
- `factory_decompose.py` `_main` (:507-518): `_refuse_on_missing_types` runs at step 4b, before
  step 5 (parent) and step 6 (task creates), and gates the step-4b backfill call too.
Proved live: CASE F (gh-sync) and CASE I/J (factory) each seed an already-recorded "created"
remnant needing an undeclared type and assert **zero** `issue create` and **zero** `updateIssue`
argv reach the fake, that the remnant's record is byte-unchanged, and the refusal message names
both the type and the `github.issue_types` key.

**3. Fail-open branches — CONFIRMED, byte-identical compatibility path.**
`query_failed` and `absent` are the only two non-`"available"` states; every type-apply site is
gated `if state == "available"` with no other entry point, in both files. Label byte-identity
checked against the pre-feature commit directly:
- gh-sync task labels `gh-sync.py:1073` == `eb9d044e:957` (unchanged)
- gh-sync backlog labels `gh-sync.py:1670` == `eb9d044e:1423` (unchanged)
- factory `ensure_labels`/`_task_labels` compat branches reduce to the exact pre-feature literal
  lists (`factory_decompose.py:395-397,341-349` vs `eb9d044e:325-332,395`)
`factory_gh.detect_issue_types` (:215-223) never raises past its own `try/except GhError`, so an
absent `gh` or a network failure classifies `query_failed` rather than crashing or defaulting to
`available`.

**4. New suites — genuinely discriminating, not gate-parity theater.**
Read all four new suites plus the unit pair. All exercise the real binary via `subprocess.run`
against a bash fake `gh` that derives its answers from the actual argv (`I_node<num>` parsed out of
`issues/<num>`), so a wrong node id or type id in a real call is caught, not just "some call
happened." Per-issue node+type pairing (CASE A/E in both gh-sync and factory suites), exact label
list equality (`labels_of(...) == [...]`, not substring), and the legacy-shape CASE J/H described
above are strong. **I could not find an assertion in the four integration suites whose failure
mode is unreachable given its own fixture** — the one pre-existing accepted risk
(PF-e74a2da89380cfa94f6b1693191d759d, the plan-level `verify:` CASE-marker grep loop) is about the
mechanical CI gate script, not these runtime assertions, and is already operator-ruled
`batched_to_signature_review` — not re-raised.

### Code-grade run (production bar 4, test bar 3), `merge-base` == `eb9d044e13383db77414f94b0e24409a15c7bbc0`

`python3 .claude/skills/harness/bin/code-grade.py --base eb9d044e13383db77414f94b0e24409a15c7bbc0 --head cd6a3c0dee795ca9261d0ecf2e67df09d2e47b86`

**must_fix (high, gates the build):**
- `.claude/skills/harness/bin/factory_decompose.py:208` `write_factory.transform` — CYCLOMATIC 5,
  COGNITIVE 4, ABC 20.5, **GRADE 3** in a bar-4 zone, driver `abc`. This diff's own change is what
  crosses the line: the added `"typed": dict(sorted(factory.get("typed", {}).items()))` entry in
  the `doc["factory"]` literal (factory_decompose.py:241) pushes ABC from just under 20 to 20.5,
  the exact grade-4 ceiling. Not grade 2, so it blocks per the code-risk-grading bar. Concrete
  consequence: this closure now carries five sibling dict/list-comprehension assignments plus the
  new sorted-dict one in a single unbroken block — a future editor adding a sixth field (as this
  feature just added the fifth) has no seam to extend without repeating the same regression, and
  the function is harder to review as one unit than as, e.g., a `_factory_doc(factory)` helper
  extracted from the closure body.

**med (grade 2, does not block; reason recorded per record):**
- `.claude/skills/harness/bin/gh_issue_types.py:105` `classify_capability` — CYCLOMATIC 15,
  COGNITIVE 16, ABC 28.7, GRADE 2, driver `cyclomatic+cognitive+abc`. Reason: this is the single
  four-state discriminator T-01/T-02 deliberately keep as one function (see gh_issue_types.py's own
  module docstring and T-02's intent: "mapping data, response parsing and argv builders only") —
  splitting the parse/errors/absent/available branches into helpers would scatter the one place the
  whole feature's safety property ("never read a failure as absent") is checked and re-verified
  against. Accepted as designed complexity, not incidental.
- 21 test functions across the four new integration suites — every `case_*` function in
  `tests/integration/test-gh-issue-types.py` (`case_a_b:233`, `case_c_d:264`, `case_f:320`,
  `case_g:350`, `case_h_h2:381`, `case_j:429`, `case_k:470`), `test-gh-backlog-issue-types.py`
  (`case_a_b:171`, `case_c:199`, `case_d:225`, `case_e:256`, `case_g:313`, `case_h:346`), and
  `test-factory-issue-types.py` (`case_a_b:293`, `case_c:336`, `case_d:367`, `case_e:398`,
  `case_f:433`, `case_h:489`, `case_i:539`, `case_j:583`). Reason, one shared cause for all 21: each
  is one arrange-act-assert scenario read top-to-bottom by a human debugging a failing `check()`
  line, and the grader's cyclomatic/cognitive weight here comes almost entirely from the
  `any(...)`/`not any(...)` generator-expression conditions inside each `check(...)` call, not from
  nested control flow a reader must trace — there is no branching between the checks themselves.
  Splitting each case into micro-helpers would force a reader to jump files to reconstruct one
  scenario's fixture-to-assertion story, which is a worse trade for test code at this project's
  established one-case-one-function convention (already used by `test-gh-sync.py`'s own case
  functions, which are not part of this diff). Accepted per the code-risk-grading skill's own bar:
  test code stops gating at grade 3, and all 21 measure grade 2, none grade 1.

### New finding

- **low** · `tests/manual/probe-issue-types.py:70-73` (owning task: T-10; the fix that makes this
  stale is D-22/T-04) — the comment claims *"gh-sync.py's detect_issue_types appends --repo
  anyway; that call path is exercised only against test-gh-sync.py's fake gh... so the
  incompatibility is invisible there (see this probe's own receipt/open_questions for the live
  finding)"*. This is now false: `gh-sync.py:929` (`detect_issue_types`) calls
  `gh_issue_types.capability_query_args(repo)` directly with no `--repo` appended, and its own
  matching comment was correctly removed. Operator ruling F-02
  (`notes/answers-build-blockers-20260905.md`) explicitly said to "delete its false explanatory
  comment" — that was done in `gh-sync.py` but a second copy of the same false claim survives
  here, in a different file the F-02 fix never touched (T-10 depends on T-02/T-09, not T-04).
  Failure scenario: a future maintainer reading this comment believes gh-sync.py's live capability
  detection is still broken against real `gh` (the exact defect F-02 fixed) and either re-opens a
  closed issue or "corrects" already-correct code back into the broken state. No functional impact
  today — `_classify` itself already omits `--repo` correctly.

### Minor code-quality note (not gating, not one of the four leads)

`gh-sync.py:568-569`'s `load_recorded` copies the *entire* `typed` dict through unfiltered
(`dict(typed) if isinstance(typed, dict) else {}`), unlike `factory_decompose.py`'s
`load_factory` (:155-159), which drops any value outside `{True, "created", "adopted"}` on every
load. Every consumer still compares by exact value (see lead 1), so this is not a REQ-10 risk
today, but it is an asymmetry between the two loaders worth noting for a future reader who might
assume both self-heal a corrupted receipt the same way. Severity: info.

## Summary

```yaml
VERDICT: FAIL
DIGEST:
  headline: Spec compliance and the four leads all hold under live-binary tests, but the mechanical grader finds one production regression (grade 3 in a bar-4 zone) this diff itself introduced, which gates.
  severity_max: high
  findings: 24
  must_fix: ["factory_decompose.py:208 write_factory.transform — GRADE 3 (CYCLOMATIC 5, COGNITIVE 4, ABC 20.5, driver abc) in a bar-4 production zone, regressed by this diff's own added typed-field serialization"]
  spec_violations: []
  code_grade: fail
  reviewed: "eb9d044e13383db77414f94b0e24409a15c7bbc0..cd6a3c0dee795ca9261d0ecf2e67df09d2e47b86"
  human_commits_in_scope: []
  open_questions: []
  files_touched: []
  expertise_update: []
artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-55-issue-types-created-work/.harness/harness/features/FEAT-55-issue-types-created-work/notes/review-harness-code-reviewer-c1.md
```
