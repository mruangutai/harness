# Goal-check — FEAT-48 at review_sha e64e863e (cycle 8)

**The feature's goal is delivered at `e64e863e`. Nine of ten criteria are MET; the tenth, SC-03, is
UNMEETABLE AS WRITTEN — not because the code is wrong but because its own text and SC-04's collide:
the ten `ea6f51f` sites must be asserted "in the same run" as a check that SC-04 requires to run in
CI, and CI's `actions/checkout@v4` clones shallow, so `ea6f51f` does not exist there.** Everything
SC-03 asks for behaviourally is proven at this sha (all ten sites hit individually, live scan clean,
six red proofs discriminating). One operator signature on remedy (B) below closes the feature; no
build work is outstanding.

Provenance: `git diff 8e7f56dc..e64e863e` leaves `test-check-domain.py`, `run-unit-tests.sh`,
`DECISIONS.md` and `notes/measurements-parallel-suite.md` untouched, so evidence for SC-01/02/04/07/09
carries across the range legitimately. The three code files are byte-identical between `e64e863e` and
this working tree (`git diff --stat e64e863e -- <3 files>` empty), so behaviour I executed is the pin's.
All runs used `env -u HARNESS_AGENT_TYPE`.

## Grades

| SC | Verdict | Method executed | Deciding evidence |
|---|---|---|---|
|SC-01|**MET**|automated (integration)|`test-check-domain.py` exit 0; `feature_schema.py` mtime_ns/size/sha256 identical before and after (`1788333510516825193 / 15881 / 943ef7a7…`) — never written, not restored; crashing-checker case still asserts the write is DENIED. Orchestrator measurement at this sha; file unchanged in range, not re-derived|
|SC-02|**MET**|inspection|`git show e64e863e:…/notes/measurements-parallel-suite.md` — `control method: isolated bin copy`, `control broken reads 4968` (>0), `post-fix broken reads 0`. Unaffected by this commit: the hazard lives in `test-check-domain.py`, unchanged in range. Neither FAILS IF fires|
|SC-03|**UNMEETABLE-AS-WRITTEN**|automated (unit)|Half one MET and gated: `test-suite-independence.py:207-219` (at pin) asserts `live_root == expected` (root recomputed by an independent marker walk inside the case), `len(files) >= 50` and `not live_findings`; `main()` calls `run_self_tests()` at `:250`, before the scan, and returns 1 on any self-failure at `:256`. Half two is asserted by no CI-run gate — see the ruling below|
|SC-04|**MET**|automated (unit)|`run-unit-tests.sh --kind unit` exit 0, 33 files, emits `PASS test-suite-independence.py`. Re-taken by me: exit 0, 33 blocks, 0 `FAIL`, `pool: 8 workers, 33 files, 13.78s wall`|
|SC-05|**MET**|inspection|**Re-taken post-rewrite by me** — see "SC-05/SC-06 sufficiency" below. Ten consecutive `--kind all`, all exit 0, zero `FAIL`, zero `MUTATED`: 78.47, 48.21, 48.85, 49.36, 49.45, 49.26, 47.94, 47.60, 48.56, 54.19s, all at 8 workers / 63 files. Tree condition: sibling c8 panel agents writing `.harness/harness/features/FEAT-48-*/notes/*` throughout (four untracked notes appeared across the ten); nothing wrote `.claude/skills/harness/bin/` — run 1's 78.47s is that concurrent load|
|SC-06|**MET**|inspection|Every one of eleven runs printed both numbers; worst wall time 78.47s ≤ 120s against the 247s serial baseline. `pool: 8 workers, 63 files, 48.21s wall` is representative|
|SC-07|**MET**|automated (integration)|`--check-kinds` exit 0, prints `check-kinds: the script arrays and test_kinds.integration.detect agree.`, runs no test; `--kind bogus` exit 2 with the legal-kinds message; `--kind unit` 33 blocks / 33 files, `--kind integration` 30 blocks / 30 files, both exit 0 — one runner block and one runner verdict per file. Failing-file→1 remains composed, not gated (caveat below)|
|SC-08|**MET**|automated (integration)|`test-run-pool.py` 12/12 `ok` at the pin, incl. *completion order is not input order* — `p_order != s_order and set(p_order) == set(s_order)`, where `s_order` is the `--workers 1` run (`test-run-pool.py:63-67`)|
|SC-09|**MET**|inspection|DEC-211 at the pin carries all five required items including change-based test selection REJECTED with reason; `gen-decisions-index.py --stdout` byte-identical (`cmp`) to `DECISIONS-INDEX.md`. Orchestrator measurement; `DECISIONS.md` unchanged in range|
|SC-10|**MET**|automated (integration)|`test-run-pool.py:78-92` asserts clean / direct / **subprocess** / creation with `MUTATED keep.txt` and `MUTATED .mutant-x.sh` (paths relative to DIR); `:109` asserts empty+missing DIR → exit 2 — all against the **new** `snapshot()`. `__pycache__` non-report **re-derived by me at this sha**: a rewritten `.pyc`, a newly created `.pyc` and a loose top-level `.pyc` all land on disk while the pool exits 0 with no `MUTATED`. Invocation clause holds verbatim: `run-unit-tests.sh:148` is `--mutation-check "$BIN_DIR"`|

