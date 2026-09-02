# Code Review c9 — FEAT-48 — `27f8105b` (delta: `993ac997` fix + `27f8105b` evidence refresh)

**BLUF: PASS.** Both c8 `must_fix` items are genuinely CLOSED — the `_record`/`_snapshot_directory`
split preserves the file-loop's guard semantics and extends it symmetrically to the directory-symlink
branch (no more unguarded second `os.lstat`), and `code_grade` is clean at the pin (reconfirmed
myself: exit 0, `PASSING: 70`, zero `SEVERITY:`/blocking lines). The `run_self_tests` and `snapshot`
decompositions are closure, not displacement — verified case-by-case below, no assertion dropped,
weakened, or made unreachable. One genuine spec mismatch found (med, non-gating) and one pre-existing
quality nit (low). My disposition on the shared T-06 open item: verify-clause bug, backlog not
must_fix — detail at the end.

## Stage 1 — spec compliance

Graded 27f8105b's diff and delta commits against `BRIEF.md` REQ/SC and `plan.yaml` D-11/T-04's
literal text.

**Finding (med, mismatch) — `run_pool.py`'s mutation-check no longer skips a loose `.pyc` outside
`__pycache__`, contradicting D-11 (`plan.yaml:245`, "excluding `__pycache__` directories and `*.pyc`")
and T-04's intent (`plan.yaml:930`, "skipping `__pycache__` directories and any name ending `.pyc`").**
`_snapshot_directory` (`run_pool.py:37-49`) only excludes the `__pycache__` *directory* from descent;
it has no suffix check for `.pyc` files sitting elsewhere. This isn't inherited from before — the
pre-fix code at `e64e863e` DID skip by suffix (`if name.endswith(".pyc"): continue`) in addition to
skipping the `__pycache__` directory; the fix commit `993ac997` removed the suffix check and, in the
same commit, added `test-run-pool.py:145 case_cache_exclusion`, which explicitly PINS the new,
narrower behavior (`loose_result.returncode == 1 and "MUTATED loose.pyc" in loose_result.stdout`).
BRIEF's SC-10 text is silent on a loose `.pyc` (only forbids reporting a `__pycache__` rewrite), so no
SC fails — but `plan.yaml`'s own decision and task-intent text are unambiguous and unamended (993ac997
touched `BRIEF.md` only for SC-03/BACKLOG-C, never this task's intent). No tracked `.pyc` file exists
outside `__pycache__` in `bin/` today (`git ls-files` confirms), so this doesn't currently redden CI;
it is a written-decision-vs-code divergence, not a live defect. `should_fix`, not gating.

Everything else Stage 1 checked is in agreement: `isolated_bin.py` matches T-01's exact shape;
`run-unit-tests.sh`'s pool invocation matches T-06's mandated line verbatim
(`--mutation-check "$BIN_DIR" -- "${SCRIPTS[@]/#/$BIN_DIR/}"`), `"${SCRIPTS[@]}"` is gone, both new
files are registered in the correct arrays; DEC-211 (re-read in full at the pin,
`DECISIONS.md:6563-6614`) carries every phrase T-05's verify greps for and its `mode`/`size`/`mtime`
correction matches `_record`'s actual tuple.

## `code-grade.py` — reconfirmed myself

`python3 .claude/skills/harness/bin/code-grade.py --base origin/main --head 27f8105b` (run from the
worktree): **exit 0, zero `SEVERITY:` lines, `PASSING: 70`.** Matches the orchestrator's figure
exactly; nothing pre-image or blocking survives at this pin.

## c8 closure — case-by-case, not by complexity delta

Diffed `e64e863e..27f8105b` on `test-suite-independence.py` (409 lines) and `run_pool.py` directly.

**`_sink` and its 4 extracted detectors (`_open_sink`/`_os_sink`/`_shutil_sink`/`_method_sink`,
`test-suite-independence.py:87-114`):** traced every branch against the original monolithic `_sink`.
`_open_mode`'s `keyword or positional or "r"` preserves the original's keyword-wins-over-positional
priority; `OS_ONE`/`OS_TWO`/`OS_DEST`/`SHUTIL_DEST`/rmtree index checks (`i < len(call.args)`) are
algebraically identical to the original's `args and ...` / `len(args) > 1 and ...` guards;
`_method_sink` reproduces the original `isinstance(call.func, ast.Attribute)` + `PATH_METHODS` gate
verbatim. No sink class dropped, no index off-by-one introduced.

