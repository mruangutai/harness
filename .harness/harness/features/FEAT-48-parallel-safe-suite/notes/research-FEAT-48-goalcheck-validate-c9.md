# Goal-check — FEAT-48 at `review_sha 27f8105b` (cycle 9)

**All ten criteria are MET at `27f8105b`, and every row's evidence was re-taken at the pin — nothing
is inherited from the c8 note.** SC-03 is graded against the amended text `BRIEF.md:69-80` carries at
the pin and reads MET: T-03's `verify:` block runs to **exit 0**, the ten `ea6f51f` sites are each hit
individually with zero extras, and all six in-file self-tests discriminate under my own monkeypatch
probe. One open item is **not** a criterion failure: T-06's own `verify:` block exits 1 on an
accidentally strict clause. Disposition and lane in §3. The feature can ship.

**Provenance rule applied.** `git diff --name-only e64e863e 27f8105b` touches `run_pool.py`,
`test-check-domain.py`, `test-check-fixture-secrets.py`, `test-run-pool.py`,
`test-suite-independence.py`, `DECISIONS.md`, `BRIEF.md` and `notes/measurements-parallel-suite.md`.
Every criterion's evidence sits on one of those files or on `run-unit-tests.sh` (unchanged in range but
whose script sets changed), so I re-took all ten rather than carry any c8 figure across the rewrite.
`run-unit-tests.sh` is byte-identical in range. Every suite invocation used `env -u HARNESS_AGENT_TYPE`;
`git status --porcelain` showed only three sibling-panel untracked notes, unchanged before and after
every run.

## 1. Grades

| SC | Verdict | Method | Evidence | Provenance |
|---|---|---|---|---|
|SC-01|**MET**|automated / integration|`test-check-domain.py` exit 0, zero `FAIL`; live `feature_schema.py` `(mode,size,mtime_ns,sha256)` = `(33188, 15881, 1788333510516825193, 943ef7a7…fbb2)` **identical before and after** — never written, not restored. FAILS IF negative: the crashing case still asserts `want=2` **and** `"CRASHED" in stderr` (`test-check-domain.py:1460-1465`), driven against `isolated_bin(root)` (`:1472-1476`), and the never-written assertion is `:1477-1481`. Not neutered|re-taken at 27f8105b|
|SC-02|**MET**|inspection|Note at pin: `control method: isolated bin copy` (`:18`), `control broken reads 4968` (`:19`, >0), `post-fix broken reads 0` (`:20`), live bytes/mtime equal (`:11-12`). **Independent corroboration mine:** any write to `feature_schema.py` during a run would print `MUTATED feature_schema.py`; my `--kind unit`, `--kind integration` and `--kind all` runs at the pin all printed **zero** `MUTATED`. Neither FAILS IF fires|re-taken at 27f8105b (note read at pin)|
|SC-03|**MET**|automated / unit + review-time pinned|T-03 `verify:` verbatim → **exit 0**. CI half: six `ok self-test` lines, `root` = `git rev-parse --show-toplevel`, `discovered 63` (floor 50), `ok no test mutates…`, `selfcmp []`. Pinned half: `--scan-dir` over the three `ea6f51f` blobs → rc 1, **10 VIOLATION lines, all ten named sites HIT individually, `extras []`**. All six self-tests discriminate (§2); `main()` runs them before the scan (`test-suite-independence.py:290`) and returns 1 on any (`:298-300`)|re-taken at 27f8105b|
|SC-04|**MET**|automated / unit|`--kind unit` exit 0, 33 files, 33 blocks, zero `FAIL`, emits `PASS test-suite-independence.py`; `pool: 8 workers, 33 files, 13.75s wall`. File is in `UNIT_SCRIPTS` (`run-unit-tests.sh:30`)|re-taken at 27f8105b|
|SC-05|**MET**|inspection|Note at pin `:31-40`: ten `run N exit 0 <wall>s` lines enumerated — 42.64, 42.73, 42.88, 44.70, 43.05, 43.19, 42.97, 43.12, 43.63, 47.82s; **all rc 0**, all ≤120s. FAILS IF negative: `tree condition:` is present and non-empty (`:43`) and credible (§2). No `FAIL` line and no short count|re-taken at 27f8105b (note read at pin)|
|SC-06|**MET**|inspection|Note `:53`/`:57` `pool: 8 workers, 63 files, 42.40s wall` — both numbers printed, ≤120s vs the 247s serial baseline (`:49`). FAILS IF negative: worker count **and** wall time both present. **Mine at the pin:** `--kind all` printed `pool: 8 workers, 63 files, 79.72s wall`, still ≤120s under a live concurrent panel|re-taken at 27f8105b|
|SC-07|**MET**|automated / integration|Four clauses, each run: (1) `--check-kinds` exit 0, prints `check-kinds: the script arrays and test_kinds.integration.detect agree.`, **zero** `PASS`/`FAIL` lines; (2) `--kind unit` 33/33 and `--kind integration` 30/30 — **every file has exactly one runner block and one runner verdict**, checked per file, not by count; (3) failing file → exit 1, composed: `test-run-pool.py` `ok one failure propagates after every file runs` and `run-unit-tests.sh:148` is `exec`, so the pool's status is the runner's; (4) `--kind nope` exit 2 with the legal-kinds message|re-taken at 27f8105b|
|SC-08|**MET**|automated / integration|`test-run-pool.py` 13/13 `ok` at the pin, incl. `completion order is not input order` — `p_order != s_order and set(p_order) == set(s_order)` against a `--workers 1` serial run, over a set built so it cannot match (`slow.py` sleeps 0.4s and is first in argv, `test-run-pool.py:86-93`)|re-taken at 27f8105b|
|SC-09|**MET**|inspection|`git show 27f8105b:…/DECISIONS.md` → DEC-211 at `:6563`, **612 words / 52 lines** (FAILS IF negative: not a sub-300-word stub). All five items stated as prose: private copy `:6567`, invariant `:6577`, mutation check `:6587`, worker rule `:6582-6585`, and **`:6606` "The proposal of change-based test selection is REJECTED"** with three reasons `:6606-6610`. `gen-decisions-index.py --stdout` = committed index, 43,459 bytes both, byte-identical|re-taken at 27f8105b|
|SC-10|**MET**|automated / integration|Every clause named separately at the pin. Vectors: direct write `test-run-pool.py:123` (`MUTATED keep.txt`, rc 1); **subprocess** `:124` (`sh -c echo >>`, rc 1); **file created** `:125` (`MUTATED .mutant-x.sh`, rc 1); clean control `:122` rc 0. Refusals: DIR empty **and** DIR missing both rc 2, `:160-165`. `__pycache__`: `:154` asserts a created cache entry is **not** reported and `:155` asserts a **loose** `loose.pyc` **is** (`MUTATED loose.pyc`, rc 1) — the skip is keyed on the directory name (`run_pool.py:40`), not the suffix. FAILS IF negatives: a **rewrite of a pre-existing** `__pycache__/x.pyc` through the real CLI → **rc 0, no `MUTATED`** (my probe); and the only non-comment pool invocation is `run-unit-tests.sh:148` `--mutation-check "$BIN_DIR"` — flag present, argument is `$BIN_DIR`, not the root|re-taken at 27f8105b|

