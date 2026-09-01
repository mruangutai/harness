# QA — FEAT-41 one-station-vocabulary — Cycle 4

review_sha `64f42ef86b5c388544f34c02a8f9b5831250df73`. Worktree HEAD `07d428d` differs from
review_sha by exactly one line (`feature.json`'s `review_sha` pin) — confirmed with
`git diff --stat 64f42ef8 HEAD`, so reading/running the live worktree is equivalent to reading the
pin. All mutation was performed on a `git archive 64f42ef8` extraction at `/tmp/feat41-c4`, never
in the worktree. Worktree `git status --short` shows no modified/tracked-file changes — only new
untracked panel note files (this one included). Both Stage 1
(spec/matrix) and Stage 2 (mutation, non-vacuity) ran.

## Stage 1 — matrix gate: **PASS**

- `--kind unit`: exit 0, **508 PASS**, 0 FAIL — matches baseline exactly.
- `--kind integration` (run serially, after unit): exit 0, **819 PASS**, 0 FAIL — matches baseline
  exactly. (First pass under-counted at 696 because `^PASS ` misses the `PASS: (…)`/`PASS  …`
  colon/double-space variants the suite also uses — corrected with `^PASS[ :]`; both regexes agree
  on 819. Flagging the counting pitfall since it nearly produced a false "different numbers"
  report.)
- `check-state.sh`: exit 1, exactly **one** `VIOLATION` line, `INV-29` on the standing
  `BUG-1080-inv6-plan-phase-runs` worktree — the stated environmental exemption, not reported as a
  finding.
- Every changed production file under `.claude/skills/harness/bin/` (`board-station.py`,
  `board_lifecycle.py`, `check-domain.sh`, `check-plan-routes.py`, `check-state.sh`,
  `factory_claim.py`, `factory_config.py`, `factory_decompose.py`, `factory_land.py`,
  `feature-schema.json`, `gh-sync.py`, `gh_board.py`, `harness_boundary.py`, `harness_yaml.py`,
  `plan-merge.py`, `plan-sign-gate.py`/`.sh`, `run-unit-tests.sh`, `worktree_terminal.py`) has a
  matching test file **also changed in the same diff** (`6ddcac3..64f42ef8`) — cross-referenced
  the two diff-stat lists directly, no gaps. `run-unit-tests.sh`'s own one-line change (adding
  `test-plan-merge.py`/`test-plan-sign-gate.py` to `INTEGRATION_SCRIPTS`) is exercised end to end
  by the 819-PASS integration run itself, which is the strongest form of proof for a kind-wiring
  change. Presence of a matching test file is not by itself proof of behavioural coverage — see
  the mutation results below for the load-bearing claims actually probed.

## D-18(a) independent re-measurement — **CONFIRMED, and the "54→57" drift explained**

