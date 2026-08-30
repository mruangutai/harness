# QA — final validation panel (SC-02, SC-18, coverage audit) — FEAT-43

pin `94383e671e51f95d142f3220f97c8e453721d516`, all reads via `git show <pin>:<path>`.

## SC-02 — hand re-derivation — MET

All 12 fixtures in `test-code-grade.py` (lines 26–53) carry an inline comment deriving A, B, C,
cyclomatic and cognitive from the constructs in the source, next to the expectation tuple. None
reads "as produced by the tool" — every one lists the specific AST constructs counted.

Three fixtures re-derived independently, by hand, against `plan.yaml` T-01's counting rules:

**`control-basics`, line 30** — `for x in xs: pass` / `with cm as y: pass` / `try: pass except
ValueError as err: assert err`.
- Cyclomatic: base 1, `for` +1, `with` (1 item, no "beyond first") +0, `except` handler +1, `assert`
  +1 → **4**. Matches.
- Cognitive: `for` at nesting 0 → +1; `with`/`try` add no increment and no nesting to their
  siblings once closed; `except` at nesting 0 → +1; `assert` is not in the cognitive list → +0.
  Total **2**. Matches.
- ABC-A: for-target `x`, with-as `y`, except-as `err` → **3**. ABC-B: no calls → **0**. ABC-C:
  `for`+`except`+`assert` → **3**. Magnitude `sqrt(9+0+9)=sqrt(18)=4.2426…` → round-half-up 1dp
  **4.2**. Matches. Grade: cyc 4≤4, cog 2≤3, abc 4.2≤8 → all land grade-5 band → **grade 5**,
  driver `cyclomatic+cognitive+abc`. Matches.

**`comprehension-filters`, lines 51–53** — one comprehension `for` clause, 8 `if` clauses, one
`bool(x)` call, three `Compare` ops (`>`,`<`,`!=`; `%`/`+`/`-` are `BinOp`, not `Compare`).
- Cyclomatic: base 1 + comprehension-for +1 + 8×comprehension-if +8 → **10**. Matches.
- Cognitive: comprehension `for`/`if` are `ast.comprehension` nodes, not `ast.For`/`ast.If`, so
  none of the cognitive triggers fire → **0**. Matches.
- ABC-A: comprehension target `x` → **1**. ABC-B: `bool(x)` → **1**. ABC-C: the rule text names
  "comprehension if" explicitly as a C-item but never names "comprehension for" — only the bare
  generic "for" — so the comprehension's generator clause is excluded from C by the rule's own
  asymmetric wording; 8 if-clauses + 3 Compare operators → **11**. Matches. Magnitude
  `sqrt(1+1+121)=sqrt(123)=11.090…` → **11.1**. Matches. Grade: cyc 10 fails grade-4's ≤8 but
  passes grade-3's ≤10 → band 3; cog 0 → band 5; abc 11.1 fails grade-5's ≤8, passes grade-4's ≤20
  → band 4. Worst (lowest) band = 3 → **grade 3**, driver `cyclomatic` alone. Matches.

**`unpacking-comprehension`, lines 42–45** — `a, b = 1, 2` then `[x for x in xs if x]`.
- ABC-A: tuple-unpack targets `a`,`b` (2) + comprehension target `x` (1) → **3**. ABC-B: no calls
  → **0**. ABC-C: one comprehension-if → **1**. Magnitude `sqrt(9+0+1)=sqrt(10)=3.1623…` →
  **3.2**. Cyclomatic: base 1 + comprehension-for +1 + comprehension-if +1 → **3**. Cognitive:
  comprehension nodes don't trigger → **0**. All three land grade-5 band → **grade 5**, driver
  `cyclomatic+cognitive+abc`. Matches all seven asserted fields.

All three hand derivations reproduce the file's asserted numbers exactly, counting from the source
text against T-01's construct-by-construct rules — not by running the tool. **SC-02: met.**

## SC-18 — stated limits — MET, all three cited by line

`.claude/skills/harness-code-risk-grading/SKILL.md` at the pin, lines 162–165:
- **Sonar approximation** (line 162): "Cognitive is a **Sonar-style approximation**, not
  SonarSource's algorithm; do not expect the same number as a Sonar report." — unhedged.
- **Shell/TypeScript excluded** (line 163): "Shell scripts and TypeScript are not graded at all."
- **Does not fix existing debt** (lines 163–164): "This grading also does not fix code already
  below the bar: that cleanup is separate and deliberately not a touch-it-fix-it ratchet."

All three plain-English, unhedged, in the "## Reference" section a reader meets right after the
band table. **SC-18: met.**

## Automated-criteria coverage audit

