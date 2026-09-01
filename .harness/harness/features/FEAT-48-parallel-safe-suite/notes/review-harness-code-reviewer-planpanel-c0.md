# Scope review — FEAT-48 plan.yaml (unsigned, adversarial read)

## BLUF

FAIL. Two HIGH findings are structural, not stylistic, and both are exactly the class of defect
this feature exists to prevent — a guard that silently computes the wrong thing and stays green.
(1) `test-suite-independence.py`'s discovery-root is hardcoded "four levels up... at the time of
writing" (T-03 intent) rather than reusing the existing marker-validated `harness_boundary.
resolve_root`/`root_above` sitting in the same directory — and since this new file is itself a
`test-*.py` that FEAT-47's `git mv` will relocate to `tests/unit/` (two levels deep, not four)
after T-03 ships, the root computation silently drifts two directories above the real repo once
that move lands, with no fail-closed check anywhere in the plan to catch it.
(2) T-04's `files:` and `verify:` blocks hard-code `test-run-pool.py` at the pre-FEAT-47 path
`.claude/skills/harness/bin/test-run-pool.py`, but D-09 mandates T-04 execute only *after*
FEAT-47 merges, at which point the correct home is `tests/integration/` — the verify block as
written checks the wrong path in exactly the scenario the plan requires.

Also flags: SC-03's `>=8` verify threshold is looser than the plan's own measured truth of
exactly 10 historical findings (T-03 intent, PM research note); T-03's live-scan verify has no
discovery-count floor so a walk that finds nothing passes trivially; T-04's sole discriminating
verify clause for 5 REQs is an exit-code-only trust of an unwritten test file; D-09's FEAT-47
merge-ordering constraint has no mechanical enforcement; and the four `verify: inspection` SCs
(02/05/06/09) rest on a measurements note whose existence nothing checks.

## SC-01 .. SC-09 — reddening change, and whether a task produces the graded artifact

- **SC-01** (mtime/bytes unchanged + crashing-case via private copy). Reddens if T-01 is reverted
  (mutation restored). T-01's own verify block IS this check (`bytes_equal`, `mtime_equal`,
  `crash_case==1`, `untouched_case==1`). Produced: yes. Clean.
- **SC-02** (poll sees 0 broken reads post-fix; control sees >0 on `ea6f51f`). `verify: inspection`.
  No task's automated verify checks that `notes/measurements-parallel-suite.md` exists or that its
  content is accurate — a note asserting "0 broken reads" with no real command output, or no note
  at all, is caught by nothing mechanical. See finding F-07.
- **SC-03** (invariant: 0 live findings, historical scan flags all 3 files+lines). `verify:
  automated evidence: unit`. Two gaps: the `>=8` threshold vs. the plan's own measured 10 (F-03),
  and no discovery-count floor on the live-tree half (F-04).
- **SC-04** (`PASS test-suite-independence.py` from `run-unit-tests.sh --kind unit`). Reddens if
  the file is unregistered or fails. Registration step is explicit in T-03 intent and is a one-line
  addition to `UNIT_SCRIPTS`. Clean, low risk.
- **SC-05** (ten clean `--kind all` runs, wall time recorded). `verify: inspection`, discharged by
  T-04's required note. Same existence/content gap as SC-02 — see F-07.
- **SC-06** (`--kind all` wall time <=120s, worker count+wall time printed). `verify: inspection`,
  same note dependency as SC-02/05 (F-07). The <=120s number itself is well-derived from measured
  8-worker (46.9-58.5s) and 4-worker (68.7s) figures with real headroom — not itself a cannot-fail
  criterion once measured, only the *evidence path* to it is unchecked.
- **SC-07** (existing `--check-kinds`/kind contract holds). `verify: automated evidence:
  integration`. T-04's own plan-verify only exercises the REGRESSION half (`--check-kinds`,
  unknown-kind) — both already pass at `ea6f51f` per PM's own research note table. The
  discriminating half (real `--kind unit`/`--kind integration` runs, deliberately-failing file →
  exit 1) is covered by the pre-existing `test-run-unit-tests-kinds.py`, which is untouched by this
  plan and continues to run in CI regardless — considered and not re-flagged, see Dismissed.
- **SC-08** (order not load-bearing). `verify: automated evidence: integration`, discharged by
  `test-run-pool.py` case (e), which is spec'd with a genuinely-scrambling fixture (first file
  sleeps 0.4s). Produced: yes, contingent on faithful implementation — same exit-code-only outer
  trust as F-05, not flagged separately.
- **SC-09** (`DECISIONS.md` entry + index regen). `verify: automated` per T-05's actual verify
  block (grep + `--stdout` diff), but BRIEF's own SC-09 text cites a `gen-decisions-index.py
  --check` flag that does not exist (confirmed against the tool's own usage banner) — see F-08.
  The substantive grep is 4 literal substrings, satisfiable by a stub — see F-09.

## Findings

**F-01** [severity: high] `test-suite-independence.py`'s discovery root is unvalidated,
FEAT-47-fragile arithmetic, not the codebase's existing marker-checked resolver.
`.claude/skills/harness/bin/test-suite-independence.py` (planned) — T-03 intent: "os.walk from
the repository root, which is four levels up from the file's own directory at the time of
writing." `harness_boundary.py:44-46` documents the identical formula (`root_from_script`,
`os.path.join(bin_dir, "..", "..", "..", "..")`) but `resolve_root` (`harness_boundary.py:53-79`)
never trusts it blindly — it checks `os.path.isfile(os.path.join(derived, MARKER))` and raises
`ValueError` (or falls back loudly) when the derived path doesn't carry
`.harness/team-config.yaml`. `root_above` (`harness_boundary.py:83+`) is a pure marker-walk with
no depth arithmetic at all. T-03's plan calls neither. Consequence: T-03 ships and passes while
still located at `.claude/skills/harness/bin/` (4 levels is correct there), but per FEAT-47's
scope (BRIEF "Blocks or bounds") every `test-*.py` under that directory — including this new file,
once T-03 has landed — gets `git mv`'d to `tests/unit/`, which is 2 levels from root, not 4. After
that move, the hardcoded formula silently computes a root 2 directories *above* the real repo (a
filesystem ancestor, e.g. containing sibling checkouts), with no fail-closed check anywhere to
catch the drift — `os.walk` simply proceeds from the wrong place. This is exactly the "guard that
cannot redden" defect class the feature's own BRIEF names (#979), now reproduced by the guard's
own root-finding rather than its taint model. Nothing in FEAT-48 or (per this review's scope)
FEAT-47 re-verifies `test-suite-independence.py`'s discovery correctness after the move.

**F-02** [severity: high] T-04's `files:`/`verify:` hard-code the pre-FEAT-47 path for a file this
task is only allowed to create post-merge. `plan.yaml` T-04 `files:` lists
`.claude/skills/harness/bin/test-run-pool.py`; the `verify:` block does
`b + "test-run-pool.py"` with `b = ".claude/skills/harness/bin/"`. D-09: "T-04 lands only after
FEAT-47 has merged to main and this branch has been rebased onto it." T-04's own intent: "if
FEAT-47 has landed, the test files live under `tests/`... registration means placing
test-run-pool.py in the integration directory." So the task's own sequencing guidance places the
new file somewhere the hard-coded verify path never checks. As authored, the verify block that is
supposed to prove REQ-03..REQ-07 (`pool.returncode==0`, requiring the file to run from the literal
bin/ path) will not find `test-run-pool.py` in the scenario the plan mandates, forcing a builder to
either (a) obey D-09/intent and place the file under `tests/`, at which point this verify block
cannot locate or run it, or (b) obey the verify block and drop the new integration test at the
deprecated bin/ location FEAT-47 has just vacated for every sibling file.

**F-03** [severity: med] SC-03's historical-scan verify accepts `>=8` findings where the plan's own
measured truth is exactly 10. `plan.yaml` T-03 verify: `len(lines) >= 8`. T-03 intent: "against
`ea6f51f` it must report 10 findings across 3 files." PM's research note lists the 10 sites
individually (`test-check-domain.py:1482,1489`; `test-check-state.py:2112,2114,2133,2248,2250,
2269`; `test-feature-worktree.py:584,605`) and states "exactly three files violate, at ten sites."
Consequence: a regressed or narrowed scanner that misses up to 2 of the known 10 violations
(e.g., drops the restore's `open('wb')` at :1489, or one `os.remove`) still satisfies
`len(lines)>=8 and named==set(names) and len(inject)==1`, and ships measurably weaker than what the
plan's own research already proved achievable, with no gate to notice the regression.

**F-04** [severity: high] T-03's live-tree half of the verify block asserts only `live.returncode
== 0`, with no floor on how many files were actually discovered. `plan.yaml` T-03 verify:
`live = subprocess.run([sys.executable, guard], ...)`, checked only via `live.returncode == 0`.
T-03 intent does specify, as prose for the file's own internal cases, "Assert the discovered file
count is at least 50 in the same case" — but that assertion lives entirely inside the not-yet-
written test file, unenforced by anything the plan itself machine-checks; the plan-level verify
block builds no independent reconstruction of it (contrast T-01/T-02, which independently
recompute bytes/mtime/directory-listing rather than trusting only exit codes). Consequence: if the
"at least 50" case is omitted, weakened, or the internal test suite doesn't literally implement it
as described, a discovery walk that finds zero files (e.g. from the very hazard F-01 describes, or
a typo'd exclude/glob) reports zero live findings and exits 0 — SC-03's "live scan reports zero" is
then true for the wrong reason, precisely the "guard that cannot redden... wearing the remedy's
clothes" pattern the BRIEF itself names for the historical-scan half only.

**F-05** [severity: med] T-04's plan-level verify has exactly one discriminating clause —
`pool.returncode == 0` — for all five REQs it traces (REQ-03..REQ-07). `plan.yaml` T-04 verify:
`--check-kinds` and unknown-kind clauses, which T-04's own intent labels "REGRESSION clauses...
measured 2026-08-31 at `ea6f51f` they already pass... prove nothing about the pool." Unlike
T-01/T-02 (independent byte/mtime/listing reconstruction) or T-03 (independent historical-scan
reconstruction via `git show` + line-count assertions), T-04 builds no external re-check of
attribution, worker-count reporting, failure propagation, or order-independence — it wholly trusts
`test-run-pool.py`'s self-report. If that newly-authored internal suite has a defect that reports
success independent of actual pool behavior, nothing else in this task's verification would notice
before sign-off.

**F-06** [severity: med] D-09's "T-04 lands only after FEAT-47 merges" has no mechanical
enforcement in the plan graph. `plan.yaml` T-04 `depends_on: [T-03]` — only intra-plan task ids;
no reference to FEAT-47's merge state exists anywhere in the schema. A builder or scheduler
walking `depends_on` alone could start T-04 immediately after T-03 lands. T-04's intent partially
hedges this (detect layout via `git ls-files`; branch on array-based vs. directory-driven; BLOCKED
if neither shape matches) which meaningfully reduces — but does not eliminate — the risk, since
correctly detecting and branching between two registration mechanisms is left entirely to the
builder's judgment with no automated gate forcing the FEAT-47-first order.

**F-07** [severity: med] SC-02, SC-05, SC-06 depend entirely on
`notes/measurements-parallel-suite.md` (required by T-04 intent), and no verify block in T-01..T-05
checks that this file exists or contains its required content. `plan.yaml` T-04 verify block (the
only automated check in that task) covers only `test-run-pool.py`, `--check-kinds`, and unknown
kind — it never references the measurements note. Consequence: if the note is skipped, or written
with only a bare claim ("0 broken reads observed") and no verbatim command/output as the intent
requires, nothing mechanical catches the gap; BRIEF's own "Verification gaps" section already
discloses that these three SCs rest on operator diligence, which somewhat mitigates the severity,
but the plan itself provides zero automated existence check even for the artifact's presence.

**F-08** [severity: low] BRIEF's SC-09 text cites a nonexistent CLI flag. BRIEF SC-09: "FAILS IF:
... `gen-decisions-index.py --check` reports no drift" (BRIEF also names it in the criterion body).
Confirmed via `gen-decisions-index.py:9-10`: "There is no `--check`: to check for drift without
writing, pipe the read-only mode into diff" and `:253-259`, which rejects any argv token other than
`--stdout` and exits 2. T-05's actual `plan.yaml` verify block correctly uses `--stdout` + Python
string comparison, so the plan mechanism is sound — only BRIEF's own SC-09 prose is factually
wrong about the flag, and would mislead an operator attempting to hand-verify it literally.

**F-09** [severity: low] T-05's DECISIONS.md verify is 4 literal substring checks, satisfiable by a
content-free stub. `plan.yaml` T-05 verify: `need = ["private copy", "change-based test
selection", "HARNESS_TEST_WORKERS", "test-suite-independence.py"]`, checked only via `n not in
txt`. Consequence: a one-line stub entry that merely name-drops all four phrases in a sentence
fragment ("This decision covers private copy, change-based test selection, HARNESS_TEST_WORKERS,
and test-suite-independence.py.") satisfies the automated gate while omitting every substantive
requirement the intent otherwise details at length (measured numbers, the rejection's three
reasons, the hazard's own description) — REQ-08's actual intent ("recorded" implies substance, not
keyword bingo) is not held to that standard by anything mechanical.

## Dismissed (considered, no consequence found)

- **Orphan/dangling REQ traces**: every REQ-01..REQ-08 is traced by at least one task
  (REQ-01→T-01/T-02, REQ-02→T-03, REQ-03..07→T-04 with REQ-07 also T-03, REQ-08→T-05); no task
  traces a REQ id absent from BRIEF. Clean.
- **`depends_on` topology (intra-plan)**: T-01[]→T-02[T-01]→T-03[T-01,T-02]→T-04[T-03]→T-05[T-04]
  is a valid linear DAG and matches what each task actually consumes (T-02 imports T-01's
  `isolated_bin.py`; T-03's "zero live findings" needs T-01+T-02 landed first). The one real gap in
  this area is the *cross-feature* edge to FEAT-47, filed separately as F-06.
- **The `<cmd> | grep .; then exit 1` masked-exit-code idiom (dispatch item 3)**: not present
  anywhere in T-01..T-05. Every verify block is a single `python3 -` heredoc; every
  `subprocess.run` call's `.returncode` is read explicitly and fed into an aggregated boolean
  before `sys.exit()`. `git show ... check=True` calls raise loudly on failure rather than being
  swallowed. No pipeline stage's exit code is discarded by a later stage.
- **T-02's poll-thread `except OSError: pass`**: the polled directory (`.claude/skills/harness/
  bin`) is not removed or relocated by anything this test does, so `os.listdir` raising `OSError`
  there is not a realistic path this test can trigger; the loop is a tight busy-poll (no sleep),
  giving fine-grained coverage of the two subprocess windows it watches. No concrete failure
  scenario found.
- **Subprocess "fails to start" in T-02's verify**: both target scripts are known-existing paths
  edited by this same task; a `FileNotFoundError`-class launch failure is not realistic, and would
  in any case raise inside `subprocess.run` and crash the outer heredoc loudly (fail-closed), not
  silently pass.
- **Taint-model rule set (T-03's sink/scope logic)**: already validated in the PM's own research
  note against the real tree (10 findings, 0 false positives across three measured variants); the
  design choices (per-scope taint, Path-typed receiver requirement, per-sink argument index) are
  each tied to a measured false-positive class. No new issue found in the rule set itself.
- **FEAT-47 scope duplication, PYTHONPATH shim direction**: out of scope per dispatch — both
  already ruled and in flight elsewhere.

## Open questions

None that block this review — every question raised above is answered by evidence in this
artifact; what remains is for the operator/PM to resolve F-01/F-02 (structural) and F-03/F-04
(threshold/floor) before signing.
