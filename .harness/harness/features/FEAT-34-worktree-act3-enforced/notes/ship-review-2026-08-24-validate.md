# Ship review — FEAT-34 Worktree act 3, enforced

**Validate phase, at `review_sha` 513c4a4. Prepared for the operator.**

## The conclusion

**The feature works, its test suite is unusually strong, and it ships one defect that all sixteen
of its own success criteria are blind to.** Do not merge yet. Four things are yours and no squad
can do any of them.

The defect is small and the failure is loud in the worst way — it wastes your time at exactly the
moment the system is trying to help you. You hit a blocked commit. `check-state.sh` refuses and
tells you a worktree is stale. You copy the removal command it prints, run it, and get
`not a linked worktree` for a directory that is plainly sitting there. The refusal is correct. The
remedy it hands you is not.

It only bites **short-named** worktrees — one whose directory is `FEAT-33` while the landed feature
directory is `FEAT-33-some-longer-name`. That is precisely why nothing caught it.

## Why sixteen criteria and a four-reviewer panel all missed it

`worktree_terminal.py:248-251` resolves a short name to the **landed** directory name and stores
that as the record's `feature_id`, while `path` keeps the **short** worktree path.
`check-state.sh:1326-1329` builds `--id` from `feature_id`. `feature-worktree.py:56-59` joins that
id into a path literally, and its first gate at `:207-214` exits 3 because no such directory exists.

The hook does it correctly: `post-merge-sweep.sh:150` derives the id from the record's own path.
So the gate and the hook disagree — which is the exact thing decision D-02 exists to prevent — and
the hook is the one that is right.

The criteria could not see it:

- **SC-01** asserts the printed command, but on an **exact-named** fixture, where the two
  derivations produce the same string and the bug is invisible.
- **SC-05** does use a short-named fixture, but only asserts that a finding *appears*. It never
  reads the command text.

So `REQ-02` — "the refusal names the exact command that removes it" — is violated in practice while
both criteria that touch it are **met as written**. pm graded them `met`, and I want to flag that
this was the harder and better call: grading SC-01 `not_met` would have pointed the fix at the code
and left the blind spot standing. Grading it `met` is what forces a new criterion to exist. A
criterion reworded until it fails has caught nothing.

## The four decisions that are yours

**1. The code fix — two files, and they must move together.** Derive `--id` from
`os.path.basename(_r29['path'])`, as the hook already does, and add a message-content assertion to
`test-check-state.py` group (f.3). Change only the first and the defect class regresses silently
the next time someone touches it. Both files are DEC-174 enforcement layer, so this is
main-session-direct: no squad can do it.

**2. Adopt SC-17.** Drafted paste-ready in `notes/research-goal-check-2026-08-24.md`. Its clause (c)
executes the printed command and asserts the worktree is gone — something no current criterion does.
Without it, REQ-02 keeps a requirement no test can falsify.

**3. Amend SC-06. It is unsatisfiable as written, and this is forced by git, not chosen.** pm
reproduced it directly: `git merge --squash` fires `post-merge` while HEAD is still pre-squash, so
the landed `feature.json` cannot be read at that moment, and the completing commit never re-fires
the hook. REQ-07 is genuinely unmet on the squash path and **no implementation could satisfy it**.
The remedy is a criterion change plus a stated verification gap. It is never a code change.

**4. Rule on SC-08 — my dispatch's premise did not survive the artifact.** I was told SC-08 is
operator-run UAT and must stay `not_met`. It is not. `BRIEF.md:202-205` declares it
`verify: automated  evidence: integration`; `plan.yaml` names `test-hooks-install.py` as its grader
under T-13, which is done; and `grep -i uat` across BRIEF.md and plan.yaml returns exactly two hits,
both `## Verification gaps` entries and neither a criterion. **SC-08 is met.** What is genuinely
outstanding is the gap at `BRIEF.md:217-221` and `:346-352`: whether *your own clone* ever gets
`core.hooksPath` repointed — which the brief deliberately refuses to make a criterion, because a
fixture can fake it and this cannot. I held SC-08's disposition open rather than grading it either
way, because only you can say which you meant.

## The goal-check

**14 of 16 met, 1 not met, 1 concern.** Full evidence per criterion in
`runs/2026-08-24-05-product/digest.md`.

- **SC-06 — not met.** The squash path, above.
- **SC-11 — concern, found this run and graded `pass` by the panel.** Its first half — "records each
  feature's terminal status, asserted per feature" — has **no assertion at all**. The fixture lands
  both features already `Done`, so the status write is unobservable. The milestone half is properly
  asserted.
- The other fourteen are met, several with genuine red proofs. SC-09 was verified by parsing each
  of the sixteen agents' `skills:` blocks individually rather than by a global grep.

## Where the quality actually is

Worth saying plainly, because the defect above is the loud part. The panel's code reviewer called
the suite behind this feature unusually strong, and the evidence supports it: SC-14's red proof
demonstrates that a shim pointing at a nonexistent target passes every other criterion and leaves
the worktree standing; SC-16 asserts six separate clauses; SC-15 tests three failure branches each
with its own red proof. The security reviewer checked five surfaces and found nothing exploitable.
The UI reviewer scoped itself out on measurement rather than assumption.