Ran the operator's own commands independently, at review_sha:
- `_STATION_KEYS` total in tracked tree: **57**, split **45** `.md` / **10** `.yaml` (all inside
  prose *values*, in exactly **3** old `plan.yaml` task descriptions — `FEAT-24`, `FEAT-33`, and
  this feature's own) / **2** `.html` — matches the operator's 45/10/2 split exactly.
- Mapping-key declarations (`^\s*_STATION_KEYS\s*:`): **0** — confirmed.
- Why cycle 3's "54" moved: at the cycle-3 fix commit `5ae94e5` the true count was **55**, not 54
  (plan.yaml's own D-18(a) text still says "54 remaining `_STATION_KEYS` hits" — that's off by one
  even against its own contemporaneous state). By review_sha the count grew to **57**: the +2 is
  cycle-3's and cycle-4's own review artifacts (`review-harness-code-reviewer-c3.md`, ship-review
  HTML/MD, orchestrator observations) quoting `_STATION_KEYS` in their own prose while discussing
  the finding. This is narrative growth, not source growth — reconfirmed zero hits outside `.md`/
  `.yaml`(prose-value)/`.html`. **Low finding**: `plan.yaml:234`'s D-18(a) text is stale by 3
  against its own re-measurement discipline (says 54, is 57); worth a one-line correction if this
  feature reopens, not worth blocking on.

## Stage 2 — mutation (non-vacuity)

### `(inv34.e)` doubled-defence — **genuinely non-vacuous, both layers independently load-bearing**

Target: `check-state.sh:211` (keying: `if doc.get("station_only") is True: continue`) and
`harness_yaml.py:326-327` (loader: refuses `tasks: []` without a `station_only: true` marker).
Reproduced all three legs from the handoff, in `/tmp/feat41-c4`:

| what I reverted | what I ran | result |
|---|---|---|
| keying only (`check-state.sh:211` → `if not doc.get("tasks"): continue`, the pre-fix form) | `test-check-state.py` | **green** — caught by the untouched loader raising `PlanSchemaError` before the loop runs at all |
| loader only (`harness_yaml.py:326-327` → `if False:`, so `tasks: []` loads without the marker) | `test-check-state.py` | **green** — caught by the untouched keying: `station_only` isn't `True`, so the loop does *not* skip, and the STATE.md-dangling-task check (`check-state.sh:220-226`, same loop body, one function below the keying line) fires on the fixture's `T-99` reference |
| both reverted simultaneously | `test-check-state.py` | **FAIL** — `case (inv34.e)` goes red, exactly as claimed |

This is real defense in depth, not two guards hitting one detector (ruled out the O-05 vacuity
shape explicitly): the loader guards at parse time, the keying+STATE.md-scan guards at inspection
time, and each is independently sufficient. All files restored; diffs confirmed empty against the
`/tmp` originals before moving on.

### MF-1 (`plan-sign-gate.py` balanced-paren scan) — **red on revert, confirmed load-bearing**

Reverted `_strip_substitutions` (`plan-sign-gate.py:141-166`) to the naive
`re.sub(r"\$\([^)]*\)", " ", line)` cycle 3 warned would leak on nesting. Ran
`test-plan-sign-gate.py`: **2 of 8 checks FAIL**, including the exact nested case
(`plan-merge.py$(echo "$(printf " ")")sign-approval`) the fix exists for. Restored; diff clean.

- **Nested form `$(a$(b))` is covered** — `test-plan-sign-gate.py:357-362`.
- **Unclosed `$(` is NOT covered anywhere in the file.** All five flat cases and the one nested
  case at lines 347-378 are well-formed (every `$(` closes). Confirmed by mutation: reverted the
  "unclosed substitution consumes the rest of the line" behavior (`plan-sign-gate.py:153-157`) to
  leave the trailing text in place instead of swallowing it — **the entire suite (`8/8`) stayed
  green**, proving this documented, deliberately-chosen security behavior has zero test coverage
  in either direction. **Finding (med):** `plan-sign-gate.py:153-157`'s unclosed-substitution
  handling is production code with a specific, non-obvious contract (swallow the rest of the line
  rather than leave a truncated `$(` for a later continuation/heredoc to complete) and no test
  exercises it; a future edit to this code path would ship silently. File:
  `.claude/skills/harness/bin/plan-sign-gate.py:153-157`. Scenario: a signing call split so the
  verb sits inside a would-be-continued, currently-unclosed `$(...)` on one physical line — no
  fixture constructs this, so a regression here (e.g. reverting to "leave text behind") is
  undetectable by the standing suite. Restored; diff clean.

### MF-2 (`harness_boundary.py` NUL fail-closed) — **red on revert, confirmed load-bearing**

Reverted `check-domain.sh:1514-1517`'s `except (OSError, ValueError):` to `except OSError:` only
(the pre-fix bug — `realpath` raises `ValueError`, not `OSError`, on an embedded NUL). Confirmed
the fixture reaches `classify` for real (its `_approval_root`/`fixture()` writes
`.harness/team-config.yaml`, satisfying the G-02/P-03 precondition — not the "invalid fixture"
mistake cycle 3's first probe made). Ran `test-check-domain.py`: **2 checks FAIL**
(`T-09 12: a NUL-bearing path is REFUSED…` and `…does not crash`) — the crash reproduces exactly.
Restored; diff clean.

### `station_only: true` keying — covered above under `(inv34.e)`; all three legs match the
handoff's claim exactly.

### Stale `verify:` — **HIGH-adjacent finding, plan.yaml's own audit trail is broken for T-14**

Per the dispatch's instruction to spot-check that every `verify:` clause can still fail and that
no later commit falsified the word it greps: **T-14's own `verify:` block no longer reproduces.**

- File: `.harness/harness/features/FEAT-41-one-station-vocabulary/plan.yaml:1380-1383` (task
  `T-14`, `status: done`).
- Scenario: the block greps `test-check-state.py`'s stdout for the literal strings
  `"ok - case (inv32.a) a stale review_sha is reported"`, `(inv32.b)`, `(inv32.c)`, `(inv32.d)`.
  Ran the four `grep -q` lines **verbatim** against the current `test-check-state.py`'s real
  output: **all four exit 1** (no match). The live test file names these cases `(inv33.a)` through
  `(inv33.d)` — confirmed with `grep -c "inv33\.[abcd]"` on the same output, 8 hits (2 print sites
  each). The rename from INV-32 to INV-33 is deliberate and documented (handoff-build.md:38:
  "T-14's invariant is INV-33 now, not 32: FEAT-45 shipped its own INV-32 first, so it owns the
  number") — but T-14's `verify:` text (both the four `grep -q` lines and the surrounding
  `intent:` prose at lines 1481-1560, which still narrates "(inv32.a)" throughout) was never
  updated after that rename. `python3 test-check-state.py` alone (line 1379, no grep) still exits
  0, so the task's headline pass/fail is unaffected — but the literal verify command recorded as
  T-14's proof of work **no longer reproduces**, which is exactly the "a later commit falsified
  the word it greps" shape this instruction was written to catch. It happened by renumbering
  rather than by a hostile edit, but the effect on trust in the record is the same: a future reader
  re-running T-14's stated verify command to confirm the receipt gets a false red.
- **Severity: med.** No live enforcement is weakened — INV-33 fires correctly in the shipped code
  and its own current-named test cases all pass. This is an audit-trail integrity defect in
  `plan.yaml`, not a security or correctness regression, and per PRINCIPLES rule 15 ("never
  falsify the record") a stale-but-truthful-when-written record is a lesser sin than a rewritten
  one — but it is unreproducible today and should be corrected (rename `inv32.*` → `inv33.*` in
  the four grep lines and the intent prose) the next time this plan.yaml is touched.

## `verify:` spot checks (presence-paired with absence, per DEC-169)

- SC-01's `grep -rn --exclude-dir=__pycache__ "_STATION_KEYS" .claude/skills/harness/bin/ ; test $? -eq 1`
  (T-01, `plan.yaml:268`): re-ran independently, exit 1 (no matches) — confirmed, and paired with
  `test-factory-config.py`'s positive assertion of the six-station declaration on the same line.
- SC-02's retired-spelling absence check (T-13, `plan.yaml:1318`,
  `grep -n "Icebox\|Drafted\|Primed\|Shipped" test-check-state.py`): re-ran, exit 1 — confirmed.
- T-08's `test_kinds.integration.detect` / `run-unit-tests.sh` membership assertions
  (`plan.yaml:1029-1031`): re-ran both independently — confirmed true (first attempt via a bash
  one-liner produced a false negative from a shell quoting collision between the outer `-c` quotes
  and Python's own single-quoted literal, not a real defect — re-ran via heredoc and got the
  correct `True`; noting this so it isn't mistaken for a finding by a later reader of this file).
- D-18 operator rulings ((a) SC-01 reading, (b) MF-4 → issue #1104, (c) sign-gate denylist → issue
  #1103): recorded faithfully in `plan.yaml:230-251`, matching the dispatch's ruling text exactly.

## Coverage gaps (Phase 1 vs Phase 2)

Phase 1 (BRIEF-only) expectation: every `verify:` block should be re-runnable as literal proof of
its task, indefinitely. Phase 2 found one that is not: **T-14's, above.**

- Unclosed-`$(` command-substitution handling in `plan-sign-gate.py` has no positive or negative
  test in either direction (detailed above under MF-1).

## SC evidence

| SC | test |
|---|---|
| SC-01 | `test-factory-config.py` (declaration) + `grep -rn --exclude-dir=__pycache__ "_STATION_KEYS" .claude/skills/harness/bin/` (absence), both independently re-run |
| SC-02 | `plan.yaml:1318-1319`'s two `grep` absence checks, independently re-run |
| SC-03/SC-06/SC-13 | `test-check-state.py` `(v.T06-pending)`, `(inv34.*)` cases, independently re-run and mutated |
| SC-04 | `test-gh-board.py`/`test-board-lifecycle.py` (in diff, part of 819-PASS run) |
| SC-07 | `test-check-domain.py` (mutation-tested above via MF-2) |
| SC-09/SC-14 | not independently mutated this cycle; `verify: inspection`/T-15's own DEC-marker-count assertion, unchanged since cycle 3 |
| SC-10/SC-11 | `test-gh-sync.py`, part of the 819-PASS integration run |

## Both stages ran

Stage 1 (matrix/spec) and Stage 2 (mutation/non-vacuity) both executed, in that order, as required.

## Verdict basis

No HIGH mutation-provable finding this cycle — the three cycle-3 fixes and the doubled-defence
guard all reddened correctly under targeted reversion, and D-18's numbers were independently
reproduced. Two MED findings (T-14's dead `verify:` grep; unclosed-`$(` zero coverage) are real
but neither is a live enforcement hole. Gate gates `advisory_unless_high` — calibrated PASS.
