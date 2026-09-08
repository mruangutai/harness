# QA Gate Review — BUG-151 check-domain fail aggregation — review-c0

**PASS on the matrix. One non-gating, plainly-stated adequacy gap: nothing permanent binds
`main()`'s discovery loop to route captured output through `_aggregation_verdict`.**

## Scope pinned

Diff under gate is exactly `tests/integration/test-check-domain.py`
(`git diff 6d969ed3..e4efd77485204e1d554dab18a3a957b190f43af1 -- tests/integration/test-check-domain.py`,
172 diff lines). Worktree HEAD is `7c384347` (one commit past the pin), but
`git diff HEAD e4efd774 -- tests/integration/test-check-domain.py` = 0 lines: the reviewed file is
byte-identical to the pin. Only `.harness/` bookkeeping differs. `git status --porcelain` clean.

## 1. Matrix resolution (`test_matrix.bugfix`, `.harness/harness.json:203-219`, predicates per
DEC-217, `DECISIONS.md:6871-6880`)

Both T-01 and T-02 are `change_type: bugfix`. `always: []`; three `when` legs:

- `touches_runtime_code` ("∃ a non-`.harness` file not under `tests/**`, not `*.md`"): **FALSE** —
  the diff's only non-`.harness` file is `tests/integration/test-check-domain.py`, itself under
  `tests/**`. Does not fire.
- `fix_confined_to_tests_and_contract_docs` ("∀ non-`.harness` files: `*.md` or `tests/**`"):
  **TRUE** — same and only file satisfies it. **Fires → requires `integration`.**
- `match_bug_class`: unresolvable placeholder, no `__bug_class__` entry in `test_kinds` (repo
  Expertise G-08). Not applicable.

**Required set: `{integration}`. `unit` is not obligated.** `matrix_ok: true`.

## 2. Kind run — verbatim command, actual result

```
env -u HARNESS_AGENT_TYPE .agents/skills/harness/bin/run-unit-tests.sh --kind integration
```
Exit **0**. Pool: 49 files, 74.46s wall. `test-check-domain.py` ran as file 1 of the pool: exit 0,
55.98s. Full-log counts (`test-check-domain.py`'s own section only, lines 2700-3182 of the captured
run): **404 `^ok` lines, 0 `^FAIL` lines**, of which 6 carry `[bug151-selfcheck]` (cases a–f, all
`ok`). Whole-suite grep: `^FAIL` = 0 across all 49 files.

`unit` is not required by the floor; not re-run (nothing in this diff warrants it — the file is
entirely under `tests/integration/`).

## 3. T-01 / T-02 `verify:` clauses — read from `plan.yaml`, run character-for-character

**T-01** (`plan.yaml:78`):
```
env -u HARNESS_AGENT_TYPE python3 -c "import importlib.util as u; s=u.spec_from_file_location('tcd','tests/integration/test-check-domain.py'); m=u.module_from_spec(s); s.loader.exec_module(m); assert callable(m._aggregation_verdict); assert m.run_bug151_selfcheck_cases()==0; print('PASS')"
```
Output: six `ok    [bug151-selfcheck] <name>` lines, then `PASS`. Exit 0. **Reproduces exactly.**

**T-02** (`plan.yaml:147`):
```
env -u HARNESS_AGENT_TYPE python3 -c "import subprocess,sys,importlib.util as u; p='tests/integration/test-check-domain.py'; r=subprocess.run([sys.executable,p],capture_output=True,text=True); L=r.stdout.splitlines(); ok=sum(1 for l in L if l.startswith('ok')); bad=sum(1 for l in L if l.startswith('FAIL')); s=u.spec_from_file_location('tcd',p); m=u.module_from_spec(s); s.loader.exec_module(m); blocks=[n for n in vars(m) if n.startswith('run_') and callable(getattr(m,n))]; print(r.returncode, ok, bad, len(blocks)); assert r.returncode==0; assert bad==0; assert 398<=ok; assert len(blocks)==24; assert 'run_bug1305_cases' not in blocks; print('PASS')"
```
Output: `0 404 0 24` then `PASS`, wall 37.75s. Exit 0. **Reproduces exactly, matches the receipt's
claimed `0 404 0 24` byte-for-byte** (`receipt-harness-backend-dev-T-02-c0.md:93`).

## 4. Summary counts

`matrix_ok: true`. Integration kind suite: exit 0, `^ok`=1627+ across the pool (script-level PASS
lines are one-per-script per repo Expertise G-04, not a case count — case-level counts above are the
load-bearing ones), `^FAIL`=0 file-wide. `test-check-domain.py` alone: 404 `ok` / 0 `FAIL`, exit 0.

## 5. Test-first audit — cited, not re-derived

