# QA cycle 1 — BUG-1071 era guard, coverage & matrix gate at 6b65ecc

**BLUF: PASS.** All three raw-number claims measured exactly as stated. All three
targeted mutants (the `_MISSING`-sentinel collapse, the F1 `bad`→`warn` regression, the
malformed-era stale-value bug) reddened their case via the real, unmodified case
functions — no mutant files left behind. The five-row `panel_era_start` table is fully
bound; the date×era cross-product has two genuine but low-risk coverage gaps (both info),
protected either by unconditional code ordering or independent, redundant guards. The
un-upgraded-project VIOLATION fires exactly once across 5 simulated plans, confirming the
"resolved once, above the loop" design — but no permanent test pins that property.
Test-first ordering is **unverifiable** for all three commits: production and test edits
land in the same commit each time.

## 1. Raw numbers — all three claims confirmed, not accepted

| Command | Claimed | Measured |
|---|---|---|
| `test-check-state.py` | 155 ok / 0 FAIL, exit 0 | **155 ok-lines / 0 FAIL, exit 0.** (154 lines match `^ok - `; case `(d)` prints `ok   case (d): ...` — three spaces, no dash — which is why a naive grep undercounts by one. Confirmed pre-existing format, not new.) |
| `check-state.sh` | exit 0 / 0 violations / 32 INV-32 notes | **exit 0, 0 `VIOLATION` lines anywhere in 691 total lines, 32 `INV-32` lines, all 32 `note` (0 `warn`, 0 `VIOLATION`).** All 32 are pre-era notes now — FEAT-40 is no longer "undated" (F1 backfilled `approval.date: 2026-08-25`), so the F1-era 31+1 split collapses to a uniform 32. |
| `run-unit-tests.sh` | exit 0, zero FAIL lines | **exit 0, 0 case-matching `FAIL` anywhere in 3416 lines of output; 1061 `PASS <script>` lines; `test-check-state.py` present and PASS.** |

No discrepancy on any of the three. FEAT-40's backfilled date is independently verified
against git: `2938a5c`, `2026-08-25 12:04:19 -0700`, message "FEAT-40 the operator signs" —
matches the fix's own citation exactly.

## 2. Five-row `panel_era_start` coverage — every row bound

| Row | Case |
|---|---|
| no `harness.json` at all | every pre-existing INV-32 case (`_NO_CONFIG` default) — `case_inv32`, `case_inv32_unrated_severity_fails_closed`, etc. |
| key absent | `case_inv32_missing_era_key_is_a_violation` |
| `null` | `case_inv32_null_era_grades_everything` |
| valid `YYYY-MM-DD` | `case_inv32_pre_era_is_exempt`, `case_inv32_era_boundary_is_exact`, `case_inv32_era_comes_from_project_config`, `case_inv32_era_guard_is_load_bearing` |
| malformed | `case_inv32_malformed_era_exempts_nothing` |

No row is empty.

### Cross-product: `panel_era_start` × `approval.date` state

Code structure matters here: the undated/malformed-date check (line ~250) runs
**unconditionally, before `_era_start` is ever read** — so date=missing/malformed behaves
identically under every era state, and era-relative date behavior (pre/exact/post) only
has meaning when `_era_start` is actually non-`None`, i.e. only the **valid** row. That
row alone is tested for all three: pre-era (exempt), exactly-boundary (graded), and
post-era (`case_inv32_era_comes_from_project_config`'s 08-25-vs-08-20 pairing). The other
four rows collapse `_era_start` to `None`, so pre/exact/post are behaviorally identical
under them (structurally guaranteed by `if _era_start is not None and signed < _era_start`)
— not a gap, just not independently re-proven per row.

**Two genuine gaps, both info, no reachable defect scenario:**
- **Missing-key + missing-date, and malformed-era + missing-date together** (double
  violation): measured directly — both cases correctly emit *two independent* VIOLATION
  lines (config-level + per-plan) with no crash, no suppression. No permanent test pins
  this double-emission. Protected by two independent, unconditional checks, so a future
  regression would need to break both simultaneously to go unnoticed — low risk.
- **The "fires once, not once per plan" property** (§4 below): true and measured, but no
  test asserts it. A future refactor that moved the check back inside the loop would
  silently multiply the VIOLATION line with nothing red.

## 3. Mutation table — measured via the actual `case_*` functions, never reimplemented

| # | Mutant | Target case | Result |
|---|---|---|---|
| A | `.get("panel_era_start", _MISSING)` → `.get("panel_era_start", None)` (collapses key-absent into null) | `case_inv32_missing_era_key_is_a_violation` | **RED** |
| B | F1's `bad.append(...)` for missing/malformed `approval.date` reverted to `warn.append(...)` | `case_inv32_undated_approval_fails` | **RED** |
| C | Malformed-era branch's `_era_start = None` changed to `_era_start = _era_raw` (leaves the raw malformed string as a stale boundary; string-compares `"2026-08-30" < "last Tuesday"` → `True`, so the plan is wrongly exempted) | `case_inv32_malformed_era_exempts_nothing` | **RED** |

All three run through `tcs.case_inv32_*()` unmodified, with `tcs._inv32_run` monkey-patched
to target the mutant script — not a hand-rolled re-implementation of the assertion. Every
mutant was written to `.claude/skills/harness/bin/.mutant-{A,B,C}.sh` and deleted in the
same call; `.claude/skills/harness/bin/.mutant-*` confirmed absent afterward.

## 4. Un-upgraded-project VIOLATION cardinality — fires once, unbound by a test

Built a fixture with **5** approved plans and a `harness.json` lacking `panel_era_start`.
Observed: `exit 1`, and **exactly 1** line matching `panel_era_start` + `VIOLATION` across
all 5 plans — confirming "resolved once, above the loop" is real, not just commented.
**No existing case builds more than one plan doc**, so this cardinality property is
verified here but not pinned by any test in the suite (info-severity gap; the code's own
structure — resolution genuinely lives outside the per-plan loop — makes an accidental
regression unlikely, but not impossible under a future refactor).

## 5. Test-first audit — unverifiable from commit history

```
bf12a96  check-state.sh + test-check-state.py (both touched, one commit)
f11b41a  check-state.sh + test-check-state.py + FEAT-40 plan.yaml (one commit)
6b65ecc  check-state.sh + test-check-state.py + harness.json + templates/harness.json (one commit)
```

Every commit bundles production and test edits together; git history cannot distinguish
red-before-green from green-then-tests-after within a single commit. `handoff-build.md`
(written at `bf12a96b`) asserts the original four cases were RED first "verified-at
75daa3bb + working tree" — a working-tree claim, not something re-derivable from the
committed history now. No updated handoff note exists covering F1/F2's four new cases, so
their ordering claim is likewise unverifiable from the repo alone. Not rated as a finding —
the dispatch itself notes this is main-session-direct work under DEC-174, out of scope to
fault for process.

## Test-matrix gate

`logic` change type, `unit` always required. `test-check-state.py` is part of the diff and
is the unit surface; confirmed present and PASS under `run-unit-tests.sh --kind unit` (line
2025: `PASS test-check-state.py`). No `ai_behavior`, `ui`, `component`, or external-service
`integration` surface touched. **`matrix_ok: true`.**

## Tree state

All mutant/scratch files (`/tmp/*.py`, `.claude/skills/harness/bin/.mutant-*.sh`) were
either outside the tracked tree or deleted in the same call that created them; confirmed
absent by directory listing after each mutation run. No permanent test cases were added.
