# Layer-0 batch B — FEAT-29, and one decision that is not mine

**BLUF.** Three things, in priority order. **(1)** Your positive control can no longer produce 8
lines — closing #586 for T-08 moved its card to `Done`, so that line is gone and the expected set is
**7**. I measured the board directly rather than inferring it. **(2)** T-03 was never dispatched and
needs a plan amendment only you can sign. **(3)** T-07 and T-09 are unblocked and are yours; run
**T-07 first**.

## 1. The positive control is now 7 lines, not 8 — measured, not inferred

While the eng segment ran, you completed T-08 and closed **#586**. GitHub's Item-closed workflow
moved that card to `Done`. The control's T-08 line reads *"plan says done, so the card should read
Done — the board reads Backlog"*, and a card that now reads `Done` agrees with the plan, so INV-26
will print nothing for it. **The line cannot reproduce.**

Your rule was *"if any line is missing, the change is rejected — it is not to be explained away."*
Applied literally that now rejects a correct change. This is not a silent break being explained
away: the cause is a board write that happened after capture, it is identified, and I measured it.

I read every relevant card directly rather than assuming the workflow fired:

| Card | Station |
|---|---|
| parent #571 | `Building` |
| T-01 #579, T-02 #580, T-03 #581, T-04 #582 | `Backlog` |
| T-07 #585, T-09 #587 | `Backlog` |
| T-05 #583, T-06 #584, **T-08 #586** | `Done` |

**So the seven lines that CAN still reproduce** are T-01, T-02, T-03, T-04, T-07, T-09 and the
parent. My recommendation: strike the T-08 line from the expected set, cite this measurement as the
reason, and keep the rejection rule absolute over the remaining seven. Seven lines still discriminate
perfectly — a broken read yields zero. **It is your amendment and your call, not mine.**

## 2. That measurement is also the first live proof the cheap read works

I ran `factory_gh.project_item_stations('mruangutai', 3, 'Status')` once, directly:

```
total items read: 486        graphql cost: 5
```

**486 items for 5 points, against 506 for the run the old path is inside.** Every test written this
session drives a fake `gh`; nothing had exercised T-01/T-02 against the real API until this. It is
corroboration for SC-01 and SC-03, **not** a substitute for them — SC-01 is a differenced
`check-state.sh` run and that is T-07's job.

## 3. THE MIRROR IS STILL FROZEN — no `start-task`, no `close-task`, until T-07 lands

Seven of the control's lines depend on cards reading `Backlog`. `start-task` moves a card to
`Building` and `close-task` to `Done`; either silently deletes a line. **T-08's close is exactly how
the eighth was lost**, and neither procedure mentions the other.

`plan.yaml` statuses are being written on schedule — T-01, T-02, T-04 now read `done` — and only the
subcommands are held. After T-07's after-measurement is captured, run the catch-up: eight
`start-task`/`close-task` pairs, about 4 points each. The mirror is never a gate (DEC-138).

## 4. Batch B — order changed, T-07 first

| # | Task | Issue | Why this order |
|---|---|---|---|
| 1 | **T-07** | #585 | Every later card move destroys a control line. Nothing else may run first |
| 2 | **T-09** | #587 | Independent of T-07; needs T-01+T-02, both landed |
| — | ~~T-08~~ | #586 | **Done** — you ran it, out of `depends_on: [T-07]` order |

Extract the intents from `plan.yaml` the same way batch A did; they are the specification and I have
not copied them.

**A gap to weigh before you run T-07.** Amendment 2 moved T-07's `intent:` but not its `verify:`. The
intent requires the control lines to reappear verbatim; the `verify:` block still only diffs
`measurement-after.md` against `measurement-before.md`, and **both of those contain zero INV-26
lines**. So the gate that amendment 2 exists to create is enforced in prose only — it will report
`OK` whether the control reproduced or not. Same shape you caught in T-08's rule-two assertion in
amendment 3, one task over.

## 5. What the eng segment delivered, and what it did not

