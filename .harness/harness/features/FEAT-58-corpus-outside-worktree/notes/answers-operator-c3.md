# Answers — FEAT-58-corpus-outside-worktree — operator review, cycle 3

One batched review pass (DEC-176). All four blocking questions answered, no finding risk-accepted,
no overrule recorded. Q5–Q8 are filed rather than folded in.

## Q1 — F-01, the four remaining cross-feature scan sites — BRING ALL FOUR IN

`board_lifecycle.py:476`, `check-plan-routes.py:835`, `validate-feature-json.py:42`,
`check-domain.sh:1916` come into FEAT-58. None is deferred, by name or otherwise.

The reasoning is the feature's own premise. These four are the audit class, and the operator's rule
is that the audit covers the active feature and nothing more. Deferring them means that the day D-1
lands they each sweep one feature of eighty-nine and report clean — which is the measured
1-of-88 / EXIT=0 fail-open this feature exists to remove, reintroduced by omission at the moment the
feature ships. A defect the plan can see and chooses to ship is worse than one it never found.

So each of the four either narrows to the active feature or refuses when it cannot reach what it
expects, and each gets the same fail-closed treatment as the sites already in scope. Where a site
turns out to need a genuinely cross-feature answer, it uses the uniqueness index (Q2) and says so.

This grows the plan, and that is accepted. Nine tasks was never the target; the target was one task
per surface. If these four are one surface, they are one task.

## Q2 — F-02, the uniqueness index is NOT a persisted artifact — COMPUTED ON DEMAND

The DoD note said "a small index resolvable from git in one read", measured at 79 rows and 5848
bytes. It did not ask for a tracked file, and a tracked file is the wrong shape: it needs a writer on
every `feature.json` creation, it goes stale between that write and the next, and — as the panel
found — its own `--check` test then reddens for the whole team the next time anyone creates a
feature. That is a standing red gate bought to avoid recomputing 5.8 KB.

Ruling: **compute it on demand from the feature records at the corpus root. No persisted file, no
generator, no regeneration hook, no staleness test.**

The cost objection does not survive contact with when the gate actually fires: `merge-gate.py` runs
its resolution only when `merge_ref(command)` matches — a merge, not every governed write. Paying
~1.2 s on a merge is not a cost worth a staleness surface. If a future consumer needs the index on a
hot path, that consumer justifies caching then, with the invalidation rule stated.

This deletes F-08 and the D-01 half of F-06. Record the deletions with this reasoning so a later
reader does not re-propose the persisted artifact.

## Q3 — D-06, the live FEAT-02 / FEAT-03 collision — ARM B, ERA-EXEMPT THE PAIR

Do not correct the records.

`FEAT-02` and `FEAT-03-subissue-mirror` both naming `feat/harness-native-foundation` is what
actually happened — an era in which two features shared a foundation branch. It is a historical
fact, not a data error. Both features are terminal, so "correcting" one means writing a branch value
that never existed, which is inventing a record. The harness does not get to tidy its own history
into something more convenient than the truth.

Arm B also dissolves the conflict the question names: no pathspec exclusion is signed, and the
nothing-altered criterion stays whole rather than carrying a named carve-out on its first day.

Requirements on the exemption, so it does not become a habit:
- The pair is named explicitly in source — the two feature ids, not a pattern, not a date window.
- The reason is recorded: shared foundation branch, both terminal, correcting would invent a value.
- A test pins **both** halves: exactly those two produce no finding, AND a NEW duplicate claim
  produces exactly one. An exemption that also silences future collisions is worse than no check.

## Q4 — F-03, F-04, F-05, F-06 — ORDER THE BATCHED FIX, NO OVERRULES

All four are correctable spec defects. Fix them in the one batched pass; nothing here is a risk I am
accepting.

**F-06 is confirmed by measurement, not taken on the panel's word.** `merge-gate.py`'s `deny()` at
`:144-145` prints a `PreToolUse` JSON payload carrying
`"permissionDecision": "deny"`, and `grep -c "sys.exit"` over the whole file returns **0**. There is
no exit contract to assert. So the criterion asserts **the deny payload** — the JSON shape the hook
actually emits — and the plan does NOT invent a non-zero exit for a gate that has never had one.
Changing merge-gate's refusal mechanism is not in this feature's scope and would be a far larger
change than the criterion that mis-stated it.

F-03 + F-05 are one edit and F-04 + F-07 are one rule, as the panel notes; land them that way rather
than as four separate amendments.

**Also re-run the goal-check.** It graded the pre-amendment plan and was not re-run, which
`check-state.sh:551-558` will WARN on at signature. Since this batched fix moves the draft anyway,
the re-run costs nothing extra and removes a known-stale grade from the artifact I am asked to sign.

## On the two disclosures, and on SC-12

Both disclosures were the right call and neither is held against the run: the stale goal-check is
being re-run under Q4, and the `cycles_used=3` versus 8 recorded FAIL runs reading as a violation is
a harness defect in the invariant, not a defect in the record. The record stands as it happened;
the reset was ordered by the operator and is not to be hidden to satisfy a check that has no concept
of one. Filed as its own ticket.

**SC-12's split into two criteria stands** — the ruling was correct and matches the rule it cites.
Non-regression in a plain checkout and nothing-altered outside the active feature are two failure
modes that break independently, so 13 rather than 12 is right. Do not merge them back.

## Q5–Q8 — filed, not folded in

Four harness defects, filed as their own tickets. Do not fix any of them inside FEAT-58:

- `plan.yaml`'s top-level `lanes:` key unwritable by every route, with `set-lanes` as the proposed
  remedy mirroring `set-panel`. Note the live table lives in D-07 meanwhile — leave it there.
- A subagent `Write` to an arbitrary absolute path outside every governed root permitted with no
  denial. This is the most serious of the four.
- The `yield called with null data` exit-1-with-valid-digest defect, seen three times this run:
  duplicate of the already-filed ticket, added there as a recurrence rather than filed again.
- `check-state.sh:762-766` grading a cycle-budget reset as a violation because the invariant has no
  recorded form for one.

## What happens next

Apply Q1 through Q4, re-run the goal-check on the amended plan, re-run the panel on the artifact
that will actually go to signature, and present again. Expect the task count to rise from nine on
Q1's account — say by how much and why. Coverage may not regress: the assertion ledger stands at 36
of 36 and no row may be dropped to accommodate the additions.

The signature is mine and has not been given.
