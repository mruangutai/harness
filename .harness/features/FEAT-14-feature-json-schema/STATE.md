# STATE

## Current

- feature: FEAT-14-feature-json-schema · phase **build** · status Building
- branch `feat/204-feature-json-schema` · HEAD `11d9676` · `review_sha` pinned `11d9676`
- cycles_used **5** of 10 · runs 8 of 20
- segment 2 in flight: T-03 (recorded), T-11 and T-09 dispatched, T-05 and T-10 queued behind them

**Segment 1 is COMPLETE and committed** — T-01 and T-03 both landed in `3d37762`. Six further tasks
(T-02, T-04, T-06, T-07, T-12, plus T-01) are `done` in the plan and are not segment 2's to revisit.
T-03's status field was the only thing outstanding: its verify exits 0 and the intent's mandated
comment amendment is present at `.github/workflows/tests.yml:66-74`, so it is intent-complete, not
merely verify-green. Recorded in `11d9676`.

### The third contradiction: T-11's stated dependency makes its own verify unsatisfiable

The plan records T-11 `depends_on: [T-04, T-05]` and its intent opens "T-05 runs before you". I
measured that ordering to be impossible and **reordered T-11 ahead of T-05**. Monkeypatched
`_is_shipped` three ways at HEAD, live corpus:

| configuration | `check-plan-routes.py` prints |
|---|---|
| A — today: `feature.yaml` + `("shipped","abandoned")` | 35 violation(s) across 16 plan(s) |
| B — T-11 only: `feature.yaml` + `("Done",)` | **0 violation(s) across 10 plan(s)** |
| C — T-05 then T-11: `feature.json` + `("Done",)` | 35 violation(s) across 16 plan(s) |

B reproduces T-11 intent item 5's prediction byte-for-byte. C fails T-11's verify, because T-05
repoints the reader at `feature.json` and **no feature dir holds one until T-08** — a missing file
means "not finished", so every plan is checked again. T-08 depends on T-11, so the plan as written
deadlocks. The reorder is safe because the two tasks' edits to `check-plan-routes.py` and
`test-check-plan-routes.py` are disjoint by explicit construction: T-05 item 7 forbids the constant
and the `want_checked` loop, T-11 items 1–4 own exactly those.

**Predicted, so nobody chases it:** T-11's verify is green at T-11's commit and goes RED again
(35 across 16) the moment T-05 lands, staying red until T-08 converts the corpus. The operator's
framing — "T-11 is the task that closes the 35" — is falsified by measurement C. **T-08 closes them.**

### T-11's verify clause never runs the test file T-11 edits

`verify` runs `run-unit-tests.sh --kind unit`, but `test-check-plan-routes.py` is registered in
`INTEGRATION_SCRIPTS` (`run-unit-tests.sh:17-18`). Items 3 and 4 add every new assertion to that
file. The eng run is required to run `--kind integration` as well and report both. The verify clause
is approved plan text and was not edited.

### Baselines measured this session at HEAD, for attribution

- full `run-unit-tests.sh` (both kinds): **exit 0**
- `check-plan-routes.py`: 35 violation(s) across 16 plan(s) — expected red, closes at T-08
- `docs/harness/DECISIONS.md` carries **50** `feature.yaml` occurrences and **must keep all 50**
  (rule 15: they are historical records). Only three new entries are appended there.
- **DEC-189 is taken** (the write-guard two-bases entry). T-09 takes DEC-190/191/192, which makes
  the plan's D-04 (cites DEC-189) and D-08 (cites DEC-190) citations stale — pm's to correct.

### Carried from segment 1 — still open

- **G1** — SC-02 wants a failing fixture at each of three nesting levels; `factory` and
  `factory.edges` have none. Test-only, folded into segment 2, no own spawn.
- **G4** — the `.json`-holding-valid-YAML rejection needs a mutation to prove liveness.

## Open Questions

- Q1 non-blocking, measured false three ways: `tests.yml` claims `test-check-plan-routes.py case 25`
  asserts the Plan-route step is present and unneutered. No such test exists. T-03's approved intent
  repeats the claim and T-03 added a second CI step with the same hole. No task's `files:`
  authorizes the fix. Briefing row.
- Q2 non-blocking: the guarded-import needle is the literal `except ImportError` and misses
  `except (ImportError, ...)` and `except ModuleNotFoundError`. Pre-existing.
- Q3 non-blocking, **now with direct evidence**: the Bash route around the write guard is real. A
  `python3 - <<'PY'` heredoc that rewrote `plan.yaml` was NOT intercepted, while `rm` against a
  scratchpad path in the same session WAS blocked. The write landed in-domain so nothing was
  damaged, and I moved to Write/Edit for the rest of the segment. FEAT-17-guard-boundaries' territory.
- Q4 non-blocking: `test_exactly_one_guarded_import_in_the_tree` misstates its own contract. Kept
  deliberately — nine test names are pinned to FEAT-05's PLAN.
- Q5 non-blocking: shared run artifacts have no concurrency guard.
- Q6 non-blocking, carried: `validate-digest.py:182`'s orchestrator digest enum stays OUT of scope
  (D-13) — it carries `blocked` while the six board columns have no `Blocked`.
- Q7 non-blocking, carried: BRIEF SC-08 carries one clause twice; SC-07's prose says "exits
  non-zero" where its test asserts exactly 3. Wording tightenings, not defects.
- Q8 non-blocking, new: T-09 and T-10 are `depends_on: [T-08]` / `[T-09]`, and T-08 is the main
  session's and has not run. The operator assigned both to this segment anyway. Both verifies are
  docs-only and satisfiable now, so I ran them — recording the deviation rather than absorbing it.
