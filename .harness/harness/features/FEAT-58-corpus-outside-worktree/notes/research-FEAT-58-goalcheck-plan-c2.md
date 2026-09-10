# FEAT-58 — plan goal-check against the operator's stated intent (c2, amended plan)

**Does this plan deliver the operator's stated intent? Yes on the bedrock rule, on all four
"Not yet specified" questions and on every cycle-1 ruling — NO at one load-bearing surface: T-17
repairs the ONE `linked_worktrees` call site in `check-domain.sh` that cannot deny anything, so
REQ-12's "ENFORCED rather than asserted" is not delivered. Verdict FAIL; the loop back is one task
edit plus two low re-opens.**

Graded against `/Users/molchairuangutai/GitHub/harness/.harness/notes/grilling-worktree-corpus-2026-09-09.md`
(corrected text, read `:1-99`). Nothing executed; `plan.yaml` and `BRIEF.md` untouched.

## Item verdicts

**1 — HEAD-content gate. (a) PARTIAL, (b) MET: the RED case IS exercised.**
(a) Both sparsifying routes are gated: `git sparse-checkout set` is reachable only from
`cmd_create` (T-08) and `migrate-worktree-corpus.py` (T-09, driven by T-10), and each evaluates
`--is-ancestor <fix-sha> HEAD` against the checkout's OWN HEAD before any cone is applied; the
`<fix-sha>` set explicitly includes T-16, so PF-5945852660e0bd21e2b5aabb8cd48383's second limb
(false branch-creation deny) is discharged too. One hole → **G-7 (T-08, med)**: T-09 makes
`<fix-sha>` a *required argument, never a default*; T-08 only says "take it from the same required
argument or environment input the migration uses" (plan.yaml T-08 intent, the CREATION-precondition
paragraph) with **no refuse-on-absent clause and no case covering an absent input**, and today
`cmd_create` has no such argument. Same paragraph should pin resolution as *the commit at which all
six are ancestors* — an earlier one passes a partially-fixed branch, which is the fail-open the
gate exists to close (`:73-74`).
(b) Falsifiable on the non-carrying side: T-08 case (f) and T-09 case (f) each assert
created-full / left-fully-materialised **and** carry a RED PROOF (guard removed in a temp copy →
exactly that case reddens, carrying case stays green); T-10's third `verify:` command runs
T-09's refusal suite, so T-10's own verify can go red on a non-carrying worktree.

**2 — T-12 cut, SC-14 grades the frames. MET as ruled; residual is WIDER than D-05 records.**
The grilling requirement is that a whole-corpus read "be stated" (`:41-42`) — recorded output
states it (D-05, D-13; SC-14 grades two distinct frame lines per reader, per reader individually).
What catches a reader that prints no frame at all: T-13's lint (bypass) and T-07's discovery-subset
scan (API caller not on the list) — on the merits they catch *enumeration* bypass and *API-caller*
omission respectively, which is the right pair. **But both scan only tracked files under
`.claude/skills/harness/bin/`** (T-13 intent, the enumeration paragraph; T-07 reuses that same
set). D-05 claims T-13 is "the instrument aimed at exactly that bypass" without that bound.
→ **G-8 (T-13, low, advisory)**: state the `bin/` scope in D-05, or widen the enumerated set.
Not a gap against the operator: the cut and its residual were accepted at Q2.

**3 — T-17 / REQ-12. NOT MET. REQ-12 is a genuine requirement of this feature; T-17 fixes the
wrong tier.**
The requirement is genuine, not creep: the grilling Facts bullet `:75-77` rests the read-only claim
on DEC-208/DEC-218 binding, and that binding runs through `check-domain.sh`. Measured at source in
this worktree: `linked_worktrees(root)` returns `[]` from inside a worktree at **three** call
chains — `claim_worktrees` (`harness_boundary.py:273`, reached from `check-domain.sh:780`, whose
`:809 if not claim_set: return` then ALLOWS), `worktree_for_feature` (`harness_boundary.py:230`,
reached from `check-domain.sh:752`, whose `:754` then ALLOWS), and the PostToolUse sweep
(`check-domain.sh:2150`). **T-17's stated change is one edit, at `:2150` only** — the sweep T-06's
own intent calls a tier that "cannot deny after the fact". SC-15 grades only that sweep's reach.
So the plan repairs reporting and leaves the two denial tiers reaching nothing.
→ **G-9 (T-17, high)**: either widen T-17 to the root passed at `:752`/`:780` and grade a denial in
SC-15, or narrow REQ-12/SC-15 to the sweep tier and record that the write-binding tiers stay
unenforced — the latter contradicts REQ-12's own wording and the operator's Q3 reasoning.

