# Plan-panel c1 — scope read — FEAT-55

**BLUF: one high-severity gap. REQ-07's "refuse before creating any issue" is implemented for all
three creation commands (T-04/T-06/T-08 all `traces: [..., REQ-07, ...]`) but is red-then-green
tested for exactly one of them.** T-03 (gh-sync `open`) has case F, `FAKE_TYPES=partial`, that
proves zero creates reach the fake and a non-zero exit before any `issue create`. T-05 (gh-sync
`backlog`) and T-07 (factory) have **no such case** — confirmed by reading every case letter in
both tasks' `intent:` (T-05: A–F; T-07: A–H) and by `grep`ping the whole plan for `FAKE_TYPES=partial`,
which occurs only inside T-03's intent (`:361`, `:403-405`). Yet T-06's intent (`:680-683`) and T-08's
intent (`:860-865`) both independently implement the identical missing-types-then-exit-2-before-create
logic for their own routes, and both tasks `traces: [..., REQ-07, ...]` (`:646`, `:808`) — while T-05
(`:572`) and T-07 (`:713`) that are meant to prove it RED do not even trace REQ-07. A bug in either
implementation (checks only the first item, refuses after some creates already reached `gh`, or
mis-orders the check relative to `apply_issue_type`) ships with every plan-defined gate green: T-06's
`verify` only runs `test-gh-backlog-issue-types.py` + `test-gh-sync.py`, T-08's only runs
`test-factory-issue-types.py` + `test-factory-decompose.py` + `test-unit/test-factory-gh.py` — none
of which contains a partial-types fixture for these two routes. BRIEF SC-08 does not name a route
(unlike SC-01/SC-07, which do), so nothing in the BRIEF forces per-route coverage either; the gap is
real end to end, not just a plan-text omission.

## Secondary finding — bounded, not gating

**T-06's own `verify:` does not run T-03's test file, though T-06's `intent:` says it should**
(`:653-654`: "tests/integration/test-gh-issue-types.py and tests/integration/test-gh-sync.py must
both still pass — test-gh-sync.py is in your verify, run test-gh-issue-types.py too and report").
T-06 edits `main()`'s trailing-parameter wiring and reuses `detect_issue_types`/`apply_issue_type`
in the same file (`gh-sync.py`) that T-04 just changed for `cmd_open`'s typed branch. A miswiring
introduced while routing `issue_types` into `cmd_backlog` could regress `cmd_open`'s "available"
path without T-06's mechanical gate (`:650-652`) ever noticing — only a full-suite run at QA time
would surface it, and only because the intent says so, not because anything enforces it. T-08's
verify, by contrast, runs all three files its own intent names — this pattern is T-06-specific.

## What I checked and found clean

- **Orphan/dangling traces:** every task trace resolves to REQ-01..REQ-11 (all eleven exist and are
  each owned); no SC id cited where a REQ was meant.
- **Dependency shape:** the twelve-task graph (`T-01→T-02→{T-03,T-05,T-07}→...`, `T-09`/`T-11`
  independent, `T-12→T-11`, `T-10→{T-02,T-09}`) is a valid DAG in declared numeric order; no cycle,
  no missing edge for a shared-file dependency I could find (T-06 correctly depends on both T-04
  and T-05; T-08 transitively reaches T-02 through T-07).
- **`files:`/lane routing:** every task's declared file(s) match the `lanes:` row's surface and its
  `execution_agent`/`execution_mode` is a member of that row's agent list (T-12's
  `main-session-direct` correctly matches the DEC-174 carve-out row).
- **D-18 REFINES D-02:** no downstream task still implements the superseded "feature→Feature"
  reading — `DEFAULT_TYPE_BY_CHANGE_TYPE["feature"] = "Task"` (T-02), and every fixture with a
  feature-`change_type` task (T-01 §5, T-03 case A, T-07 case A) asserts `IT_task`, never
  `IT_feature`.
- **T-12's byte-identical-wording regex** (`re.compile(r'whether a target repository supports
  native Issue Types.*?explicit create opt-in')`, no `re.DOTALL`) looked like it could false-fail
  if the pinned ~500-char sentence wrapped across lines in either target file. Checked against the
  files' own convention: `DECISIONS.md` already carries single lines up to 929 chars (measured,
  `awk` length sort) and `github-mirror.md`'s existing read-back table rows are single-line cells
  of comparable length — no wrapping convention exists in either file, so the regex is sound
  against this codebase's actual style. Not a finding.
- **Sampled goal-check closures against the plan text directly (not the repair notes' prose):**
  F-05 (`"feature": "Task"` in T-02, D-18/D-02 rewrite) — confirmed. F-03 (T-11 §3 / T-12 §1
  byte-identical eighth-purpose wording) — confirmed identical. N-01 (positive-provenance-only
  read, key-presence test prohibited) — confirmed in T-04 §6 and T-08 §8 language. c3's repairs —
  the `CASE $c:` per-case marker loops are present in T-01/T-03/T-05/T-07's `verify:` exactly as
  claimed, BRIEF SC-12 exists, and T-05 case E now asserts `typed` "exactly false — not absent, and
  not a missing item key." All genuinely closed, not prose-only.

## Open question for the panel

Is REQ-07's per-route test coverage a plan-time gap the panel should send back (add a
`FAKE_TYPES=partial`-style refusal case, T-05 case G / T-07 case I, and add REQ-07 to both tasks'
`traces:`), or is single-route coverage (T-03) an accepted floor because the three refusal
call sites share `gh_issue_types.missing_types`/`refusal_text` and only the surrounding
caller code differs? I did not decide this — it changes what ships red-then-green, which is the
operator's call at signature.
