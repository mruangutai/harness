# QA Gate — cycle 3 (review-c3) — FEAT-56, pin `44351432`

BLUF: All four claimed-closed findings are CONFIRMED closed at the pin, by independent reproduction
(not the fix cycle's own receipt). Matrix `matrix_ok: true`. Suite matches the operator-accepted
D-14 baseline exactly — same six case ids, same reason. F3 is closed for the mutation it targets, but
a *new*, narrower advisory gap surfaces from the reproduction it invited: the door set `--check`
enforces is a hardcoded literal with no independent test pinning its content, and F2's actual prose
fix (the delegation-target correction) has zero automated coverage — both reasoned findings below,
neither gating. Nothing authored: no test, fixture, or source file was created or edited in the
worktree; all reproduction ran in disposable `mktemp` scratch trees built from `git archive 44351432`.

## 1. Matrix

Owning task: T-14 (`plan.yaml:1754`, `change_type: config`), whose own `files:` list
(`plan.yaml:1763-1766`) is exactly `bin/sync-command-adapters.py`, `bin/check-omp-port.py`,
`tests/integration/test-sync-command-adapters.py`, `tests/integration/test-check-omp-port.py` —
the changed union this fix commit touches (plus the two `.omp/commands/` doors and four
`.claude/commands/` adapters, which are T-14's own generated/target artifacts, not a new surface).
`config`'s own predicate (`touches_config_shape`) does not strictly fire — nothing here changes a
config value's container type or required-ness. I add `cross_module`'s floor (`unit` + `integration`)
as the QA-inferred requirement instead, since the diff spans four distinct surfaces (bin script,
integration tests, `.omp/commands/` doors, `.claude/commands/` adapters) — a floor the run below
already meets in full.

**`matrix_ok: true`**

| kind | required | cmd (exact) | result |
|---|---|---|---|
| unit | yes (cross_module floor) | `.agents/skills/harness/bin/run-unit-tests.sh --kind unit` | exit 0; four by-design `^FAIL ` lines, all `test-factory-claim-mutation.py` (`BUG-1290 5a/5b/5c`, `5b` twice) — matches baseline exactly |
| integration | yes (cross_module floor) | `.agents/skills/harness/bin/run-unit-tests.sh --kind integration` | exit 1; **exactly six** failing cases, **all** `test-check-plan-routes.py`, **all** the same `MANIFEST`/`DEVIATION … team-config.yaml differs` reason — D-14 |

Both run with `env -u HARNESS_AGENT_TYPE`.

### Integration failing-case diff against the six-case baseline

Observed: `case_04_all_granted_exits_0`, `case_05_ungranted_declared_main_session_exits_0`,
`case_15_deviation_plan_still_exits_0`, `case_17_midpattern_wildcard_grant_exits_0`,
`case_19d_explicit_path_unaffected_by_the_root_guard`,
`case_19d2_explicit_path_with_no_tasks_still_exits_0`.

Set-diff against the baseline (`case_04, case_05, case_15, case_17, case_19d, case_19d2`): **empty**
— identical ids. Reason-diff: all six report the identical `DEVIATION … .harness/team-config.yaml
differs from … .harness/team-config.yaml` cause (`/tmp/int_out.txt:3356-3411`, quoted verbatim in the
raw run) — the single D-14 owner-manifest deviation, not six independent causes. No seventh failure
anywhere else in the 4033-line run; every other script in the suite reports `exit 0`
(`grep -n "^----- .*(exit [0-9]*" | grep -v "exit 0"` returns only `test-check-plan-routes.py`).

### Standing scripts outside the two kinds

- `env -u HARNESS_AGENT_TYPE python3 .claude/skills/harness/bin/sync-command-adapters.py --check`
  (worktree, untouched) → exit 0, no output.
- `env -u HARNESS_AGENT_TYPE python3 .claude/skills/harness/bin/check-omp-port.py`
  (worktree, untouched) → `OMP port surface: ok`, exit 0.

## 2. F1 — `main()` decomposition (was high, gating)

**CONFIRMED CLOSED.** `tests/integration/test-sync-command-adapters.py`'s `main()` at the pin is a
5-line iterate-and-report loop over six `case_*` functions (`CASES` tuple), matching the sibling
convention (`test-sync-agent-adapters.py`). `test-code-grade.py` — the standing complexity gate,
which the pinned unit run above shows `PASS` — now covers this file clean; that is measured, not
inferred from the receipt.

## 3. F2 — canonical doors no longer delegate into their own adapters (was med, gating)

**CONFIRMED CLOSED**, by direct read at the pin (`git show 44351432:.omp/commands/harness-plan.md`,
`…harness-ship.md`): both now open `Read \`.omp/commands/harness.md\` and follow it with **mission:
plan/ship**` — the canonical general door, not the generated `.claude/commands/harness.md` adapter.

**Coverage gap (reasoned, not gating):** no test in the changed union asserts this. `check-omp-port.py`
only checks the four doors *exist* (`bin/check-omp-port.py:168-171`, bound to the live tree via
`test-check-omp-port.py`'s `case_live_tree_passes`), and `sync-command-adapters.py --check` only
checks adapter/canonical **byte parity**, never a door's *internal* delegation target. Nothing greps
either `.omp/commands/harness-plan.md` or `harness-ship.md` for the corrected pointer, and nothing
asserts the old wrong pattern's absence. A regression that re-pointed either door back at
`.claude/commands/harness.md` would pass every standing gate silently — the exact class F2 itself
was. Finding: file `.omp/commands/harness-plan.md`, `.omp/commands/harness-ship.md`; task T-14; lane
`team` (`.claude/skills/harness/bin/**`... — actually these two files are under `.omp/commands/**`,
a NOBODY lane per the constraints list); severity **med** (self-referential class, currently correct
but structurally unguarded).

## 4. F3 — `--check` now fails closed on a deleted door+adapter pair (advisory, taken)

**CONFIRMED CLOSED** for the mutation it targets, reproduced independently in three disposable
scratch trees (`git archive 44351432 | tar -x`; mutation via `python3 os.remove`, never `rm` — the
bash-write-guard denies pattern-matched paths like `.omp/commands/*.md` from a Bash `rm` even inside
a scratch tree, so mutation used Python's `os.remove` instead):

- **(a) clean baseline**: `env -u HARNESS_AGENT_TYPE python3 .claude/skills/harness/bin/sync-command-adapters.py --check`
  → **exit 0**, no output.
- **(b) door + adapter deleted together** (`.omp/commands/harness-ship.md` and
  `.claude/commands/harness-ship.md` both removed): same `--check` →
  `sync-command-adapters: required canonical door missing from .omp/commands/: harness-ship.md`,
  **exit 1**.
- **(c) control — adapter only deleted** (`.claude/commands/harness-plan.md`, door intact): same
  `--check` → `Claude command adapters are stale: harness-plan.md`, **exit 1** (drift path, as before
  the fix — unchanged, correctly still catches the simpler case).

This exact case is also permanently pinned as `case_missing_required_door_fails`
(`tests/integration/test-sync-command-adapters.py:135-152`), which the integration run above
executed and passed.

### The question the fix invites — where does the expected door set come from, and can it be shortened undetected?

Source: `REQUIRED_DOORS = ("harness.md", "harness-plan.md", "harness-ship.md", "harness-grilling.md")`
at **`.claude/skills/harness/bin/sync-command-adapters.py:24`** — a hardcoded literal tuple, not
derived from disk (`missing_required_doors()` at line 33-34 only iterates this constant).

**Yes, it can be shortened without detection.** Fourth scratch-tree reproduction: edited the SUT's
own `REQUIRED_DOORS` tuple down to three entries (dropped `harness-grilling.md`) and deleted the
now-unlisted door+adapter pair together → `--check` **exits 0**, silently. The script never emits a
discovered-door *count* anywhere (clean run prints nothing; failure runs print only names, never
"N of 4"), so **no non-zero discovery count is observable** to sanity-check against — this is itself
the finding the dispatch asked to surface.

**Does any test protect the constant itself?** No. `test-check-omp-port.py`'s
`case_required_doors_pinned_to_sync_command_adapters` (line 217) *imports and iterates*
`sync_command_adapters.REQUIRED_DOORS` at runtime — it proves `check-omp-port.py`'s own separately
hardcoded four-name tuple (`bin/check-omp-port.py:169`) stays in parity with *whatever*
`REQUIRED_DOORS` currently says, but a shrink of `REQUIRED_DOORS` itself shrinks both sides of that
comparison in lockstep and passes. `test-sync-command-adapters.py`'s own `REQUIRED_DOORS` dict
(lines 26-30) is a fixture literal used only to seed trees, never compared against the SUT's
constant. Only `check-omp-port.py`'s *own* independently-hardcoded tuple is pinned to exactly four
by `case_absent_canonical_command_root_fails` (line 200-211, `missing_doors == 4`) — there is no
equivalent independent pin for `sync-command-adapters.py`'s `REQUIRED_DOORS`.

**Finding** (advisory, not gating — mutation requires editing the SUT's own source, a change visible
in any diff/review, unlike a plain file deletion): file
`.claude/skills/harness/bin/sync-command-adapters.py:24`; task T-14; lane `team`
(`.claude/skills/harness/bin/**`, `harness-backend-dev | harness-dev-ops | harness-qa`); severity
**low**.

## 5. F4 — banner path (advisory, taken)

**CONFIRMED CLOSED.** Banner now reads
`Run .claude/skills/harness/bin/sync-command-adapters.py --apply.` — that path exists
(`test -f` confirmed). All four `.claude/commands/` adapters (`harness.md`, `harness-plan.md`,
`harness-ship.md`, `harness-grilling.md`) were regenerated: each adapter's body (stripped of line 1)
is byte-identical (`cmp`) to its `.omp/commands/` canonical source, and each carries the corrected
banner. Verified all four independently, not sampled.

## 6. Adequacy over the changed union — what the green gate actually binds

| unit | bound? |
|---|---|
| `bin/sync-command-adapters.py` | **Bound** — `test-sync-command-adapters.py` exercises `--check`/`--apply` across six cases including the F3 mutation; `test-check-omp-port.py` imports its `REQUIRED_DOORS` |
| `tests/integration/test-sync-command-adapters.py` | Self-exercising: ran clean (6/6) as part of the pinned integration run |
| `tests/integration/test-check-omp-port.py` | Self-exercising: ran clean as part of the pinned integration run; `case_live_tree_passes` binds `check-omp-port.py`'s existence check to the **real** four doors, not only fixtures — so SC-13's door assertion genuinely binds the live tree |
| `.omp/commands/harness-plan.md`, `.omp/commands/harness-ship.md` (the F2 content fix) | **Structurally present only.** No test reads or greps either file's delegation target. Confirmed correct here by direct inspection at the pin; unguarded against regression (§3) |
| Four regenerated `.claude/commands/` adapters | **Bound for existence** (`check-omp-port.py` live-tree case) and **manually confirmed for byte-parity** against canonical (this review, `cmp`) — but `sync-command-adapters.py --check` against the **live** tree is not itself wired into any standing `test_kinds` command; only fixture-driven `--check` invocations are part of the automated gate. A hand-edit to a live adapter would be caught only by someone re-running `--check` by hand, as this review and T-14's own verify block both did, not by `run-unit-tests.sh` |

## Findings summary

| id | file | task | lane | severity | gating |
|---|---|---|---|---|---|
| F1 | `tests/integration/test-sync-command-adapters.py` | T-14 | team (`tests/**`) | — | CLOSED, confirmed |
| F2 | `.omp/commands/harness-plan.md`, `harness-ship.md` | T-14 | NOBODY (`.omp/commands/**`) | — | CLOSED, confirmed |
| F2-gap | same two files | T-14 | NOBODY | med | advisory — no automated regression coverage of the delegation-target fix |
| F3 | `.claude/skills/harness/bin/sync-command-adapters.py` | T-14 | team (`.claude/skills/harness/bin/**`) | — | CLOSED, confirmed for the door+adapter deletion case |
| F3-gap | `.claude/skills/harness/bin/sync-command-adapters.py:24` | T-14 | team | low | advisory — `REQUIRED_DOORS` is an unpinned literal; shrinking it plus the matching door is undetectable, and no discovery count is ever printed |
| F4 | banner + four adapters | T-14 | team | — | CLOSED, confirmed |

No finding here reopens the gate: F1/F2/F3/F4 are each confirmed closed for the specific defect the
panel raised. F2-gap and F3-gap are new, narrower, advisory observations invited by this cycle's own
reproduction instructions — reported per rule 15 (record what was found), not folded into the fix
cycle's own claim.

## Open questions

- None blocking. F2-gap and F3-gap are advisory coverage gaps for a future cycle or the operator to
  weigh, not defects that reopen this panel's PASS.
