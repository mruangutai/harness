# Plan-panel review — scope reader — BUG-1507 cycle 0

**BLUF: traceability is clean (no orphan REQ/SC, `depends_on` is topological, no `verify:` clobbered
by a predecessor) — but two of the five `verify:` blocks are the exact fail-open shape this panel was
told to hunt: they check that a phrase exists, not that it binds to the thing the requirement needs
it bound to. Both have an `inspection` SC as backstop, so nothing ships silently wrong, but both let
their own task's automated gate go green on a wrong edit.** No re-raise of the seven landed cycle-1
repairs.

## Traceability (clean)

REQ-01..06 each traced by >=1 task (T-01→REQ-01; T-02→REQ-01,04; T-03→REQ-02; T-04→REQ-03,06;
T-05→REQ-05); no task cites a non-existent REQ. Every SC maps to a discharging task or an explicit,
disclosed non-task grading path (SC-01/SC-05, actor named, BRIEF:71-95). `depends_on` is topological:
only `T-05: [T-01, T-02]` (plan.yaml T-05), and that edge is deliberate — T-05 is the witness over the
files T-01/T-02 fix. No task's `verify:` asserts something a later task changes out from under it.

## Finding A — T-02's `verify:` doesn't bind the tool name to the literal it requires

`plan.yaml:113` checks `'set-feature-station --station building' in t` (whitespace-collapsed) with
no requirement that `plan-merge.py` — or any correct tool — precedes it. REQ-04/SC-06 need the
Building row to name **which tool** writes the feature station; the check only proves the *argument
phrase* is present somewhere in the file. A doer who writes the Building writer-cell citing the wrong
tool (or garbles the sentence around the phrase) still gets exit 0 on this task's own gate — the
substring is the assertion's subject, not the sentence's truth. SC-06 (`verify: inspection`) is the
only thing that would catch a wrong-tool edit; T-02's automated proof does not.

## Finding B — T-03's `verify:` doesn't bind the instruction to segment 1

`plan.yaml:181` slices `SKILL.md` between `## The build phase` and `## Routing a lead` — i.e. **all
four** build-phase segments — and only checks the phrase is present *somewhere in that span*. The
intent (`plan.yaml:189`) is explicit that the addition belongs in **segment 1, "The eng segment"**
specifically, because REQ-02/SC-04 require the write to happen "when the eng segment starts
dispatching." An edit that lands the sentence in segment 2, 3 or 4 instead — or a sentence that
mentions the phrase without actually committing to the "eng segment starts dispatching" timing — still
passes this verify. Same shape as Finding A: presence, not placement or claim, is what's checked.
SC-04 (`inspection`) is the only backstop.

Neither finding is a re-raise of a landed repair (R-1..R-7 touched `BRIEF.md` prose and T-02's
`intent:` backtick-span note, not either `verify:` command's binding logic).

## Considered and not filed

- SC-01/SC-05's "performed by hand from the worktree copy" (BRIEF:73-75, 93-95): no task instructs
  the actor who executes it at the relevant moment to consult the worktree file instead of the
  loaded skill/command. Plausibly executable in practice — this same orchestration process reads
  `BRIEF.md`'s SC text as its own runbook (observed doing exactly that in this run), and `SKILL.md`
  segment 4 already shows the orchestrator obeying an in-file station-write instruction verbatim
  (worktree `SKILL.md:152`) — so I did not file this as a finding, only note it as a live assumption
  worth the operator's awareness at signature.
- T-01's 2-match / T-05's two-PASS-label greps: re-derived by hand: T-05's `MIN_OCCURRENCES=6` floor
  (plan.yaml:298) blocks the classic vacuous-empty-set pass, and T-01's pattern only matches the two
  tool-invocation shapes present in the file, so no plausible wrong edit both keeps 2 lowercase
  matches and misses the intended line. Not filed.

```yaml
findings:
  - reader: scope
    summary: "T-02 verify (plan.yaml:113) checks the phrase 'set-feature-station --station building' is present but never that plan-merge.py (or any tool) precedes it"
    severity: med
    why: "A Building-row edit that names the wrong tool, or garbles the sentence around the required phrase, still passes T-02's own automated gate; only SC-06's later human inspection would catch a wrong-tool-attributed writer, so REQ-04's actual claim is unverified at the task level."
  - reader: scope
    summary: "T-03 verify (plan.yaml:181) slices the whole four-segment build-phase block, not segment 1 alone, so it can't tell whether the instruction landed in 'the eng segment' as required"
    severity: med
    why: "An edit that adds 'plan-merge.py set-feature-station --station building' to segment 2, 3, or 4 instead of segment 1, or mentions the phrase without committing to the 'when eng segment starts dispatching' timing, still exits 0 on T-03's gate, leaving REQ-02/SC-04's timing requirement checked only by later inspection."
```
