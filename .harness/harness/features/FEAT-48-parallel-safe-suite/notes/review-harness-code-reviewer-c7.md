# Code review — FEAT-48-parallel-safe-suite — validate c7

Pinned range `d135364e..8e7f56dc`. `.claude`/`.github` are byte-identical to `b86ce66a` (measured by
the dispatcher), so this review is of that build commit. Read-only: nothing here was fixed, nothing
was run through `run-unit-tests.sh` or `run_pool.py`'s CLI over the live suite — that is qa's
instrument. Original probes below ran against copies of code loaded via `importlib` from system
tempdirs, or against the shipped files directly with `read`/`grep`; nothing in the worktree was
written. `code-grade.py` was run directly (a grading tool, not the suite runner) with
`--base $(git merge-base origin/main 8e7f56dc)=d135364e --head 8e7f56dc`.

## Stage 1 — spec compliance

Per REQ, citing what I read, not what I ran (qa's `notes/qa-c7.md` measured the green suite; I
verified the code that produced it):

- **REQ-01** (no shared-state writes) — PASS for the six call sites in scope. `test-check-domain.py`
  SITE A (`run_schema` case 3, `:1469-1500`) and SITE B (`_feat50_mutant_between`, now taking `iso`,
  `:3281-3294`, with **three** callers fixed — `_feat50_binding_red_case:3299`,
  `_feat50_digest_red_case:3371`, `_bug1124_red_case:3457` — one more than T-01 intent's dated
  "two callers", correctly re-derived rather than trusted). `test-check-state.py`'s four sites
  (`:2241`, `:2264`, `:3285`, `:3590`) and `test-feature-worktree.py:583` and
  `test-bash-write-guard.py:900` all route through `isolated_bin()` with `shutil.rmtree(iso_root,
  ignore_errors=True)` in every `finally`; grepped the whole diff for any surviving
  open-then-restore-live-bytes idiom — none found.
  `test-feature-worktree.py`'s `FEATURE_WORKTREE_BIN=mutant` (`:592`) correctly points at the
  **iso** path per T-02's explicit instruction, confirmed by reading the full case
  (`case_behind_default_branch`, `:559-604`).
  Two files outside every task's `files:` — `test-check-fixture-secrets.py` (2 sites) and
  `test-validate-digest.py` (3 sites) — are also fixed, identically. Neither is in T-01/T-02/T-07's
  `files:` lists. This is legitimate under D-10's boundary clause (both under the lanes glob, so
  lane-resolved, no escalation required) **and** was properly named: `notes/census-d10-2026-09-02.md`
  records the widened set and `notes/handoff-build.md`'s "Dead ends" section states it plainly. Not
  scope creep — D-10 explicitly authorizes and requires exactly this naming discipline, and it was
  followed.
