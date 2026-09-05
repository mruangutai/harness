# Goal-check — BUG-1286-test-tree-enforcement — build c2 @ `bb3a31ed`

**19 of 19 MET. 0 UNMET.** Both cycle-1 misses are closed and every criterion that was MET at
`9adbce6b` was re-derived from scratch at `bb3a31ed` — none carried forward. The B-1 decomposition
of `violations`/`_registry_findings` into named helpers changed no observable behaviour: every
unit and integration assertion passes, the tree-audit row set at `4b343d80` and at `bb3a31ed` is
byte-identical, and the four-mutation discrimination probe on case 11 still reddens on all four.

Grading ref is `bb3a31edc1971447b998fda1f9a736944bc8e612`. All content evidence read with
`git show bb3a31ed:<path>`; `git diff bb3a31ed..HEAD` touches `feature.json` alone and the worktree
is clean, so suite runs in the tree exercise the graded source. Nothing committed, staged, or moved.

## The two remedies, re-derived

**SC-12 — MET (`inspection`).** All three clauses hold at `bb3a31ed`.
- (a) `git merge-base --is-ancestor 4b343d8083d94d97477d3f2ebd7b848e83f01871 bb3a31ed` → **exit 0**.
  The note's line-3 SHA is now an ancestor of `review_sha`.
- (b) Subjects identical — both `BUG-1286: add the tree-audit census subcommand [harness:t-03]`.
  The orphan `5f76d6b1` is **still reachable as a dangling object in this checkout**, so I compared
  the two subjects directly rather than by proxy.
- (c) `suite-census.py tree-audit --ref 4b343d80 --against <note as committed at bb3a31ed>` →
  **exit 0**, no `MISSING`, no `EXTRA`, `TOTAL 85 OUTSIDE 9 VIOLATIONS 0` — which is exactly the
  measurement the note's BLUF asserts at that commit. The same run at `--ref bb3a31ed` is also
  exit 0, and `diff` of the two row sets is empty, so no tracked vocabulary match was added or
  removed between `4b343d80` and `bb3a31ed`. The note carries exactly 2 fence lines = one block.
  Both refusals re-proved live against throwaway notes: `note carries no fenced block: …` exit 2,
  `note carries 2 fenced blocks, expected exactly 1: …` exit 2.

**SC-16 — MET (`automated/unit`).** Clause 1 is asserted by case 9 (`:392-393`, PASS). Clause 2 is
now asserted by `violations() has exactly one non-test caller repository-wide` (`:173-176`, PASS).
I proved its discrimination by AST-extracting the **shipped** `_violations_callers` /
`_is_violations_invocation` from `git show bb3a31ed:tests/unit/test-suite-layout.py` and running
them over synthetic Git fixtures (no re-implementation):

- Traversal scope, read from source: `git ls-files` at the real root (repository-wide, **2743**
  tracked paths), skipping `tests/**` and any extension outside `suite_layout.SOURCE_EXTENSIONS`
  (`.py .sh .ts .tsx .js .mjs .cjs`), skipping comment lines.
- **Goes RED for a second caller anywhere**: proved in `bin/*.py`, `.harness/tools/*.py`, a
  top-level `*.sh`, and `.omp/extensions/*.ts` — each reddens naming the offending path.
- **Not satisfiable or trippable by prose**: Markdown notes and `BRIEF.md` are excluded by
  extension, so the nine `notes/`+BRIEF mentions of `violations()` cannot reach it; a commented-out
  call and `layout_fixtures.py`'s zero-arg docstring mention are both correctly ignored.
- Residual, advisory only (R-2 below): two aliased-import forms evade the regex.

## Corroboration — and two places disk contradicts the reported figures

Matching: unit `--kind unit` **342 checks / 0 FAIL / 27 files, exit 0**; `test-suite-layout.py`
alone **47 checks, exit 0**; `test-run-unit-tests-layout.py` **14/0, exit 0**; `--check-layout`
exit 0; tree-audit `TOTAL 85 OUTSIDE 9 VIOLATIONS 0`; `check-decision-anchors.py` **30 examined /
0 failed**; `code-grade.py --base 1977ebd6 --head bb3a31ed` **exit 0, PASSING 33**, two grade-2
records (`suite_layout.tracked_paths` bar 4, `test-suite-layout._literal_key_present` bar 3), no
grade-1. Full `--kind integration`: 46 files, 0 FAIL, exit 0.

