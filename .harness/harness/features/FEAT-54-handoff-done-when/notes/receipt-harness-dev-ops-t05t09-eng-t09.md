# Receipt — harness-dev-ops — FEAT-54 T-09 (persist comprehension probe)

## VERDICT: BLOCKED — genuine plan/repo mismatch, not implemented

T-09's `files:` list and D-04 both pin the new probe's path to
`.claude/skills/harness/bin/probe-handoff-comprehension.py`. That path is incompatible with a
currently-enforced, currently-green repository invariant: `suite_layout.violations()`
(`.claude/skills/harness/bin/suite_layout.py:29-33`) unconditionally flags *any* file matching
`test-*.py`, `*.test.*`, or `probe-*` sitting directly under `.claude/skills/harness/bin/` as
`"test-shaped file remains under bin: <path>"` — with **no exception for registration in
`test_kinds`**. This is not incidental: `tests/unit/test-suite-layout.py:92-94` ("all layout
violations reported") plants exactly `.claude/skills/harness/bin/probe-planted.py` and asserts it
counts as one of 4 expected violations, and `"real layout is valid"` (line 50) asserts the live
tree currently has zero violations.

## Evidence

- Empirically confirmed: planted an empty `.claude/skills/harness/bin/probe-test-scratch.py`,
  called `suite_layout.violations('.')` — returned
  `["test-shaped file remains under bin: .claude/skills/harness/bin/probe-test-scratch.py"]`.
  Removed the scratch file immediately after (git status confirms it's gone).
- `env -u HARNESS_AGENT_TYPE python3 tests/unit/test-suite-layout.py` → exit 0, all 20 cases PASS
  as of HEAD (63af2eda), including `"real layout is valid"` and `"all layout violations reported"`.
- The precedent probe this task was told to follow the shape of,
  `probe-omp-session-accessor.py`, in fact lives at `tests/manual/probe-omp-session-accessor.py`,
  **not** under `bin/` — consistent with `suite_layout.py` forbidding probe-shaped files in
  `bin/` regardless of `test_kinds` status. `omp_session_accessor`'s `test_kinds` entry
  (`.harness/harness.json:277-283`) points `detect`/`cmd` at `tests/manual/…`.
- `run-unit-tests.sh` (current, post-`139f6afe` "move tests to directory-based suites") has no
  `KINDCHECK` heredoc / `UNIT_SCRIPTS` / `INTEGRATION_SCRIPTS` at all — it delegates layout
  enforcement entirely to `suite_layout.violations()` before running `run_pool.py`. Several of this
  feature's own research notes (`notes/research-FEAT-54-goalcheck-plan-c2.md:147`,
  `notes/review-harness-code-reviewer-planpanel-c0.md:41-45`) still describe the pre-migration
  `KINDCHECK`/`UNIT_SCRIPTS`/`INTEGRATION_SCRIPTS` shape at length; the plan's D-04/T-09 text
  ("run-unit-tests.sh's probe-drift check requires exactly this shape and exits 2 on any other")
  reads as written against that same stale mental model, not the live `suite_layout.py` gate.

## Why I did not implement anyway

Writing the probe at the plan-specified path would turn a currently-green test
(`test-suite-layout.py`'s `"real layout is valid"`) red, and would make
`run-unit-tests.sh` exit 2 on `MISCONFIGURED: test-shaped file remains under bin: …` — a failure
directly *caused* by the two files this task is scoped to (not a pre-existing red I could
attribute to another script), which the dispatch's own "Drift check" step is explicit I must not
paper over. My write scope is exactly the two named files; resolving this needs either a third
file edit (`suite_layout.py`, to exempt `probe-*` files that are registered `locally_run` in
`test_kinds`) or relocating the probe to `tests/manual/` alongside its stated shape-precedent —
both are plan/decision changes, not mine to make.

## What I did do

Nothing written to either target file. No `.harness/harness.json` edit. No probe file. Working
tree is otherwise as T-05 left it (`_handoff_done_when_baseline_note` /
`handoff_done_when_baseline`, 141 paths, unchanged and unread past inspection).

## Open question for the plan owner

Q1 (blocking): Either (a) relocate the probe to `tests/manual/probe-handoff-comprehension.py` to
match `probe-omp-session-accessor.py`'s actual, tested-safe location and amend D-04/T-09's `files:`
accordingly, or (b) add a `suite_layout.py` exemption for `bin/`-resident probes that are
registered `locally_run` in `test_kinds` (a third file, a scope change, and a design decision about
the layout invariant) and amend T-09's `files:` to include it. Either resolution needs a plan
amendment before this task is re-dispatched.
