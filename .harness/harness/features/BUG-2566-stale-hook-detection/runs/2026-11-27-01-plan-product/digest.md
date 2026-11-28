# BUG-2566 plan run — team digest (2026-11-27-01-plan-product)

**BLUF:** BRIEF (10 SCs, 3 perspectives) and plan.yaml (2 main-session-direct tasks, D-01..D-04) are
ready for signature with approval `pending`. Goal-check passes all three perspectives and all five
operator constraints. Two **high** scope-reader findings were remediated at apply but are recorded
`open` (record-panel lands every finding open) and nobody re-read the fix: the operator must
mark them resolved (T-01) or overrule at signature.

## Steps
| step | persona | verdict | artifact |
|---|---|---|---|
| draft | harness-pm | PASS | BRIEF.md, plan.yaml, notes/research-stale-hook-detection.md |
| scope | harness-code-reviewer | FAIL (findings) | notes/review-harness-code-reviewer-plan-c1.md |
| should-not-exist | fable-advisor | PASS, ran | findings in panel-c1.md |
| design | harness-ui-reviewer | FAIL (findings) | notes/review-harness-ui-reviewer-plan-c1.md |
| apply | harness-pm | PASS | plan.yaml, BRIEF.md (record-panel + check exit 0) |
| goalcheck | harness-pm | PASS | notes/research-BUG-2566-stale-hook-detection-goalcheck-plan.md |

Cycles (send-backs): 0. Reader FAIL verdicts are findings fed to apply, not invalid returns.

## Assessment
- scope #2 and design #1 were one defect (schema dir hashed as one key) — fixed once in T-01.
- scope #1 (merge order): kept 2565-first as the dispatch/grilling ordering, now an explicit D-04 for
  the operator to sign; "either order builds" claim removed; precondition grep matches only the live import.
- fable #1/#2 contradict operator-settled fingerprint scope; kept in plan, surfaced as non-blocking
  signature questions. fable #3 (BLOCKED-yield carve-out) vs operator's "every governed call":
  D-02 kept, DEC-204/DEC-100 amended, carve-out surfaced for the operator.
- The 2565 interaction rests on the sibling's **unsigned** plan (not in main corpus). If 2565's re-read
  keeps digest-schema.ts or DIGEST_SCHEMA_DIR, T-01's precondition stops the build BLOCKED (D-04) — safe, but re-plan then.
- Prototype gate (host call, visual-designer not in this team): no prototype — the only user-facing
  surface is one refusal text line, verified live by UAT SC-10. Overridable either way.
- No `scope: mission` proportionality finding; no downgrade recommended.

