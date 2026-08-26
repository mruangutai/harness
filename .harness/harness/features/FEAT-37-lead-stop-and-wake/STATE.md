# STATE

## Current

- feature: FEAT-37-lead-stop-and-wake
- run: .harness/harness/features/FEAT-37-lead-stop-and-wake/runs/2026-08-24-03-product/digest.md
- squad: none — plan phase at its seam; two BRIEF edits still UNAPPLIED
- status: awaiting-user

**MISSION: debug (DEC-139). DIAGNOSIS COMPLETE. `source_issues` = [811, 831], split ruling PENDING.**

**THE CAUSE IS MEASURED — and it is #831's missing rule, NOT the hook.** Specimen
`agent-a8f1c68d9a0d69f25` (`harness-product-lead`, "FEAT-34 emergent SC judgment") carries the loop
signature with **ZERO** `returned with children in flight`. That lead never attempted to stop, so the
#551 hook was never in that loop. #831's own stated cause was an INFERENCE; the absence was measured,
the causation was not. Two compounding causes:
1. No end-your-turn rule in the five lead-preloaded files — necessary and sufficient.
2. The `Agent` tool's result text ("continue other work... in the meantime"), which the transcript
   literally obeys. **PLATFORM-SUPPLIED** — absent from `.claude/`, `.harness/`, `docs/` — so the
   harness cannot edit it and the rule must EXPLICITLY OVERRIDE it.

**THE ONCE-ONLY BOUND IS SETTLED: "at most once per CONSECUTIVE STOP SEQUENCE; it re-fires on each
wake while a child is still live."** I re-verified the decisive pair myself in
`agent-a89be3fd837d1b779` (an orchestrator): line 178 names TWO children (eng-lead
`22:59:07.135172`, product-lead `22:59:28.731235`); line 392 names ONE — the SAME eng-lead claim.
Different child sets prove 392 is a distinct event, not replayed context. (`grep -c` gives 19
matching LINES; the reported 9 is distinct EVENTS — consistent, a line can carry replayed context.)
Corroborated first-hand on me: refused, second stop SHIPPED; woken, refused again next sequence.

**CONSEQUENCE FOR THE FIX — the reason this was blocking.** After the fix every dispatch's first stop
meets a live child and IS refused. So the fix MUST carry an **INOCULATION**, not merely an
end-your-turn sentence: the refusal is EXPECTED and the correct response is to stop again, never "you
may not return". `.claude/skills/harness/SKILL.md:50` already does this for the orchestrator and it
demonstrably works — I was refused three times today and did not loop.

**DEC-199 IS CONTRADICTED AS WRITTEN.** `DECISIONS.md` ~:6698-6705: "so a stop refusal fires at most
once." Must be corrected whatever the split ruling is (never falsify the record); amend-or-STRIKE
(DEC-188) is the operator's call, documentor's execution.

**MY SPLIT RECOMMENDATION (REVERSAL, awaiting the operator): SPLIT #811 BACK OUT.** My earlier "do not
split" rested on the hook being causal; measurement overturned that. With the inoculation, #831 ships
safely and is independently verifiable, which was my own stated criterion. **NO RULING HAS BEEN
GIVEN — no approval or consent exists.** pm is instructed to plan the #831 core as the spine and put
any #811 hook work in a separately STRIKE-ABLE block with its own D-NN.

**LANE — two independent sources, never conflate (verified at `9165162`):**
- `.claude/skills/harness-team/SKILL.md` -> **NOBODY**. The GUARD forces main-session-direct.
- `validate-digest.py` / `test-validate-digest.py` -> **harness-backend-dev harness-dev-ops**. The
  guard PERMITS a squad; only **DEC-174's carve-out** (`DECISIONS.md:4709`, am.4 `:4854-4877`) forbids
  it. `check-plan-routes.py` will print DEVIATION; the D-NN must cite the POLICY, never a NOBODY
  resolve.
- `.harness/harness/docs/DECISIONS.md` -> `harness-documentor` (team).

**Unchanged:** DEC-201 is orchestrator-scoped, so extending it to leads is a decision change; #610 and
#552 closed, `SendMessage` NOT reintroduced; #804's four exact-literal greps are defeated by a reword;
any hook change must PRESERVE the false-reporting catch (`:903-907`, occurrence 7).

**cycles_used stays 0.** The pm re-plan is triggered by an operator amendment and an overturned
premise, not by a FAIL, an unmet SC, or a send-back — DEC-157's three rework categories. Counting it
would penalise the feature for a scope change, the exact failure DEC-157 names. Flagged, not silent.

## Open Questions

- Q1 (BLOCKING): split ruling on #811 — recommendation above.
- Q2: DEC-199 amend or STRIKE (DEC-188)?
- Q3: `notes/root-cause-*.md` is in no member's domain, so debug reports fall back to receipt paths.
- Q4: engineer DIGESTs carry no `files_touched`, so a member that wrote a receipt reported no files;
  the lead reconstructs it by hand. Schema gap or intended?
- Q5: single-flight is keyed per checkout; this session's cwd is the FEAT-34 worktree, so several
  orchestrators' children share one registry.
