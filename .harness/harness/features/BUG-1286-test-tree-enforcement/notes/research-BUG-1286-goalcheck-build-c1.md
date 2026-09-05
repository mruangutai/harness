# Goal-check — BUG-1286-test-tree-enforcement — build c1 @ `9adbce6b`

**17 of 19 MET. 2 UNMET: SC-12 (behaviour wrong — record provenance) and SC-16 (unproven only —
missing assertion).** The shipped predicate does what the feature set out to do: every unit and
integration assertion passes, the four-mutation discrimination probe on case 11 reddens on all four,
and the audit's row set reproduces exactly at `review_sha`. Both unmet criteria are one-line-shaped
defects, neither in `suite_layout.py`.

Every grade below was taken at `9adbce6b`; content evidence read with `git show 9adbce6b:<path>`.
Nothing committed, staged, or moved. Suites re-run, corroborating the orchestrator: unit
`test-suite-layout.py` 46/46 exit 0, `test-run-unit-tests-layout.py` 14/14 exit 0,
`test-layout-migration.py` exit 0, `--check-layout` exit 0, `check-decision-anchors.py`
30/0 failed, `tree-audit --ref 9adbce6b --against notes/qa-tree-audit.md` exit 0 (TOTAL 85 OUTSIDE 9
VIOLATIONS 0).

## The two UNMET

