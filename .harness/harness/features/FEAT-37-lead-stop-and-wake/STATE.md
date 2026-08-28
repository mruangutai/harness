# STATE

## Current

- feature: FEAT-37-lead-stop-and-wake
- run: runs/qa-2026-08-27-03-validator/digest.md
- squad: none — review panel next
- status: Review

**ALL SIX TASKS DONE. QA GATE GREEN AT `4e652f9`.** Runs 17/20. Cycles 1/10 — three consecutive runs
with ZERO send-backs, so nothing was added. `review_sha` is pinned at `4e652f9` and stays there; no
source has changed since.

**THE EVAL QUESTION IS SETTLED, AND ON A RULING RATHER THAN ON THE CONFIG.** qa ruled
`test_matrix.ai_behavior` does not block T-02. The config still literally reads `["eval"]` and
`test_kinds.eval` is still `cmd: null`. What settles it is that NO SCRIPT READS THE MATRIX — qa reads
it, so DEC-70 governs the reading, and DEC-70 is narrowed at `4e652f9` to prompt/model/tool-integration
with markdown playbooks routed to conduct. T-02's file set is one markdown playbook.

**THE NARROWING DID NOT REACH THE SURFACES AN AGENT PRELOADS AT GATE TIME. I confirmed this myself
by grep, not on report.** `.claude/skills/harness-qa-gate/SKILL.md:40` still classifies `ai_behavior`
as "prompts, model calls, agent definitions, tool definitions" with no playbook carve-out;
`.claude/agents/harness-ai-dev.md:38,41` and `.harness/harness.json:63` are unqualified too. The
narrowing landed only in `DECISIONS.md`, `DECISIONS-INDEX.md` and `SPEC.md`. **The next qa spawn
classifying a playbook edit reads the gate skill, not DEC-70, and reproduces this whole blockage.**
Out of the documentor's domain by design, out of this feature's SCs, and pm's and the operator's to
decide. Not fixed here.

**ALL SEVEN INV-26 VIOLATIONS ARE GONE, cleared the legitimate way.** They widened to zero the moment
`gh-sync.py status <feature-dir> Review` ran, exactly as the build handoff predicted
(`check-state.sh:1522` — INV-26 widens at feature.json status `Review`). No card was moved by hand and
`check-state.sh` was not touched. The operator does not need to do anything about them.

**SC-05 HAS NO EVIDENCE FROM ANY RUN and the panel is its only remaining source.** qa correctly
declined it as not its artifact. SC-04's non-mechanical half currently rests on validator-lead's own
reading, which is not independent. Both are the panel's to settle.

**SC-08 STAYS not_met AND THIS BUILD PRODUCED FIRST-HAND EVIDENCE FOR WHY.** The stop-guard refusal I
received twice this run reads "this refusal fires ONCE" — the OUTER checkout's
`inflight_registry.py:274`. The branch's corrected text at `4e652f9` reads "at most once per
consecutive stop sequence" at `:339`. An agent inside this worktree was governed by the UNCORRECTED
outer file, which is precisely D-13's mechanism. The operator runs SC-08 after merge.

**THE 266-LINE INDEX DIFF IS THREE ROWS.** Normalising `@NNNN` anchors away leaves exactly DEC-70,
DEC-199 and DEC-201 changed; ~130 other rows moved only by line-offset drift. "Change no other entry"
was honoured. Told to the panel so no reviewer spends a cycle on it.

**SIMPLIFY REMAINS DELIBERATELY OMITTED** — 661 insertions of non-doc surface, 641 of them the one
test file whose shape is pinned by SC-03's six fixtures. The spare run is held for a FAIL.

## Open Questions

- Q1 (was: the eval's author) — CLOSED by the strike. No eval, no author.
- Q2 (was: the grader firing one rule alongside others) — MOOT. The grader is unwound.
- Q3 (the route checker validating against the wrong config) — folded into issue #910 as scope, by
  operator ruling. Not this feature's work.
- Q4: `notes/root-cause-*.md` is in no member's domain, so debug reports fall back to receipt paths.
- Q5: engineer DIGESTs carry no `files_touched`, so a member that wrote a receipt reported no files.
- Q6 (the #866 deadlock) — half closed by FEAT-42. The dispatch end is fixed; the return end is what
  this feature corrected. This feature does not close #866 and never claimed to.
- Q7: single-flight is keyed per checkout, so several orchestrators' children can share one registry.
  CONFIRMED by measurement 2026-08-27, and Q5-of-the-t09-run is an instance of it: the registry is one
  file at the OUTER root, `.harness/.inflight-claims.json`, shared by every worktree.
- Q8: a lead holds no `SendMessage`, so a finding made after dispatch cannot reach a member in
  flight. That is D-03's deliberate consequence, not a defect to fix here. Backlog.
- Q9: the `gates` block in `harness.json` — `qa_gate`, `review`, `uat`, `merge` — is read by NO
  script. Agents honour it as prose. Folded into issue #910 by operator ruling.
