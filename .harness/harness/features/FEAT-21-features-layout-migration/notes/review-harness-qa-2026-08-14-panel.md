# QA gate — FEAT-21 — panel review at `b1d3925`

**PASS. Matrix earned on the widened set, not the floor — same shape as the prior segment. SC-10's
case is SOUND: both halves of "reddens if either side changes alone" are now independently
mutation-proven, one by the orchestrator, one by me. The dispatch's provenance framing for `5c39f8c`
is wrong; the fact underneath it is fine.**

## Job 1 — test_matrix gate re-run at `b1d3925`

Run in a disposable worktree (`.claude/worktrees/qa-panel-b1d3925`, checked out at `b1d3925`, removed
after use — never the live tree).

```
$ .claude/skills/harness/bin/run-unit-tests.sh --kind unit         → exit 0, 15/15 suites PASS (706 ok)
$ .claude/skills/harness/bin/run-unit-tests.sh --kind integration  → exit 0, 12/12 suites PASS (634 ok)
```

`b1d3925` touches exactly one file: `test-layout-migration.py` (61+/64-, no production source). That
file is `T-01`'s binding suite, `change_type: logic` per `plan.yaml:241`, and is listed in
`UNIT_SCRIPTS` (`run-unit-tests.sh:17`) — unchanged by this commit. So the per-task binding table qa
built at the prior pin (`notes/qa-c0.md` Job 1) still holds exactly: floor (`logic` → `unit` only)
does not execute the binding suites for T-03/T-04/T-05/6-of-8-T-06/T-10's gh-sync half, because
`unit.cmd` runs only `UNIT_SCRIPTS` while those suites sit in `INTEGRATION_SCRIPTS`. Confirmed still
true at `b1d3925` — nothing in this range's three new commits (`5c39f8c`, `649b36b`, `3df7002`, all
bookkeeping — see Job 2) or in `b1d3925` itself changes any binding.

`matrix_ok: true` **is earned on the widened set (`unit` + `integration`, both required for this
change shape and both green), not on the floor alone.** Under the literal floor, T-03/T-04/T-05 would
report zero kind coverage — the same near-vacuous-floor finding the prior segment made, unchanged.

Kinds: `unit` = satisfied (15/15 suites, named, including `test-layout-migration.py` itself).
`integration` = satisfied, added past the floor, required for this change shape (12/12 suites named).
No kind missing, n/a, or blocked.

## Job 2 — provenance check

`git log --oneline 62fef85..b1d3925` → **8 commits, not 5**: `4b16f47`, `ea937b1`, `5afa7e3`,
`d033b9d`, `5c39f8c`, `649b36b`, `3df7002`, `b1d3925`. The dispatch's five-commit enumeration
undercounted by three: `5c39f8c` ("enters validation"), `649b36b` (goal-check), `3df7002` (SC-10 fix
routing) — all FEAT-21 bookkeeping (STATE.md/feature.json/notes/observations only, confirmed via
`git show --stat` on each; zero source or test files).

`5c39f8c` **is a real, unrewritten commit and an ancestor of `b1d3925`**
(`git merge-base --is-ancestor 5c39f8c b1d3925` → true; `git cat-file -t 5c39f8c` → `commit`). It sits
as the fourth commit in the range, between `d033b9d` and `649b36b` — not absent from the range as the
dispatch's framing suggested.

**The dispatch's premise was wrong, and the underlying fact is unremarkable once corrected.** The
prior qa segment's own note (`notes/qa-c0.md:3`) states plainly that `5c39f8c` was its **pin**
(`HEAD = 5c39f8c`, range audited `62fef85..5c39f8c`) — the endpoint of a five-commit range at that
time, not a sixth commit missing from a five-commit set. Once the range grew to `b1d3925` by four more
commits, `5c39f8c` naturally becomes an interior ancestor. There is no rewrite, no orphaned SHA, no
provenance defect — just an inaccurate re-statement of a fact the prior segment already recorded
correctly. Not a blocker, per the dispatch's own framing; recorded as a correction for the digest.

## Job 3 — SC-10 case soundness

**Sound. The fix genuinely removes the mirror-drift failure mode; it does not relocate it.**

