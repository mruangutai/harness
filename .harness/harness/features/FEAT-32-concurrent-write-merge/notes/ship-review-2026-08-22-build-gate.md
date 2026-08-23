# FEAT-32 — where it stands, and the one thing only you can do

**Bottom line.** The concurrency machinery is built, tested and committed. Six of the eight team tasks
and four of the nine you own are done, and I re-ran every one of their verification blocks myself
rather than taking a report. **Two tasks remain and both are blocked behind one signature.** Nothing
is broken and no gate has failed. The feature is not stuck for a technical reason — it is stuck
because three sentences you signed need correcting, and an agent may not correct a sentence you signed.

**What you sign is one page:** `notes/research-FEAT-32-operator-request.md`. Three items, batched
deliberately. Two of the three have **no do-nothing option** — declining costs a signature too and
buys a worse outcome for the same price.

---

## What actually got built

One locked read-modify-write core, and four consumers now sharing a single lock dialect. The design
choice that matters: the lock file is opened `O_CREAT` and **never** `O_EXCL`, and is deliberately never
deleted — because a create-and-delete lock survives a `kill -9` and then refuses every later write,
which for a feature's plan file means no plan can be written at all, ever. Writes land through a
temp file and an atomic rename, so a concurrent reader sees the whole old file or the whole new one,
never half of either.

**Verified, not asserted.** I ran all six verification blocks at final bytes: T-02 (18/18), T-03,
T-04, T-05, T-06 (55/55), T-10. Every one exits clean.

**I also audited the tests' ability to fail**, which is the part that usually lies. Each task ships a
deliberately broken copy of itself and requires the suite to go red. I checked that each broken copy
actually *loads* — a broken copy that dies on startup produces the same exit code as a real finding —
and then counted which checks failed:

| Sabotage | Checks that failed | Reads as |
|---|---|---|
| lock disabled (core) | 2 of 18, both the kill-9 recovery case | precise |
| merge disabled (plans) | 59 of 110 | broad, as expected |
| byte-preservation disabled | 22 of 110 | targeted |
| approval-refusal disabled | 10 of 110 | targeted |
| merge disabled (observations) | 6 of 33 | targeted |
| lock disabled (expertise) | 2 of 38, one case | precise |

A sabotage that breaks everything or nothing is a broken experiment. These each break a small, named,
sensible subset — that is what real coverage looks like.

**No test was weakened.** Three assertions were deleted, all three sanctioned in writing, all three
about a lock file that under the new design is never removed — so they were either red or meaningless.
I counted the file before and after: 30 checks became **32**. Three removed, five added.

**Two success criteria are already provably met.** Every one of the four writers goes through the
shared core and none keeps a lock of its own. And the test suite did not shrink: 187 result lines
against a 179 baseline, 470 against 221, zero failures, exit clean.

**A runner that was silently dead is alive again.** Before T-10, the test runner exited with an error
having run **zero tests** — its registration check aborts everything before a single test executes. It
now runs, its internal consistency check executed for the first time in its existence and agrees, and
the test that measures all this went from 15 of 23 to **23 of 23**.

---

## The one decision that is yours

Three corrections, on one page, in `notes/research-FEAT-32-operator-request.md`:

1. **A count says "seven"; it is eight.** Two independent kinds of evidence, and the strong version of
   the claim was measured against the validator rather than argued.
2. **The new lock files would be committed to git.** One line fixes it. **No do-nothing option.**
3. **Two YAML readers disagree about what a valid plan file is.** Fails loudly, not silently. Record it
   and fix it later, outside this feature. **No do-nothing option.**

**One refinement I would add to item 1 before you sign it.** The count moved *again while I was
building*. The defect being fixed is one where a supervising agent gets forced to declare a verdict on
work it cannot see — and it fired twice more during this feature's own construction, once with the
validator actively refusing an honest "I don't know". So: **do not freeze an integer into a document
that nothing re-checks.** Sign wording like *"eight measured occurrences as of this commit, and the
mechanism fired again during this feature's own build"* rather than a bare number that will be wrong
again by next week. That is a recommendation, not a finding — the number itself is yours.

