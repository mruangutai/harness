# Receipt — harness-dev-ops — T-13 (c1)

## BLUF

T-13 delivered. `.claude/skills/harness/bin/test-hooks-install.py` created, 27/27 cases PASS,
exit 0 — the only automated evidence for SC-08, SC-13 (all three clauses) and SC-14. Registered
in both `.harness/harness.json` `test_kinds.integration.detect` and `run-unit-tests.sh`
`INTEGRATION_SCRIPTS` (T-05's precedent honoured — both, not one). Both named RED PROOFS (case
(d) and case (e)) were run and demonstrably fail for the reason the plan names, not an incidental
one. `test-post-merge-sweep.py` and `test-worktree-terminal.py` are unmodified and stay green.
`check-state.sh` is exit 0 / zero VIOLATION lines. `run-unit-tests.sh` reports **no KIND-DRIFT and
no MISCONFIGURED** — but the full suite's exit code is 1, from one PRE-EXISTING failure in
`test-validate-digest.py` unrelated to any of my three files (open_question below, non-blocking
for this task).

## Scope — exactly three files, all in plan.yaml's `files:` list

- `.claude/skills/harness/bin/test-hooks-install.py` (new)
- `.harness/harness.json` — one literal path appended to `test_kinds.integration.detect`
- `.claude/skills/harness/bin/run-unit-tests.sh` — one literal path appended to
  `INTEGRATION_SCRIPTS`

`git status --porcelain` confirms no other file was touched.

## Task's own `verify:`