| SC | verdict | evidence |
|---|---|---|
| SC-01 | met | `test-code-grade.py:377–385` — 12 fixtures (`len(FIXTURES)>=12`), `grades=={1,2,3,4,5}` asserted as a set, each fixture's full 10-field tuple checked. |
| SC-02 | met | see above — every fixture hand-derived in-line; 3 independently re-derived and matched. |
| SC-03 | met | `test-code-grade.py:394–402` — `DIRECTION_PAIRS` has 4 "worse" (`nested-early-return`, `nested-loops`, `third-condition`, `inline-helper`) + 2 "better" (`early-return-better`, `condition-better`), covering all four named habits; each pair asserts both the named metric moves and the grade moves in the matching direction. Hand-checked `third-condition`: cyc before=4 (base1+if1+BoolOp-beyond-first1+assert1), after=5 (BoolOp-beyond-first becomes 2) — after>before, "worse" confirmed. |
| SC-04 | met | `test-code-grade-cli.py:233–282` (`test_diff_and_determinism`) — byte-identical stdout/exit across two working-directory copies with reversed file-enumeration order, plus a distinct cwd, plus an injected reversed `_diff_paths` order; renamed/odd-character path round-trips repo-relative. |
| SC-06 | met, narrow | `test-code-grade-cli.py:108–116` (`--paths` mode): syntax-error file reported `PARSE ERROR`/`UNGRADED`, `PASSING: 0`, exit 3 (distinct from 0/1). **Gap**: only single-file corpora are tested in `--paths` mode; the CLI's `--base/--head` diff path (`code-grade.py` `_diff_report`, the mode the actual review pipeline uses per D-08) has categorically different behavior on a parse error — it drops **every** record for the whole diff, not just the broken file's — and that path is never exercised with a syntax-error fixture anywhere in the suite. Advisory, not blocking: SC-06's literal wording ("a corpus containing one file with a syntax error…") is satisfied by the tested path-mode corpus, and the diff-mode behavior is provably no less conservative (exit 3, never 0). |
| SC-07 | met | `test-code-grade.py:214–282` (`check_changed_function_resolution`) — seven-way fixture (new, worsened, improved, renamed-unchanged-body, whitespace-reformat, signature-change-no-branching, whole-file-move); `gated_names` set-equality to `{newly_added, worsened}` (line 269) plus 5 individual absence checks (lines 275–279: `improved`, `renamed_new`, `reformatted`, `signature_changed`, `moved`). |
| SC-08 | met | same fixture, lines 280–281: `already_bad` (a 21-operand `BoolOp` function, cyc 21 → grade 1) asserted absent from `gated_names` and present in `informational_names`. |
| SC-10 | met | `test-code-grade.py:333–364` (`check_delivery`) — nested loop over `(.omp/agents, .claude/agents) × (5 agents)`, one `check()` call per iteration → 10 individually-labelled assertions, never an aggregate. Independently confirmed at the pin: `harness-code-risk-grading` appears exactly once in each of the 10 files' frontmatter `skills:`/`autoloadSkills:` list. |
| SC-13 | met | `test-gate-policy.py:55–90` (`check_policy_loading`) — all four gate keys resolved individually by name (lines 60–63); unrecognised value (`qa_gate="sometimes"`) raises `GatePolicyError` naming the gate and offending value (lines 64–67); non-string value, absent `gates` block, absent single key, unparseable JSON, and unreadable path each independently raise loudly, never default (lines 68–89). |
| SC-16 | met | `test-check-plan-routes.py` `case_27` (lines 1411–1461): owner manifest is an empty `agents: {}` team-config paired with a linked worktree whose branch team-config is the **real, broadly-granting** production manifest; `check-plan-routes.py`'s `resolution_manifest()` reports a `DEVIATION` line, which `main()` counts as a violation (`code-grade.py`-adjacent `check-plan-routes.py:797-799`), giving nonzero exit — a reported violation. `case_27b` (lines 1433–1441) re-runs the **pre-feature revision** (`df63193f…`) of the same three files against the identical fixture and asserts it exits 0 with `"OK T-01"` and no deviation line — proving the new assertion is capable of failing, satisfying the "previous revision reports OK" clause verbatim. |

**No `must_fix`.** The only gap found (SC-06's diff-mode blind spot) does not meet the bar for
blocking: SC-06 as literally written is satisfied by the tested corpus, the untested diff-mode
behavior is strictly more conservative than what's required (it never silently passes — it
guarantees a non-zero, non-all-clear exit), and D-09/REQ-07's intent ("never counted as passing")
holds in both modes. Concrete scenario if this were exploited: a reviewer running `code-grade.py`
directly on the touched paths (as the skill's own worked instructions do,
`SKILL.md:170–171`) would still see the per-file `PARSE ERROR`/`UNGRADED` report correctly scoped
to only the broken file — the diff-mode blanket-drop is a different, additionally-conservative
code path that the review flow also uses, and its coarser behavior is not itself a defect, just an
unverified.

## Re-run: unit and integration suites — MATCH claimed evidence

- `run-unit-tests.sh --kind unit`: exit 0, all 29 of the 29 `UNIT_SCRIPTS` entries individually
  confirmed `PASS <script>` in the output (a stray grep for `PASS .*\.py$` at 30 was a false
  positive — `case_floor_inflight_registry.py` is an internal per-case label printed by
  `test-inflight-registry.py`, not a 30th script). **29/29, matches claim.**
- `run-unit-tests.sh --kind integration`: exit 0, all 28 of the 28 `INTEGRATION_SCRIPTS` entries
  (27 base + `test-code-grade-cli.py` appended) individually confirmed `PASS <script>`.
  **28/28, matches claim.**
- Did not re-run the full 955-suite repository suite; the one known failure
  (`test-hooks-install.py` case `(e-green) SC-14`) is out of scope per the batch context and was
  not re-investigated.

## Verdict inputs

All two inspection criteria owned by this panel (SC-02, SC-18) are `met`. The nine
automated-criteria spot-checked are all `met`, one (`SC-06`) with an advisory (non-blocking) note
about untested diff-mode coverage. The claimed unit/integration evidence in
`runs/validate-regate-c13-r01-validator/digest.md` reproduces exactly on a fresh run at the pin.
