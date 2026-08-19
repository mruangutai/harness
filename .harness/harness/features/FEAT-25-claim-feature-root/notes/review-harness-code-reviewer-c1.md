# Code review — FEAT-25-claim-feature-root — cycle 1

`review_sha = 8d7b273`, base `d1ffd7f`. Graded diff: exactly the six `.claude/skills/harness/bin/`
files (`factory_claim.py`, `layout_fixtures.py`, `layout_migration.py`, `test-factory-claim.py`,
`test-factory-integration.py`, `test-layout-migration.py`), confirmed via `git diff --stat
d1ffd7f...8d7b273 -- .claude/skills/harness/bin/`. `DECISIONS.md`/`SPEC.md`/the three lead files are
held dirt from another workstream — not read, not cited for any Stage-1 judgement below.

## VERDICT: PASS, advisory notes only

No `must_fix`. `severity_max = med`. All three handed-down findings are real and confirmed by
measurement, but none falsifies a signed SC at `8d7b273` — each is a durability/coverage gap in
test harness that stays true today and could go silently wrong on a **future** edit. Per the
calibration in the dispatch, that is advisory, not gating.

## Stage 1 — spec compliance: PASS

- `FEATURES_ROOT` at `factory_claim.py:45` reads `os.path.join(factory_config.harness_root(),
  ".harness", "harness", "features")` — literal, fixed segment, no new `factory_config` API (D-01,
  REQ-01). Directory exists in this checkout.
- `_BlockerCache` refactor (`factory_claim.py:90-127`) matches T-02's spec exactly: one private
  loader (`_plan`), no duplicated `try/except`, `task()`/`plan_loaded()` both route through `_plan`
  so a plan is read once per poll. `plan_path` is the sole `abspath` site (REQ-02, SC-04).
- `_blocker_gate` (`:150-166`) returns `("no_plan", path, root_exists)` before falling through to
  `edge_i`, exactly as D-03 specifies; blocking semantics unchanged.
- `_blocker_reason_text` (`:187-199`) adds the two `no_plan` texts, neither containing "no matching
  plan task" (checked by grep at source — true).
- `layout_migration.py` READER_TABLE gains the `factory_claim.py` row (`:92-94`), the DO-NOT-READ
  docstring entry is removed and replaced with a dated note (`:42-46`) — verified live: `python3 -c
  "... 'factory_claim.py' in (lm.__doc__ or '')"` → `False`.
- `layout_fixtures.py` STUB gains the matching entry (`:45-48`), fragment-shaped as the convention
  requires.
- SC-08 both clauses hold: `git diff --name-only d1ffd7f...8d7b273 -- .` (minus the feature's own
  bookkeeping dir) shows no forbidden file (`factory_config.py`, `fleet.yaml`, `harness.json`,
  `gh_board.py`, `check-domain.sh`) and no added `load_board` reference — checked individually by
  grep, all six sub-verdicts negative.
- Re-ran all three suites myself at `8d7b273` (working tree, byte-identical to the pin for these
  six files): `test-factory-claim.py` exit 0, 120 ok-lines (114 baseline + 2 T-01 + 4 T-02);
  `test-layout-migration.py` exit 0, 41 ok-lines (40 baseline + 1); `test-factory-integration.py`
  exit 0, 106 ok-lines (baseline, unchanged count). Matches SC-07 exactly and matches the
  orchestrator's own gate-measurement note. No scope creep, no omission found against
  REQ-01..04 / D-01..D-04 / SC-01..SC-08.

## Stage 2 — the three handed-down findings, ruled

### F-1 — `test-layout-migration.py:416-418`, pre-existing report-loop fail-open

**Mutation proof, isolated (no confounding from `case 1`'s real-root scan, which doesn't resolve
correctly when the script runs from scratchpad).** Copied `test-layout-migration.py` +
`layout_migration.py` + `layout_fixtures.py` + `harness_yaml.py` into the session scratchpad,
mutated **one line**, ran the copy. The repo file was never touched (`Write` is not permitted on it
and I did not use it).

Mutated line (`test-layout-migration.py` line ~118 in the isolated copy, corresponding to repo
line 304):
```python
check("case 18: clean -> exit_code 0", lm.exit_code(r_clean) == 999)  # MUTATED (was == 0)
```
This preserves the ORIGINAL two-argument `check()` call — no `detail` — exactly the trap condition.

Output of the mutated run:
```
ok   - case 18: scan() prints nothing and does not exit
FAIL - case 18: clean -> exit_code 0
ok   - case 18: mixed -> exit_code 1
ok   - case 18: cannot-verify -> exit_code 2
EXIT CODE: 0
```
Both halves hold: (a) the mutation applied — the falsified line is shown above and matches the
scratchpad copy exactly; (b) the script ran to completion and printed the `FAIL - case 18: clean ->
exit_code 0` line. **Exit code was 0 with a FAIL line printed — the fail-open is real and
reproducible.**

**Ownership** — already settled by the dispatch and reconfirmed: `git diff d1ffd7f...8d7b273 --
.claude/skills/harness/bin/test-layout-migration.py` touches only lines 402-410 (case 22); the
report loop at 412-419 is unchanged context. Not introduced or touched by this feature.

**Blast radius** — the same `if not ok and detail:` pattern exists in 3 more places
(`test-check-state.py:1630,1685,1811`), so this is a 2-file, 4-site defect class in the shared test
harness, not unique to this diff.

