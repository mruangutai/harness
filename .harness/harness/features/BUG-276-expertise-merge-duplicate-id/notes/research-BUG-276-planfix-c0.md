# Plan fix — BUG-276, goal-check must_fix applied

**All six findings from `notes/research-BUG-276-goalcheck-plan-c0.md` are applied; BRIEF and plan
are now internally consistent and no claim in either is unsupported.** No instruction in
`plan.yaml`, executed literally, now fails a criterion in `BRIEF.md`. Neither the FIX's scope nor
the BUG's scope changed. The two answered questions were applied, not re-argued: F-03 trimmed to
codes 9 and 11 (Q1 = TRIM), F-02 restated rather than struck (Q2 = RESTATE).

## What changed, by finding

| Finding | Edit | Where |
|---|---|---|
| F-02 | the false field-evidence sentence replaced with the truthful dating | `BRIEF.md` Problem, ~12-18 |
| F-01 | the false "fully closed by refusing the ambiguous input" clause corrected, twice | `BRIEF.md` last Constraints bullet; `plan.yaml` D-06 `because` |
| F-03 | STEP 3 now adds ONLY 9 and 11, and says why 10/12 must not be added | `plan.yaml` D-05 `choice` + `because`, T-01 `intent` |
| F-01 | new decision recording the parse/render drop as a separate known defect | `plan.yaml` D-07 |
| F-06 | one clause naming SC-04's evidence as the pre-existing case | `plan.yaml` T-02 `intent` |
| F-05 | both verify blocks strengthened to assert behaviour directly; position recorded | `plan.yaml` T-01/T-02 `verify`, D-08 |

D-06's *decision* is untouched — monotonicity and content-presence remain out of scope; only its
reason was false and is replaced.

## F-05: position (a), STRENGTHEN — and it is measured, not asserted

Each verify keeps its `PASS <name>` greps and gains one behaviour assertion that no check name can
satisfy. Both were **run at 6d969ed3 before being written into the plan**, standalone, because an
`&&` chain short-circuits at the first failing grep and a new final conjunct's redness is otherwise
assumed rather than observed:

- T-01's addition (module loaded by path, `compute_union` must raise code 11): **exit 1**, 0.05s.
- T-02's addition (real CLI, duplicate proposal, temp `.harness/expertise/` destination, exit 11
  expected): **exit 1**, 1.25s — and it reproduced the defect verbatim,
  `ADDED P-02 / PRESERVED P-01 / APPLIED <path>` at exit 0.

Both remain single shell blocks, both are literal `|` scalars in the file (verified: newlines
survive the amend, 23 and 25), both far under 60s. The temp-tree writes go through python's
`open()`, never a shell redirect, so `bash-write-guard.sh` does not deny the verify.

## Evidence the file is intact

- `plan-merge.py` amend/apply succeeded on every write — seven amends (`D-05.choice`,
  `D-05.because`, `D-06.because`, `T-01.intent`, `T-02.intent`, `T-01.verify`, `T-02.verify`) plus
  one `apply` adding D-07 and D-08. No Edit, no Write, no redirect touched `plan.yaml`.
- `safe_load` round-trips: `approval: {status: pending}`, no `panel:` key, decisions D-01..D-08,
  tasks T-01/T-02, no backticks or markdown in any decision value.
- `check-plan-routes.py <plan>` → `0 violation(s)`, exit 0.
- `amend --key tasks --id T-01 --field intent --show` → STEP 1 (line 10), STEP 2 (line 43),
  `CONSTRAINTS. python3` (line 69) all present; `MISSING TARGET` and `MALFORMED OPS` absent. The
  splice was diffed against the pre-amend value and the difference is confined to STEP 3's four
  lines.
- `BRIEF.md` SC-06 is byte-unchanged; the reproduction (Problem, lines 5-11) and the
  `check-expertise.sh` blindness sentence are intact; neither false clause survives anywhere.

## F-03's contradiction, closed

The docstring table holds 0, 6, 7, 8 today. T-01 now adds exactly 9 and 11, giving 0/6/7/8/9/11 —
precisely the set `apply` can return (`cmd_apply` :470-474, :492-510, plus the new guard). SC-06
grades "every code apply can return, and no code it cannot": executed literally, T-01 now **meets**
it where before it failed it.

## Open for the operator, at signature

- **D-07 wants its own ticket.** The parse/render silent drop is real, reachable after this fix, and
  no live Expertise file trips it today (goal-check F-01). Recommended as a separate bug.
- **F-04 stands unaddressed by design**: the dispatch said "keeping only the last-seen one"; it is
  FIRST-wins. BRIEF and plan both record the measurement correctly — say the correction out loud so
  the operator does not sign with an inverted model.