## 2. The two judgements the criteria turn on

**Six self-tests discriminate — my own probe, not inherited.** Importing the pin's module and patching
one collaborator at a time inside `run_self_tests()`: blinded `scan_file` reddens the three red idioms;
over-eager `scan_file` also reddens `clean controls` and `live tree`; `resolve_scan_root` never
returning `None` reddens `live tree` and `unresolved root refuses`. **Never-red cases: none.** Baseline
through the same harness is green (0 failures), so the harness reached the real artifact.

**Measured, not typed — the judgement SC-05 and SC-06 exist to collect.** The note carries three fences
and they are not equal in worth.

- **Fence 3 (`:51-55`) IS verbatim runner output.** `PASS <file>` + `pool: N workers, M files, Ws wall`
  + a three-item `slowest:` list is exactly and only what `run_pool.py:105`, `:133` and `:135-136`
  emit. My own `--kind all` at the pin produced the identical shape. **SC-06 is measured.**
- **Fences 1 and 2 are harness summaries, not any named command's output.** No command emits
  `run N exit 0 42.64s` (`:31-40`), and `control command:` (`:8`) is pseudo-code with a `<copy>`
  placeholder a reader cannot run. So for SC-05 and SC-02 the fence does **not** discharge
  measured-versus-typed by itself. What does, circumstantially: the ten walls are a tight non-round
  42.64–47.82s band with a single high tail, consistent with fence 3's 42.40s from the same period,
  and my own run of the same command under a loaded machine took 79.72s — the band tracks machine
  state rather than sitting at invented round numbers. **My judgement: credible, and this is a
  reviewer's input, not a FAILS IF** (`BRIEF.md:154-156` says so explicitly). Advisory below.
- **`tree condition:` (`:43`) is credible for those numbers.** Its "no process wrote bin" half is
  self-corroborating: a bin write during any run would have printed `MUTATED` and exited non-zero, and
  all ten exited 0. The quiet-machine half is corroborated by the band above.

## 3. T-06's `verify:` — a plan-artifact defect that gates nothing

Reproduced verbatim at the pin: **exit 1**. Cross-checked against `plan.yaml` T-06 — the string matches
the dispatch byte for byte. Every substantive clause passes; the sole failure is `post == ["0"]` against
`post == ['0','0']`.

**Product ruling: no approved success criterion fails on it.** SC-02, SC-05 and SC-06 are
`verify: inspection` and their content is present, in range and graded above; SC-04's line is graded by
the suite; no criterion asserts that a task `verify:` block exits 0. Pre-existing since `b86ce66a`.