- **`check-state.sh` exits 1, not 0** (reproduced twice, ~75s each). Exactly one `VIOLATION`, over
  `…/runs/2026-09-05-02-validator/digest.md` — a **gitignored** (`.gitignore:7`) run artifact from
  an earlier validator run today, absent from `bb3a31ed`'s tree and from `git status`. No SC covers
  it and no BUG-1286 deliverable is implicated, but the reported exit 0 is not what disk says.
- **`run-unit-tests.sh` (kind `all`) reds under a pm dispatch env.** With `HARNESS_AGENT_TYPE=harness-pm`
  exported, `tests/integration/test-plan-merge.py` returns 10 FAILs (`REFUSED: harness-pm may not
  sign an approval`). With the variable unset it is **291 checks, exit 0**. The suite is not
  hermetic against the caller's agent identity — a harness defect, not a BUG-1286 one (Q1).

## Stale BRIEF pins — documentation defects, no behaviour behind them

The decomposition moved line numbers throughout `suite_layout.py`, so two pins moved again since
cycle 1. None changes a grade; each names a real construct at a moved line.

| BRIEF pin | at `bb3a31ed` |
|---|---|
| SC-06 `suite_layout.py:20-28` (under-`tests/` rglob clause) | **STALE** — `:20-28` is the `DOCUMENTED_EXCEPTIONS` body; the clause is `_runner_selection_findings` at **`:135-148`** (was `:115-123` at `9adbce6b`) |
| SC-07 `tests/unit/test-suite-layout.py:104-105` | **STALE** — assertion at **`:108-109`** |
| SC-19 template-equality assertion `:100-103` | **STALE** — configs load at `:102-103`, the two assertions at **`:106-107`** |
| SC-15 `run-unit-tests.sh` line 47 | **accurate** at both `1977ebd6` and `bb3a31ed` |
| SC-09 `test-layout-migration.py:62` | **accurate** |
| `code_grade.py:458-473` (`_is_test_path`) | **accurate** — `def` at `:458` |
| census `85 / 9 / 0` at `c040c319`; "counted-outside-`tests/` set is EMPTY" at `cab6adb2` | **both reproduce** at `bb3a31ed` (85/9/0; `offenders(real_tracked) == []` over 2743 paths) |

## Grades — all at `bb3a31ed`, none imported

