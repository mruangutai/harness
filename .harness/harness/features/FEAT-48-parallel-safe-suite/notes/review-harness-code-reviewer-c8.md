# Code Review c8 — FEAT-48 — `e64e863e`

**BLUF: FAIL.** `run_pool.py:37-40` has a new, reproduced crash bug (unguarded second
`os.lstat` on a directory symlink, TOCTOU race) introduced by this exact commit, and
`code_grade` is mechanically `fail` (9 blocking records; this commit added 2 of them,
grades 2 and 1). One prior HIGH (M1, symlink blindness) and one HIGH (zero self-test) are
genuinely closed. Two prior MEDs (M4, M5) remain open, unfixed, undisclosed.

## Q1 — `snapshot()` fail-open surface, file loop vs directory loop

**File loop `except OSError: continue` (:48-51):** does NOT still hide the two named
vectors — both close via `os.lstat` succeeding on a dangling symlink (P3, reproduced
independently by me: same-size/mtime-swap probe below confirms the tuple format).
Remaining triggers for this `except` (ENOENT/EACCES/ENAMETOOLONG on a name `os.walk`
already listed) are a same-call TOCTOU window of microseconds between `os.walk`'s
listdir and this `lstat`. For every such miss, the key-union compare at `run_pool.py:105-106`
(`before.keys() | after.keys()`, `before.get(name) != after.get(name)`) still catches it
**unless the failure is identical in both the before- and after- snapshot** — at that point
the file is unstat-able throughout the run and no metadata-based detector (pre- or
post-fix) can observe it. Not a live defect introduced by this commit; a pre-existing,
structural limit of stat-based detection. No finding.

**Directory branch `os.lstat(path)` at :38 is unguarded — REPRODUCED CRASH.** Unlike the
file loop, nothing wraps this call. `os.path.islink(path)` (:37) and the explicit
`os.lstat(path)` (:38) are two separate syscalls; if the symlink is removed between them
(e.g., by a test script's own cleanup of a scratch symlinked dir it created under the
watched root — the exact watched root is `$BIN_DIR` itself per `run-unit-tests.sh:148`,
shared by all 63 concurrently-run files), the second call raises `FileNotFoundError`
uncaught, propagating out of `snapshot()` through `main()` — the entire pool run crashes,
not just the one file. Reproduced deterministically by making `os.path.islink` unlink the
target as a side effect before returning `True` (simulating the interleaving):
`CRASHED: FileNotFoundError: [Errno 2] No such file or directory: '.../linked-dir'`.
Confirmed via `git show b86ce66a:...run_pool.py` that this second-`lstat`-after-`islink`
pattern did not exist pre-fix (old code just did `dirs[:] = [d for d in dirs if d !=
"__pycache__"]`, no symlink special-case) — **this is new code this commit introduced
while closing M1, not a residual gap.** Severity: MED (narrow window, no current test
removes a directory symlink mid-run so it's latent, not currently firing in CI) but real,
reproduced, and a regression against the fix's own goal of hardening this exact code path.
`must_fix`.

## Q2 — `__pycache__`/`.pyc` exclusion (:34-35, :45-46)

Necessary, not a hole. `run_pool.py` executes `[sys.executable, path]` for every watched
script; several scripts under `$BIN_DIR` `import` sibling modules (e.g.
`test-suite-independence.py:13 import harness_boundary`), and Python writes
`__pycache__/*.pyc` for every imported module. Confirmed empirically: a bare run of
`test-suite-independence.py` left 40 `.pyc` files already sitting in `bin/__pycache__`
(gitignored, `.gitignore:24`). Without the exclusion, `--mutation-check "$BIN_DIR"` would
report a spurious `MUTATED` for interpreter bytecode caching on effectively every
invocation — a 100% false-positive rate that would make the invariant unusable. The
exclusion is a correct, necessary fix. No finding.

## Q3 — `run_self_tests` as production test infrastructure

**(a) Embedded fixture literals (:172-197, :204-212):** maintainable as-is at this size
(4 cases, ~30 lines total of source strings) — inlining keeps each case's expected line
numbers visually adjacent to the source that produces them, which a data table would
obscure. Not a finding; would become one past ~2x this many cases.

**(b) Live-tree upward walk (:207-215) is a THIRD copy of the MARKER constant, not an
independent control.** `harness_boundary.py:41` names `MARKER = os.path.join(".harness",
"team-config.yaml")` specifically to stop per-caller reinvention (comment at
`harness_boundary.py:35-40` names FEAT-42 T-01 and cites wayfind.py's bare-`.harness`
probe as a recorded fail-open). `test-suite-independence.py:210` hardcodes
`os.path.isfile(os.path.join(current, ".harness", "team-config.yaml"))` — the literal
path segments, not `harness_boundary.MARKER`. The WALK algorithm is genuinely independent
of `root_above`'s implementation (that's the self-test's real value — proving the
algorithm, not the constant), but the marker string is duplicated by value, exactly the
class this repo already fixed once. `should_fix`, med: reference `harness_boundary.MARKER`
in the `os.path.join` call while keeping the hand-written while-loop; this keeps the
algorithmic independence the self-test needs and removes the duplicate literal.

