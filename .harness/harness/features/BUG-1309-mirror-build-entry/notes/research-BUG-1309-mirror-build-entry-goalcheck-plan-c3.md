# Goal-check — the plan as it NOW stands vs the operator's stated intent — BUG-1309, cycle c3 (FINAL)

**Does this plan deliver the operator's stated intent? Yes, with residuals — none of them a defect in
what the plan BUILDS, one of them a disclosure the operator has not yet been given.** Seven of the
eight `## Settled` bullets are delivered outright, one (bullet 6) is partially delivered by two
carve-outs already on the record, none is missing. No `## Out of scope` line is crossed. All six
items the c2 grading raised are CLOSED by the c4/c5 amendments, verified against current plan text.
The fourth-exposure hunt found **two named interactions**, both real, both uncovered by any single
task's text. Authority re-read at source:
`/Users/molchairuangutai/GitHub/harness/.harness/notes/grilling-mirror-build-entry-2026-09-06.md`
(`:6-14` settled, `:20-23` out of scope). This note SUPERSEDES `…-goalcheck-plan-c0/-c1/-c2.md`.

## 1 — The eight `## Settled` bullets (enumerated from the intent artifact, `:7-14`)

| # | Bullet (short quote, intent line) | Verdict | Task(s) | Pointer |
|---|---|---|---|---|
| 1 | "`Ship` → the post-merge terminal phase … releases the worktree" (`:7`) | delivered | T-08, T-09, T-03 | `plan.yaml:1067-1074` (the new doc block), `:345-348` (ship skip keeps `gh-sync: SKIP`), T-09 `:1113-1125` |
| 2 | "`Build entry` → the signed-plan transition that starts execution and runs `gh-sync.py open`; never called Ship" (`:8`) | delivered | T-08, T-09 | `plan.yaml:1064` (trigger cell replaces the `ab4d2fdc` phrase), `:1081-1094` (SKILL.md new step 1) |
| 3 | "Build → refuses when the required local Build-entry outcome is absent; may proceed after a recorded temporary … failure" (`:9`) | delivered | T-04 | `plan.yaml:412-475`; era carve-out `:413-421` is the operator's own bullet 7, on the record |
| 4 | "Enabled sync → `opened` or `recovery-required`; local configuration/contract errors and partial remote writes block Build" (`:10`) | delivered | T-02, T-01 | D-04 `plan.yaml:71-73`, D-09 `:92-95`, T-02 `:196-227`, T-01 `:125-139` |
| 5 | "Disabled or unconfigured sync → `not-applicable` … approved no-mirror delivery mode" (`:11`) | delivered | T-02, T-01, T-05, T-06, T-07 | `plan.yaml:213-215`, `:131-133`, T-05 self-gate `:590-591`, T-07 sync-false `:922-924` |
| 6 | "`recovery-required` → main session reruns idempotent `open` before merge and refuses the merge until a normal receipt is recorded" (`:12`) | **partially delivered** | T-05, T-02, T-08 | Refusal `plan.yaml:630-632`; idempotence `:233-235`, `:260-261`. TWO carve-outs narrow it, both on the record: era corpus merge-ALLOWED (`:612-620`, forced by bullet 7 + out-of-scope iii) and gh-outage fail-open when the local branch matches no feature (`:633-644`, D-07 `:84-85`, DEC-138) |
| 7 | "Legacy already-merged enabled-sync → explicit operator-approved recovery … milestone plus parent/source issue, never historical task sub-issues" (`:13`) | delivered | T-03 | `plan.yaml:286-332` (zero sub-issues, `github.issues` left as found), D-03 `:67-69`, D-05 `:75-77` |
| 8 | "Legacy recovery while GitHub is unavailable → remains non-terminal and retains its worktree until recovery and Ship succeed" (`:14`) | delivered | T-07, T-03 | Retention on the RECORDED value `plan.yaml:925-947`, case `:1020-1030`; T-03 skip funnel `:332-337`. **How it holds for the ERA corpus is finding E2 below** |

Counts: **delivered 7 · partially delivered 1 · not delivered 0.**

## 2 — The three `## Out of scope` items (`:21-23`)