**Does the real-subprocess call remove mirror drift?** Yes, on the mechanism SC-10 exists to police.
Both call sites — `check-state.sh:1310-1322` and `layout_migration.render()` (this file's CI side) —
compose their reader/blame text from the **same** shared functions, `layout_migration.blame()` /
`blame_text()` / `cause_text()`. The session-entry side in the test (`test-layout-migration.py:358`)
now runs the real `check-state.sh` binary as a subprocess against a fixture tree
(`_sp.run([_CHECK_STATE], cwd=tmp, ...)`), and the CI side calls `lm.render(lm.scan(tmp))` over the
identical tree. `_inv27_text` (the old hand-mirror) is gone — confirmed by grep, zero hits. A drift
between the two call sites' own **framing** (the bash script's own f-string composition at
`check-state.sh:1317` vs `render()`'s own line-building) is what this now actually exercises; a drift
inside the shared `blame()`/`cause_text()` functions themselves would move both sides together and
this parity case would not catch it — but that is a pre-existing, separately-covered surface (the
seven INV-26 station-mirror cases named in the prior digest), not something SC-10 claims to cover.

**Six of seven cause paths — verified independently.** `layout_migration.py:232-256` enumerates
exactly seven verdict/cause branches: `MIXED`, `CLEAN`, and five `CANNOT_VERIFY` causes (`no-rows`,
`undeclared-segment`, `unreadable`, `neither`, `no-evidence`). Case 20's six `_parity()` calls
(`test-layout-migration.py:381-395`) cover `MIXED`, `neither`, `unreadable`, `no-evidence`,
`undeclared-segment`, `CLEAN` — six of the seven, `no-rows` excluded. Count confirmed independently
against the source, matching the claim exactly.

**Is the `no-rows` exclusion legitimate?** Yes. `no-rows` fires only when `scan()` is called with a
`table` argument whose rows are filtered for a surface (`layout_migration.py:232`,
`if not rows: ... "no-rows"`) — `check-state.sh` always runs the production `READER_TABLE`, which is
never empty, so the real gate can structurally never produce this cause. A fixture tree cannot trigger
it without overriding the table, and overriding the table breaks the "real gate" premise the whole
case exists to prove. One inaccuracy in the file's own comment (`test-layout-migration.py:396-398`):
it attributes `no-rows` wording coverage to "check-state's own case_x" — grepped `test-check-state.py`
for `no-rows`/`no reader rows`, zero hits. The actual coverage is **this same file's case 16**
(`test-layout-migration.py:267-274`, `table=no_docs`, asserts the literal phrase
`"no reader rows for this surface"`), not check-state's suite. Low-severity: the wording is genuinely
covered, just misattributed in a comment — not a coverage gap, a documentation nit.

**Render-side mutation probe — the half the orchestrator did not run.** Scratch copy at
`/private/tmp/.../scratchpad/bin-render-probe/` (copied from the `b1d3925` worktree's `bin/`, outside
the repo). Mutated `render()` alone: gated the `readers:` clause behind `if False and rep.verdict in
(MIXED, CANNOT_VERIFY):` (`layout_migration.py:340`), leaving `check-state.sh`'s own composition
untouched. **Mutation applied, confirmed by diff** against the unmutated worktree copy (one line
changed, exactly the guarded conditional). **Suite ran, confirmed by exit code and named FAILs**: `python3
test-layout-migration.py` → exit 1 (was exit 0 clean), 12 FAIL lines. Three are the discriminating
case-20 parity assertions themselves: `MIXED, one migrated reader...`, `CANNOT_VERIFY neither...`,
`CANNOT_VERIFY unreadable...` — each failing on `real gate and render name the same reader set`, with
the GATE output still naming `readers .harness/team-config.yaml [migrated]` etc. while the CI output
(mutated) names none. **Baseline provenance, stated precisely rather than implied:** the orchestrator's
scratch-copy BASELINE (unmutated) shows three case-1 failures (real-repo-root scan unreachable from a
scratch location, per the dispatch) with case 20 itself green — orchestrator-measured, cited here, not
independently re-run by me. Against that baseline, my render-only mutation turns three case-20
assertions RED while the rest of the suite's case-20 lines stay green, which is the discriminating
delta. **This closes the half the orchestrator's probe did not cover**: SC-10 now has independent
mutation evidence that the case reddens if the **gate** side changes alone (orchestrator, prior run —
dropping the blamed-reader clause from `check-state.sh`'s own MIXED-branch f-string) *and* if the
**render** side changes alone (this run, `layout_migration.py`'s `render()`). Neither probe touched the
other's call site — both sides consume the identical `tmp` tree per `_parity_tree()`, so a fixture
mismatch cannot manufacture the drift; it has to come from the composition logic each side owns
separately, which is exactly what SC-10 (per `5afa7e3`'s own commit message: "pins CI/session-entry
parity for blame and cause text") claims to police — reader-set and cause-clause parity, not a
full-string diff.

**The case-1 baseline failures are a scratch-location artifact, not a fix defect.** Case 1
(`test-layout-migration.py:130-133`) asserts `code == 0` and non-zero feature/reader counts scanning
`HERE` — the real repository root. A scratch copy living outside the repo has no `.harness/`
control-plane marker at that path, so case 1 fails at baseline regardless of any mutation. Verdict is
scoped to the case-20 assertions specifically (which use `tempfile.mkdtemp()` fixture trees, not
`HERE`), not to the suite's aggregate exit code — consistent with the dispatch's own framing.

## Standing items — actually re-run at `b1d3925` in the worktree, not relayed from suite PASS

- `layout_migration.py .` at pin: **exit 0** — `features: CLEAN — evidence migrated`,
  `docs: CLEAN — evidence legacy`, `examined 21 feature dir(s), 1 doc root(s), 7 reader file(s)`,
  `layout: 2 surface(s) clean, 0 mixed, 0 cannot-verify`. Reproduces exactly.
- `check-state.sh` (`CLAUDE_PROJECT_DIR` pointed at the worktree) at pin: **exit 0**, `grep -c INV-27`
  on the full output → **0**. (Per `notes/qa-c0.md` Job 3, `test-check-state.py`'s own suite never
  exercises the real tree, so that suite's PASS was never evidence for this line — running the binary
  itself, as done here, is.) The only `note`-severity lines present are unrelated pre-existing INV-23
  STATE.md-shape findings on `FEAT-02`/`FEAT-05`, dated before this feature.
- `check-plan-routes.py` at pin: **exit 0**, `0 violation(s) across 1 plan(s)`,
  `examined 21 feature dir(s); 20 skipped as shipped`. (Per `notes/qa-c0.md`, the real-tree
  non-zero-count assertion was deliberately removed from that suite's own tests on 2026-08-13 — so
  again, running the script directly, not the suite's PASS, is what confirms this.) The ten `DEVIATION`
  lines for FEAT-21's own tasks (backend-dev/dev-ops grants vs plan's `main-session-direct` lane) are
  the DEC-174 carve-out shape the prior panel already ruled on — 0 `VIOLATION`s, which is the number
  this script actually gates on.
- All items in the dispatch's "ALREADY RULED" list (MF-1, VF-1..4, ADV-1..5, Q-H, SC-02/07/11/12
  inspection-only, ~181/186 cases unprobed) are unchanged by this pin — `b1d3925` touches only the
  SC-10 test case, nothing that bears on any of them.

## SC evidence (unchanged from `notes/qa-c0.md`, reconfirmed live at `b1d3925`)

| SC | Test |
|---|---|
| SC-04 | `run-unit-tests.sh --kind unit`/`--kind integration`, 15+12 suites PASS at `b1d3925` |
| SC-10 | `test-layout-migration.py`, case 20 `parity` — PASS at `b1d3925`; SOUNDNESS independently verified above (six-of-seven count, both mutation halves) |
| SC-01/03/05/06/08/09/13/14 | unchanged; see `notes/qa-c0.md` for the full table — none touched by this range's three bookkeeping commits or by `b1d3925`'s test-only edit |
| SC-02/07/11/12 | inspection-only per `BRIEF.md:163-164`; no runner covers them, unaffected by this pin |

## Coverage gaps (Phase 1 vs Phase 2 — unchanged)

- None new. `b1d3925` is a test-file-only edit to an existing, plan-pinned case; it does not open new
  Phase-1-derivable surface. The standing gaps from the prior segment (D-08 delivery-half label
  unpinned, `check-state.sh` zero-discovery unbound on the real tree, ~181/186 cases unprobed) all
  carry forward unchanged — none are this dispatch's to close.

## New, low-severity finding

- **NF-1 · low · misattributed coverage comment.** `test-layout-migration.py:396-398` attributes
  `no-rows` wording coverage to "check-state's own case_x"; the actual coverage is this same file's
  case 16. Not a gap — the wording is genuinely tested — but a successor reading the comment would
  look in the wrong file. Cosmetic; not a `must_fix`.

artifact: .harness/harness/features/FEAT-21-features-layout-migration/notes/review-harness-qa-2026-08-14-panel.md