**(c) Failure detail is actionable.** Traced `failures` → `run_self_tests` return →
`main():253-262`: each case appends a specific string (`"{name}: expected {sorted},
got {sorted}"`, `"clean controls: {findings!r}"`, `"live tree: root=... expected=...
discovered=... findings=..."`, `"root refusal: resolved=... refused=..."`), and every
`FAIL self-test <name>` line (printed inline by `run_self_tests` itself) is followed in
CI output by `FAIL self-test detail: <that string>`. A maintainer can locate the broken
case by name and see the actual-vs-expected values without re-running anything. No finding.

## Q4 — `run_self_tests()` runs unconditionally, including under `--scan-dir` — REPRODUCED

Ran `test-suite-independence.py --scan-dir /tmp/feat48-scan-target` (empty dir): output
still printed `ok self-test live tree, independent root and discovered floor` — confirming
`run_self_tests()` scans the **live checkout**, not the caller's requested root, regardless
of `--scan-dir`. Then, without editing any file, monkeypatched `scan_directory` to inject
one synthetic finding only when called with the live root and re-ran
`main(["--scan-dir", <empty tmpdir>])`: exit code **1**, `discovered 0` /
`FAIL 0 live-tree mutation site(s)` for the requested target, but the run still failed
solely because of `FAIL self-test detail: live tree: ... findings=1` — **a live-tree
violation fails a run that asked to scan somewhere else entirely.** Cost: measured
`discover()` called twice over the same live root in the default (no `--scan-dir`)
invocation, ~1.18s total vs the ~0.6s a single pass takes — real but modest per-invocation
duplication. Rule: this is a defect in `--scan-dir`'s contract (it implies "scope the check
to this directory," which it does not do), MED, `should_fix` — either skip
`run_self_tests()`'s live-tree case when `--scan-dir` is set, or document that
`--scan-dir` narrows only the reported violations, not the self-test gate.

## Q5 — c7 finding reconciliation

| Finding | Disposition | Evidence |
|---|---|---|
| HIGH — `snapshot()` blind to dangling/dir symlinks (M1) | **closed** | P3 reproduction stands; independently re-derived the same before/after asymmetry via `os.lstat` semantics. Superseded in part by the new Q1 finding above — same code region, different defect (crash, not miss). |
| HIGH — zero durable self-test (self-test suite) | **closed** | Traced `main():250` → `run_self_tests()` unconditional; 6 cases read line-by-line, each appends a distinguishable failure string on mismatch (Q3c). Matches P1/P2. |
| HIGH — `code_grade: fail`, 5 blocking records | **open, worse** | Reran `code-grade.py --base d135364e --head e64e863e`: confirms 9 FAIL records (was 7 at `8e7f56dc`). See Q6. |
| MED — same-size/same-mtime swap defeats detection (M5) | **open** | Reproduced directly: wrote `keep.txt`="AAAA", snapshotted, overwrote to "BBBB", `os.utime`-restored the exact `mtime_ns`, snapshotted again — `mutated == []`. Tuple is `(st_mode, st_size, st_mtime_ns)` only, no content hash; unfixed and undisclosed by this commit. |
| MED — no `__pycache__`/`.pyc` leg in `test-run-pool.py` | **open** | Read the full mutation-check test body (`test-run-pool.py:75-109`): clean/edit/subprocess/create/dangling-symlink/dir-symlink/empty/missing legs only. The exclusion added at `run_pool.py:34-35,45-46` (Q2, judged correct) has no test pinning it — a future typo (`.pyc`→`.pyx`, or dropping the `__pycache__` name check) would go undetected. |

## Q6 — `code_grade`

**`code_grade: fail` is a real gate (mechanical, `validate-digest.py`-enforced) that this
commit currently fails to clear, and it made two records worse while doing so — both
things are true at once; it is not purely inherited debt.**

Reran `code-grade.py --base d135364e --head e64e863e` myself (`d135364e` = confirmed
`merge-base(origin/main, e64e863e)`, the canonical range `validate-digest.py` will
independently recompute): **exit 1, 9 FAIL / 19 PASS, confirms the lead's count exactly.**
Re-ran against `--head 8e7f56dc` (the commit immediately before this fix) to partition:

- **7 pre-existing, untouched by this diff** (confirmed via `git diff b86ce66a..e64e863e`
  — only `run_pool.py:29-54 snapshot()` changed in `run_pool.py`; `main()` body is
  byte-identical, its FAIL record just shifted from line 52→64 as `snapshot()` grew):
  `run_pool.py:64 main` (grade 1, high), `test-check-domain.py:1432 run_schema` (grade 1,
  high), `test-check-fixture-secrets.py:171 run_sk_ant_red_proof` (grade 2, med),
  `test-run-pool.py:35 main` (grade 1, high), `test-suite-independence.py:58
  _path_receiver` (grade 2, med), `:70 _sink` (grade 1, high), `:98 _scan_statements`
  (grade 1, high).
- **2 introduced by this diff:** `run_pool.py:29 snapshot` (grade 2, med, driver
  cognitive), `test-suite-independence.py:170 run_self_tests` (grade 1, high, driver abc,
  CYCLOMATIC 14 / COGNITIVE 29 / ABC 49.7).

Because the pre-existing 7 are untouched, unmodified code outside this diff's blast
radius, I score them for transparency but exclude them from `must_fix` — gating this
landing on unrelated debt in 5 other functions this commit never opened would itself be
scope creep. The 2 introduced records are squarely in scope and are `must_fix`.

**Decomposition, concretely, per introduced record:**
- `run_self_tests` (:170-238): the diff already extracted `_fixture_findings` and
  `_resolved_root_or_exit` as leaf helpers (confirmed in the diff), but left the four
  self-test blocks — the 3-case loop, the clean-controls check, the live-tree check, the
  unresolved-root check — sequential in one function body. Extracting leaf utility calls
  did not touch the orchestrating function's own complexity because the complexity lives
  in the *four independent, mutually-uncoupled* blocks, not in the calls between them.
  Splitting each block into its own top-level function (each returning its own failure
  list) genuinely reduces `run_self_tests`'s measured grade rather than relocating it: the
  four extracted functions have no data coupling beyond a shared `tempfile.TemporaryDirectory`
  scope for the first two, and the orchestrator becomes ~5 lines (4 calls + list
  concatenation), well under bar. This is a real fix, not a shell game — recommend it.
- `snapshot` (:29-54, driver cognitive): the added directory-symlink branch nests a new
  `if os.path.islink(path): ... else: ...` inside the existing `for name in dirs` loop,
  and the file loop already carries its own `try/except`. Extracting "resolve one dir
  entry" and "resolve one file entry" into two small helpers removes two levels of nesting
  from `snapshot`'s own body (nesting depth drives cognitive complexity specifically);
  plausible this alone clears the grade-2 bar to 3+, though unverified without applying it.

**What the c7 panel's prediction says about the advice:** the panel predicted
decomposition would clear 3 of the 5 pre-existing grade-1 records; this fix cleared none
of those and added 2 more instead — while itself performing a *partial* decomposition
(`_fixture_findings`, `_resolved_root_or_exit`) that didn't touch the orchestrator's own
score. The advice is directionally correct (both new records above do have a genuine,
non-relocating decomposition available) but was not applied to the code being written in
*this* commit, and nothing in the pipeline currently blocks a grade-1 addition at
commit-time — the gate only fires at review. Advice without a write-time enforcement point
gets skipped even by the author actively fixing adjacent grade-1 debt in the same file.

```yaml
VERDICT: FAIL
DIGEST:
  headline: "Reproduced a new unguarded-lstat crash on directory-symlink removal (run_pool.py:38), and code_grade is fail with 2 records this commit introduced (9 total, was 7)."
  severity_max: high
  findings: 6
  must_fix:
    - "run_pool.py:38 snapshot() — unguarded os.lstat after os.path.islink on a directory entry crashes the whole pool run if the symlink is removed between the two calls; reproduced via forced interleaving. New in this commit (pre-fix code had no directory-symlink branch)."
    - "code_grade: fail — run_pool.py:29 snapshot (grade 2, med) and test-suite-independence.py:170 run_self_tests (grade 1, high, CYCLOMATIC 14/COGNITIVE 29/ABC 49.7) are both introduced by this diff; 7 other FAIL records are pre-existing and untouched, excluded from this must_fix."
  spec_violations: []
  reviewed: "d135364e..e64e863e"
  human_commits_in_scope: []
  open_questions:
    - { id: Q1, question: "test-suite-independence.py --scan-dir narrows reported violations but not the unconditional live-tree self-test gate — is that the intended contract, or should --scan-dir suppress the live-tree case?", blocking: false }
  files_touched: []
  expertise_update: []
artifact: .harness/harness/features/FEAT-48-parallel-safe-suite/notes/review-harness-code-reviewer-c8.md
```