**`_scan_statements` split into `_record_sinks`/`_update_assignment`/`_update_with`/`_nested_blocks`
(`:125-166`):** the original ran TWO separate if/elif chains per statement (Assign/With, then
FunctionDef/If-For-While-Try); the new code merges `With` into `_nested_blocks`'s first branch
alongside `FunctionDef`/`AsyncFunctionDef`. Since `With` and `FunctionDef` never overlap as AST node
types, this merge is behavior-preserving — same recursion count, same taint-set threading order
(`_update_with` mutates `taint` in place before recursion, matching original ordering). Traced by
hand against every original branch; no case unreachable.

**`run_self_tests` split into `_red_fixture_failures`/`_clean_fixture_failure`/`_live_fixture_failure`/
`_root_refusal_failure` (`:211-284`):** all 3 red fixture sources, the clean-control fixture, the
live-tree check and the root-refusal check are byte-identical in content to `e64e863e`, just
relocated into named functions; still exactly 6 self-tests, still called unconditionally from
`main()` before the scan (`:295` `self_failures = run_self_tests()`), still fails loud
(`:299-301`). The clean-control fixture GAINED a case T-03's own intent required but c8-era code
never had: `changed=text.replace('a','b')` used as the write target
(`_clean_fixture_failure:221-235`) — T-03's intent (`plan.yaml`, clean-control bullet) explicitly
lists "`src.replace(...)` on text read from `__file__`" as a required clean-control shape; this was
missing before and is now present. Net: coverage gained, not lost.

**`_independent_expected_root` now references `harness_boundary.MARKER`** instead of the literal
`os.path.join(".harness", "team-config.yaml")` — this is exactly my own c8 `should_fix` (Q3b)
applied correctly: it reuses the CONSTANT, not the resolver FUNCTION, so the inline while-loop stays
a second, independent computation of the root exactly as T-03's intent mandates ("do NOT build the
expectation by calling harness_boundary" refers to calling the resolver, not to reusing its marker
string).

**`_record`/`_snapshot_directory` split (`run_pool.py:29-49`):** `_record`'s `except OSError: return`
now wraps BOTH the directory-symlink branch (`if os.path.islink(path): _record(...)`) and the file
loop — the exact asymmetry c8 reproduced as a crash is gone; a race on either branch now silently
drops that entry from `state` rather than propagating `FileNotFoundError`. This is the same
structural limit c8 already accepted for the file loop (a miss identical in both before/after
snapshots is invisible to any metadata-based detector) — no new finding, now applied symmetrically.

**Verdict: genuine closure on both c8 must_fix items — the crash and the code_grade regression.**

## Stage 2 — code quality, full handed-down file set

- **`run_pool.py`** — examined, one item above (already reported as Stage 1 mismatch; not
  independently re-listed here). `_record`'s fail-path is a disclosed, symmetric, structural limit
  (see above), not a fail-open regression.
- **`isolated_bin.py`** — examined, nothing. Matches T-01's spec exactly: real `shutil.copytree`
  (never symlinked), source resolved from `os.path.realpath(__file__)`, single caller shape.
- **`run-unit-tests.sh`** — examined, nothing new (unchanged by this delta; re-read in full at the
  pin). Drift detector, kind cross-check, and the pool invocation all intact.
- **`test-check-domain.py`** — examined. `run_schema`'s SITE A split into
  `_schema_case`/`_inject_schema_crash`/`_schema_copy_control`/`_schema_crash_control`/
  `_schema_crash_cases` preserves every case name the T-01 verify block string-matches on
  (`"CRASHING schema module DENIES"`, `"never written"`) and the fails-counter arithmetic. The
  redundant local `import shutil` was dropped; `shutil` is imported at module scope
  (`test-check-domain.py:15`), so no bug.
- **`test-check-fixture-secrets.py`** — examined. `run_sk_ant_red_proof` split into
  `_sk_ant_mutant`/`_exercise_sk_ant_mutant` preserves the `ok` boolean logic exactly. **Finding
  (low, non-gating):** the split MERGED two distinct diagnostic messages — "the fixed sk- pattern
  anchor was not found" and "mutant is byte-identical" — into one generic "mutant could not be
  constructed" (`:171-178`). Both paths still register `ok=False` so no coverage is lost, but a
  future maintainer debugging why this red-proof went inconclusive loses the distinction between
  "the guard's source changed shape" and "the byte-for-byte revert didn't take."