```yaml
VERDICT: FAIL
artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-2566-stale-hook-detection/.harness/harness/features/BUG-2566-stale-hook-detection/runs/2026-11-27-01-plan-product/digest.md
DIGEST:
  headline: 'Team verdict is FAIL because two reader FAILs roll up (worst wins). The
    deliverable is done: the BUG-2566 BRIEF and 2-task plan are pending signature,
    record-panel and check pass, and the goal-check passes all perspectives. Two high
    scope findings were fixed at apply but stay recorded open and were not re-read.
    They need an operator ruling at signature, not a re-cycle.'
  team: plan
  steps_run: 6
  cycles_used: 0
  members:
  - step: draft
    persona: harness-pm
    verdict: PASS
    headline: Drafted the BRIEF (10 SCs, 3 perspectives) and a 2-task plan. Fingerprinting
      re-hashes content on every call (0.35 ms median measured). plan-merge check
      passes.
    files_touched:
    - .harness/harness/features/BUG-2566-stale-hook-detection/BRIEF.md
    - .harness/harness/features/BUG-2566-stale-hook-detection/plan.yaml
    - .harness/harness/features/BUG-2566-stale-hook-detection/notes/research-stale-hook-detection.md
    - .harness/harness/features/BUG-2566-stale-hook-detection/observations/harness-pm.md
  - step: scope
    persona: harness-code-reviewer
    verdict: FAIL
    headline: T-01 blocks on the current base and cannot name the changed schema files.
      The mission and both tasks stay. 6 findings, 2 of them high.
    files_touched: []
  - step: should-not-exist
    persona: fable-advisor
    verdict: PASS
    headline: 'The plan core is right. 3 findings: whether to keep schemas/digest,
      whether to keep the digest-schema.ts entry, and a BLOCKED-yield carve-out. No
      objection at mission scope.'
    files_touched: []
  - step: design
    persona: harness-ui-reviewer
    verdict: FAIL
    headline: 'The refusal cannot name the changed schema file. This duplicates scope
      finding #2.'
    files_touched: []
  - step: apply
    persona: harness-pm
    verdict: PASS
    headline: Added D-04 (2565 lands first), per-file schema entries, a guard against
      non-regular entries, the mtime-mutant evidence, and amendments to DEC-204 and
      DEC-100. record-panel and check exit 0.
    files_touched:
    - .harness/harness/features/BUG-2566-stale-hook-detection/BRIEF.md
    - .harness/harness/features/BUG-2566-stale-hook-detection/plan.yaml
    - .harness/harness/features/BUG-2566-stale-hook-detection/observations/harness-pm.md
  - step: goalcheck
    persona: harness-pm
    verdict: PASS
    headline: The plan delivers the operator's intent. The operator, orchestrator
      and code maintainer perspectives all pass, and all five constraints hold.
    files_touched: []
  must_fix:
  - "Operator ruling at signature on the two high scope findings recorded open (merge\
    \ order \u2192 D-04; per-file schema naming \u2192 T-01): mark resolved_by T-01\
    \ or overrule. No re-cycle needed."
  files_touched:
  - .harness/harness/features/BUG-2566-stale-hook-detection/BRIEF.md
  - .harness/harness/features/BUG-2566-stale-hook-detection/plan.yaml
  - .harness/harness/features/BUG-2566-stale-hook-detection/notes/research-stale-hook-detection.md
  - .harness/harness/features/BUG-2566-stale-hook-detection/observations/harness-pm.md
  branch: none
  open_questions:
  - id: Q-01
    question: 'Signature ruling on two high scope findings. Both were fixed in T-01
      at apply but are recorded with disposition open, and no reader re-read the fix.
      (a) Merge order: D-04 now requires BUG-2565 to land first, and the precondition
      greps only the live import. (b) The refusal must name each changed schema file:
      the fingerprint now keeps one entry per file. Recommendation: mark both resolved_by
      T-01, after checking the D-04 and T-01 text yourself.'
    blocking: true
  - id: Q-02
    question: 'fable-advisor #1 (med) asks whether to drop schemas/digest from the
      fingerprint. After 2565, the loaded hook never reads that directory. Result:
      regenerating the schemas refuses calls when nothing changed (false positive),
      while edits to .omp/agents frontmatter go undetected (false negative). The plan
      keeps the set you settled. The reader recommends dropping the directory or re-deciding,
      possibly by fingerprinting .omp/agents instead.'
    blocking: false
  - id: Q-03
    question: 'fable-advisor #2 (low) asks whether to drop the digest-schema.ts entry.
      Under D-04 that file is permanently absent, and three SC-01 cases test states
      that cannot occur. The plan keeps the set you settled. The reader recommends
      dropping the entry.'
    blocking: false
  - id: Q-04
    question: 'fable-advisor #3 (low) asks whether a stale process should still let
      a persona yield VERDICT BLOCKED, as the held-run gate does. Without that exception,
      in-flight subagents are stranded. The plan keeps D-02, which refuses every governed
      call, and amends DEC-204 and DEC-100. The reader recommends the carve-out. Choosing
      it flips D-02, SC-02''s BLOCKED-yield case and T-02.'
    blocking: false
  - id: Q-05
    question: Possible harness defect. In the plan team, plan readers return FAIL
      to carry findings, and apply consumes those findings in the same run. Worst-wins
      roll-up then forces the team VERDICT to FAIL even after a clean apply and goal-check,
      so the verdict cannot tell 'plan ready, findings applied' from 'plan failed'.
      Should a reader's FAIL be exempt from the roll-up once apply has run?
    blocking: false
  escalations: []
  expertise_update: []
  adequacy_notes:
  - The team FAIL is a roll-up of reader verdicts, not a failed deliverable. The plan
    is pending signature, and plan-merge record-panel and check both exit 0. The prose
    BLUF in digest.md was written before the validator applied the roll-up. check-domain
    then refused a rewrite, so where the prose reads as ready, the appended fenced
    block overrides it.
  - The handling of BUG-2565 rests on the sibling's unsigned plan, which is not in
    the main corpus. If 2565's re-read keeps digest-schema.ts or DIGEST_SCHEMA_DIR,
    the D-04 precondition stops T-01 as BLOCKED. That fails safe, but this plan would
    then need re-planning.
  - 'Prototype gate: the host decided this, because visual-designer is not in the
    plan team. No prototype is needed: the only user-facing surface is one line of
    refusal text, and UAT SC-10 verifies it live. The operator can override this either
    way.'
  - 'fable-advisor wrote scope: task on its three substance findings. Because the
    digest validator accepts scope only on proportionality findings, they are carried
    here as none. panel-c1.md keeps the reader''s original text, and record-panel
    drops that key for substance findings anyway.'
  - No proportionality finding at mission scope, so no downgrade is recommended.
  sc_status:
  - id: operator
    verdict: pass
    method: inspection
    evidence: 'goalcheck: SC-01/02/03/10 via T-01, SC-09 via T-02'
  - id: orchestrator
    verdict: pass
    method: inspection
    evidence: 'goalcheck: SC-04, SC-05 via T-01; D-01'
  - id: code maintainer
    verdict: pass
    method: inspection
    evidence: 'goalcheck: SC-06/07/08 via T-01'
  needs_approval: true
  severity_max: high
  matrix_ok: none
  coverage_gaps: []
  findings:
  - kind: substance
    scope: none
    severity: high
    reader: code-reviewer
    summary: T-01 cannot build before BUG-2565 despite claiming either merge order
      works.
    why: Live digest-schema.ts import on current base stops the build; grep could
      self-match on resume. Remediated at apply via D-04; recorded open.
  - kind: substance
    scope: none
    severity: high
    reader: code-reviewer
    summary: T-01 cannot name changed schema files in the refusal.
    why: Directory hashed as one key. Remediated at apply with per-file entries; recorded
      open.
  - kind: substance
    scope: none
    severity: med
    reader: code-reviewer
    summary: A non-regular schema entry can hang the OMP process and stop Main recovery.
    why: FIFO read in synchronous walk; remediated at apply.
  - kind: substance
    scope: none
    severity: med
    reader: code-reviewer
    summary: The decisions record omits the held-run yield contract changed by D-02.
    why: DEC-204 BLOCKED-yield exception overridden; remediated with DEC-204 and DEC-100
      amend rows.
  - kind: substance
    scope: none
    severity: med
    reader: code-reviewer
    summary: "The task does not schedule SC-04\u2019s timestamp-mutant evidence."
    why: Old-hook failure does not prove content vs mtime discrimination; remediated
      at apply.
  - kind: proportionality
    scope: task
    severity: low
    reader: code-reviewer
    summary: T-01 exposes unused fingerprint internals and gates on the export.
    why: Trimmed at apply; verify now asserts internals are not exported.
  - kind: substance
    scope: none
    severity: med
    reader: ui-reviewer
    summary: T-01 reports the schema directory instead of the changed, added, or removed
      schema file.
    why: 'Duplicate of code-reviewer high #2; remediated with it.'
  - kind: substance
    scope: none
    severity: med
    reader: should-not-exist
    summary: 'Drop (or re-decide with the operator) the schemas/digest directory in
      the fingerprint: after the mandated 2565-first ordering, the loaded hook never
      reads it.'
    why: Contradicts operator-settled scope; kept, surfaced as Q-02.
  - kind: substance
    scope: none
    severity: low
    reader: should-not-exist
    summary: The digest-schema.ts fingerprint entry guards a state the plan's own
      precondition makes unreachable; three SC-01 cases test it.
    why: Contradicts operator-settled scope; kept, surfaced as Q-03.
  - kind: substance
    scope: none
    severity: low
    reader: should-not-exist
    summary: D-02's removal of the BLOCKED-yield exception (unlike BUG-1898's held-run
      gate) strands every in-flight subagent the moment staleness trips, with no operator
      decision recorded.
    why: Operator constraint is every governed call; D-02 kept with DEC-204/DEC-100
      amend; surfaced as Q-04.
  readers:
  - reader: scope
    status: ran
    persona: harness-code-reviewer
    reason: none
  - reader: should-not-exist
    status: ran
    persona: fable-advisor
    reason: none
  - reader: design
    status: ran
    persona: harness-ui-reviewer
    reason: none
  - reader: goalcheck
    status: ran
    persona: harness-pm
    reason: none
```