Verbatim, cross-checked byte-for-byte against `plan.yaml:851-852` before running (matches the
dispatch's quoted copy exactly):

```
python3 .claude/skills/harness/bin/test-hooks-install.py
```

Output (27/27, exit 0):

```
PASS: commands verbatim: step 1's command string is present in SKILL.md
PASS: commands verbatim: step 2's set command is present in SKILL.md
PASS: commands verbatim: step 2's get command is present in SKILL.md
PASS: (a) SC-08 first half: before the setup step, core.hooksPath does not resolve to the tracked hooks directory
PASS: setup step exits 0 on a fresh clone
PASS: (b) SC-08 second half #1: after the setup step, core.hooksPath resolves to the tracked hooks directory
PASS: (b) SC-08 second half #2: the post-merge file there is executable
PASS: (c) SC-13 clause 1: both runs exit 0
PASS: (c) SC-13 clause 1: value after the second run equals the first
PASS: (d) SC-13 clause 2: the step's stdout carries the value it found
PASS: (d) found value reported equals the pre-set unrelated value
PASS: (d) SC-13 clause 3: no run leaves the clone pointing at a directory the harness did not write without having said so — value is unchanged and the report above proves it was said
PASS: (d) RED PROOF precondition: unconditional variant still passes clause one (idempotence)
PASS: (d) RED PROOF: unconditional variant FAILS clause 2 — it never reports the value it found
PASS: (d) RED PROOF: unconditional variant also silently overwrites the unrelated value (clause 3 violation) without having said so
PASS: (e-green) setup step exits 0
PASS: (e-green) core.hooksPath points at the tracked dir after setup
PASS: (e-green) real merge succeeds
PASS: (e-green) SAFETY: sweep resolved its root inside this fixture, never the real harness checkout
PASS: (e-green) SC-14: the terminal feature's worktree is gone after a real merge, with NOTHING hand-installed into .git/hooks/
PASS: (e) RED PROOF still passes (a): before setup, not installed
PASS: (e) RED PROOF still passes (b): after setup, resolves + executable
PASS: (e) RED PROOF still passes (c): idempotent
PASS: (e) RED PROOF still passes (d): reports the unrelated value found
PASS: (e-red) setup step exits 0
PASS: (e-red) core.hooksPath points at the tracked dir after setup
PASS: (e-red) real merge succeeds
PASS: (e-red) RED PROOF: the shim reports the missing sweep rather than silently doing nothing
PASS: (e-red) RED PROOF: with the shim repointed at a nonexistent sweep, the worktree SURVIVES the merge
EXIT=0
```

`task_verify: pass`.

## Design decisions, ahead of trust

1. **The "setup step" under test is `run_setup_step()`**, a small orchestration this file defines
   from ONLY the two literal command strings SKILL.md carries (step 1, step 2's set+get). Step 3
   is prose with no command and contributes nothing runnable — matching the dispatch's own
   derivation. `case_commands_verbatim_in_skill()` asserts all three literals appear byte-for-byte
   in `harness-init/SKILL.md` before anything runs them.
2. **Case (d)'s RED PROOF is "skip step 1, run only step 2"** (`run_setup_step_unconditional()`),
   per the dispatch's own resolution of the ambiguity: since step 1 is what carries the report,
   skipping it is the natural model of "writes the config unconditionally." Verified: it still
   passes idempotence (writing the same value twice is still idempotent) and FAILS the reporting
   clause — demonstrated, not asserted (see the RED PROOF output block below).
3. **SC-13's third clause** ("no run leaves the clone pointing at a directory the harness did not
   write without having said so") is pinned by the assertion literally named
   `"(d) SC-13 clause 3: ..."` in `case_sc13_reporting_and_red_proof()` — it checks the unrelated
   value survives the GREEN run unchanged, and is the direct counterpart to the RED PROOF's
   assertion that the unconditional variant silently overwrites it. Not left ungraded.
4. **Case (e) fixtures are REAL `git clone`s** of a throwaway origin that commits real copies
   (never symlinks — see G-05/G-14 in Expertise re: env-redirect fallbacks and cross-boundary
   symlink fragility) of every file under `BIN_DIR` plus the real, unmodified T-11 shim at
   `.claude/skills/harness/hooks/post-merge`. The mandatory safety belt from
   `test-post-merge-sweep.py` (`_assert_resolved_root_in_fixture`) is reused verbatim in the
   GREEN branch: the sweep's own "resolved repository root" line is read back and asserted to
   equal the fixture and never `REAL_ROOT`. (The RED branch has no such line to check by
   construction — the mutated shim reports the missing sweep and returns before the sweep's root
   print ever runs; asserted instead on that exact report string.)
5. **Case (e)'s RED PROOF repoints the shim's `_sweep=` line** to a path verified absent, in a
   `_mutated_copy`-style textual substitution (needle asserted present in the real shim's source
   before mutating, so a defeat cannot be a no-op) — then re-runs (a)-(d) against a clone of that
   SAME mutated origin to prove they are unaffected (the setup step never inspects or executes the
   shim), before showing (e) itself fails.

## RED PROOFS — verbatim, both demonstrated failing before the fix reads as a pass

**Case (d)**, run inside `case_sc13_reporting_and_red_proof()` against `clone-d-red` (core.hooksPath
pre-set to `some/other/hooks-dir`), invoking ONLY step 2 (`run_setup_step_unconditional`):

```
out_red = "" (step 1 never ran, so nothing reporting "some/other/hooks-dir" is ever printed)
val_red = ".claude/skills/harness/hooks"   # silently overwritten
```
Assertions that read this as red: `"some/other/hooks-dir" not in out_red` → True (clause 2 fails)
and `val_red == TARGET and "some/other/hooks-dir" not in out_red` → True (clause 3 violated). Both
recorded as PASS in the suite above because the suite is asserting the red proof's failing
behaviour is real — the discriminator is genuine (absence of a report string that the GREEN path
always produces), not an incidental crash.

**Case (e)**, repointed-shim origin, real `git merge` (verbatim stdout+stderr, git's hook stdout
lands on git's stderr channel):

```
Updating e7ee81b..813f308
Fast-forward
 .harness/harness/features/FEAT-90-e-red-thing/feature.json | 1 +
 1 file changed, 1 insertion(+)
 create mode 100644 .harness/harness/features/FEAT-90-e-red-thing/feature.json
post-merge: /private/var/.../clone-e-red/.claude/skills/harness/bin/does-not-exist-sweep.sh is missing or not executable — no worktree sweep ran.
```

The worktree at `dest` (`.claude/worktrees/harness/FEAT-90-e-red-thing`) is confirmed present
afterwards (`os.path.isdir(dest)` True) — the discriminator is the shim's own T-11-authored refusal
message ("missing or not executable — no worktree sweep ran"), the exact string the tracked shim
prints for this exact condition, not a crash or an unrelated error.

## Registration

`INTEGRATION_SCRIPTS` (`run-unit-tests.sh:18`) and `test_kinds.integration.detect`
(`.harness.json:119`) both now carry `test-hooks-install.py`, an explicit literal path matching
the form of every existing entry. Verified by running `run-unit-tests.sh` in full (below) — no
KIND-DRIFT, no MISCONFIGURED, both of which would fire loudly (exit 2, before any test runs) on a
one-sided registration.

## Verify sweep — every command, raw exit code and counts, no pipe before `$?`

**`python3 .claude/skills/harness/bin/test-hooks-install.py`** — 27 PASS / 0 FAIL, `EXIT=0`
(script's own printed line), exit code `0`.

**`python3 .claude/skills/harness/bin/test-post-merge-sweep.py`** — measured **41 PASS / 0 FAIL**,
exit code `0`. The dispatch's prior figure of "36 PASS" does not match what this checkout runs
right now — reported as measured, against the framing, per Expertise P-07. Not a regression: 0
FAIL lines, `EXIT=0` printed, and I did not touch this file or its test.

**`python3 .claude/skills/harness/bin/test-worktree-terminal.py`** — measured **34 PASS / 0 FAIL**,
exit code `0` — matches the dispatch's stated figure exactly.

**`.claude/skills/harness/bin/run-unit-tests.sh`** (full run, all 45 unit + integration scripts,
`$?` captured directly, no pipe): exit code **`1`**. Grep for `KIND-DRIFT` and `MISCONFIGURED`
across the entire run: **zero matches at the top level** — the only lines containing those tokens
are `test-run-unit-tests-kinds.py`'s own synthetic test cases exercising the drift detector by
name, not a real drift report from this run. Per-script tally: **49 `PASS test-*.py` lines, 1
`FAIL test-*.py` line** — `FAIL test-validate-digest.py`, at `1441:FAIL test-validate-digest.py`.
Reran it standalone (`python3 .claude/skills/harness/bin/test-validate-digest.py`) and it fails
identically, reproducibly: `8/14 hook cases passed`, `6 FAILING`, first failure
`[hook] DEC-156: missing file fails OPEN with the INV-15 pointer, not a block — expected exit 0,
got 2`. **Not caused by any of my three files** — I never touched `check-digest`,
`test-validate-digest.py`, or anything DEC-156 governs, and confirmed via `git status --porcelain`
that neither file appears in my working-tree diff. Flagged as `open_questions` below,
non-blocking for this task: `test-hooks-install.py` itself passes in full, and the specific
loud-failure modes this task's registration could have caused (KIND-DRIFT, MISCONFIGURED) are
both absent.

**`.claude/skills/harness/bin/check-state.sh`** — exit code `0`. `grep -c "VIOLATION"` on the raw
output: `0`.

## SC-13 clause coverage — explicit, per the dispatch's own requirement

All three clauses are graded, none silently passed:
- Clause 1 (idempotence) → `case_sc13_idempotence()`.
- Clause 2 (reporting) → `case_sc13_reporting_and_red_proof()`, first half.
- Clause 3 (no silent displacement) → the same function's `"(d) SC-13 clause 3: ..."` assertion,
  and its RED-PROOF counterpart.

## Open questions

- { id: Q1, question: "test-validate-digest.py fails reproducibly (6/14 hook cases) on a
  pre-existing, unrelated DEC-156 mismatch between check-digest's hook behaviour and the test's
  expectation for a missing digest.md file (expects exit 0 with an INV-15 pointer, hook returns
  exit 2). Not touched by T-13's three files. Should route to whichever engineer/lead owns
  check-digest right now.", blocking: false }