**SC-12 — UNMET, `behaviour wrong` (record defect, not a code defect).** Two of three clauses hold:
the note carries EXACTLY ONE fenced block (2 fence lines, counted by hand), and its row set is
identical to the re-run at `review_sha` (`--against` exit 0, no MISSING/EXTRA). The instrument's two
refusals are real and distinct — `note carries no fenced block: <p>` and `note carries 2 fenced
blocks, expected exactly 1: <p>`, both exit 2, proved against two throwaway notes. The third clause
FAILS: the note's recorded SHA `5f76d6b139c9cd5fc3cc7d4011f063335210cb8e` is **not an ancestor of
`9adbce6b`** — `git merge-base --is-ancestor` exits 1 and `git branch -a --contains` is empty. It is
a dangling pre-rebase twin of `4b343d80` (same subject, differing only by
`.harness/notes/audit-decisions.py`, which upstream #1288 deleted under the branch). Mitigation, and
it is only that: `tree-audit --ref 5f76d6b1` and `--ref 9adbce6b` produce **byte-identical row
sets**, so no vocabulary match was added or removed. The remedy is a one-token SHA correction in
`notes/qa-tree-audit.md` line 3, not a rebuild.

**SC-16 — UNMET, `unproven only`.** Clause 1 holds and is asserted: case 9 (`:346-362`) proves the
repository-wide clause inert on a root not shipping `suite_layout.py`. Clause 2 — "`violations()`
still has exactly one caller, Harness's own `run-unit-tests.sh`" — is **true but unasserted**.
Measured at the pinned tree: `git grep -n 'violations(' 9adbce6b` gives exactly one production call
site, `run-unit-tests.sh:33`; `suite-census.py` imports the vocabulary tuples and `is_test_shaped`,
never `violations`. No unit assertion pins it: the nearest, `runner delegates layout once`
(`:141-143`), counts `suite_layout` lines **inside `run-unit-tests.sh`** and stays green if a second
caller appears in any other file. This conjunct is the decisive one — the eng-lead plan review
(`notes/review-harness-eng-lead-plan-c0.md:26`) established that an onboarded product checkout DOES
carry `.claude/skills/harness/bin/`, so case 9's self-ownership condition may be SATISFIED there and
is not what protects a product checkout; the single-caller fact is. The gap: a repository-wide
caller-count assertion in `tests/unit/test-suite-layout.py`. Declared method is `automated/unit`; no
unit test reaches the clause.

## Grades

| SC | method | verdict | evidence at `9adbce6b` |
|---|---|---|---|
| SC-01 | automated/unit | MET | case 1 `:179-181` PASS — names `.harness/tools/test_rogue.py` |
| SC-02 | inspection | MET | `receipt-...-T-01-c1.md:10-32` records real RED against the unmodified predicate: `FAIL case 1: rogue tracked file reported exactly once …` + `AttributeError: … DOCUMENTED_EXCEPTIONS`, exit 1; qa audits it at `qa-matrix-gate-c1.md:51-58`. Subject is SC-01's covering assertion, and that one is named failing |
| SC-03 | automated/unit | MET | case 3 `:229-232` PASS — three rogues in sorted order, repeat call identical |
| SC-04 | automated/integration | MET | integration case 2 `:82-94` PASS — exit 2, `MISCONFIGURED:` names the rogue, no sentinel on stdout |
| SC-05 | automated/unit | MET | case 4 `:236-249` PASS — exactly one `cannot enumerate…`, no tracked-dependent finding |
| SC-06 | automated/unit | MET | case 1 exact-equality with `DOCUMENTED_EXCEPTIONS` rebound to `()` `:191-193` PASS. Rationale re-derived: planted `tests/manual/test-x.py` IS refused, `probe-x.py` is not. **Pin stale**, see below |
| SC-07 | automated/unit | MET | `manual tests are not actively detected` PASS. **Pin stale**: BRIEF says `:104-105`, actual `:108-109` |
| SC-08 | automated/unit | MET | `real layout is valid` `:54` and case 7 `:327` PASS — `violations(ROOT) == []` |
| SC-09 | automated/integration | MET | `layout_fixtures.py` present in the `9adbce6b` tree; `import layout_fixtures as lf` at `test-layout-migration.py:62` (pin accurate); that file exits 0 |
| SC-10 | automated/unit | MET | five items each separately asserted and passing: glob `:288`, duplicate `:296`, unnecessary `:304`, no-longer-tracked `:312`, live-entry-removal `:325`. Live registry is one exact path + written reason (`suite_layout.py:18-27`) |
| SC-11 | automated/unit | MET | case 1 `:179` (tracked, reported) and case 2 `:204` (identical shape untracked, not reported) |
| SC-12 | inspection | **UNMET** | see above — recorded SHA not an ancestor of `review_sha` |
| SC-13 | inspection | MET | DEC-213 amendment `DECISIONS.md:6696` states the repository-wide clause and marks the bin-only enumeration "superseded as a statement of the predicate's REACH"; `DECISIONS-INDEX.md` **byte-identical** to a fresh `gen-decisions-index.py --stdout` (`cmp` clean) and its row `@6651` states the invariant |
| SC-14 | inspection | MET | `git diff 1977ebd6..9adbce6b -- .harness/harness.json` → **empty** |
| SC-15 | inspection | MET | exactly one `run_pool.py` invocation, `--mutation-check "$BIN_DIR"`, at line 47 at BOTH `1977ebd6` and `9adbce6b` — pin accurate |
| SC-16 | automated/unit | **UNMET** | see above |
| SC-17 | automated/unit | MET | case 5 `:251-262` PASS — non-git tree returns exactly its four directory+bin findings |
| SC-18 | automated/unit | MET | both directions, separate cases: case 10 `:373-378` names `session_test.md` and `run.test.jsonl` in two own assertions; case 8 `:338-342` requires `.md` clean and `.py` flagged. No single case carries both halves |
| SC-19 | automated/unit | MET | probe over the SHIPPED helpers at `9adbce6b`: 4 running kinds, 7 detect patterns, each certified individually (4 inside-tests, 3 guard-covered), `hygiene_uncertified == []`; all four adversarial mutations redden by name (`tests/../evil/**`, `**/test_*/**`, `**/test_*.p?`, `**/*.spec.*`); control DERIVED by the live matcher = `.harness/tools/test_dir/gen.py`, detected exactly and only it (not INAPPLICABLE); behavioural half green over synthetic and over 2732 real tracked paths. Corpus carries `test_x.pw`/`a_test.pw` (`:426`) |

## Stale pins — documentation defects, no behaviour behind them

Reported separately from the misses, per the routing distinction. All three name a real construct at
a moved line; none changes a grade.

- SC-06 cites `suite_layout.py:20-28` for the under-`tests/` rglob clause. At `9adbce6b` lines 20-28
  are the `DOCUMENTED_EXCEPTIONS` body; the clause is at **`:115-123`**.
- SC-07 cites `tests/unit/test-suite-layout.py:104-105`; the assertion is at **`:108-109`**.
- SC-19 cites the template-equality assertion at `:100-103`; it is at **`:102-107`**.
- Accurate and re-verified: `code_grade.py:458` (`_is_test_path`), `test-layout-migration.py:62`,
  `run-unit-tests.sh:47`.

One nuance, not a defect: SC-19's `tests/../evil/**` mutation is refused with reason "core contains a
directory separator" rather than by the `..` rejection the BRIEF names. It is refused by name either
way; two guards cover it and the earlier one fires first.

## Recommendation to the operator — not adopted into any grade

- **R-1 (advisory, no SC covers it).** Integration case 2's sentinel-absence clause asserts only
  `"PASS test-unit.py" not in stdout`, while case 4 asserts both. It remains a valid tripwire for the
  reordering failure mode (a runner dispatching before the gate prints BOTH sentinels), so this is a
  tightening, not a hole. New relative to `## Verification gaps`, which discloses nothing of this
  shape.

Nothing else emerged that the BRIEF's `## Verification gaps` has not already disclosed — the
directory-component residual, the null-kind activation consequence and the sufficient-not-proof
hygiene rule are all signed residuals, and all three behaved exactly as disclosed under the probe.
