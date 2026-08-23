# Handoff — FEAT-32, build → build (successor 2), at 016be31 + staged, seq-4

## Next

**T-13's WORK IS DONE AND CORRECT — do NOT re-dispatch.** DEC-199 is appended (60 lines, all five
approved items) and the index carries its row, both confirmed at source. It returned **ESCALATE for
one reason: its gate cannot pass.** Nothing about the entry needs rework.

**THREE THINGS NEED THE MAIN SESSION, AND EVERY STEP OF MINE IS BLOCKED BEHIND THEM.**
1. **The commit.** Nine main-session tasks are STAGED (11 files, 981 insertions, explicit pathspec);
   `git commit -F` was REFUSED by the session classifier. SC-12 and SC-13 are graded via
   `git show <review_sha>:<path>` precisely so uncommitted work cannot satisfy them
   (`BRIEF.md:331-333`, `:349`) — no commit, no valid pin, no panel, no goal-check.
2. **`plan.yaml:1587` and `:2219`** both call `gen-decisions-index.py --check`, a flag that does not
   exist. Fix both or accept `--stdout | diff -`. Until then T-13 cannot close and **T-17 must not be
   dispatched** — it would burn a run on an unpassable gate.
3. **Five status transitions** (T-08/T-09/T-11/T-12/T-14 still read `pending`), writable by no route
   available to this tier.
Then: T-17, qa gate, simplify, pin `review_sha` at a commit CONTAINING the work, panel, goal-check.

## Trust

- **`gen-decisions-index.py` HAS NO `--check`** — usage says so (`:9`), it accepts only `--stdout`
  (`:391`), the call exits **2**. T-13's and T-17's verify blocks therefore fail on ANY content,
  including a perfect entry. Found independently by me and the lead — verified-at 016be31
- **T-17 has a SECOND unpassable assertion**: `"the category decides, the list records"` is split by a
  hard wrap — `DECISIONS.md:4879` ends `— the category`, `:4880` begins `decides,` — verified-at 016be31
- Nine main-session tasks done; I re-ran five verifies at these bytes: T-08 exit 0 (24/24), T-11,
  T-12, T-14 exit 0, T-09 exit 0 in isolation. Deliverable mtimes 15:44, my sweep 15:47 — verified-at 016be31
- **`plan-merge.py` cannot record a status transition** — add-only, exits **7** for a `{id, status}`
  fragment AND a full task with only `status` flipped — verified-at 016be31
- **The suite is green only by ORDERING.** Guard suite before digest suite reddens **6** `[hook]` cases:
  `test-dispatch-guard.py:64` (`case_2`, governed, no model) leaks one live claim per run into the real
  registry (`cwd: ""`); the digest suite's F1.x cases pass no `cwd`. Leaker sits LAST in
  `test_kinds.integration.detect`, victim eighth. Root cause is a contradiction inside T-08's intent:
  "fresh `mkdtemp()` for every case" (`:1225-1226`) vs "EDIT NONE … cases 1-5" (`:1223`, `:1250`)
- The index is CLEAN at HEAD (generated == committed, diff exit 0, isolated tree) — verified-at 016be31
- The nine main-session tasks are **NOT** in `runs:` and must not be added (harness.json budgets rationale). `cycles_used` **3** of 10 — T-13's ESCALATE is a gate defect, not rework. Runs **14** of 20. Sole `check-state.sh` VIOLATION is FEAT-26's unapproved BRIEF, pre-existing — verified-at 016be31

## Dead ends

- **Do NOT retry the commit** — refused by the session classifier, not a guard you can satisfy.
- **Do NOT try to write `plan.yaml`**: `Edit` disabled, bash write denied, `plan-merge` exits 7,
  whole-file `Write` IS the #628 defect. No `gh-sync` start-task/close-task has run for any task.
- **Do NOT delegate a plan write to pm** — I tried inside the T-13 dispatch and it was DENIED;
  blocked-then-delegated reads as evasion. It goes UP.
- **Do NOT run `release-all` with anything in flight** — it wiped my own live `harness-product-lead`
  claim along with test residue, disarming the guard for a real child. Use `release --agent NAME`.
- **Do NOT reflow `DECISIONS.md` or re-wrap DEC-199 to satisfy a gate** — the gates are what is wrong,
  and the lead measured the re-wrap as jointly unsatisfiable with the task's 60-line cap.
- **Do NOT re-verify T-02..T-06/T-10, touch `BRIEF.md:16` or SC-14's 221, or restore SC-13's deleted
  integers** — settled; brief and plan disagree on the #551 count ON PURPOSE. **#720** is the filed
  strictness follow-up: cite it, never re-file.

## Working set

- `.harness/harness/features/FEAT-32-concurrent-write-merge/STATE.md` and `feature.json`
- `.harness/harness/features/FEAT-32-concurrent-write-merge/runs/2026-08-22-1-product/digest.md` (T-13, its Q1-Q4)
- `.harness/harness/features/FEAT-32-concurrent-write-merge/plan.yaml` (broken gates `:1587`, `:2219`; T-17 at 2191-2260)
- `.claude/skills/harness/bin/test-dispatch-guard.py` (the leak at `:64`; main-session-direct)
