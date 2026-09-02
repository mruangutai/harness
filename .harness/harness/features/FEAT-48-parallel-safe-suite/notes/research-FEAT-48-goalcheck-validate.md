# Goal-check — FEAT-48 at review_sha 8e7f56dc

**Nine of ten criteria are met. SC-03 is unmet, for a test-only reason, and it is
approved-but-unmet: T-03's signed intent mandates six in-file red-proof cases in
`test-suite-independence.py` and the shipped file contains none.** Every grade below was taken by
executing the criterion's own declared method in this worktree today; file content is read at
`8e7f56dc`. The validator panel's digest was read only after these ten grades were written.

## Grades

| SC | Verdict | Method executed | Deciding evidence |
|---|---|---|---|
|SC-01|**met**|automated (integration)|`python3 bin/test-check-domain.py` → exit 0; `md5sum`+`stat -f %m` on `bin/feature_schema.py` identical before/after (`7df7ef56…`, mtime `1788333510`); the three schema cases print `ok`, including *a CRASHING schema module DENIES the write* which still asserts `returncode==2` and `"CRASHED" in r.stderr` (`git show 8e7f56dc:.claude/skills/harness/bin/test-check-domain.py:1491-1498`)|
|SC-02|**met**|inspection|`git show 8e7f56dc:…/notes/measurements-parallel-suite.md` — `control method: isolated bin copy`, `control broken reads 4968`, `post-fix broken reads 0`. Control is capable of the hazard: `git show ea6f51f:…/test-check-domain.py:1482` is `open(fs,"w")` on the live module. Neither FAILS IF clause fires|
|SC-03|**unmet**|automated (unit)|`git show 8e7f56dc:…/test-suite-independence.py` holds **no assertions at all** — no injection-idiom case, no mutant-beside-original, no PID-named variant, no clean control, no live-tree case asserting `discovered>=50` or an inline-recomputed root, no root-refusal case; `tempfile` is imported at `:9` and never used. See below|
|SC-04|**met**|automated (unit)|`run-unit-tests.sh --kind unit` → exit 0, emits `PASS test-suite-independence.py`; the block above it prints `root <worktree>`, `discovered 63`, `ok …`|
|SC-05|**met**|inspection|measurements note `## Ten consecutive runs`: ten `run <i> exit 0 <wall>s` lines (46.84–53.16s), plus a non-empty `tree condition:` line. Corroborated, not substituted: my own `--kind all` today exited 0 with no `FAIL` and no `MUTATED`|
|SC-06|**met**|inspection|note records `pool: 8 workers, 63 files, 48.13s wall`. **Re-taken by me:** `pool: 8 workers, 63 files, 44.02s wall`, exit 0. 44.02s ≤ 120s; both worker count and wall time are printed|
|SC-07|**met**|automated (integration)|`--check-kinds` → exit 0, agreement line, no `-----` block, no file verdict; `--kind bogus` → exit 2 with the legal-kinds message; `--kind unit` 33 blocks/33 files, `--kind integration` 30 blocks/30 files, exit 0. Failing-file→1 established by composition (see caveats)|
|SC-08|**met**|automated (integration)|`bin/test-run-pool.py` → 11/11 `ok`, incl. *completion order is not input order*: `p_order != s_order and set(p_order)==set(s_order)`, where `s_order` is the `--workers 1` run and therefore the input order (`as_completed` over one worker yields submission order). All three clauses ride that one check|
|SC-09|**met**|inspection|`git show 8e7f56dc:.harness/harness/docs/DECISIONS.md:6563-6614` = DEC-211, **573 words**, stating private-copy isolation, the derived-scope invariant, the runtime snapshot with its watched-set reason, the literal worker rule `min(8, max(2, os.cpu_count() or 2))`, and change-based selection **REJECTED** with three reasons (coverage becomes a function of the diff; the floor is one file most diffs reach; bash→test forks are not statically knowable). `gen-decisions-index.py --stdout \| diff -` → identical, re-run by me|
|SC-10|**met**|automated (integration)|`test-run-pool.py` asserts clean/direct/**subprocess**/creation in one conjunction plus `MUTATED keep.txt`, `MUTATED .mutant-x.sh` (paths relative to DIR) and empty+missing DIR → exit 2; all `ok`. `__pycache__` non-report **re-derived by me** in a tempdir: a rewritten *and* a newly created `.pyc` under the watched dir land on disk while the pool exits 0 with no `MUTATED` line. Invocation line is exactly `exec python3 "$BIN_DIR/run_pool.py" --mutation-check "$BIN_DIR" -- "${SCRIPTS[@]/#/$BIN_DIR/}"` (`run-unit-tests.sh:151`)|

## SC-03 — why unmet, and the lane

The criterion needs the live-tree zero **and** the ten `ea6f51f` sites in the same run, each site
asserted individually, with `discovered>=50` and the printed root checked.

- **The historical half passes when run.** I extracted T-03's `verify:` block from
  `plan.yaml:599-632` and executed it verbatim: exit 0, `root == git rev-parse --show-toplevel`,
  `discovered [63]`, `found 10 missing [] extra []`. All ten sites are asserted as set membership,
  so none can be quietly lost. The lead's reading of the plan is confirmed at source on this half.