T-01, T-02 and T-04 landed `PASS`. I re-ran the suite myself rather than taking the report: **exit 0,
zero `^FAIL` lines, 139 `PASS` lines**. The lead reported 198/198 cases; the runner emits a
`N/N cases passed` line for only some scripts, so I can corroborate the zero-failure result but not
that total, and I am not restating it as mine.

Verified independently: `check-state.sh` and `gh-sync.py` are byte-unchanged (`git diff --stat` empty
on both, so the DEC-174 carve-out held), `board_stations` now calls `project_item_stations`
(`gh_board.py:135`), the budget message string is present (`factory_gh.py:83`), and the truncation and
null-path guards raise rather than fail open.

**Two send-backs, both on T-04**, both spent on one assertion — that an unrelated `gh` failure does
*not* produce the budget headline, the only thing pinning that the message is not matched to every
failure. It was green before the change and after it, and had never executed under a mutation until
cycle 3. `cycles_used` is now **3 of 10**.

**T-03 was never dispatched, and the lead was right not to dispatch it** — see below.

## 6. The decision I need from you: T-03

I verified the lead's premise rather than relaying it, and **it is correct and slightly worse than
reported**. `run-unit-tests.sh:40-55` walks `BIN_DIR/test-*.py` and exits **2** for any file in
neither `UNIT_SCRIPTS` nor `INTEGRATION_SCRIPTS`. T-03 creates `test-gh-cost-log.py`.
`run-unit-tests.sh` is not in T-03's `files:`.

**The drift detector runs over the UNION regardless of `--kind`** (its own comment says so). So
creating that file does not merely make T-03 unverifiable — it makes **every task's `verify:` exit 2**
until the file is registered. It would have taken the whole suite down.

Two blocking questions, both reducing to one amendment:

- **Q1** — may T-03's `files:` gain `.claude/skills/harness/bin/run-unit-tests.sh`, for the one array
  entry?
- **Q2** — `measured()` adds two `rate_limit` subprocess calls per `gh` call, and
  `test-factory-gh.py`'s recorder asserts call counts, so the existing suite breaks. The lead found
  `HARNESS_GH_COST_LOG=0` in `test-factory-gh.py` to be the only route that makes no live `gh` call —
  also outside T-03's `files:`. May it gain that file too?

Both widen a signed artifact, so neither is mine. I did not route this to pm: the amendment is two
entries in one list, you have signed three amendments today directly, and a pm round trip produces a
recommendation you would still have to sign. Say the word and I will send pm instead.

**Two smaller ones, non-blocking, for whoever amends:** T-03's intent anchors the wrap point at
`factory_gh.py:79`, which is `_first_line`; `run_gh`'s `subprocess.run` is at `:92-94` (the function
name governs, the anchor is stale). And `test-gh-sync.py` is in `INTEGRATION_SCRIPTS`, so
`--kind unit` never executes T-03's `gh-sync.py` half — that portion would be unproven by its own
`verify:`.

## 7. Residual findings, not gating

- `gh_board.py:142`'s `or {}` guard is unreachable — `project_item_stations` always returns dicts
  and has one caller. Found the honest way: a mutation reddened nothing and the member went looking
  for why instead of banking the green.
- `test-factory-gh.py` **aborts rather than reddens** under any mutant that adds one subprocess call.
  That is one root cause with two symptoms: it cost both T-04 send-backs, and it is what makes T-03
  unlandable. Worth a follow-up.
- T-04's fixtures gained four spare results so such a mutant reddens; the price is that four fixtures
  now tolerate an unexpected extra `gh` call silently. Only `ensure_labels` still catches it.

## 8. Budget and housekeeping

**The window reset while I was writing this — GraphQL reads 6 of 5,000, so 4,994 are available.** My
whole session spent 46 points in the previous window: 40 for `gh-sync open`, 1 for the issue-state
query, 5 for the live board read. `check-state.sh` still runs at **zero** cost under
`FACTORY_GH=/nonexistent/gh`, and I used it for every pre-commit gate.

**`CLAUDE.md` is uncommitted and I have not staged it.** It now carries both your working edits and
T-08's delivered rule. It is `NOBODY` in the domain map and yours by instruction, so the commit is
yours to make or to hand back to me.
