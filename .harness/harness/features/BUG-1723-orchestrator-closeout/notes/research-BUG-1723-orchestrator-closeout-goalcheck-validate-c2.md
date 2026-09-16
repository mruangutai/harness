# BUG-1723 goal-check — validate c2

## Conclusion

FAIL at pinned review SHA `972d5c054e6a1dbab811f957ff5d5186a7445f63`. SC-01 through SC-04 are met and SC-05 remains `deferred_not_yet_verifiable` exactly as approved. C1-V02 and C1-V03 are closed. C1-V01 is only partially repaired: the ledger now matches all-stations INV-43 behavior, but the feature's pinned DEC-159 addition still says a retrospective succession is only a note at a terminal station. The operator and orchestrator perspectives pass; the code-maintainer perspective remains partial because the pinned range leaves two permanent authorities defining opposite contracts.

## Authority and scope

- Reviewed the complete pinned range `1a1c1925171803db8ac7f7464560a3767fa902a8..972d5c054e6a1dbab811f957ff5d5186a7445f63`, not `HEAD`. The range changes 33 paths, including both `.harness/harness/docs/DECISIONS.md` and the executable/playbook surfaces.
- `BRIEF.md` and `plan.yaml` are approved at the pin. QA ran the scoped T-01, T-02, and T-03 commands plus the required unit and integration matrix in a detached worktree at the exact pin; all passed (`notes/review-harness-qa-c2.md:3-23,30-36`). This goal-check did not rerun tests.
- The known INV-43 reports for BUG-1723-orchestrator-closeout and BUG-285-canonical-reader are specified behavior, not regressions.
- Correcting the remaining authority would touch `.harness/harness/docs/DECISIONS.md` (and regenerate its index), but neither path is owned by approved T-03. That scope change requires operator approval; `needs_approval: true`.

## Perspective grades — exactly one line per declared perspective

- **pass — orchestrator** — SC-01 and SC-04 are met: the public command closes a run in one invocation with named first-refusal behavior, and all three pinned playbook files keep `STATE.md`, handoff, and commit separate while quarantine remains wake-only.
- **pass — operator** — SC-03 is met and the ledger now accurately exposes retrospective succession at every station; SC-05 remains `deferred_not_yet_verifiable` until the approved first complete post-shipment plan mission and does not downgrade this perspective.
- **partial — code maintainer** — SC-02's focused command evidence is met, but the complete pinned range does not leave one maintainable phase-seam contract: `.harness/harness/docs/DECISIONS.md:3815-3818` says terminal retrospectives are notes while the ledger and `check-state.py` say they are violations.

## Success-criterion status

- **SC-01 — met (automated).** `972d5c05:tests/unit/test-feature-record.py#CloseRunTest` covers successful close-out, paired task/station and judgement, exact `n_a`, validation refusals, and the single spend-bearing line. QA records the direct T-01 command passing 48 tests at the pin and cites the six-case pre-change red receipt (`notes/review-harness-qa-c2.md:17,21,30-32`).
- **SC-02 — met (automated).** The pinned refusal cases require nonzero authority codes, the first named stage, no later stage, and retained earlier writes (`972d5c05:tests/unit/test-feature-record.py#CloseRunTest`). QA records 48 direct tests passing and cites both the original fail-first receipt and the c2 judgement/public-spend reds (`notes/review-harness-qa-c2.md:18,22,30-32,38-44`).
- **SC-03 — met (automated).** `972d5c05:.claude/skills/harness/bin/check-state.py` implements INV-43 with aware-instant comparison, silence for earlier/equal chronology, CANNOT VERIFY for unreadable chronology, and violations at every station. `972d5c05:tests/integration/test-check-state-feat59.py#case_inv43_chronology`, `#case_inv43_unreadable`, and `#case_inv43_scope` cover the clauses; QA records the direct T-02 command and integration matrix passing and cites the pre-change reds (`notes/review-harness-qa-c2.md:19,23,30-36`). The contradictory decision prose is a permanent-contract finding, not a claim that the executable criterion failed.
- **SC-04 — met (inspection).** At `972d5c05`, `.claude/skills/harness/SKILL.md` under `Adjust and record — ONE command closes the run`, `.claude/skills/harness/references/build-phase.md` under `Every run in this phase closes the same way` and `The seam out of this phase`, and `.claude/skills/harness/references/ledger.md` under `Runs` present `close-run`, keep the three separate writes, and keep quarantine at wake time. QA's supplied T-03 inspection exits 0 (`notes/review-harness-qa-c2.md:32`).
- **SC-05 — deferred_not_yet_verifiable (uat).** The approved `BRIEF.md` reserves this measurement for the first complete plan mission after shipment. That mission has not occurred, so no model-call, median-context, or retrospective-succession UAT verdict is yet available.