## Disclosure

**No report round was spawned.** This is assembled by reading run digests from disk directly.
Sources: `runs/2026-08-24-03-eng/digest.md` (simplify), `runs/2026-08-24-04-validator/digest.md`
(panel), `runs/2026-08-24-05-product/digest.md` (goal-check), plus the nine earlier plan- and
build-phase digests under `runs/`.

**Two recorded runs have no digest on disk** — `2026-08-23-1-product` and `brief-fix-1-product`,
both recorded PASS, both plan-phase. Their run directories do not exist. This document's account of
the earliest planning therefore rests on `BRIEF.md` and `plan.yaml` themselves, not on a digest.

**Three claims that did not survive re-derivation this phase, recorded rather than smoothed:**
Q6's premise reached me inverted (the code and tests are correct; `plan.yaml:499-500` is the wrong
artifact). The validator lead retracted its own "stale-citation class falsified" claim after its
pattern proved unable to match two-thirds of the citations. And the product lead's SC-09
corroboration was a text grep that reported 16/16 where a proper per-agent parse finds 15 — it said
so itself rather than letting the number stand.

**The 15.6s suite baseline is dead.** The integration suite measures **235-236s**, reproduced twice
as confirmed sole runner. The earlier "concurrent machine load" explanation is falsified, and
nobody has attributed the 15x gap to a cause. Do not cite either number as this suite's cost.

## Proposed backlog

Anything not listed here dies silently, so everything that survived collation is listed. Strike any
row by ID.

| ID | Nature | What |
|---|---|---|
| B-1 | chore | `test-post-merge-sweep.py`'s module docstring omits `case_linked_worktree_main_checkout` entirely — the only red proof for the FEAT-35 wrong-copy defect. Corrected wording is paste-ready in the simplify receipt |
| B-2 | chore | Stale line citations: 3 of 12 checked are wrong, including `check-state.sh:1209` citing INV-26 at `:1203` when it is at `:1363`. INV-29's insertion shifted them |
| B-3 | enhancement | INV-30 budgets 15s+60s of timeout on a call measured at 0.475s — 75s worst case on a pre-commit gate whose common path costs 0.78s — and repeats a `gh auth` round trip INV-26 already makes at `:1397`. Two constants |
| B-4 | chore | The segment-resolution helper is duplicated at `worktree_terminal.py:107-129` and `post-merge-sweep.sh:100-118`. De-duplicating widens a public surface D-10 pinned, so it needs a decision, not a refactor |
| B-5 | bug | T-10's `verify:` cannot go red: the agent loop discards its result via `|| true`, and the rest greps 3 skill files — not the 16 agents SC-09 quantifies over — then pipes to `wc -l`, so it always exits 0 |
| B-6 | chore | `BRIEF.md:246` and `:359` still read "NOT YET RE-SIGNED" against `:449` recording all three signed. The cause is structural — the banner is pasted from pm's draft block and is false the instant you sign — so fix the convention, not the two lines |
| B-7 | bug | SC-11's first half has no assertion; the fixture lands both features already `Done`, making the status write unobservable. Widen the fixture or narrow the criterion |
| B-8 | enhancement | SC-09 is met 16/16, but `harness-orchestrator` is covered by a different skill with different wording than the other fifteen — and it is the tier most likely to be asked to remove a worktree |
| B-9 | chore | Integration suite runs 235-236s against a documented 15.6s baseline, sole-runner reproduced twice. Cause unattributed |
| B-10 | bug | Leads hold `Agent` but no way to message an in-flight member, so continuing one costs a duplicate spawn. Two leads hit this independently; one burned ~74,000 tokens on unusable output |
| B-11 | bug | The orchestrator has no `Edit` tool, so D-04's prescribed route for a task status change does not exist as written |
| B-12 | bug | `feature-worktree.py remove` exits 5 DIFFERS when the default branch is ahead |
| B-13 | chore | `plan.yaml:499-500` — T-04 case (f)'s prose describes a shape the code does not have. The code is correct; the plan text is wrong |
| B-14 | chore | Two runs are recorded in `feature.json` with no digest directory on disk |
| B-15 | chore | At distillation, drop `harness-backend-dev` observations line 5 — it records a conclusion D-10 falsified, and left standing it teaches a falsehood into permanent Expertise |

## Budget and process

**Runs 16 of 20. Cycles 6 of 10.** Both inside budget, and no crossing to report. No cycle was
charged this phase: a cycle is rework routed back to the lead whose member produced it, and nothing
here was produced by a squad — the defect is in hand-written, main-session-direct files.

**I did not commit and did not open a PR.** Both are yours, by your instruction. The working tree
carries only the `review_sha` pin write and your log append; nothing under `.claude/` was modified
by any agent this phase, so the pin the panel and the goal-check both graded is intact.