**Ruling: does not gate FEAT-25.** The discriminator is whether the finding falsifies a signed SC
at `8d7b273` — it does not: case 18's real (unmutated) assertions are true today, and I verified the
live suite passes for the right reasons. Two backstops exist for THIS feature's own grading, though
neither is general: (1) T-03's `verify:` block in `plan.yaml` greps ok-line TEXT
(`hasok "case 22: ..."`), which fails regardless of exit code if case 22 reddens; (2) the same
verify's `k -ge 41` ok-line-count threshold would ALSO catch a case-18 regression, because a failed
case prints `FAIL - ` instead of `ok   - `, decrementing the count independently of exit status. But
`run-unit-tests.sh:59-66` — the actual CI/QA gate for `--kind unit` — routes purely on
`python3 "$s"; status=$?`, with no line-count or text check at all. So the general CI gate has no
backstop, and a future regression to any of case 18's three assertions (or the 3 in
test-check-state.py) would go undetected there indefinitely. **Severity: med, advisory** — real,
reproducible, cross-file, worth a backlog row to whoever owns the shared harness pattern (fix: move
`fails += 1` outside the `and detail` guard in all 4 sites). Not FEAT-25's to fix; it neither
introduced nor edited these lines.

### F-2 — `test-layout-migration.py:409-410`, case 22 does not pin row presence

**Mutation demonstrated, not just asserted.** Built a paired mutation in
`scratchpad/f2/`: deleted the `factory_claim.py` row from `READER_TABLE` in a copy of
`layout_migration.py` AND the matching entry from `STUB` in a copy of `layout_fixtures.py` (kept in
sync on purpose — the RuntimeError guard at `layout_fixtures.py:72-75` only fires on a set
*mismatch*, so a paired deletion evades it, exactly as the dispatch predicted). Ran a
case-22-equivalent scan against the REAL repository root:

```
features: CLEAN — evidence migrated
docs: CLEAN — evidence migrated
exit_code: 0
CASE-22-EQUIVALENT ASSERTION (code == 0 and "features: CLEAN — evidence migrated" in features_line): True
factory_claim.py in surviving READER_TABLE: False
```

Confirmed: with `factory_claim.py` entirely absent from `READER_TABLE`, case 22's literal
assertion (`code == 0 and "features: CLEAN — evidence migrated" in features_line`) still passes.
The surface-level CLEAN verdict is computed over whatever rows remain, so removing one reader (this
one) does not change the surface verdict text case 22 checks. Case 22's own comment
(`:403-406`) claims coverage of "every FEATURES reader, including factory_claim.py" — the literal
assertion does not deliver that; it is a surface-level check, not a row-presence check.

**Ruling: does not gate FEAT-25**, and I rate it lower than F-1. SC-06 is factually true at
`8d7b273` (confirmed above: the row exists, is tagged migrated, surface is CLEAN) — nothing is
falsified. T-02's — sorry, T-03's `intent:` explicitly says "Add nothing else" about case 22, so
strengthening the assertion would have been a plan deviation by the implementer, not a defect they
introduced; the gap is in what the plan authorized case 22 to assert, not in how it was built.
**Severity: low, advisory.** Worth a backlog row to whoever owns `layout_migration.py`'s reader
table: either add a row-presence assertion to case 22, or narrow its comment to match what it
actually proves.

### F-3 — `factory_claim.py:189-199`, unpinned diagnostic string — confirmed, and a related gap is worse

Confirmed at source: the two `no_plan` return texts (`:190-196`) share the prefix `"issue #{num}
carries a feature: label that resolves, but no plan could be read at {path} - the feature "` and
diverge only in the trailing clause. T-02's embedded probe and the four B5-ter cases in
`test-factory-claim.py` assert only `absent_root in err` and `"no matching plan task" not in err` —
substring checks, never an exact match. A wrapping slip (dropped/doubled space at the f-string
boundary) would pass every current test. **Severity: low, advisory** — SC-04 does not require exact
text, only that the path and "no plan could be read" language appear and are distinguishable from
edge (i), which they are.

**A related, more consequential gap I found while confirming this** (not one of the three handed
down, but directly on point): `_blocker_reason_text`'s SECOND `no_plan` branch — `root_exists ==
True`, "the feature directory or its plan.yaml is missing or unparseable" (`:193-196`) — has **zero
test coverage of any kind**, not even a substring check. Grepped `test-factory-claim.py` for
`unparseable`, `root_exists`, `YamlParseError`, `corrupt`, `malformed`: no hits. Every existing
`no_plan` case (B5-ter, T-02's probe) constructs an absent root, which only ever exercises the
FIRST branch (`root_exists == False`). In production, `FEATURES_ROOT` will almost always exist
(that is the whole point of T-01's fix), so the realistic `no_plan` case — a candidate whose
`feature:` label resolves to a directory with no `plan.yaml` or a malformed one, while the shared
root is fine — goes through the untested SECOND branch, not the tested first one. **The tested
branch is the rare one; the untested branch is the common one.** A future refactor that collapses
the two branches, swaps their order, or drops the second `return` would go undetected by every
suite in this repo. Not a spec violation — SC-04's literal scope names only "root does not exist"
and "edge (i)" as the two scenarios to verify, so this branch is outside what SC-04 promises to
pin — but a real Stage-2 gap. **Severity: med, advisory**, same non-gating reasoning as F-1/F-2:
nothing false today, a real hole for tomorrow. Recommend a follow-up case exercising
`root_exists=True` with an unreadable/missing `plan.yaml`.

## Scratchpad artifacts (session-local, not part of the repo)

- `.../scratchpad/{harness_yaml,layout_migration,layout_fixtures,test-layout-migration}.py` — F-1
  proof (isolated case-18-only mutant).
- `.../scratchpad/f2/{harness_yaml,layout_migration,layout_fixtures,drive_case22}.py` — F-2 proof
  (paired READER_TABLE/STUB deletion).

No repository file was written, edited, staged or committed.