- **No gate re-executes it.** The shipped unit evidence is `test-suite-independence.py`, whose
  automated result is the live scan's exit code alone — the very shape SC-03's FAILS IF names
  ("an exit code alone is satisfied by a scanner that walked nothing"). `discovered 63` and the
  resolved root are *printed*, never asserted, so a resolver landing one level off, or a walk that
  found nothing, still exits 0.
- **The plan's other half was not built.** T-03's intent (`plan.yaml:756-794`) mandates *ITS OWN RED
  PROOF, in the file, so CI keeps proving the guard can fail* — six named cases. `grep` over the
  committed file finds no `check(`/`case(` machinery and no fixture strings; the unused `tempfile`
  import is the residue. CI therefore never proves this guard can fail, and a future edit that
  weakens `_sink` reddens nothing.

**Remedy lane: test-only** — add the six mandated cases to `test-suite-independence.py`. It is
**approved-but-unmet**: already required by the signed plan, so no new operator ruling is needed.
DEC-174 makes that file `main-session-direct`, so the fix is a main-session step, not a squad task.

## Caveats on met grades — advisory, not gating

- **SC-07's failing-file clause is composed, not gated.** No test drives `run-unit-tests.sh`
  end-to-end with a deliberately failing file, and `test-run-unit-tests-kinds.py` is unchanged and
  covers only `--check-kinds`/unknown-kind. I proved the missing link myself:
  `HARNESS_TEST_WORKERS=0 run-unit-tests.sh --kind unit` → exit 2, i.e. the `exec`ed pool's status
  is the runner's, and `test-run-pool.py` asserts rc 1 for a failing file.
- **Six file-shaped verdict lines are duplicated** (`test-expertise-merge`, `test-feature-worktree`,
  `test-observations-merge`, `test-panel-findings`, `test-plan-merge`, `test-quarantine` each print
  their own `PASS <file>.py` self-summary). All six did so at `d135364e`, so this is pre-existing and
  **not** an SC-07 regression. The runner still emits exactly one block and one verdict per file.
- **SC-08's verdict-set clause runs over an all-pass set**, so parallel-vs-serial equivalence is
  untested for a mixed set. Neither FAILS IF fires.
- **SC-10's `__pycache__` clause has no committed fixture** and its invocation clause has no
  automated assertion — both hold today (I checked both) but can regress silently.
- **SC-02's numbers are not re-derivable.** The fenced blocks beside the control are hand-composed
  key/value lines, not a verbatim transcript, and the poll harness is not committed or cited by
  path, so `4968` cannot be reproduced by a reader. The BRIEF's own `## Verification gaps` concedes
  this limit; it does not fire a FAILS IF.

## Emergent — not SC-covered, candidate backlog rows

1. **`run_pool.py:33-42` cannot see a new symlink.** `os.stat` on a dangling symlink raises and is
   swallowed by `continue`; `os.walk` does not descend a symlinked directory and does not list it as
   a file. So a test creating a symlink under `bin/` — a plausible mutation vector adjacent to
   `.mutant-*.sh` — reports clean. Reproduced by the orchestrator this session in a tempdir; not
   named by SC-10, which enumerates the ordinary-file case. Nature: **bug** (low severity).
2. **A size-preserving overwrite plus a nanosecond-exact `os.utime` restore is invisible** to
   `snapshot()`, which records `(st_size, st_mtime_ns)` and no content hash. Credited to the panel
   (M5); I did not find it. A deliberate forge, outside every SC-10 clause. Nature: **documentation**
   — the DEC-211 / D-11 disclosure edit that states M1's boundary should state this one too.
3. **`PASS <file>.py` is not a runner-reserved line shape** (caveat 2 above). Any test file can
   forge a file verdict. Pre-existing, unchanged by this feature. Nature: **chore**.

None is adopted as a criterion — that is the operator's call.

## Panel comparison — second opinion, read after the grades above

`runs/2026-09-02-16-validator/digest.md` (FAIL, `severity_max: high`), `notes/qa-c7.md`,
`notes/review-harness-*-c7.md`.

**Agree, independently reached.** M2 = my SC-03 unmet; the panel's mutation proof (`scan_file`
patched to `return []` yields byte-identical exit-0 output) is stronger evidence than my read and
points the same way. M1 = my emergent 1. M4 = my SC-10 `__pycache__` caveat. Their "69 PASS over 63
files is pre-existing" ruling matches mine, derived separately at `d135364e`.

**Differ — and my grade stands.** The panel records SC-03 under *two* statuses and routes the choice
up as its Q1 ("some automated run at build time asserted it" versus the literal reading). That
question dissolves at source: `plan.yaml:776-789` — signed — mandates the live-tree half **in the
file**, "asserted as a case rather than only as the exit code", asserting `discovered >= 50` and a
root *recomputed inside the case*. SC-03's "having first printed the root it resolved and a
`discovered` count of at least 50" is that case. It does not exist. So SC-03 is unmet on the signed
text, not on a choice between readings, and no operator ruling is needed to grade it.

**Theirs, not mine, and not an SC.** M3 `code_grade: fail` (5 grade-1 records; I re-ran nothing of
it) and M5 are gate/disclosure matters that fire no SC-01..SC-10 clause. M5 is now emergent 2 above.

**Not overturned by them.** Their `qa_gate: matrix_ok: true` and three green `--kind all` runs are
consistent with my own runs and do not bear on SC-03: a green suite is exactly what an unfalsifiable
invariant produces.
