# plan-panel c6 — scope reader — BUG-1286-test-tree-enforcement

**Conclusion: the case-11 partition, as written, has a genuine third defeat — a substitution mutant
that keeps case 11 fully GREEN while reproducing exactly the counted-by-map/no-runner-reach gap the
amendment exists to close.** Two lower-severity issues also found. Everything else probed (the
one-fence contract's identity across all three sites, SC-06/T-03-counts/T-04-dispositions surviving
the widening, REQ/SC traceability, `depends_on` topology, verify vacuity, all cited anchors) checks
out.

## Findings

### F1 — HIGH — case 11's literal-prefix check does not normalize `..`, so a clean substitution stays GREEN

Case 11 excuses a directory-only glob when its *literal prefix — the leading segments before the
first wildcard segment, joined by `/` — is exactly `"tests"` or `str.startswith("tests/")`*. That
is a pure string operation on the unresolved glob text; the spec never normalizes `.` / `..`
segments before the comparison.

Substituting `tests/../evil/**` for `tests/unit/**` in **both** `.harness/harness.json` and
`.claude/skills/harness/templates/harness.json` (a one-for-one substitution, structurally identical
to the already-verified-RED `docs/**` mutant) mechanically traces as:
`segs = ["tests", "..", "evil", "**"]` → first wildcard segment is `"**"` at index 3 → literal
prefix = `"tests/../evil"` → `"tests/../evil".startswith("tests/")` is **True** → **EXCUSED**.

I ran the full case-11 algorithm (partition, synthesis, `is_test_shaped` judgment) against this
exact mutant string: rogue set `[]`, excused count `1` (unchanged from today — the "exactly one
excused" side-assertion does not fire either), all three basename globs still synthesize and pass.
**Result: GREEN**, end to end, mechanically verified, not inferred.

Consequence: `tests/../evil/**` in `unit.detect` makes qa's kind map count *every* file under
`evil/` (a directory entirely outside `tests/**`) as a unit test, unconstrained by any basename
check because the glob is directory-only — so the repository-wide guard (which only ever inspects
basenames) refuses none of them — and unreachable by `run-unit-tests.sh` (which selects only
`tests/unit` and `tests/integration`). That is the exact "counted by the map, permitted by the
guard, executed by no runner" defect BUG-1286 exists to close, reproduced silently through the very
assertion GAP-1's fix was written to prevent. The same class of defeat needs no glob-string
trickery at all: a symlink placed at `tests/<name>` pointing outside the repository, paired with an
entirely ordinary-looking `tests/<name>/**` detect entry, defeats the same unnormalized
string-prefix check — that variant is even more realistic than the `..` string, since nothing about
the `detect` value itself looks unusual.

Remedy is not mine to specify (I am read-only and the two engineering-tier alternatives on
`violations()` itself are off the table), but the fix is local to the partition rule: normalize the
literal prefix (e.g. `posixpath.normpath` and re-check for any `..` component before the string
comparison) before deciding EXCUSED vs ROGUE.

### F2 — MED — the "exactly one excused" side-assertion has no remedy guidance distinguishing a legitimate widening from a partition regression

Case 11 additionally asserts "that exactly one of **today's** globs is EXCUSED, so a partition bug
that excuses every glob and empties the check cannot pass silently." Read literally this is a
hardcoded count, not a derived one — consistent with its own wording ("today's globs").

The rogue-set assertion carries an explicit remedy: "fix `detect`, or record why the new root is
genuinely discoverable … NEVER to delete, narrow or skip this assertion." No equivalent sentence
exists for the excused-count assertion. A legitimate future widening that adds a second, genuinely
safe `tests/`-rooted directory-only glob (e.g. a new `tests/e2e/**` kind) changes the excused count
from 1 to 2 and reddens this specific check — for a reason that has nothing to do with a partition
regression. The builder facing that red has no case-11-specific text telling them updating the
literal is the correct maintenance step, and the blanket "NEVER to delete, narrow or skip this
assertion" sitting in the same paragraph can be misread as covering it too. That is exactly the
"fails for the wrong reason, and the plan doesn't stop someone from mishandling it" shape the panel
was asked to probe — just via this side-assertion rather than via `harness.json` moving (which I
checked separately: a moved/renamed `.harness/harness.json` crashes the whole test file via the
same unguarded `repo_cfg["test_kinds"][kind]["detect"]` read six pre-existing assertions already
depend on, so that particular failure mode is inherited infrastructure risk, not new to case 11, and
its cause is unambiguous — not the risk worth flagging here).

### F3 — LOW — SC-12 misquotes T-03's zero-fenced-blocks message as identical to its two-or-more message

T-03 specifies **two distinct** stderr strings: zero blocks → `"note carries no fenced block:
{path}"`; two or more → `"note carries {n} fenced blocks, expected exactly 1: {path}"`. SC-12's own
text states both "a note carrying zero fenced blocks, or two or more" are refused with the *same*
quoted string, `note carries {n} fenced blocks, expected exactly 1`. That conflates T-03's two
messages into one. (T-04 is not guilty of this: it only cites the two-or-more message, which is the
only direction its own qa-authored note can plausibly trip.) Consequence: a reviewer grading SC-12
(`verify: inspection`) who takes the quoted string literally and builds a zero-fence test note would
look for a string that T-03's own spec never produces for that case, risking either a false rejection
of a correct implementation or a missed check that the zero-case message is what T-03 actually
requires.

## Falsification evidence — what I checked and did not find a problem in

- **Anchors, re-measured against the live tree, all match exactly:** `suite_layout.py:20-33` is the
  under-`tests/` clause plus the bin clause verbatim, matching BRIEF's "only looks in two places"
  claim. `tests/unit/test-suite-layout.py:100-103` (detect-matches-template loop), `:104-105`
  (manual-not-actively-detected), `:136-139` (runner-delegates-layout-once) all land inside the cited
  ranges. `tests/manual/suite-census.py:24` is exactly `re.findall(r"```(?:text)?\n(.*?)\n```",
  text, re.S)`, matching T-03's description of `baseline()`'s fence pattern. `run-unit-tests.sh:47`
  is exactly the one `run_pool.py --mutation-check "$BIN_DIR"` invocation SC-15 cites (47-line file).
  `--check-layout` already exists in `run-unit-tests.sh`, so T-01's verify clause needs no new
  runner work.
- **Today's four `unit.detect` globs, re-derived from the live `.harness/harness.json` and
  `templates/harness.json`** (byte-identical between the two), classify exactly as the plan states:
  `tests/unit/**` excused, the other three basename, zero rogue. Both of the two already-claimed-RED
  mutants (`**/*.spec.*` added; `docs/**` substituted) reproduce RED under a direct simulation of the
  algorithm as written. I then found a third (F1) that stays GREEN.
- **The one-fence contract at T-03/T-04/SC-12**: the refusal message for the two-or-more case, and
  the exit-2 code, are the identical literal string/value at all three sites — genuine identity, not
  paraphrase (except the zero-case mismatch at F3). T-03's combination rule is total: fence-count ≠ 1
  → exit 2 unconditionally; else row-difference or violation-row → exit 1; else exit 0 — every
  combination of the three conditions maps to exactly one code, and exit 2 is reachable and
  distinguishable from exit 1 by construction (T-03 says so explicitly and no other rule contradicts
  it).
- **REQ/SC/task traceability**: REQ-01..REQ-09 are each traced by at least one task (T-01 alone
  covers REQ-01..05, REQ-08, REQ-09; T-02 covers REQ-01..03; T-03/T-04 cover REQ-06; T-05 covers
  REQ-07) — no orphan REQ, no task tracing a REQ that doesn't exist. REQ-09's only grader in the
  traceability table is SC-19; no other SC references REQ-09.
- **`depends_on` is a valid topological order**: `T-01:[]`, `T-02:[T-01]`, `T-03:[T-01]`,
  `T-04:[T-03]`, `T-05:[T-01,T-02]` — no forward references, no cycles, listed order is itself
  admissible.
- **Verify vacuity**: T-03's and T-04's verify clauses invoke a `tree-audit` subcommand that does
  not exist in the live `tests/manual/suite-census.py` (only `verdict-lines`, `migration`,
  `residue`, `children` are registered) — both fail outright today, non-vacuously. T-05 states an
  explicit non-vacuity precondition (`grep -c "tracked test-shaped file outside"
  DECISIONS-INDEX.md` reports 0) and I reproduced it: both of T-05's grep targets return 0 hits
  against the live tree today. T-03/T-04 don't state an equivalent precondition, but the asymmetry
  is justified, not an omission: T-05 edits existing prose in place (a real risk of a coincidental
  prior match), while T-03/T-04 build wholly new functionality with no plausible way to already pass.
- **SC-06 / T-03 counts / T-04 dispositions all survive the amendment**: case 11 plants no fixture
  file (confirmed by its own intent text and by the fact that it reads `.harness/harness.json`
  rather than any tempdir), so case 1's one-element exact-equality list is untouched. Case 1's
  fixture basename `test_rogue.py` does not collide with the agnostic pair (no `_test.` substring).
  D-05's line citation (`probe-omp-session-accessor.py:54-55`) matches the live file exactly (the
  `PROBE = (... / "probe-session-accessors.ts")` assignment spans those two lines).
