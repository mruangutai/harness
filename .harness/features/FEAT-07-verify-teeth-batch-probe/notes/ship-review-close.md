# FEAT-07 — Verify teeth, batched signature, probed environment

**Recommendation: ship.** Ten of ten tasks delivered, the blocking QA gate passes, and 17 of 18
success criteria are met with the 18th deliberately carved out. Two things need your eye before you
decide, and both are below in full: the cost overrun, and one criterion nobody has formally
re-graded.

---

## What changed, in outcome terms

Before this feature, an engineer agent could return "everything passed" without ever running the
check its own plan declared, and nothing would notice. Three specific lies were accepted by the
validator: a dev reporting its test suite FAILED alongside a PASS verdict; a QA agent reporting the
test-matrix gate FALSE alongside a PASS verdict; and a dev-ops agent declining to report at all.
All three are now rejected.

The feature also added a `task` field, so a return has to name which planned task it is reporting
on — or say plainly that it carries none. That turns the audit from "did you answer?" into a
string comparison between two durable artifacts.

Two process rules shipped alongside it: change requests at a signature gate are now collected in one
review pass and dispatched as a single fix, and a bounded question about how the environment
actually resolves something must be measured before the answer is relayed to you.

**What it does not buy, stated plainly:** an agent can still fabricate the output it pastes into its
receipt. The honest claim is that skipping a check now leaves evidence in a file that QA, the code
reviewer and you already open — not that skipping is impossible.

---

## The three squads

**Product** ran nine runs and found this feature's own defect class inside the feature three times,
each time by running a command rather than reading code. Its sharpest catch: a decision entry
shipped at 32 words against a 30-word cap that is enforced only by a unit test no task's `verify:`
invokes and that the file's own header does not state — a gate authored and then run by nobody,
one task away from the fix for exactly that.

**Validation** ran the panel. The blocking QA gate passed; the *advisory* code review found the only
defect — a requirement stated on two surfaces where the criterion said exactly one. Its own
assessment is worth quoting: `matrix_ok: true` was matrix-correct and thin as assurance, because
nine of ten tasks were documentation changes that the test matrix maps to no test kind at all.

**Engineering executed zero build tasks.** Eight of ten were done directly in the main session under
the rule that the harness does not execute changes to its own guards, and two went to Product. Its
single architecture review, during planning, found the blocking design gap that two planning passes
had missed — and proved it with its own return, which was itself an example of the defect.

---

## Goal check — and the one thing to look at

pm graded all 18 criteria: **13 met, 1 carved out, 4 unmet.** All four have since been closed.

**The gap you should know about:** those four fixes were verified by me, using each criterion's own
declared method — inspection for the documentation surfaces, the unit suite for the fixtures — but
**pm has not formally re-graded them.** A second full 18-criterion pass costs roughly $60 on a
budget already 28% over, so I did not order one without asking. If you want the formal re-grade,
say so and it is one run.

**The carve-out is SC-12**, and it could not have been met by anyone. It requires the agent that
recorded three decisions to write a verification receipt; that agent holds no grant to write receipt
files — only the five engineering specialists do. No agent in the organisation could satisfy it as
written. The substance was captured anyway: the precondition ran before any edit, exited clean, and
absorbed no pre-existing drift.

**No user acceptance test was required** — the brief defines no UAT criterion, and the feature has
no end-user surface.

---

## Cost

| | |
|---|---|
| **Spent** | **$702.82** |
| Budget | $550 (itself raised from $120 during planning, with a measured basis) |
| Over by | $152.82 — **28%** |

Where it went: planning $242 across five runs including an architecture review you ordered; build
and validation $331; the closing distillation $129. The $550 figure was my own arithmetic and it was
short. What it missed was the validation panel and goal check finding real gaps that cost four
follow-up runs, and the close phase.

You ruled distillation was kept rather than struck, on the grounds that it buys the next feature's
starting position rather than narrating this one. That decision is on the record and `max_cost_usd`
has **not** been re-baselined to make the number look better.

---

## What a human diff read did and did not buy

The rule that the harness plans its own guard changes but does not execute them was honoured: the
riskiest file was edited directly, its tests were run explicitly, and you read the diff and ruled on
one silent-failure default. **That read did not catch everything, and neither did the panel.** You
settled a question of intent that no agent could have settled. The code reviewer caught a stale
line-number reference in the same file that a careful human reader passes over. They are
complements with disjoint blind spots — that is the honest framing, not "reviewed and cleared".

---

## Proposed backlog

Everything below survived collation and does not gate the ship. **Anything not on this list dies
silently**, so strike what you do not want rather than assuming it will resurface.

| # | Item | Nature |
|---|---|---|
| 1 | `sc_status.verdict` has no enum, so a `partial` grade would have reached this briefing unchallenged. The grade that gates a feature is itself ungated. | bug |
| 2 | `DECISIONS.md:4519` cites a line range that does not contain what it claims; the real anchor is `:378`. | bug |
| 3 | The 30-word ruling cap and 20-character floor on index rows are stated in no header and invisible to both the generator and the docs checker. | chore |
| 4 | `harness-documentor` and `harness-pm` hold no receipt-file grant, so criteria that name a receipt cannot be met by them. Three dispatches hit this. | chore |
| 5 | `bash-write-guard.sh` blocks redirects whose target is a shell variable, even into the session scratchpad. | chore |
| 6 | SPEC §8.1 never states that dev-ops `suite: fail` with a PASS verdict is *accepted* — an omitted permission a reader could infer wrongly. | chore |
| 7 | A clause-count check comparing a criterion's enumerated items against its fixture cases would catch the dominant defect class this feature exposed. | enhancement |
| 8 | Reviewer personas keep no observations log; distillation for them is digest-skim only. | enhancement |
| 9 | `validate-digest.py --help` prints a misleading "unknown persona" line. | chore |

**Known residue, deliberate, not backlog:** dev-ops reporting `suite: fail` alongside PASS is still
accepted. That is your D-03 ruling, recorded in the brief and pinned by a test that goes red if
someone later "tidies" it away.

---

## The decision

Eleven commits sit on `feat/FEAT-07-verify-teeth-batch-probe` — ten of work, one recording the flow's own artifacts. **The pull request and the merge are
yours** — nothing has been pushed or merged. Ship, fix, re-scope or stop.
