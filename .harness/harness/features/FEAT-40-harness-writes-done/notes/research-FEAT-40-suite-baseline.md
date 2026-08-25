# research — FEAT-40 — the red suite baseline, and three T-09 gaps

**BLUF.** Five task verifies (`T-04`..`T-08`) open with `run-unit-tests.sh --kind all`, which exits 1
if any script fails. Six scripts fail at `cc84b29` in this worktree, all six in `UNIT_SCRIPTS`, none
of this feature's making. The runner cannot select individual scripts (`run-unit-tests.sh:24-40`), so
those five tasks can never be marked done as written. The remedy is a new first task, **T-11**, that
repairs exactly one script — the only failing one any later task edits — and records the rest as an
enumerated, diagnosed baseline the five verifies compare against, plus one owned-script `PASS`
assertion per task so a green result still discriminates.

## 1. The measured failing set — 24 of 24 unit scripts, complete

Measured by me at `cc84b29` in
`/Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-40-harness-writes-done`, with
`HARNESS_PROJECT_DIR` set to that worktree. `UNIT_SCRIPTS` ran to completion: **18 PASS, 6 FAIL, 24
total** — the array's full length (`run-unit-tests.sh:17`). Independently reproduced in the main
session's own `--kind unit` run at the same sha, same six names, same order.

| script | failing cases | root cause, one line, as far as the output shows |
|---|---|---|
| `test-factory-config.py` | 1 of ~35 | case (21): a `CLAUDE_PROJECT_DIR` with no probe file is discarded but the discard is not announced on stderr |
| `test-validate-feature-json.py` | 1 | `case_migrated_depth` expects zero files and the sweep reports 37 — the case is scanning the real worktree's `.harness/*/features/*/feature.{json,yaml,yml}` rather than an isolated fixture |
| `test-branch-create-gate.py` | 3 of 8 | all three are `self-gate:` cases expecting exit 0 with no stdout — no github block, `github.sync` false, and repo unpinned |
| `test-layout-migration.py` | 7 | every one is `case 20 parity` — the real gate and the render do not name the same reader set, and the cause clause differs between them |
| `test-inject-expertise.py` | 9 | tier precedence, truncation caps (40 / 150 lines) and the empty-disk case all fail — reads like one changed injection contract, not nine bugs |
| `test-board-lifecycle.py` | ~40 | two visible root causes: a linkage guard refusing `project 3 (mruangutai) is not linked to 'mruangutai/harness'` that the test's `gh` fake does not satisfy, and a `workflow detection matches by NAME only` banner on **stdout** that the audit assertions compare against |

**Honest sizing.** Six scripts, roughly 60 failing assertions, clustering into about six root causes —
not sixty. But at least one is a behaviour question rather than a fixture fix: `board_lifecycle`'s
linkage guard either is correct and the test is stale, or the reverse, and that is a decision. Two
(`inject-expertise`, `layout-migration`) look like a contract that moved without its test. Repairing
all six is plausibly a feature of its own, comparable in size to `T-04`. **That is why T-11 repairs
one and quarantines five.**

**What is NOT measured, and nobody has measured it yet.** The integration bucket beyond
`test-validate-digest.py` and `test-gh-sync.py` has never been seen to completion in this worktree.
Both my `--kind all` run and the main session's `--kind integration` run were still inside
`test-check-state.py` after 5 and 14 minutes respectively, with three concurrent
`test-check-state.py` processes competing (pids 24690, 50143, 52814 observed). The main session's
earlier "20 PASS and SIX FAIL" is the same 26 scripts and stops at the same place — it was not
truncated by a reader, the run had not got further. `T-11` step 1 exists to settle this.

It is not a hang: `check-state.sh` children were still being forked at roughly one every 5–10
seconds after 40 minutes (`ps` on pids 52814 and 24690), with system load ~1.9. `test-check-state.py`
simply forks the whole state checker many times and each fork scans the repository. Run it alone.

**Runtime is itself a defect in these five verifies:** `--kind all` does not complete in under 60
seconds, which `harness-spec-driven` requires of a `verify:`. Pre-existing across the whole plan and
not changed here; raised as `Q12`.

## 2. Why not the two alternatives

- **Narrow each verify to the scripts the task touches.** Unavailable through the runner, and the
  bypass — invoking `python3 .claude/skills/harness/bin/test-*.py` directly — loses the drift
  detector (`:42-61`) and the kind cross-check (`:63-127`), which run on **every** invocation
  precisely so a mismatch is "not skippable by choosing a kind" (`:82`). `T-07` depends on exactly
  that mechanism to prove its own two-place registration of `test-gh-close-gate.py`.
- **`--kind integration`.** `harness.json:107` configures the project's unit gate separately, so a
  red unit set is red either way; and `T-05`'s `files:` names `test-validate-feature-json.py`, a
  **unit** script and one of the six. Narrowing `T-05` to integration would stop looking at the one
  test `T-05` edits. That is green-because-it-stopped-looking.

## 3. The chosen remedy, and what it stops checking

`T-11` (new, no dependencies, `depends_on` edge added to `T-04`, `T-05`, `T-06`, `T-07`, `T-08`):