- **REQ-02** — PASS on detection logic (independently re-read `test-suite-independence.py` in full,
  180 lines; taint rule, content-read exclusion, and sink list match D-3/T-03's spec verbatim). See
  Stage 2 HIGH finding below: the file that enforces REQ-02 has no regression protection for its own
  correctness.
- **REQ-03/REQ-04/REQ-05** — PASS. `run_pool.py`'s `ThreadPoolExecutor` schedules all scripts
  (`:78-88`); each block prints `----- name (exit rc, Ns) -----` / captured output / `PASS`|`FAIL
  name` (`:83-87`, matches D-07 exactly); `pool: N workers, K files, Ts wall` and `slowest:` lines
  print unconditionally (`:96-98`); worker count follows D-06's rule exactly (`:12-25`).
- **REQ-06** — PASS. Diffed `git show d135364e:…/run-unit-tests.sh` against the shipped file myself
  (not trusting the intent text): drift detector, `--check-kinds`, unknown-kind exit 2, and the
  `PASS $s`/`FAIL $s` line shape are byte-identical up through the point the serial loop used to
  start; that loop (`for s in "${SCRIPTS[@]}"; do … done`, the only line containing
  `"${SCRIPTS[@]}"` literally) is replaced by the single `exec python3 "$BIN_DIR/run_pool.py"
  --mutation-check "$BIN_DIR" -- "${SCRIPTS[@]/#/$BIN_DIR/}"` line T-06 specifies. `exec` makes
  `run_pool.py`'s own exit code the script's exit code, and `run_pool.py` returns 0/1/2 with the
  same generic meanings (0 all-pass, 1 a-file-or-mutation-failed, 2 usage/configuration). One new,
  narrow avenue to exit 2 that did not exist before — a malformed `HARNESS_TEST_WORKERS` in the
  caller's environment — is intentional per D-06 ("a typo … must not be invisible") and is declined
  as a finding: it is a configuration refusal, not a contract break, and the sole caller
  (`run-unit-tests.sh`) never sets `--workers` or a bad env value itself.
- **REQ-07** — PASS. `test-run-pool.py`'s "completion order is not input order" case
  (`main()`, the `slow.py`/`parallel`/`serial` block) drives `--workers 4` against `--workers 1` and
  asserts `p_order != s_order and set(p_order) == set(s_order)`, matching SC-08 exactly.
- **REQ-08** — PASS. Read `DEC-211` in full myself. All seventeen required phrases from T-05's verify
  are present with correct context (not keyword bingo — each sentence states the fact accurately,
  including the two additional "third/fourth uncovered class" statements from D-11 that most builds
  would drop). `gen-decisions-index.py --stdout` drift was independently reported clean by qa; I did
  not re-run it (constraint: only qa invokes runners), but the entry text itself is sound.

**SC-09 (inspection)** — confirmed by direct read: DEC-211 states private-copy isolation,
`test-suite-independence.py`, the worker-count rule, `--mutation-check`, and change-based selection
REJECTED with its reason, each in >=1 full sentence. No stub.

**Verification gaps section** — accurately scoped; nothing here rests on a null `cmd` kind.

## Stage 2 — code quality, fail-open hunt

### HIGH (new) — `run_pool.py`'s `--mutation-check` is blind to two symlink vectors it claims to cover

`snapshot()` (`run_pool.py:29-42`) walks `root`, and any per-path `os.stat` failure is swallowed
silently: `except OSError: continue` (`:38-40`) drops that name from `state` entirely — it is not
recorded as absent-with-a-marker, it simply never existed to the diff. Confirmed by direct
reproduction against the shipped module (loaded via `importlib` from a system tempdir, never
touching the checkout):

1. **A newly created dangling symlink inside the watched dir is invisible.** `before`/`after`
   snapshots around `os.symlink(<nonexistent target>, watched/"evil.sh")` are byte-identical;
   `mutated = []`. This is exactly the "new file created under DIR" vector D-11 names as the one a
   git-based watched set cannot see and this mechanism is built to catch — it does not catch it when
   the created path is a broken symlink, because `os.stat` follows the link, the target does not
   exist, and the `except OSError: continue` drops it.
2. **A newly created symlinked subdirectory hides everything under it, permanently.** `os.walk`'s
   default `followlinks=False` means a symlink-to-directory is listed in `dirs`, never recursed
   into. Reproduced: creating `watched/linked -> <external tempdir>` and then rewriting a file
   inside the external target produces `before` and `after` snapshots that are **both empty** —
   `mutated = []` on both a create and a subsequent content change. Nothing under a symlinked
   subdirectory of `BIN_DIR` is ever measured, before or after.

Concrete failure scenario: a test (buggy, or a future author reusing an existing idiom without
knowing this constraint) does `os.symlink("/tmp/attacker", ".claude/skills/harness/bin/.stage")`
then writes a payload file under `.stage/`. `run_pool.py --mutation-check "$BIN_DIR"` exits 0, no
`MUTATED` line — the exact "no test mutates state shared with any other process" property REQ-01
exists to hold, silently violated by the very mechanism D-11 built as backstop against the static
scanner's own blind spots. Neither D-11's "WHAT IT COVERS AND WHAT IT DOES NOT" paragraph nor
DEC-211's "coverage boundary is explicit" section names this limit — both describe the runtime check
as "vector-agnostic" inside `DIR`, which these two vectors falsify. Root-as-a-symlink (the
`--mutation-check` argument itself pointing through a symlink) was also probed and is **not** a
problem — `os.path.isdir`/`os.walk` follow it transparently and the watched files are measured
correctly; the gap is specific to symlinks *appearing inside* the watched tree during a run.
Pointer: `run_pool.py:29-42` (`snapshot`), `:38-40` (the swallowing `except`).

### MED (new) — same-size/same-mtime content swap defeats detection; undisclosed

`snapshot()` records only `(st_size, st_mtime_ns)`, no content hash. Reproduced: overwrite a
watched file with same-length different content, then `os.utime(path, ns=(atime_ns,
original_mtime_ns))` to restore the exact nanosecond mtime — `mutated = []`. This requires a
deliberate forge (nanosecond-exact `os.utime`), not an accidental collision, so it is a narrower
threat than the symlink gap above and I am not raising it as a blocking defect on its own. What I am
flagging: D-11's "WHAT IT COVERS AND WHAT IT DOES NOT" paragraph and DEC-211's "coverage boundary"
section both go out of their way to name precise, narrow blind spots elsewhere (the `__file__`-only
taint seed, the content-read exclusion, the subprocess/helper vectors) — this stat-only resolution
limit is the same *class* of honest disclosure the rest of the decision insists on, and it is the
one boundary condition missing from both. Pointer: `run_pool.py:29-42`; `plan.yaml` D-11 "WHAT IT
COVERS AND WHAT IT DOES NOT"; `DECISIONS.md` DEC-211 "The coverage boundary is explicit."

### HIGH (corroborated, extends qa's finding with an independent read) — `test-suite-independence.py` has zero durable self-test

Independently re-read the full 180-line file (not just qa's description): `main()`, `scan_file`,
`_scan_statements`, `_sink`, `discover`, `scan_directory`, `resolve_scan_root` — no `case()`, no
`case_*` function, no fixture-source string anywhere in the file. Running it with no arguments does
exactly one thing: scan the live tree, print `root`/`discovered`/any `VIOLATION` lines, exit 0 or 1.
T-03's `intent:` mandates, verbatim, seven in-file red-proof cases (injection idiom, mutant-beside-
original, PID-named variant, a clean control, a live-tree case with `discovered >= 50` and an
independently-recomputed root, and a root-refusal case) so that "CI keeps proving the guard can
fail." None exist. Agree with qa's mutation result (I did not re-run it — that is qa's instrument —
but the code read alone is sufficient: there is no assertion machinery in the file that a mutated
`scan_file` could possibly trip). Consequence: `test-suite-independence.py`'s own correctness — the
mechanism that stands as this feature's "completeness instrument" per D-10 — has no CI-enforced
regression protection past this one build. Pointer: `.claude/skills/harness/bin/test-suite-independence.py`
(whole file); `plan.yaml` T-03 intent, "ITS OWN RED PROOF, in the file."