| SC | method | verdict | evidence |
|---|---|---|---|
| SC-01 | automated/unit | MET | case 1 `:212-214` PASS — names `.harness/tools/test_rogue.py`, exactly once |
| SC-02 | inspection | MET | `receipt-harness-backend-dev-T-01-c1.md:10-32` records real RED against the unmodified predicate (`FAIL case 1: rogue tracked file reported exactly once…` + `AttributeError: … DOCUMENTED_EXCEPTIONS`, exit 1); qa's test-first audit names it at `qa-matrix-gate-c1.md:51-58`, verdict satisfied |
| SC-03 | automated/unit | MET | case 3 `:262-265` PASS — three rogues in sorted path order, repeat call identical |
| SC-04 | automated/integration | MET | integration case 2 `:82-95` PASS — `returncode == 2`, `MISCONFIGURED:` names the rogue, `"PASS test-unit.py" not in stdout`; file 14/0 exit 0 |
| SC-05 | automated/unit | MET | case 4 `:276-280` PASS — exactly one `cannot enumerate…`, and no tracked-dependent finding |
| SC-06 | automated/unit | MET | case 1 exact-equality with `DOCUMENTED_EXCEPTIONS` rebound to `()` `:224-226` PASS (one-element list); manual `probe-fixture.py` unnamed `:215-216`. Pin stale, above |
| SC-07 | automated/unit | MET | `manual tests are not actively detected` `:108-109` PASS. Pin stale, above |
| SC-08 | automated/unit | MET | `real layout is valid` `:54` and case 7 `:360-361` PASS — `violations(ROOT) == []`; tree-audit `--ref bb3a31ed` VIOLATIONS 0 |
| SC-09 | automated/integration | MET | `layout_fixtures.py` present at `bb3a31ed` (blob `72b60628`); `import layout_fixtures as lf` at `test-layout-migration.py:62`; that file exits 0 |
| SC-10 | automated/unit | MET | five items, each its own passing assertion: glob `:321`, duplicate `:329`, unnecessary `:337`, no-longer-tracked `:345`, live-entry-removal `:358`. Registry is one exact path + written reason (`suite_layout.py:18-26`) |
| SC-11 | automated/unit | MET | case 1 `:212` (tracked → reported) and case 2 `:237-238` (identical shape untracked → not reported) |
| SC-12 | inspection | MET | three clauses re-derived above: ancestor exit 0, one fenced block, row sets identical, `--against` exit 0 |
| SC-13 | inspection | MET | DEC-213 amendment (`DECISIONS.md:6696`) states the repository-wide clause and reads "The bin-only enumeration above is superseded as a statement of the predicate's REACH, not as a rule"; `DECISIONS-INDEX.md` **byte-identical** to a fresh `gen-decisions-index.py --stdout` (`cmp` clean); its DEC-213 row `@6651` states the invariant |
| SC-14 | inspection | MET | `git diff 1977ebd6..bb3a31ed -- .harness/harness.json` → **0 bytes of output** |
| SC-15 | inspection | MET | exactly one `run_pool.py` invocation at `bb3a31ed`, `--mutation-check "$BIN_DIR"`, at **line 47** — identical at `1977ebd6`; pin accurate |
| SC-16 | automated/unit | MET | see the re-derivation above — `:173-176` PASS, red on a second caller anywhere, inert to prose |
| SC-17 | automated/unit | MET | case 5 `:293` PASS — non-git tree returns exactly its four directory+bin findings, none from the tracked clause |
| SC-18 | automated/unit | MET | both directions, separate cases: case 10 `:406-411` names `session_test.md` and `run.test.jsonl` in two own assertions; case 8 `:371-375` requires `.md` clean and `.py` flagged. No single case carries both halves |
| SC-19 | automated/unit | MET | probe over the SHIPPED helpers at `bb3a31ed`: 4 running kinds, 7 detect patterns, `hygiene_uncertified == []` (4 inside-tests, 3 guard-covered); all four adversarial mutations RED by name (`tests/../evil/**`, `**/test_*/**`, `**/test_*.p?`, `**/*.spec.*`); control DERIVED by the live matcher = `.harness/tools/test_dir/gen.py`, reported exactly and only it (not INAPPLICABLE); behavioural half green over synthetic and over 2743 real tracked paths; corpus carries `test_x.pw` / `a_test.pw` (`:459`) |

## Recommendations — not adopted into any grade

- **R-1 (carried from c1, still open).** Integration case 2 asserts only `"PASS test-unit.py" not in
  stdout`, while case 4 asserts both sentinels. A tightening, not a hole — no SC covers it.
- **R-2 (new).** SC-16's caller assertion matches the literal `suite_layout.violations(<arg>`. Two
  alias forms evade it — `from suite_layout import violations` and `import suite_layout as sl`.
  Neither exists in the repository and neither is the repo's import convention, so the property
  holds; the tripwire is narrower than the property. Worth widening if `violations()` ever gains a
  second legitimate consumer.
- **R-3 (new).** SC-19's `tests/../evil/**` mutation is refused with reason "core contains a
  directory separator" rather than by the `..` rejection the BRIEF's failure list names. Refused by
  name either way; two guards cover it and the earlier fires first. Same nuance as c1, not a defect.

Nothing emerged that the BRIEF's `## Verification gaps` has not already disclosed: the
directory-component residual, the null-kind activation consequence and the sufficient-not-proof
hygiene rule all behaved exactly as signed.
