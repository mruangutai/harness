# Fix cycle 1 — dispositions for FEAT-48's plan panel findings

## BLUF

**All five cycle-1 findings are dispositioned; four fixed in the artifacts, one dismissed with a
reason.** The headline repair is `D-11`: the watched set is no longer "every git-tracked file under
ROOT" but "every file, tracked and untracked, at or below `$BIN_DIR`, excluding `__pycache__` and
`*.pyc`". That answers both readers at once — it now *sees* the untracked-creation vector T-02's
sites actually used, and it no longer reddens when a sibling agent writes a note. The `because` was
rewritten to drop the false "every vector" claim and to state, in the entry itself, what the check
does not cover. One finding of my own: T-06's old serial-loop assertion was **unsatisfiable**.

## Dispositions

| id | disposition | where |
|---|---|---|
| G-01 | **FIXED (FEAT-48 half)** | `BRIEF.md:169-184` no longer predicts FEAT-47's behaviour. It claims only what FEAT-48 controls — the two files *require* no edit to their logic — and names the narrower truth: `test-suite-independence.py` anchors its `harness_boundary` import on its own directory, so the move **does** require an edit to that import. It records that FEAT-47's T-03 text was stale as read on 2026-08-31 and that the correction is FEAT-47's. Mirrored at `plan.yaml` D-09 (`:112-118`) and T-03 intent (`:445-450`). FEAT-47's pm confirmed by IRC it has removed its restatements of D-11 and cites D-11 by reference |
| G-02 | **DISMISSED, no edit** | The lead's instruction stands: a hand-typed note passes T-06's shape gate, tightening the regexes buys nothing, and only a reader catches fabrication. Already disclosed in two places — `plan.yaml` T-06 intent and `BRIEF.md` `## Verification gaps` — so the gap is on the record where the user signs. What the fix cycle *did* add there is a required `tree condition:` line, which is a different gap (VL-02), not this one |
| G-03 | **FIXED** | Registration moved into the task that creates the file. T-04 now edits `run-unit-tests.sh` and `.harness/harness.json` (`plan.yaml:561-565`), its verify asserts `--check-kinds` exits 0, and its intent step 3 (`:713-725`) records why. T-06 no longer registers anything and dropped `harness.json` from `files:`. `change_type` on T-04 becomes `cross_module`. Verified live: `on: push: branches:[main]` plus bare `pull_request:` at `.github/workflows/tests.yml:19-22`, so this was a live red build, not a window |
| VL-02 | **FIXED** | `D-11`'s watched set narrowed (below), and the operating condition is now stated in the decision rather than mis-framed as an operator slip. T-06 must record `tree condition: <...>`, parsed by its verify; `SC-05` requires it and fails without it |
| reader's `D-11` overclaim | **FIXED** | The sentence "against every vector including the two the scan is blind to" is gone. `D-11`'s `because` now carries an explicit *what it covers / what it does not* paragraph: vector-agnostic inside DIR, **blind outside it**, where T-03's static scan with its two known holes is the only enforcement — and it says the two together are not complete |
| reader's SC-08 note | **DISMISSED, no edit** | Both readers named it and declined to file it; agreed, and their reason is already recorded in the c1 note |
| **PM-01 (mine, new)** | **FIXED** | T-06's verify required `not loop` where `loop` was every line starting `for s in`. Line 64 of `run-unit-tests.sh` is `for s in "${ALL_SCRIPTS[@]}"` — the drift detector, which the same intent says must stay — so the block **could never pass**. Replaced with `'"${SCRIPTS[@]}"' not in sh`: line 148 is that string's only occurrence and the new invocation spells `"${SCRIPTS[@]/#/$BIN_DIR/}"`. The intent now warns the next author off the old idiom |

## D-11's new mechanism, and the evidence for it

`--mutation-check DIR` walks DIR, recording `(size, st_mtime_ns)` per file, before the first child
and after the last; `MUTATED <path relative to DIR>` on stdout; exit 1 on any finding; **exit 2 when
DIR is absent or holds no files** — the refusal that replaces "git failed", so a check that measured
nothing can never report clean. No git at all.

