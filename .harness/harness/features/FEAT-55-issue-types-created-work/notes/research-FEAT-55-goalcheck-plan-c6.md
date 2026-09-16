Does this plan deliver the operator's stated intent? — **YES.**

# Goal-check c6 (plan revision c7) — delta over c5

Unhedged. c5's single NO was BRIEF SC-06's chore leg; c7 closed it at T-03 case E, the change is
confined to T-03, and `check-plan-routes.py` still prints `0 violation(s)`. SC-10 stays `partial`
and is a pre-signature standing item, not a defect. This is a DELTA note: every other criterion
carries its c5 grade unchanged and is **not re-derived** here.

## 1. SC-06 re-graded from source — MET

BRIEF SC-06 (`BRIEF.md:124-127`): declared names for "defect, capability and chore work … for both a
task sub-issue and a parent", `verify: automated  evidence: integration`.

Content anchors, read out of the current `plan.yaml` T-03 (never by line number):

- override map — `E. FAKE_TYPES=available with harness.json github.issue_types set to` /
  `{"Bug": "Defect", "Task": "Maintenance", "parent": "Epic"}`
- per-issue assertions — `assert the bugfix sub-issue's updateIssue call carries IT_defect, the` /
  `parent's updateIssue call carries IT_epic, and the config task's and the feature` /
  `task's each carry IT_maintenance - three DECLARED, non-default type ids, one per` /
  `override key, each asserted BY TYPE ID on its own issue`
- fake declares the id — `nodes array declaring Bug, Feature, Task, Defect, Epic and Maintenance with` …
  `IT_maintenance);`
- gate literal — `for s in IT_feature IT_bug IT_task IT_defect IT_epic IT_maintenance updateIssue …`

**(a) Is it the integration evidence SC-06 declares?** Yes. T-03's only `files:` entry is
`tests/integration/test-gh-issue-types.py`, and T-04's `verify:` runs
`python3 tests/integration/test-gh-issue-types.py || exit 1` — so the assertion is exercised green on
the integration route, not merely written. All three legs land in one case: **defect** = bugfix sub-issue
→ `IT_defect`; **capability** = the parent → `IT_epic` (the `parent` key is the capability-work name
under `type_for_parent`); **chore** = config task + feature task → `IT_maintenance`. Both roles SC-06
words are covered — task sub-issue (defect, chore) and parent (capability).

**(b) Falsifiability — can case E FAIL an implementation that ignored the `Task` override?** **Yes.**
An implementation honouring `Bug` and `parent` but dropping `Task` resolves the config task and the
feature task to the default `Task` → `IT_task`, and case E's two named per-issue assertions
(`the config task's and the feature task's each carry IT_maintenance`) both fail. The assertion is by
type id, on its own issue, against a fake that declares `Maintenance → IT_maintenance` — so the
declared and default ids are distinguishable. Not true-by-construction.

*Residual, unchanged and already recorded:* T-03's `verify:` loop is a file-global `grep -qF`, so the
GATE only proves the literal `IT_maintenance` exists somewhere in the file — that is
`PF-e74a2da89380cfa94f6b1693191d759d` (`med`, `batched_to_signature_review`), not an SC-06 gap. SC-06's
evidence is T-04's green run of the test, which the gate does not substitute for.

## 2. Confinement — c7 touched T-03 `intent` and T-03 `verify`, nothing else

`git -C <worktree> diff --numstat` on `plan.yaml`: **207 insertions, 85 deletions**. c5's baseline was
`plan.yaml | 278` with deletions 85 ⇒ 193 insertions. So c7 is **+14 insertions and zero new
deletions**: no committed line was newly touched; every c7 byte lands inside the already-uncommitted
block. Fields the c7 portion touches: `tasks[T-03].intent` (case E map, case E assertions + rationale,
the `available` fake node/id list) and `tasks[T-03].verify` (one literal inserted into the required-string
loop). Corroborating content re-checks, all reproducing their c5 state verbatim:

- T-07 case D unchanged: `Do not override Task in this case` and `still carry IT_task` both present.
- T-01 a5 unchanged: `type_for_change_type("feature", {"Task": "Story"}) == "Story"`.
- `panel.findings` = 12 entries; `approval: {status: pending}`; 12 tasks, 20 decisions.
- Every `files:` list unchanged — the route check's per-task OK lines are identical to c5's.
- `Maintenance` ×7 / `IT_maintenance` ×3, and outside T-03 they occur only in T-01's a5
  (`type_for_nature("chore", {"Task": "Maintenance"})`) and a12 (`refusal_text(… "Maintenance", "Task")`).
  Those are the **unit**-layer chore assertions that existed at c6 — precisely why c5 could call SC-06
  provable in principle yet unproven on its declared `integration` evidence.

*Limit, stated honestly:* c6 was never committed, so no byte-level c6-vs-c7 diff exists. Confinement is
established by the insertion/deletion arithmetic plus anchor reproduction, not by a snapshot diff. Any
error in that reading could only be a T-01 addition, which would strengthen SC-05/SC-06 and falsify no
other grade.

## 3. Carried c5 grades — carried, not re-derived

All eleven REQs remain covered (c5 §2 roll-call, carried). SC verdicts **carried unchanged from c5**:
SC-01, SC-02, SC-03, SC-04, SC-05, SC-07, SC-08, SC-09, SC-11, SC-12 = `met`; SC-10 = `partial`. The
eleven c4 baseline findings stay closed (c5 §6, carried) and R1–R5 stay verified (c5 §7, carried). c7
touched no field any of these grades rests on, per §2. **Only SC-06 was re-derived this cycle.**

## 4. Route check

`python3 /Users/molchairuangutai/GitHub/harness/.agents/skills/harness/bin/check-plan-routes.py <FD>/plan.yaml`
(positional; the tool has no `--help`). Printed: **`0 violation(s) across 1 plan(s)`**, **exit 0**.
Matches the c5 and c4 baseline. `OK T-12: declared main-session-direct (…github-mirror.md ungranted)`
is the expected DEC-174 carve-out line, not a violation.

## 5. SC-10 — pre-signature standing item, not a defect

SC-10 is `partial`: planned and reachable (T-09 registers the `locally_run` kind, T-10 is the probe),
and under ruling R4 the explicit create opt-in is exempt from the configured-repository availability
gate, so a live pass is reachable for the operator. It stays unmet **until the operator runs the probe
and records one of the three verdicts** — BRIEF: `SC-10 stays unmet until one of the three is
recorded`, and `a locally_run kind does not run in CI`. **No fix cycle can close it and none should be
routed.** It is an item for the signature conversation.

## Read-only proof — `git -C <worktree> diff --stat` at exit

```
 .../FEAT-55-issue-types-created-work/BRIEF.md      |   8 +-
 .../observations/harness-pm.md                     |   9 +
 .../FEAT-55-issue-types-created-work/plan.yaml     | 292 +++++++++++++++------
 3 files changed, 221 insertions(+), 88 deletions(-)
```
Byte-identical to c7's exit state: `plan.yaml | 292`, `BRIEF.md | 8`. `BRIEF.md` sha256
`36a7c6ab3f284f3df75abb73fcdbd63ac3b3e604bfdd748ae46178cbe40eff5d` — unchanged since c5. `plan.yaml`
sha256 `70d5ef5ced41a194f732c9912887b6b3772b7068c5e7832ca49c8a107bbda298` (c7's value; c5's
`3e1ffeb71b9a…` graded c6). I wrote only this note. Neither file moved.

*Record-keeping note (non-blocking):* c5's summary line `208 insertions(+), 85 deletions(-)` is
inconsistent with its own per-file lines (`BRIEF.md` is 5/3, so the c5 totals were 205/88). The
per-file changed-line counts — the figures the acceptance names — match exactly. Nothing moved.

## Open questions

- **Q1 (non-blocking, carried from c5 Q2, premise re-tested):** three panel findings carry
  `awaiting_user` / `batched_to_signature_review` dispositions after being ruled. `panel:` is
  correctly untouched by c6 and c7. Who moves them — a pm transcription dispatch, or the main
  session's `approval.rulings`? Not a plan defect; a signature-time bookkeeping question.