## The five c7 findings, reconciled at `e64e863e`

- **M1 (HIGH, symlink blindness) — CLOSED, with a red proof.** `snapshot()` now `lstat`s, records
  `st_mode`, and records a symlinked directory as an entry instead of declining to descend
  (`run_pool.py:29-53`, the dir branch at `:33-41`). Orchestrator's pre/post probe: pre-fix copy exit 0 / no MUTATED for both
  vectors, post-fix `exit 1 MUTATED dangling` and `exit 1 MUTATED linked-dir`, clean control exit 0
  in both — no false positive traded for the fix. Durably enshrined at `test-run-pool.py:101-105`.
- **M2 (HIGH, no durable self-test) — CLOSED.** Six cases, run unconditionally before the scan, and
  all six discriminate under monkeypatch (blinding `scan_file`, over-eager `scan_file`, and a
  `resolve_scan_root` that never returns None each redden a distinct subset; none is never-red).
- **M3 (HIGH, `code_grade: fail`) — NOT fixed, and moved the wrong way: 7 records at `8e7f56dc`, 9
  at `e64e863e`.** The fix added `run_pool.py:29 snapshot` (grade 2) and
  `test-suite-independence.py:170 run_self_tests` (grade 1, high — CYCLOMATIC 14, COGNITIVE 29, ABC
  49.7). This is a **gate, not a criterion**: it fires no SC-01..SC-10 clause and I have not graded it
  as one. Where it bears: the two new records are both in code this commit added, so the ship
  decision buys nine SCs and a worse grade on the same diff. `run_self_tests` is one 60-line function
  holding five unrelated case groups; splitting it per group would cost nothing behavioural.
- **M5 (MED, size+mtime forge) — still open.** Emergent (i) below.
- **M4 (MED, no `__pycache__` leg) — still open.** Emergent (ii) below.

## SC-03 — the ruling, and the re-plan recommendation

**The premise is confirmed, not assumed.** `git show e64e863e:.github/workflows/tests.yml` has one
job, `integration`, whose first step is a bare `- uses: actions/checkout@v4` with no `with:` block.
Measured, not reasoned: a `git clone --depth 1` of this branch gives `rev-list count: 1` and
`git cat-file -e ea6f51f` → `fatal: Not a valid object name` (exit 128). The `.agents/` vs `.claude/`
discrepancy is a non-issue: `.agents/skills` is a tracked symlink (mode `120000`) resolving to
`.claude/skills`, so CI runs the same runner the diff names.