### MED (corroborated) — `test-run-pool.py`'s mutation-check case has no `__pycache__` leg

Independently re-read the full 96-line file. The mutation-check block (`main()`, the `watched =
…` section) builds exactly four legs — clean, direct edit, subprocess edit, new-file creation —
plus the empty/missing-directory refusal. No `__pycache__` reference anywhere in the file. T-04
intent item (g) explicitly requires this leg ("it must NOT be reported, or the check reddens on the
interpreter's own byte-code caching every real run"). `run_pool.py`'s `snapshot()` does correctly
exclude `__pycache__` (`:32`, `dirs[:] = [d for d in dirs if d != "__pycache__"]`) — this is a test
gap, not an implementation defect, but a real one: a future edit that drops the exclusion ships
green until the next real run reddens spuriously. Pointer: `test-run-pool.py` (whole file, no
`__pycache__` string); `run_pool.py:32`; `plan.yaml` T-04 intent item (g).

### Code grade — `code-grade.py --base d135364e --head 8e7f56dc` (exit 1, PASSING: 18)

`code_grade: fail`. Five grade-1 records block the build; two grade-2 records require a reasoned
answer (neither blocks on its own).

**Grade-1, blocking (HIGH each):**
- `run_pool.py:52 main` — CYCLOMATIC 19, COGNITIVE 29, ABC 58.1, GRADE 1, bar 4, driver `abc`. The
  CLI does argument parsing, worker-count resolution, the mutation-check snapshot pair, pool
  execution/printing and the summary lines in one function — five distinct responsibilities that
  the file's own `snapshot`/`run_one`/`worker_count` helpers show it knows how to extract; `main`
  itself was never decomposed the same way.
- `test-check-domain.py:1432 run_schema` — CYCLOMATIC 6, COGNITIVE 5, ABC 48.1, GRADE 1, bar 3,
  driver `abc`. ABC-dominated (not branching): a long sequential chain of `fire(...)`/`case(...)`
  calls across many schema-validation scenarios; this task's own diff added the copied-hook control
  step to an already-large function rather than splitting it.
- `test-run-pool.py:35 main` — CYCLOMATIC 33, COGNITIVE 25, ABC 103.2, GRADE 1, bar 3, driver
  `cyclomatic+abc`. Entirely new file; every one of the nine test-run-pool.py cases (attribution,
  failure propagation, run-once, worker env x2, invalid-worker x2, order, cap, mutation-check x4
  legs, empty/missing) lives inline in one `main()` with no `case_*` decomposition — the same shape
  qa flagged as missing a `__pycache__` leg is also, independently, a grading-bar violation.
- `test-suite-independence.py:70 _sink` — CYCLOMATIC 36, COGNITIVE 42, ABC 54.5, GRADE 1, bar 3,
  driver `cyclomatic+cognitive+abc`. The sink-matching dispatch (`open`/`os.*`/`shutil.*`/Path
  methods) is one long sequential `if` chain rather than a table keyed by `(owner, name)`; the same
  file's `_call_name` shows the pieces exist to build one.
- `test-suite-independence.py:98 _scan_statements` — CYCLOMATIC 20, COGNITIVE 45, ABC 34.4, GRADE 1,
  bar 3, driver `cognitive`. Recursive per-statement-kind handler (`Assign`/`With`/`FunctionDef`/
  `If`/`For`/`While`/`Try`) with nested nesting through nested control-flow bodies; the cognitive
  score is the recursion-through-branches pattern the metric is built to catch.

**Grade-2, reasoned (MED each, non-blocking):**
- `test-suite-independence.py:58 _path_receiver` — CYCLOMATIC 11, GRADE 2. REASON: a small,
  side-effect-free recursive AST-shape matcher; every branch is a direct pattern match over the
  finite path-construction shapes (`BinOp`/`Div` recursion, `Path(...)` call, `pathlib.Path(...)`
  call) rather than nested business logic. Accepted at grade 2 without restructuring.
- `test-check-fixture-secrets.py:171 run_sk_ant_red_proof` — CYCLOMATIC 5, ABC 27.3, GRADE 2.
  REASON: a red-proof test case in this suite's established idiom (mutate source, write to an
  isolated copy, fire the hook twice, assert); ABC is driven by call count on an otherwise
  straight-line sequence, matching the shape of every other `*_red_case`/`run_*_red_proof` function
  in this file and its siblings. Accepted at grade 2 without restructuring.