**It is not mutually unsatisfiable with T-06's intent, but it is inconsistent with its own siblings.**
The intent mandates both the fenced verbatim output *and* the summary lines, and the probe chose to
print the summary shape — a probe printing `post-fix broken reads: 0` would satisfy both, so the
collision is contingent, not structural. The real defect: `ctrl`, `wall` and the `PASS …` check all
tolerate the duplication the intent's own structure produces (truthiness, `[0]`, substring) and only
`post` uses exact-length matching. It is accidental strictness, not a considered assertion.

**Recommendation — fix inside this feature, one token:** `post == ["0"]` → `post and set(post) == {"0"}`,
matching its siblings. It touches no shipped artifact, so nothing needs re-testing. **What must NOT
happen: deleting the duplicate line from the note.** That line is inside the fence the intent mandates
and is part of the measured-not-typed evidence SC-02/SC-05/SC-06 rest on — striking it to green a
verify would weaken real evidence to satisfy a defective assertion.

**Lane: main session.** `plan.yaml` is `approval.status: approved` (`approved_by: Mike Ruangutai`,
`2026-09-02`), so editing a task's `verify:` needs an operator ruling recorded in `approval.rulings` —
the only tier with a user channel — after which pm applies it via `plan-merge.py apply`. Not a dev
squad's: `.claude/skills/harness/bin/**` and the plan are `main-session-direct` (DEC-174). If the
operator prefers zero further edits this cycle, the fallback is a `BRIEF.md` BACKLOG-D row — but then
T-06 keeps `status: done` behind a verify that has never returned 0, which is the record-honesty cost
worth naming to them.

## 4. `HARNESS_AGENT_TYPE` — genuinely NEW, the operator's to adopt

I read c8's residual list end to end (five residuals, four caveats). Residuals 1, 2, 3 and 5 are all
**closed at the pin** by `993ac997`: DEC-211 now states the metadata-snapshot boundary (`:6602-6604`)
matching `_record`'s `(st_mode, st_size, st_mtime_ns)` tuple (`run_pool.py:34`) exactly; the
`__pycache__` leg is a committed fixture (`test-run-pool.py:145-157`); the clean control carries the
`src.replace(...)` shape (`test-suite-independence.py:225`); and the `.pyc` skip is now keyed on the
directory name, so the criterion and the implementation agree.

Residual 4 stands and is **NEW, not covered.** With `HARNESS_AGENT_TYPE` set, `test-plan-merge.py`
fails 11 checks — a file **not** in this feature's diff (`git diff --name-only origin/main 27f8105b`
confirms). No REQ or SC in `BRIEF.md` quantifies over the ambient environment: REQ-01/REQ-07 and
SC-07/SC-08 are about independence from other *tests*, and the goal sentence names the *scheduler*.
Adopting it would change what "done" means for this feature, so it is the operator's, not mine.
**Recommendation: a separate `BUG-NN`.** FEAT-48 neither caused it nor touches the file, and folding it
in resets an approved plan.

## 5. Advisories — none gating

- **The ten-run fence should paste each run's own `pool:` line** (a T-06-shaped note edit), so a reader
  sees runner-shaped output ten times instead of a driver summary. Backlog row; SC-05's FAILS IF does
  not reach it.
- **SC-07's failing-file clause remains composed, not gated** — no test drives `run-unit-tests.sh`
  end-to-end with a deliberately failing file (`test-run-unit-tests-kinds.py` covers only
  `--check-kinds` and argument parsing). The `exec` at `:148` carries it. Unchanged from c7/c8.
- **SC-08's verdict-set clause runs over an all-pass set**, so parallel-vs-serial equivalence is
  unproven for a mixed set. Unchanged from c8.
- **Duplicate file-shaped verdict lines persist** — 34 verdict lines over 33 unit blocks, 35 over 30
  integration blocks, from six test files printing their own `PASS <file>.py` self-summary
  (`test-panel-findings.py`; `test-feature-worktree.py`, `test-expertise-merge.py`,
  `test-plan-merge.py`, `test-observations-merge.py`, `test-quarantine.py`). Pre-existing, and the
  runner still emits exactly one block and one verdict per file.
- **SC-02's `4968` is not reproducible by a reader** — the poll harness is neither committed nor cited
  by path. `BRIEF.md:144-156` concedes it; BACKLOG-C covers the adjacent SC-03 gap.
- **Record hygiene, for the main session:** `BRIEF.md`'s `## Approval` block is byte-identical across
  `b86ce66a`, `e64e863e` and `993ac997`, so the SC-03 amendment `993ac997` landed carries no distinct
  re-signature act in the file. Only the operator's hand can date it.
- Unrelated FEAT-51 `check-state.sh` findings are pre-existing and outside this feature; not graded.

## Pointers

- `BRIEF.md` SC-01..SC-10 `:57-142`, Verification gaps `:144-162`, Approval `:234-238`
- carrier note `notes/measurements-parallel-suite.md` at `27f8105b`
- orchestrator measurements `notes/validate-evidence-c9.md` (checked, and every figure I depended on
  reproduced)
- prior round `notes/research-FEAT-48-goalcheck-validate-c8.md`, `notes/handoff-validate.md`