| Item | Crossed? | Ground |
|---|---|---|
| (i) Requiring sync for `github.sync: false` or unconfigured GitHub (`:21`) | **no** | `not-applicable` gates nothing (`plan.yaml:131-133`); T-05 step 1 self-gate `:590-591`, T-06 skip `:765`, T-07 `:922-924` all exit before deciding. D-09 (`:92-95`) binds only a project that set `sync: true` and left `repo` unpinned — opted in, not the fenced category (orchestrator ruling, on the record). Closest edge is finding E1 |
| (ii) Creating task-level historical mirror records after work completes (`:22`) | **no** | T-03 creates zero sub-issues (`plan.yaml:299-301`, cases `:363-380`); `recovery_command_for` exists to stop a message sending the operator to a bare `open` (`:815-826`); three refusal lines forbid the `open` token (`:453-454`, `:620`, `:790-792`) |
| (iii) Changing the user-gated merge policy (`:23`) | **no** | The merge stays the operator's act; the deny fires on the LOCAL receipt only (`plan.yaml:611-632`), never on a failed GitHub read (`:633-644`), and allows the whole era corpus (`:612-620`). The refusal it does add is bullet 6, which the operator settled |

## 3 — Did c4/c5 close what c2 raised? Six lines

- a. **D-08's corrected boundary — closed.** `D-08.choice` `plan.yaml:88` now reads "The ONE frozen set … governs the three REFUSALS … POST-MERGE RETENTION (T-07) keys on the RECORDED VALUE, not on era membership"; `because:` `:89` carries settled bullet 8 as the reason.
- b. **T-04's two message variants — closed.** `plan.yaml:463-474`: non-era keeps "the MERGE is refused until gh-sync.py open records opened" (`:464-465`); era prints "Build proceeds. … so its merge is not refused" (`:467-471`), carrying no `open` token.
- c. **T-07's INV-29 pointer paragraph and its two era cases — closed.** Corrected paragraph `plan.yaml:949-965` ("THAT PREDICTION IS FALSE, measured at source", `worktree_terminal.py:389-394`, `gh-sync.py:1799-1800`/`:1962`/`:1975`); cases `T-07 era-exempt absent build_entry is swept` `:1011-1019` and `T-07 era-exempt recovery-required keeps the worktree` `:1020-1030`, declared a PAIR, both in `verify:` `:908`.
- d. **Literal era fixture names — closed.** A FIXTURE DIRECTORY NAMES block in all four tasks: T-04 `plan.yaml:496-509`, T-05 `:678-690`, T-06 `:846-855`, T-07 `:995-1007`; each states the frozen-literal fact and names its own literals. No "the test controls the set" clause survives.
- e. **The BUG-*-named symmetry case — closed.** `T-04 BUG-named non-era absent refuses` `plan.yaml:511-517`, in T-04's `verify:` loop `:401` (second position), and T-04's `traces:` now carries REQ-01 `:385-387`.
- f. **SC-06's corpus wording — closed.** `BRIEF.md:118-127` now says retention keys on the RECORDED value and never on era membership, names both halves and both grading cases.

## 4 — Fourth amendment-introduced-exposure hunt: **two found**

**E1 (new, and the one the operator has not been told). D-09's unpinned-repo Build block × T-05's
merge deny — no task's text covers the composition.** With `github.sync: true` and `github.repo`
unpinned, D-09 (`plan.yaml:92-95`) makes `open` record NOTHING, so `build_entry` stays ABSENT. T-05's
self-gate keys on `github.sync` only (`:590-591`); step 5 then DENIES on an absent key (`:630-632`)
for **every** harness feature in that project — reachable with no `gh` at all through the `git merge
<ref>` route (`:597-598`). The deny reason names `gh-sync.py open <feature-dir>` (`:653-656`), a
command that in this exact configuration provably records nothing, so the message names a remedy
that cannot clear it. Consequence: a sync-true, repo-unpinned project has Build refused AND every
merge denied, and the only escape (`/harness-init --upgrade`) appears solely in `open`'s own skip
text (`:212`). D-09 discloses the Build half; the merge half is disclosed nowhere.

