# Operator rulings — panel c7 escalation — BUG-1309-mirror-build-entry — 2026-09-08

**All three surviving high findings are ruled FIX, and the amended BRIEF is re-signed.** The ship is
not blocked on a decision any more; it is blocked on main-session-direct implementation (DEC-174)
plus the operator's own SC-10 UAT.

> **Correction, 2026-09-08, after pm's Q5:** this note first said `plan.yaml` carried *six*
> `approval.rulings` entries. It carries **four** (`plan.yaml:7-25`, all dated 2026-09-06). Corrected
> below; recorded here rather than silently, because a miscount in this file would later read as
> evidence that the signature moved.

## Provenance — read this before trusting the four rulings below

These were relayed **inline by the main session** in the resume dispatch that opened this
orchestrator run; there is no `notes/answers-<runid>.md` on disk for this round, and this file is
**not** that channel. The orchestrator may not author an answers file (issue #671), so this note is
an orchestrator-authored TRANSCRIPTION of a main-session relay, and it is evidence of the relay,
never a substitute for it. One ruling is independently corroborated on disk:

- `ea0bdd6b` *"docs BUG-1309 re-sign amended brief"*, authored by Mike Ruangutai, changes exactly one
  line — `BRIEF.md` `## Approval` `date: 2026-09-06` → `2026-09-08`. `BRIEF.md:172-176` now reads
  `status: approved`, `approved-by: Mike Ruangutai`, `date: 2026-09-08`.
- `plan.yaml:3-25` still reads `status: approved`, `date: '2026-09-04'`, with four
  `approval.rulings` entries. **The plan signature has NOT moved and does not yet cover the
  amendments R-1..R-3 forced.**

## The four rulings

**R-0 — the amended BRIEF is re-signed (corroborated, `ea0bdd6b`).** SC-03 and SC-07, rewritten from
an unevidenceable red-before-green sequencing clause into a present-tense DISCRIMINATION requirement,
are covered by the operator's 2026-09-08 signature. The BRIEF approval gate is GREEN.

**R-1 — PANEL-1 / F-01 is FIXED, by refusing ambiguity.** `merge-gate.py:98-109` `feature_for` returns
the first `glob.glob` match, and `glob.glob` guarantees no ordering, so two **well-formed dict records
that both legitimately carry the merge's branch** decide the merge nondeterministically — silent
bypass in one direction, misattributed deny in the other, reproduced 5/5 both ways at the pin
(`notes/review-harness-security-reviewer-c7.md`). The remedy is a **deterministic refusal on
ambiguity**: two or more valid, attributable records claiming the same branch is an unresolvable
state and must DENY with both feature ids named, never pick one.

**The bound on R-1, restated because a previous cycle got this exactly wrong.** Cycle-11's
`473d82cb` shipped a scan-wide sentinel that let an unrelated malformed record deny a merge on a
branch that owed nothing; panel c5 failed it and `894adc0f` scoped it back. R-1 **must not resurrect
that**. The standing contract, unchanged: *only a valid dict record whose `branch` matches the
current merge branch owns that merge; an unreadable, non-object or unattributable record elsewhere in
the scan can never impose a refusal.* Ambiguity means **two or more OWNERS**, never one owner plus
noise. `tests/integration/test-merge-gate.py`'s last two cases — *"unrelated non-object feature record
does not block healthy merge"* and *"no-record branch ignores unrelated malformed record"* — are the
regression fence and must stay green unmodified.

**R-2 — PANEL-2 / F-02 is FIXED, in the parser.** `merge-gate.py:44-48` `git_merge` drops every
`-`-prefixed token and then tests `args[0] != "merge"`, so ordinary value-taking Git globals shift
the check off by one and the gate SILENTLY ALLOWS: `git -C <dir> merge X`, `git -c k=v merge X`,
`git --work-tree <d> merge X`. `-C` is not exotic — `merge-gate.py`'s own `local_branch()` and this
repo's test helper both use it. The fix is a **flag-aware ordered walk that consumes each global
flag's value**, not a blanket strip.

Scope of R-2, explicitly: the shell-variable indirection case (`B=feature/x; git merge $B`) and a
fourth-level `bash -c` nest past `nested_merge`'s depth cap were reported in the same finding and are
**NOT** ruled in. A gate cannot resolve shell variables it never evaluates; both stay backlog rows.

**R-3 — PANEL-3 / F-03 is FIXED, and the signed plan is AMENDED to allow it.** The non-era branch of
`_build_entry_recovery_notice` (`gh-sync.py:1386-1389`) prints `the MERGE is refused until gh-sync.py
open records opened` unconditionally, while for the same feature in the same state
`feature_schema.recovery_command_for` returns `recover-terminal` and `merge-gate.py:152-154`'s own
DENY prints `recover-terminal`. Following the notice runs `cmd_open`, which creates real GitHub
sub-issues for finished work. The operator's ruling is the first horn of the panel's Q1: **derive the
command through `feature_schema.recovery_command_for` like every sibling site, and amend the plan
string that pins the wrong word** (T-04, then at `plan.yaml:779-791`). It is NOT accepted as a
signed-wording residue.

## What each ruling binds, and to whom

| ruling | code surface | lane | plan text it contradicted |
|---|---|---|---|
| R-1 | `merge-gate.py` `feature_for` + its caller | **main-session-direct** (`plan.yaml:47-49` lanes row, DEC-174) | T-05 step 4: "the feature whose feature.json top-level branch equals the resolved head branch" — silent on multiplicity |
| R-2 | `merge-gate.py` `merge_ref`/`git_merge` | **main-session-direct**, same row | T-05 step 2: "git followed by merge as its **first non-flag argument**" — that clause literally specified the defect |
| R-3 | `gh-sync.py` `_build_entry_recovery_notice`, non-era branch | **main-session-direct** (`plan.yaml:34-36` lanes row: "gh-sync.py start-task refusal") | T-04 intent — pinned the wrong command verbatim |
| R-1/R-2 tests | `tests/integration/test-merge-gate.py` | **main-session-direct** (`plan.yaml:73-75` lanes row — each gate's own test is inside the carve-out) | — |
| R-3 test | `tests/integration/test-gh-sync.py` | **main-session-direct**, T-04 is `execution_mode: main-session-direct` | — |

No squad may execute any of it. The harness plans this change and hands it to the operator to run.

## What was done under these rulings, and what is left

**Done (cycle 13, this run).** pm amended the signed plan in two passes —
`notes/research-BUG-1309-planamend-c13.md` and `-c13b.md`: T-04's `intent` now derives the non-era
recovery command from the classifier and pins no literal; T-05's `intent` carries the flag-aware
subcommand walk and the two-or-more-owners DENY with the attribution bound restated; T-05's `verify`
gates 19 case names and T-04's gates 6; decisions D-13/D-14/D-15 record the rulings. `approval:` is
byte-identical throughout (earliest changed line 203). The implementation is fully specified in
`notes/direct-packet-2026-09-08-panel-c7.md`.

**Left.** The code itself (main session, by hand), then qa + panel c8 + goal-check, then the three
operator acts below.

## Consequences the operator has not yet been asked about

1. **The plan signature must move.** `amend` leaves `approval:` byte-for-byte by design, so the plan
   reads `approved 2026-09-04` over text amended on 2026-09-08 until the main session runs
   `plan-merge.py sign-approval`. **Required before ship.**
2. **SC-04 under-covers the new ambiguity DENY (open question).** SC-04 enumerates deny for a
   *single* feature and pins a reason shape naming one feature and a re-run command; an ambiguity
   deny names several features and no command clears it. The behaviour is gated by T-05's `verify`,
   but it traces to no success criterion. Widen SC-04, add an SC, or disclose it in
   BRIEF `## Verification gaps` — all three are operator acts, since the BRIEF was re-signed today.
3. **No plan-panel re-run is being ordered.** The playbook re-runs the panel when a re-plan RESETS
   approval to pending; `amend` does not reset it, the amendments are the panel's OWN remedies under
   an operator ruling, and the amended code still faces qa and a scoped review panel at a new
   `review_sha`. Recorded as an orchestrator execution-time judgement, not a pm decision.
4. **SC-10 still blocks the ship** and is independent of R-1..R-3
   (`notes/uat-BUG-1309-mirror-build-entry.md`, 8 steps). It must run BEFORE the worktree is
   released, because the script points at that checkout.
5. **Cycle budget: 13 of 14 used.** One cycle remains. A failed implementation round plus a failed
   re-review would exhaust it, and exhaustion is a hard stop.