**The capability is proven at this sha, re-taken rather than inherited** (`scan_file`'s file changed
in range, so the predecessor's green was not carried): loading the pin's module and running
`scan_file` over `git show ea6f51f:` copies of all three files gives **found 10, missing 0, extra 0**,
each site hit individually. What is missing is only its enshrinement in a CI-run gate.

- **(A) `fetch-depth: 0` + assert the ten sites inside the invariant.** Bandwidth is the cheap part
  and I priced it: 1,023 commits, `size-pack 22.57 MiB` — seconds per run today, growing. The real
  costs are two. It makes a **unit test depend on the git object store**, so the invariant reddens in
  any shallow, exported or vendored checkout — a new failure mode on the file whose job is to be the
  trustworthy gate. And the workflow is edited by the PR that CI runs from the PR's own ref: this
  same file already documents that trap twice, for the plan-route and layout gates, and records that
  nothing detects it.
- **(B) Amend SC-03 so the ten-site assertion is a review-time automated check.** That is exactly
  T-03's `verify:` block, executed cleanly twice now (predecessor at `8e7f56dc`, me at `e64e863e`).
  The cost is real and small: CI stops re-running the historical half. It is small because the three
  idioms those ten sites embody — `dirname(realpath(__file__))` injection, mutant-beside-original,
  pid-named mutant — are each reproduced as a committed fixture case with exact expected line
  numbers, and all three are proven to redden when `scan_file` is blinded. CI keeps the idiom
  coverage; it loses only the literal blob.
- **(C), mine: vendor the ten sites as committed fixtures** — copy the three pre-fix snippets into
  the self-test corpus with expected line numbers, giving a CI-run, history-independent assertion of
  all ten. It buys back what (B) gives up, but the line numbers become *fixture* line numbers, so
  SC-03's literal `test-check-domain.py:1482` wording still needs amending — (C) is (B) plus work,
  not an alternative to it. A fourth shape, making the historical half conditional on
  `git cat-file -e ea6f51f` and printing `SKIP` in CI, I reject: a gate that is off in CI and loud
  only locally is this repository's most-repeated defect.

**Recommendation: (B).** (A) trades a documented, undetectable self-edit hole and a git-dependency in
the suite's own gate for a literal blob whose three idioms are already asserted by discriminating
in-file fixtures — the criterion's purpose is served, only its wording is not, and the wording is the
cheaper thing to change. Take (C) later as a backlog row if the idiom coverage ever feels thin.

**Under remedy (B), SC-03 reads MET at `e64e863e` on today's evidence — no further work.** Half one
is gated in-file and proven to discriminate; half two is a review-time automated check that has now
been executed cleanly at this exact sha with all ten sites individually hit. The feature can ship on
a signature alone.

## SC-05 / SC-06 — sufficiency of post-rewrite evidence, stated plainly

**The committed `notes/measurements-parallel-suite.md` ten are STALE evidence for SC-05 and I did not
inherit them.** They were taken before `snapshot()` was rewritten; `snapshot()` is part of the pool
SC-05 exists to watch, and the rewrite changes it in both directions (symlinks and `st_mode` now
recorded — more ways to redden; `.pyc`/`__pycache__` now skipped — fewer). A single `--kind all` does
**not** carry SC-05: its own text demands ten consecutive runs with each wall time and the tree
condition recorded, and its stated purpose is catching a new failure the pool introduces, which is
precisely what changed. So I re-took all ten (row SC-05 above). SC-06's text asks for one run and I
have eleven, so one would have sufficed there — but it too was re-taken post-rewrite.

Advisory, not a FAILS IF: SC-05's clause is "recorded", and the ten are now recorded here at the
graded sha. The plan-designated carrier note still holds the pre-rewrite ten, so refreshing it (a
T-06-shaped `main-session-direct` edit) keeps the durable record honest. Nothing gates on it.

## Emergent residuals — one disposition each

1. **M5, the size+mtime content swap.** `snapshot()` records `(st_mode, st_size, st_mtime_ns)` and no
   content hash, so a same-size overwrite plus a nanosecond-exact `os.utime` restore is invisible.
   → **Backlog row.** Rec: state the boundary in DEC-211 / `plan.yaml` D-11 beside M1's, as a
   deliberate-forge limit; no code change earns its weight.
2. **M4, the absent `__pycache__` leg in `test-run-pool.py`.** → **Covered by an existing SC** —
   SC-10 names it as a FAILS IF and it is MET, but on my hand-run probe rather than a gate. Rec:
   backlog a fixture leg so it cannot regress silently.
3. **The clean control's missing `src.replace(...)` leg.** The control
   (`test-suite-independence.py:192-205`) has a read-live/write-temp leg but not the
   read-then-mutate-then-write-temp shape that three live files use
   (`test-bash-write-guard.py:515`, `test-check-domain.py:2370`, `test-validate-feature-json.py:619`).
   → **Backlog row.** Rec: add that leg, so a future widening of `scan_file` cannot false-positive
   the repository's own standard red-proof idiom.
4. **The suite is green only with `HARNESS_AGENT_TYPE` unset** — set it and `test-plan-merge.py`
   fails 11 checks, in a file this feature does not touch. → **Genuinely new, and the operator's.**
   It is not covered: REQ-01/REQ-07 and SC-07/SC-08 are about independence from other *tests*, never
   from the ambient environment, yet "a green run means the tests passed rather than that the
   scheduler happened to be kind" is the feature's own goal sentence, one substitution away. Rec:
   take it as a separate `BUG-NN`, not a FEAT-48 scope expansion — FEAT-48 neither caused it nor
   touches the file, and folding it in would reset an approved plan.
5. **Mine: the new `.pyc` skip is by extension anywhere under DIR, not only inside `__pycache__`**
   (`run_pool.py:45`, against the `__pycache__` directory skip at `:34`; my probe above shows a loose top-level `loose.pyc` rewrite going unreported).
   SC-10's text licenses only "does not report a rewritten `__pycache__` entry", so `e64e863e` widened
   the blind spot past the criterion. No tracked `.pyc` exists under `bin/`
   (`git ls-files '.claude/skills/harness/bin/*.pyc'` → 0), so nothing is broken today.
   → **Backlog row.** Rec: gate the skip on a `__pycache__` path component — one condition, and the
   implementation then matches the criterion exactly.

## Caveats on MET grades — advisory, not gating

- **SC-07's failing-file clause is composed, not gated** (unchanged from c7): no test drives
  `run-unit-tests.sh` end-to-end with a deliberately failing file. The link holds —
  `test-run-pool.py` asserts rc 1 for a failing file, and the runner `exec`s the pool at :148, so the
  pool's status is the runner's.
- **Duplicate file-shaped verdict lines persist** (35 verdict lines over 33 unit blocks, 36 over 30
  integration blocks): several test files print their own `PASS <file>.py` self-summary. Pre-existing
  at `d135364e`, not an SC-07 regression; the runner still emits exactly one block and one verdict
  per file.
- **SC-02's numbers remain non-reproducible by a reader** — the poll harness is neither committed nor
  cited by path. The BRIEF's `## Verification gaps` concedes this; it fires no FAILS IF.
- **SC-08's verdict-set clause runs over an all-pass set**, so parallel-vs-serial equivalence is
  untested for a mixed set.