**4 — the five deletions. MET, one substitution lands in a different module.**
Byte-parity clause (T-04) → replaced by exit status + verdict set per module (T-04 intent, and its
integration cases; SC-14 says parity is not claimed) — nothing left unverified. T-05's whole-corpus
route → replaced by one plain local read plus a plain-local fallback scan; SC-04's merge-gate
refusal (case a), the duplicate-owner denial (case d) and the read budget (case f) all still
graded, so the narrowing strengthens rather than drops. T-07's re-execution → each sweep row now
names its owning suite and asserts it exists non-empty; refusal itself is still graded once by
SC-04's suites (note: file-exists is a deletion detector, not a gutting detector). T-05's D-11
latency rider and T-06's `linked_worktrees` rider → moved, not lost. **The one to watch:** the
prose "resolve ONCE" pins deleted from T-03/T-04 are replaced by T-06 case (f), which instruments
`check-domain.sh` — so no instrument grades the call count of `check-state.sh` (21 sites) or the
four validators. That is exactly what the operator ruled at Q4 ("keep exactly one pin"), so it is
an accepted residual, not a gap; D-11's branch-deletion is what carries it.

**5 — whole-plan re-grade. MET, re-derived here, not taken from the dispatch.**
12 REQ / 15 SC in `BRIEF.md`; every one appears in some task's `traces:`; no trace names a
nonexistent id. 16 tasks, 14 decisions. `depends_on`: every edge resolves, no cycle, **no reference
to T-12 anywhere in `tasks:`/`depends_on:`** — its 4 surviving mentions are 1 historical in D-13 and
3 inside `panel:` (the cycle-1 record, correctly untouched). `check-plan-routes.py` on this plan:
**0 violations, exit 0**, 11 informational DEVIATION lines. No `verify:` asserts something a
predecessor deletes; T-17 carries `test-check-domain-worktree.py` forward after T-06 edits the same
file. Out-of-scope scan re-run after T-17: zero reflink/clonefile/archive/prune hits; `du` appears
once, as a prohibition.

**6 — known and blocked. CONFIRMED, both, still exactly as described.**
`lanes.rows` holds five rows and none for `.claude/commands/**` (issue #1596); the ruling lives in
D-14 and in T-14's `execution_reason`. The backwards DEC-174 gloss ("the harness plans this and
does not execute it") occurs **exactly once** in `plan.yaml` — `lanes.rows[2].reason` — and **zero**
times in `BRIEF.md`. Neither re-filed.

## Cycle-1 carry-over

No c1 MET has regressed, and c1's open Q1 (frame naming history while bytes came from a path) is
CLOSED by the two-frame shape now in T-03/T-04/T-05, REQ-05 and SC-14. But the dispatch's premise
that all six c1 gaps were applied is wrong on two: **G-1 (T-07, low) is still open** — `T-07`/REQ-09
still name three unclassified hook scripts; `inject-expertise.sh` and `validate-digest.py` appear
nowhere in either file — and **G-5 (T-08, low) is still open** — SC-03 / T-08 case (c) still says
"a content search" with no command and no ref named, the one measured claim without a mode
(`:96-99`). G-2, G-3, G-4, G-6 are applied and correct.

## Open question

- **Q1 (blocking, for the operator).** G-9's remedy is a routing question, not pm's: widening
  `claim_worktrees` to the owner root makes every governed write read every sibling worktree's
  registry for the first time — the same "new reach reviewable on its own terms" the Q3 ruling
  asked for, one tier deeper. Widen T-17, or accept the denial tiers as they are and narrow REQ-12?