---

## What I could not do, and who must

- **The worktree is one commit behind `main`** and I cannot fix it: moving `HEAD` is refused for every
  governed agent, correctly, because it re-points files under every other agent in the tree. **This is
  yours**, and the window is open now — the tree is clean and nothing is running.
- **Five of your nine tasks remain**: T-08, T-09, T-11, T-12, T-14. T-14 was blocked and is now
  unblocked — its dependency's verification was impossible to satisfy (a one-character typo made an
  assertion unsatisfiable by construction) and that is fixed and verified.
- **Two findings land on T-08/T-09 and would otherwise cost a fix cycle.** The claim function **fails
  closed** when it cannot get the lock, which in a dispatch hook *blocks the dispatch* — while the
  signed design says that particular uncertainty should let dispatches through. And the key naming the
  *dispatching* agent was never actually confirmed; the measurement that exists confirms the
  *dispatched* one. Do not let either task assume it.

---

## Proposed backlog

Unstruck rows become issues on your acceptance; anything not listed here dies silently, so this is
everything that survived.

| ID | Item | Nature |
|---|---|---|
| B-1 | The exemption map that blocked every state write for this feature was fixed by hand for two features. Its tests prove lookups work but never that the map covers the features that exist — which is exactly why two were missing. | bug |
| B-2 | The installer template that seeds every other repository has no lock rule either, so a fix here leaves installed projects exposed. It also still carries a path pattern the multi-repo migration outdated. | bug |
| B-3 | Nothing records what re-opens an approval signature. The rule was invented twice this week and lives only in a notes file. | chore |
| B-4 | A task's instructions now teach a measurement that is false — it says two entries are missing from a list where they are already present, because the fix landed after the measurement. | chore |
| B-5 | A supervising agent cannot idle while its worker runs: the return contract has no "in progress" value, so the only permitted answers are verdicts it has not earned. Two leads and I all hit this during this feature. | bug |
| B-6 | Run directories are named by a scheme that once sorted a new run before an existing one and overwrote a completed run's record. Nothing renames them, because that would destroy the evidence. | bug |
| B-7 | A refusal branch in three concurrency tests is permitted but was never actually taken in 20 attempts each, because the timeout makes the loser wait rather than fail. The behaviour is covered elsewhere; those particular cases do not exercise it. | chore |

---

## How this briefing was assembled — no report round was spawned

I did not spend three lead spawns re-narrating files I can open. Every claim above comes from a digest
on disk or a measurement I ran myself. The digests, by path, under
`.harness/harness/features/FEAT-32-concurrent-write-merge/`:

- `runs/build-eng/digest.md` — T-02..T-05, PASS, 3 send-backs
- `runs/t06t10-eng/digest.md` — T-06, T-10, PASS, 0 send-backs
- `runs/t13-count-product/digest.md` — the occurrence count, ESCALATE
- `runs/t15-verify-product/digest.md` — the unsatisfiable assertion, PASS
- `runs/lockgap-product/digest.md` — the lock files, PASS
- `runs/yamlgap-product/digest.md` — the YAML readers, PASS
- `runs/2026-08-21-1-product/`, `runs/2026-08-21-2-product/`, `runs/2026-08-21-01-product/` — the plan phase

**One gap I will not paper over:** two recorded runs from the planning phase have no surviving digest.
A run-directory naming defect overwrote one and never created the other. Their substance survives only
in this feature's state file history. That is backlog row B-6, and it is why I am telling you rather
than presenting a complete-looking list.

**Not a goal-check.** The formal criteria review has not run — it comes after every task is done. Two
criteria are provably met and I have said which; the rest are unassessed, not passed.

**Budgets.** Rework cycles **3 of 10**, all three from one segment, and both send-backs that segment's
lead initiated closed real defects rather than cosmetics. Runs **11 of 20** — under budget, and each
one resolved something or advanced a criterion.