## C1 findings re-measured

- **C1-V01 — retained, partially repaired.** The original ledger contradiction is fixed at `972d5c05:.claude/skills/harness/references/ledger.md#The seam has an order`: retrospective INV-43 is now a violation at every station, `done` included. But the feature's own pinned DEC-159 addition at `.harness/harness/docs/DECISIONS.md:3815-3818` still says the opposite: “a violation on a live feature, a note on one at a terminal station.” The c2 receipt's claim that no terminal-note wording remains in `DECISIONS.md` is therefore false at the pin. The same authority contradiction survives and remains high severity.
- **C1-V02 — closed.** `notes/receipt-main-session-fix-c2.md:5-15` records the exact judgement and public-spend refusal tests red against the pre-close-run command: one fails because argparse has no `close-run`, the other because the module has no `cmd_close_run`. QA accepts both as distinct, discriminating fail-first outcomes (`notes/review-harness-qa-c2.md:22,41`).
- **C1-V03 — closed.** `972d5c05:tests/unit/test-feature-record.py#test_spend_stage_refusal_through_close_run_names_spend_keeps_earlier_writes` invokes public `cmd_close_run`, runs every non-spend subprocess through the real stage plan, injects exit 3 only for the tuple whose argv contains `spend`, and asserts the stage name, exit code, absent success summary, retained run-end, and preceding judgement. A renamed or reordered tuple now reddens the observable assertions (`notes/review-harness-qa-c2.md:42`).

## Surviving finding

- **C1-V01 — kind: substance; severity: high; task: T-03; attribution: goalcheck / harness-pm.** The pinned decision authority says terminal retrospective succession is a note (`.harness/harness/docs/DECISIONS.md:3815-3818`), while the pinned ledger says it is a violation at every station and the executable adds every in-era INV-43 hit to `bad` (`.claude/skills/harness/references/ledger.md:52-59`; `.claude/skills/harness/bin/check-state.py:3058-3064`). **Concrete failure scenario:** a maintainer follows DEC-159 while changing or diagnosing INV-43 and restores or expects the terminal note exemption; terminal `done` data then behaves contrary to that authority and to the approved all-stations contract, either reopening a fail-open path or making the documented rule unusable. The required correction is outside T-03's approved file list, so the ownership gap is raised as an approval question rather than silently widening scope.

```yaml
VERDICT: FAIL
DIGEST:
  headline: "All applicable SCs pass, but C1-V01 survives in the pinned DEC-159 authority, leaving the code-maintainer perspective partial."
  feasibility: risky
  surface: M
  flags: [documentation-contract, scope-change]
  recommend: reframe
  tasks: 3
  decisions: 2
  needs_approval: true
  risk: high
  sc_status:
    - { id: SC-01, verdict: met, method: automated, evidence: "notes/review-harness-qa-c2.md:17,21,30-32; notes/receipt-main-session-T-01-fail-first.md" }
    - { id: SC-02, verdict: met, method: automated, evidence: "notes/review-harness-qa-c2.md:18,22,30-44; notes/receipt-main-session-fix-c2.md:5-15" }
    - { id: SC-03, verdict: met, method: automated, evidence: "notes/review-harness-qa-c2.md:19,23,30-36; notes/receipt-main-session-T-02-fail-first.md" }
    - { id: SC-04, verdict: met, method: inspection, evidence: "972d5c05:.claude/skills/harness/SKILL.md#Adjust and record; 972d5c05:.claude/skills/harness/references/build-phase.md#The seam out of this phase; 972d5c05:.claude/skills/harness/references/ledger.md#Runs" }
    - { id: SC-05, verdict: deferred_not_yet_verifiable, method: uat, evidence: "Approved BRIEF.md SC-05 and Verification gaps; first complete post-shipment plan mission has not occurred" }
  open_questions:
    - { id: Q1, question: "Approve widening T-03 to correct the BUG-1723 clause in DECISIONS.md and regenerate DECISIONS-INDEX.md, since neither path is in the approved task file list?", blocking: true }
  files_touched:
    - /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-1723-orchestrator-closeout/.harness/harness/features/BUG-1723-orchestrator-closeout/notes/research-BUG-1723-orchestrator-closeout-goalcheck-validate-c2.md
  expertise_update: []
artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-1723-orchestrator-closeout/.harness/harness/features/BUG-1723-orchestrator-closeout/notes/research-BUG-1723-orchestrator-closeout-goalcheck-validate-c2.md
```