Prototyped the exact mechanism in a tempdir (2026-08-31). Each leg is the concrete change that
makes it red:

| leg | result |
|---|---|
| clean run | `[]` |
| `__pycache__/*.pyc` rewritten mid-run | `[]` — **the exclusion is load-bearing**: `bin/__pycache__/` exists in the tree today, so without it the check reddens on the interpreter's own byte-code caching every run |
| append to an existing watched file | `['keep.txt']` |
| **create `.mutant-x.sh`** (the T-02 vector) | `['.mutant-x.sh']` — invisible to a `git ls-files` set |
| delete a watched file | both paths reported |
| empty dir / absent dir | refuses |

Why `$BIN_DIR` and not ROOT: agents write `.harness/harness/features/**` continuously while suites
run (operator measurement: 1,904 tracked files modified in three hours across the live worktrees),
and `run-unit-tests.sh` is invoked *by* those agents. `bin/` is the shared code every test imports
from, both observed hazard sites are in it, and no agent writes it during a run. The accepted
residual: an edit to a file in `bin/` during a run trips it — rarer, and not a false alarm in the
same sense, since the suite's own code changed underneath it.

`SC-10` was rewritten to grade this and can still fail: seven named failure modes, including the new
creating-fixture leg, the `__pycache__` false-positive leg, and *"`run-unit-tests.sh` invokes the pool
with any argument other than `"$BIN_DIR"`"* — so a later revert to root-wide is a red gate.

## The unevaluable item, now pinned

T-03's live-tree root case (`plan.yaml:509-523`) must compute its expected root by an **inline marker
walk written in the case body**, not by calling `resolve_scan_root` or `harness_boundary`. A
comparison of the resolver to itself is explicitly forbidden and named as vacuous. The verify block
also rejects any single line mentioning `resolve_scan_root` twice — stated in the intent as catching
only the literal self-comparison shape, which is why the recomputation is mandated rather than merely
checked.

## Evidence

- `check-plan-routes.py <plan>`: **0 violations, exit 0.** Six `DEVIATION` lines are by design and
  documented in the plan's `lanes:` block (DEC-174). T-04 hit the 50-line machine-field budget at 53
  and was trimmed to 49.
- Every task's `verify` body compiles (`compile()` over all six, after dedent).
- T-06's assertions proven to discriminate: against today's script `inv 0 / serial True / flag False`
  (red); against the script with the specified line substituted, `inv 1 / serial False / flag True`
  (green). The same run shows one `for s in` line surviving a correct change — PM-01, empirically.
- Cycle-0 repairs confirmed present after my edits: F-01 (`root_above` mandated, "Do NOT spell a
  four-levels-up climb" intact), F-02/F-06 (D-09 ships whole and first), F-03 (the `want` set parses
  to exactly the ten named sites; `len(lines) >= 8` absent), F-04 (`disc[0] >= 50`, `len(disc) == 1`),
  F-05 (attribution, `fails == ["FAIL bad.py"]`, `pool: 3 workers, 3 files` all still reconstructed
  independently, now plus two mutation vectors and the registration check), F-07 (note regexes
  intact), F-08 (BRIEF's "There is no `--check` flag"), F-09 (`words >= 300` plus the phrase list,
  now 16 entries).
- `approval.status: pending`, `approved_by: None` in `plan.yaml`; `status: pending` in `BRIEF.md`.

## Open questions for the tier above

- **Q1** — the `--mutation-check` watched set is bin-only, so a test that mutates
  `.harness/harness.json`, a workflow file or a doc is caught only by T-03's static scan, with that
  scan's subprocess and helper-wrapped blind spots. `D-11` now says so plainly. Closing that
  remainder needs a watched set that can tolerate concurrent agent writes — a per-path allowlist or
  a two-tier snapshot — which is new design, not a fix-cycle edit. Not blocking.
- **Q2** — after FEAT-47's move, should the watched set also cover `tests/unit`, `tests/integration`
  and `tests/manual`? `run_pool.py` takes exactly one DIR by design. Raised with FEAT-47's pm as a
  FEAT-47 decision. Not blocking FEAT-48.