- **Off-the-table items respected**: D-05's exception/archival coupling, D-01's two-group
  vocabulary, and the rejected `tracked_paths_fn`/unified-vocabulary alternatives are not re-argued
  here; I checked D-05's *description* against the live consumer file for a new inaccuracy and found
  none.

## Severity

`severity_max: high` (F1). `must_fix: [F1]`. F2 and F3 are advisory, not gating.

## Code grade

No code exists at plan phase and no `review_sha` can be pinned before the Building-to-Review seam
(INV-6/DEC-207/BUG-1080) — `code_grade: n_a`, `reviewed:` binds to the plan itself.

```yaml
VERDICT: FAIL
DIGEST:
  headline: Case 11's literal-prefix check treats `tests/../evil/**` as EXCUSED (unnormalized `..`), so a one-for-one substitution mutant keeps case 11 fully GREEN while reproducing the exact counted-by-map/no-runner-reach gap the amendment exists to close; two lower-severity issues also found, everything else probed checks out.
  severity_max: high
  code_grade: n_a
  findings: 3
  must_fix: ["F1: case-11 literal-prefix escape via unnormalized `..` (or an outside-tree symlink under tests/) stays GREEN under a clean substitution mutant, mechanically verified"]
  spec_violations: []
  reviewed: "plan:/Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-1286-test-tree-enforcement/.harness/harness/features/BUG-1286-test-tree-enforcement/plan.yaml"
  human_commits_in_scope: []
  open_questions: []
  files_touched: [".harness/harness/features/BUG-1286-test-tree-enforcement/notes/review-harness-code-reviewer-planpanel-c6.md"]
  expertise_update: []
artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-1286-test-tree-enforcement/.harness/harness/features/BUG-1286-test-tree-enforcement/notes/review-harness-code-reviewer-planpanel-c6.md
```