Per `receipt-harness-backend-dev-T-01-c0.md` and `notes/qa-BUG-151-c0.md:57-71`: T-01 has a shown
red→green transcript (six `NameError` failures before `_aggregation_verdict` existed, green after).
T-02 has **no git-visible red state for its own refactor** — steps 1–7 were already committed at
`36446eb5` before this receipt, which supplies only step-8 evidence. This is recorded as an
already-flagged advisory in the prior qa segment note, not a new finding, and not gating: T-02 is a
structural refactor (deletion + discovery) graded by inspection (SC-02) plus a red *proof* of the
resulting safeguard, not new behavior requiring a fresh failing test.

Per the signed ruling in this dispatch: T-02 step 8(b)'s one-off red proof (receipt PHASE C,
`receipt-harness-backend-dev-T-02-c0.md:62-84`) is deliberately not a permanent test. Not raised as
a finding here, per the ruling.

## 6. Adequacy — what a green matrix here does NOT establish

**Reasoned finding** (not itself mutation-proven at this dispatch — GATE-ONLY, author nothing):
`run_bug151_selfcheck_cases` (T-01) pins `_aggregation_verdict`'s predicate purely on synthetic
`(printed_text, total)` pairs constructed in memory (`test-check-domain.py:5213-5241`). It never
calls `main()`, never touches `_AggTee`, and never exercises the discovery loop's actual wiring at
`test-check-domain.py:5278-5284` (`with contextlib.redirect_stdout(block_tee): total = block_fn()`
followed by `_aggregation_verdict(block_name, block_tee.text(), total)`).

**Concrete failure scenario:** if a future edit drops the `redirect_stdout(block_tee)` wrapper
around a discovered block's call (or otherwise decouples `block_tee` from the block's real stdout),
that block's own `print("FAIL  ...")` lines still reach the terminal (unaffected — pass-through was
never the safeguard's job) but `block_tee.text()` becomes `""`. `_aggregation_verdict` then sees
`printed=0` against whatever `total` the block returns; if that block also has the original BUG-151
defect (`total==0` despite a real printed FAIL, e.g. a return-path bug), both sides read zero,
agreement-of-zeroness holds, no diagnostic fires — the exact silent-failure mode this feature exists
to close, reopened, with **every committed case in `run_bug151_selfcheck_cases` still green**,
because that function never observes the discovery loop at all. The only evidence this wiring is
correct today is the T-02 receipt's one-off, uncommitted, in-memory monkeypatch proof
(PHASE C-ii), which by the signed ruling is intentionally not preserved as a suite member.

This is a **coverage gap in the safeguard's own regression protection**, not a defect in the shipped
code (PHASE C-ii's own measurement, independently re-derived in `qa-BUG-151-c0.md:80-84`, shows the
wiring is correct as of this pin). I rate it **non-blocking for THIS gate** (the matrix, the
declared `verify:` clauses, and BRIEF's SC-01..05 are all satisfied by what was asked for and
approved — D-01/D-02 do not mention wiring-regression coverage as an SC), but it is real and
plainly reportable: nobody watching only `run_bug151_selfcheck_cases` would notice a regression at
the actual integration seam.

## SC evidence (independently confirmed, matches prior qa segment)

| SC | test | note |
|---|---|---|
| SC-01(a) | `test-check-domain.py::run_bug151_selfcheck_cases` | permanent, 6 synthetic cases, re-run here, PASS |
| SC-01(b) | T-02 receipt PHASE C (one-off, deliberately not committed per signed ruling) | not re-run here (author-nothing); cited |
| SC-02 | inspection — discovery at `test-check-domain.py:5275`, no `sorted()`, `run_bug1305_cases` absent | graded by reading code |
| SC-03 | equality of `^ok` name sets, baseline (398) vs post-change (404 minus 6 selfcheck = 398) | confirmed via T-02 verify clause's own counts, 398<=404 satisfied |
| SC-04 | full suite green, 0 diagnostic lines | confirmed: integration kind exit 0, 0 `^FAIL` |
| SC-05 | inspection — false comment removed | not independently re-greped this pass; unchanged file since prior qa segment confirmed it |

## must_fix

None.

## Advisory (non-blocking, carried/added)

- (carried from `qa-BUG-151-c0.md`) T-02's receipt supplies no failing-then-passing transcript for
  its own refactor.
- (new, this gate) The discovery loop's routing of captured block output through
  `_aggregation_verdict` has no permanent regression test — see §6. Recommend, for a future cycle
  only (out of scope for this GATE-ONLY dispatch): one committed case that runs a real (or minimal
  fake) discovered block through `main()`'s actual loop with the tee/redirect deliberately
  unhooked, asserting the safeguard's silence reproduces the pre-fix defect. Not raised as
  must_fix — BRIEF's SCs do not require it and inventing new test obligations is outside this
  dispatch's non-goals.