### Declined findings (recorded per P-15, not re-raised as gates)

- `run_pool.py`'s `--workers 0` CLI-level path (as opposed to the tested `HARNESS_TEST_WORKERS=0`
  env path) is not exercised by `test-run-pool.py`. Not required by T-04's intent items (a)-(g), the
  code path is trivial and symmetric with the tested env-var path (`worker_count`, `:12-25`,
  single shared `if explicit <= 0: raise` guard covers both), and T-04's own build-time `verify:`
  block did exercise `--workers 3` at least once. Not gating.
- The new avenue to exit 2 in `run-unit-tests.sh` via a malformed `HARNESS_TEST_WORKERS` — declined
  above under REQ-06, restated here: a real behavior change, but an intentional and narrow one, and
  unreachable through the only caller in scope.
- Root-directory-as-symlink for `--mutation-check DIR` itself: probed, confirmed correct (detects
  mutations to the target transparently). Not a finding.

## Verdict rationale

`severity_max: high` — three independent sources of HIGH: the new `run_pool.py` symlink gap, the
corroborated `test-suite-independence.py` self-test absence, and five grade-1 code-grade blocking
records (`code_grade: fail`). `must_fix` non-empty. FAIL. Nothing here is stylistic; every finding
states a concrete failure scenario I reproduced or read to confirmation, never "this could be
fragile."