1. Re-measure the full suite to completion and record the true set.
2. **Repair `test-validate-feature-json.py` to green.** It is the only failing script that appears in
   any later task's `files:` — `T-05` edits it to drop `parent_origin` fixtures. Repairing it is what
   makes `T-05` verifiable at all.
3. **Diagnose but do not repair** the other five. One line of root cause each, into the baseline note.
4. Write `notes/suite-baseline.md`, whose machine-read part is a fenced list of bare script names.

Each of the five verifies then: runs the suite once, asserts `rc != 2` (the drift detector and kind
cross-check still bite), asserts the set of `FAIL` lines equals the baseline file's list exactly, and
asserts `PASS <script>` for each script that task owns.

**What is no longer being checked, stated plainly.** A regression this feature introduces *inside*
one of the five quarantined scripts would be invisible: they are tolerated as `FAIL`, so their
failure count can grow without the set changing. Accepted because none of the five appears in any
task's `files:` and no task writes the surface they cover — with one real exposure:
`T-07` edits `.harness/harness.json`, and `test-branch-create-gate.py`'s three failing cases are
precisely its `harness.json` self-gate cases. `T-07` therefore carries an extra clause running that
script directly and asserting its case count is unchanged at `5/8 cases passed`, which is a
discriminator aimed exactly at the blind spot. `test-board-lifecycle.py` is red while `T-01`'s verify
runs `board_lifecycle.py audit` live; the live run is not the test, but a reader should know the
script's own suite is red.

## 4. The three T-09 gaps

- **The read-back sentence (`github-mirror.md:7-9`) is already false at `cc84b29`, on two counts, not
  one.** `gh-sync.py:804-806` documents `start-task` performing one board read and one issue read
  before its writes and calls it "squarely inside DEC-186's second sanctioned purpose"; `D-02` adds a
  third at ship. New edit `A.11` replaces the first two sentences with the enumerated six purposes
  `DEC-203` carries, copied from the entry `T-03` writes, and **keeps the second clause verbatim** —
  no read-back reaches an approval-gated artifact — because it is the only stated bound on what a
  read-back may do.
- **The verify was blind to part C.** Measured: `github-mirror.md` 5 matches of the absence-grep,
  `commands/harness.md` 1, `harness-init/SKILL.md` **zero**. Part C only adds a sentence to the file
  that already satisfies an absence test. The verify now carries five clauses, three positive, one of
  which (`INV-31` present in `harness-init/SKILL.md`) fails today and can only pass if part C landed.
  The intent's "all three strings are present in these files" — true of the set, false of each file —
  is replaced with the per-file counts.
- **`SC-13` has the same blindness and I did not touch it.** It is a pure absence criterion and no
  `SC` asserts part C's positive deliverable. Changing an approved criterion is the operator's.
  Raised as `Q11`.

## 5. The `close-task` sentence, and the comment nobody was fixing

`github-mirror.md:30` says `close-task` "remains, as the deliberate single-issue close". `Q8` — keep
or remove — goes up unanswered and must stay that way, so `A.12` rewrites the sentence to what is
**mechanically true while the command exists**: it closes one recorded sub-issue and writes no
station for it, so under `DEC-203` the issue's closed field stops matching its card. The words
"remains" and "for when you want exactly that" go, because both are claims `Q8` could overturn; and
if `Q8` returns "remove", the sentence is deleted with the command rather than rewritten. The gate
does **not** refuse `close-task` — `gh-sync.py` reaches `gh` through `subprocess` (`:147`), already
recorded as `D-06` — so `A.12` must not say it does.

**`gh-sync.py:850-851` was the omission.** Its comment reads "close-task writes NO station for its
OWN sub-issue: closing it is what lands it in Done through the board's own Item-closed workflow
(measured, D-03)" — the exact premise `T-09` part `A.5` deletes from the docs as measured-false. If
it is false, `close-task` under the new open rule produces issue CLOSED / card NOT at Done, the state
this feature exists to end, while the comment tells the reader it cannot happen. Added as `T-04` step
`8c`, which is where the file is already open and where step `8b` already establishes the principle.
The falsifying evidence (FEAT-34's 13 sub-issues closed and at `Review`) is **inherited from the
plan, not re-measured here**, so step `8c` opens with one cheap `gh issue view 818` read and says
what to do if it comes back the other way.

## 6. Advisory, not changed

`T-09` part `A.10` says to cite `DEC-203` "wherever the file currently cites `DEC-196`".
`github-mirror.md` contains **zero** `DEC-196` citations at `cc84b29`, so that edit is a no-op. Left
in place with a measured note beside it rather than deleted, so nobody manufactures a citation to
satisfy it.

## Open questions

`Q1`..`Q8` are unchanged and travel up as raised. New: `Q9` (no REQ covers a verifiable suite, so
`T-11`'s `traces:` is the nearest true one), `Q10` (does FEAT-40 carry the repair of the five
quarantined scripts, or a separate feature — the project's configured `unit` gate is red either way),
`Q11` (`SC-13` and part C), `Q12` (`--kind all` exceeds the 60-second `verify:` budget).