- **`test-run-pool.py`** — examined. All prior cases (attribution, failure propagation,
  exactly-once, worker selection, completion order, default cap, file mutations, symlinks, invalid
  watch) are relocated into named `case_*` functions with byte-identical assertions.
  `case_cache_exclusion` (`:145-157`) is genuinely NEW — it did not exist at `e64e863e` — closing
  c8's M4 (no test pinning the `__pycache__` exclusion), and it is the test that locks in the Stage-1
  mismatch reported above.

**Pre-existing, not introduced by this delta (info):** `_scan_statements`'s per-statement full
`ast.walk(stmt)` plus separate recursion into `stmt.body`/`orelse`/handlers means a sink call nested
inside an `If`/`For`/`While`/`Try`/`With`/`FunctionDef` whose taint predates that block gets checked
twice (once by the outer walk, once by the recursive per-statement pass), which can double-count a
finding. Present identically in the `e64e863e` code this delta refactored — not new. It cannot flip
a pass/fail verdict (the live-tree check asserts `not findings`, and the pinned-site check dedupes
via a `set()`), so it is cosmetic (an inflated "N site(s)" count) rather than a correctness gap. Not
gating; flagged for completeness since I examined the whole file.

## T-06 disposition (my own lens, not applied)

Reproduced directly: `^post-fix broken reads \d+$` matches `measurements-parallel-suite.md` TWICE
(line 15, inside the fenced verbatim block T-06's own intent requires; line 20, the parsed summary
line the same intent also requires), so `re.findall(...) == ["0", "0"]` and `post == ["0"]` is False.

**The verify clause is wrong, not the note.** The structurally identical `control broken reads`
field is checked tolerantly (`ctrl and int(ctrl[0]) > 0` — passes on the first match regardless of
duplicates), while `post` demands exact list equality. The note produces the same fenced-plus-summary
duplication for both fields, by design (T-06 intent mandates both forms); the verify author simply
wrote the `post` assertion less permissively than the `ctrl` one for no evidenced reason. Minimal
remedy: change `post == ["0"]` to the same shape as `ctrl`'s check, e.g. `post and post[-1] == "0"`
or `set(post) == {"0"}`, in `plan.yaml`'s T-06 `verify:` block — never touch the note.

**Disposition: backlog (`should_fix`), not `must_fix`.** Every substantive clause in T-06's verify
passes; the sole failure is a self-inflicted regex bug in a convenience script, not a defect in the
delivered measurements. SC-02, SC-05 and SC-06 are `verify: inspection` — the actual gate for their
content is direct reviewer reading, which I did above (control 4968 > 0, post-fix 0, ten runs all
exit 0, wall 42.40s ≤ 120s, tree condition stated, `PASS test-suite-independence.py` present) — and
all read correct. Fixing plan.yaml is out of my domain and out of scope for a validate mission
regardless.

```yaml
VERDICT: PASS
DIGEST:
  headline: "Both c8 must_fix items are genuine closures (verified case-by-case, no assertion dropped); code_grade reconfirmed clean (PASSING: 70, exit 0); one med spec mismatch (.pyc exclusion narrowed without a plan amendment) and one low diagnostic-message regression found, neither gating."
  severity_max: med
  findings: 4
  must_fix: []
  spec_violations:
    - { kind: mismatch, path: ".claude/skills/harness/bin/run_pool.py:37-49", ref: "D-11 / T-04" }
  reviewed: "d135364e..27f8105b (delta graded: 993ac997, 27f8105b)"
  human_commits_in_scope: []
  open_questions:
    - { id: Q1, question: "T-06's verify block: post == [\"0\"] fails because the note's required fenced-plus-summary duplication produces two matches while ctrl's check tolerates the same duplication. I rule this a verify-clause bug (backlog, remedy: match ctrl's tolerant check) rather than a carrier-note defect or a must_fix — does the panel concur?", blocking: false }
  files_touched: []
  expertise_update: []
artifact: .harness/harness/features/FEAT-48-parallel-safe-suite/notes/review-harness-code-reviewer-c9.md
```
