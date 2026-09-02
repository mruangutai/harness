# Review — PR #1250 (BUG-613-expertise-near-budget)

VERDICT: **PASS** (notes only, nothing blocking)

## Stage 1 — spec compliance (informal spec: issue #613, no BRIEF/plan in this direct-flow PR)

Issue #613 asked for: a near-budget ADVISORY in `check-expertise.sh`, threshold ≈10% of the tier
budget, message shape `ADVISORY … N lines of a M-line budget; the next entry must displace, not
append`. The diff delivers exactly this — no more, no less:

- `check-expertise.sh`: `NEAR_BUDGET_FRACTION = 10` + the threshold check, both tiers.
- `test-check-expertise.py`: 9 new cases (`case7:` block).
- `SPEC.md`: one paragraph documenting it, placed right after the existing token-advisory
  paragraph, same "ADVISORY (never blocking)" phrasing.

No scope creep, no missing piece. Extending the advisory to the repo tier (issue's examples were
all craft-tier) is a documented, correct generalization — `inject-expertise.sh` truncates both
tiers by the same mechanism, so the headroom signal is equally real for repo files. Not a spec
violation.

## Stage 2 — code quality

**Threshold math (item 1) — correct.** `near_budget_threshold = line_budget - line_budget //
NEAR_BUDGET_FRACTION` gives 135 for craft (150-line budget, 15 lines headroom) and 36 for repo
(40-line budget, 4 lines headroom) — verified by direct computation, matches the code comment and
`SPEC.md`'s "within 10%" claim.

**Boundary condition (item 2) — correct, verified live.** `near_budget_threshold <= len(lines) <=
line_budget` is a closed interval capped at `line_budget`; the hard-failure check is `len(lines) >
line_budget` (strict). These ranges are structurally disjoint — over-budget can never also be
near-budget — so double-reporting is impossible by construction, not just by test luck. Ran
`check-expertise.sh` on a synthetic 151-line craft file: `over budget` fires, no `ADVISORY`. Ran it
on an exact-150-line file: `ADVISORY` fires (`0 of headroom`), no over-budget problem — the
exact-budget boundary is correctly folded into the advisory, not missed.

**Test coverage (item 3) — a real but low-risk gap.** Computed the two threshold values directly:
craft=135, repo=36. The new tests exercise 140/130 (craft) and 37/30 (repo) — all comfortably
inside or outside the window, never at the threshold itself (135/134) or its repo equivalent
(36/35). Ran the full `test-check-expertise.py`: 31/31 pass. An off-by-one in the threshold formula
(e.g. `<` instead of `<=`, or `- 1`) would not be caught by any of the 9 new cases — none of them
pins the exact edge. Given the change is advisory-only (never affects exit code or `problems`), the
blast radius of such a regression is a cosmetically wrong line count in a warning message, not a
build break — so this is a should-fix test-hygiene note, not a must-fix.

**ADVISORY message format (item 4) — matches the grep-able convention, one wording nit.** Both the
existing (issue-340) and new advisory strings share the `ADVISORY {path}` prefix that any grep for
`^ADVISORY` picks up, and the new one is clearly a file-level (no `:{lineno}`) variant, which reads
sensibly. Two purely cosmetic inconsistencies, neither functional: (a) the new message reads `({N}
of headroom)` — missing "lines", should read "{N} lines of headroom"; (b) the new message ends
with a trailing period, the pre-existing issue-340 advisory does not. Confirmed by running the
check against a synthetic 140-line file: `ADVISORY …: 140 lines of a 150-line budget (10 of
headroom) — the next entry must DISPLACE an existing one, not append (issue #613).`

**Test ordering nit.** The new `case7:` block is spliced in between the pre-existing `case5:` and
`case6:` blocks (`test-check-expertise.py`), so run order is 5, 7, 6. Purely cosmetic — labels are
strings, not an enforced sequence — but a future reader skimming top-to-bottom will find the
numbering confusing.

**`code_grade`** — ran `code-grade.py --base <merge-base bde73ad3> --head HEAD`: `PASSING: 0`,
exit 0. The only changed `.py` file (`test-check-expertise.py`) only edits inside an existing
function (`run_extra`); no new or worsened gated function. `check-expertise.sh`'s embedded Python
(a heredoc inside a `.sh` file) is outside `code-grade.py`'s scope entirely — expected, not a
defect of this PR.

## Verdict rationale

No `must_fix`, `severity_max = low`. The two message-wording nits and the boundary-test gap are
`should_fix` at most — none change behavior a caller depends on, none affect the exit code, and the
core arithmetic/boundary logic is provably correct by construction (disjoint ranges) and confirmed
live against both edges (150, 151).