**E2 (real, non-blocking, and load-bearing for bullet 8). T-03's preserved `gh-sync: SKIP` funnel ×
T-07's era-sweep ordering.** T-07 places its new block AFTER the existing `gh-sync: SKIP` and
`gh-sync: FAILED` gates (`plan.yaml:918-921`; the operator's verified fact, intent `:27`), and T-03
keeps the literal `gh-sync: SKIP` prefix on the no-milestone ship message (`:347-348`). So for the 17
milestone-less legacy directories `BRIEF.md:160-164` names, and for any era feature whose recovery
fails while GitHub is down (T-03 `:334-337` records nothing → key ABSENT), the OLD gate retains the
worktree and returns before T-07's era sweep is ever reached. That is what actually delivers settled
bullet 8 for the era corpus — not the new receipt-named retention — and no task's text says so.
T-07's era-sweep case is built on the fixture whose faked ship prints "NO SKIP and NO FAILED line"
(`:1009`, `:1011-1012`), so the suite never observes the real composition; the era sweep is reachable in
production only for an era feature that DOES record a milestone (the FEAT-55 shape). Behaviour is
correct and safe-side in every branch; the plan's account of WHY is incomplete.

**Checked and clean:** every `verify:` is passable in the declared `depends_on` order (T-01→T-06→
{T-04,T-05,T-07}; T-02→T-03→{T-04,T-07}; all→T-09) — T-04/T-05/T-07 each import `feature_schema`
names T-06 adds and each depends on T-06; no task's `verify:` greps a case a later task writes.
Every fixture is constructible: all era fixtures use names in the frozen snapshot (c5 re-derived
membership, 75 names), all non-era fixtures use synthetic ids the snapshot cannot contain. No message
a task prints is contradicted by another task's behaviour (the c4b pass fixed the last two).

## 5 — Signature readiness

| # | Residual | For signature | The ONE clause that closes it |
|---|---|---|---|
| R1 | E1 — sync-true + repo-unpinned denies every merge, naming a remedy that cannot clear it | **blocking FOR SIGNATURE** (disclosure only; no build change) | Extend D-09's `choice:` (`plan.yaml:93`) with one sentence: the unpinned-repo state also causes T-05 to deny the merge, and the only remedy is `/harness-init --upgrade`; and name that command in T-05's deny reason for the absent-key case |
| R2 | E2 — bullet 8's era half rests on the pre-existing SKIP/FAILED gates, unstated and never exercised in composition | **non-blocking FOR SIGNATURE** | One sentence in T-07's WHY paragraph (`plan.yaml:949`) recording that the pre-existing SKIP/FAILED gates return before the era sweep, so an era feature with no milestone is retained by them |
| R3 | D-09's unpinned-repo Build block itself — bullets 4 and 5 collide on this case and the orchestrator resolved it on the operator's behalf | **non-blocking FOR SIGNATURE — a DECIDED ambiguity to sign knowingly, not a defect** | Already disclosed at `plan.yaml:94`. Overturnable at signature: the alternative is recording `not-applicable`, which makes a misconfigured mirror project an approved no-mirror one |
| R4 | The era-exemption / retention split — the three REFUSALS frozen on the era set, T-07 retention keying on the recorded VALUE | **non-blocking FOR SIGNATURE — a DECIDED ambiguity to sign knowingly, not a defect** | Already stated in D-08 `:88-89` and T-07 `:949-965`; it is what settled bullet 8 requires. Closing clause if the operator disagrees: make T-07's era gate cover `recovery-required` too — which would delete the worktree bullet 8 preserves |
| R5 | Bullet 6's merge refusal is narrowed by the era allow and the gh-outage fail-open | **non-blocking FOR SIGNATURE — accepted by design** | None owed. D-07 `:84-85`, DEC-138, SC-04 `BRIEF.md:110-112`; reversing it changes the out-of-scope merge-policy line, which is the operator's |
| R6 | The legacy corpus is not backfilled; the guarantee is forward-only | **non-blocking FOR SIGNATURE — disclosed** | Already at `BRIEF.md:157-164`, naming all 17 directories as KNOWINGLY UNRECOVERED |

## Not graded here (measured by the orchestrator, cited as given)

`check-plan-routes.py` exits 0 (3 expected DEC-174 deviations); execution modes T-01/T-02/T-03/T-09
team, T-04..T-08 main-session-direct; every REQ-01..REQ-10 traced by at least one task; `depends_on`
acyclic. `plan.yaml` and `BRIEF.md` were not written by this run; nothing was approved; HEAD was not
moved.
