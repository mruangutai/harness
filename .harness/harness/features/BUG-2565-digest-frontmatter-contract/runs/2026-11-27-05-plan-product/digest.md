# BUG-2565 plan run 2026-11-27-05-plan-product — PASS, ready for signature

**BLUF:** pm applied the operator's Q-R4-1 answers in full. The plan is at panel cycle 4 with approval `pending`. No high, critical or unrated finding is still open; the highest open severity is med (PF-dc87…, a form finding).

## Steps
- answers (pm) PASS. Map: `notes/research-answers-c4-apply.md`.
  - T-01 gained three per-invocation flags: `run_a_matched`, `run_c_first_matched` and `run_c_repeat_matched`, the last being `none` only when `run_c_invocations` is 1. A receipt passes only when every flag is yes, so equal totals are no longer enough. The verify computes and prints `leak` before any other check.
  - T-02's batch targets now carry the distinct literals `probe-qa` and `probe-scout`. Each target is asserted with toStrictEqual, and the verify greps for both literals.
  - Verbs, each exit 0: apply, then set-panel, then record-panel `--cycle 4` from `runs/2026-11-27-05-plan-product/panel-c4.md`, then check. Check reported 6 tasks, 36 anchors and 0 failures. No APPROVAL-RESET was printed. BRIEF is unchanged because SC-03 and SC-11 already state the outcome.

## Lead assessment
- I checked the work against `criteria.md`, which I wrote before the return.
  - A token grep of plan.yaml found `run_c_first_matched`, `run_c_repeat_matched`, the `need = {...}` per-flag check, `probe-qa` and `probe-scout`.
  - The panel block in plan.yaml shows cycle 4 with `last_run` 2026-11-27-05-plan-product.
  - The five dispositions are recorded as resolved: PF-cbf8…, PF-25a8… and PF-3e23… by T-01, and PF-120f… and PF-5002… by T-02. All four high findings are resolved.
- The panel schema allows only `open` or `resolved` (`panel_findings.py` DISPOSITIONS). The operator's "superseded" is therefore recorded as resolution by the task that closes the superseding finding. The supersession itself is written in pm's note.
- Open after the pass: PF-dc87… (med form), PF-7436… (low proportionality, `scope: task`), PF-09df… (low), PF-6cd5… (low), and PF-d6fb…, PF-24f8… and PF-6b29… (info). None of them gates under the signature rule.
- By operator order, no reader re-read the cycle-4 T-01/T-02 text; the operator accepted it unread at signature.
- `panel-c4.md` adds no findings. The readers are recorded as `ran`, each with the reason it was not re-run.
- Every check-state footer still lists the same standing items: BRIEF is unsigned (expected), INV-29 for the FEAT-2557 worktree, and INV-37 for the Build-entry receipt. This run did not cause them.
- Prototype gate unchanged: there is no end-user surface. That is my call and can be overridden. There is no `scope: mission` proportionality finding, so I make no downgrade recommendation. 0 send-backs.
- `notes/panel-c2-set-panel.yaml` and `notes/research-panel-c3-set-panel.yaml` are throwaway files that can still be deleted before signature.

```yaml
VERDICT: PASS
artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-2565-digest-frontmatter-contract/.harness/harness/features/BUG-2565-digest-frontmatter-contract/runs/2026-11-27-05-plan-product/digest.md
DIGEST:
  headline: 'BUG-2565 plan ready for signature: Q-R4-1 is applied, panel cycle 4 is
    recorded, no high, critical or unrated finding is open, check reports 0 failures,
    and approval is pending.'
  open_questions: []
  files_touched:
  - .harness/harness/features/BUG-2565-digest-frontmatter-contract/plan.yaml
  - .harness/harness/features/BUG-2565-digest-frontmatter-contract/notes/research-answers-c4-apply.md
  - .harness/harness/features/BUG-2565-digest-frontmatter-contract/runs/2026-11-27-05-plan-product/state.yaml
  - .harness/harness/features/BUG-2565-digest-frontmatter-contract/runs/2026-11-27-05-plan-product/criteria.md
  - .harness/harness/features/BUG-2565-digest-frontmatter-contract/runs/2026-11-27-05-plan-product/panel-c4.md
  expertise_update: []
  team: plan
  steps_run: 1
  cycles_used: 0
  members:
  - step: answers
    persona: harness-pm
    verdict: PASS
    headline: T-01 now requires each Run A and Run C invocation's own matched flag
      (run_a_matched, run_c_first_matched, run_c_repeat_matched), and the leak is
      evaluated first. T-02's batch targets carry distinct literals, probe-qa and
      probe-scout, each asserted. Five findings resolved. apply, set-panel, record-panel
      --cycle 4 and check each exited 0, with 0 failures. Approval pending; BRIEF
      unchanged.
    files_touched:
    - .harness/harness/features/BUG-2565-digest-frontmatter-contract/plan.yaml
    - .harness/harness/features/BUG-2565-digest-frontmatter-contract/notes/research-answers-c4-apply.md
  must_fix: []
  branch: none
  escalations: []
  adequacy_notes:
  - I checked the work against runs/2026-11-27-05-plan-product/criteria.md, written
    before the return. A token grep of plan.yaml found run_c_first_matched, run_c_repeat_matched,
    the per-flag need check in T-01's verify, and probe-qa and probe-scout in T-02.
    The panel block shows cycle 4 and last_run 2026-11-27-05-plan-product.
  - 'The panel schema allows only the dispositions open and resolved (panel_findings.py
    DISPOSITIONS). The operator''s ''superseded'' is therefore recorded as resolved
    by the closing task: PF-cbf8dece and PF-25a87adf by T-01, via PF-3e23, and PF-120f5374
    by T-02, via PF-5002. pm''s note records the supersession.'
  - 'No reader re-read the cycle-4 T-01/T-02 text; the operator ordered this (Q-R4-1)
    and accepts the clauses unread at signature. panel-c4.md adds no findings. Its
    readers are recorded as ran, each with the reason it was not re-run in cycle 4:
    scope last ran in cycle 3, and should-not-exist, design (self-scoped out) and
    goalcheck ran in cycle 1. These reasons are also in plan.yaml''s panel.'
  - 'Open after the pass, none of them gating: PF-dc87 (med form), PF-7436 (low proportionality,
    scope task), PF-09df (low), PF-6cd5 (low), and PF-d6fb, PF-24f8 and PF-6b29 (info).'
  - 'Every check-state footer still lists the same standing items: BRIEF is unsigned
    (expected at pending), INV-29 for the FEAT-2557 worktree, and INV-37 for the Build-entry
    receipt. This run did not cause them.'
  - 'Prototype gate unchanged: there is no end-user surface. That is the lead''s call
    and can be overridden. There is no scope: mission proportionality finding, so
    no downgrade recommendation.'
  - notes/panel-c2-set-panel.yaml and notes/research-panel-c3-set-panel.yaml are throwaway
    files and can be deleted before signature.
  sc_status: []
  needs_approval: true
  severity_max: med
  matrix_ok: none
  coverage_gaps: []
  findings: []
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
