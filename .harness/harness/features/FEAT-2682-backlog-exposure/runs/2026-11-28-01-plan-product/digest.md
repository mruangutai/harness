# FEAT-2682 patch intake — product run 2026-11-28-01-plan-product

**BLUF.** The patch intake is ready for signature, and both artifacts are `pending`:
- `BRIEF.md` (106 lines) has SC-01..SC-06, every patch-lane section, and the FEAT-2643 sequencing
  constraint marked BLOCKS.
- `plan.yaml` has exactly one task, T-01 (`main-session-direct`, DEC-174 carve-out with FEAT-2622
  as precedent). Its `verify:` is a literal block that includes a red-first check.
- pm reports that `plan-merge.py check` exited 0. I could not rerun it because I have no shell.

## Member
- draft · harness-pm · PASS. Wrote `BRIEF.md` and `plan.yaml`. Neither has readers, a panel or a goal-check, per the patch lane.

## Lead assessment
- **change_type is `api`, not the `enhancement` the dispatch asked for.** I checked this at the
  source: `enhancement` exists only in `gh_issue_types.DEFAULT_TYPE_BY_NATURE`, a backlog nature.
  `DEFAULT_TYPE_BY_CHANGE_TYPE` (lines 13–26) has no `enhancement` key, so `gh-sync open` would
  refuse it. The dispatch mixed up a backlog nature with a plan change_type. I adopt `api`; the
  operator can override it (Q-01).
- **`tests/unit/test-issue-types.py` is run unchanged, not moved.** It never calls the verb: grep
  shows only `type_for_nature`. SC-04 holds it to passing unchanged. That is the correct reading of
  "moves to the new form".
- **The DEC-138 and DEC-260 dispositions are both `keep`, and DEC-174 is added as `keep`.** pm's
  reasoning holds: a discounted row stays struck, so "unstruck rows become issues" is still true.
- **Sequencing guard (advisory).** The first verify lines take
  `git log -1 --grep=FEAT-2643 main` as proof that FEAT-2643 merged. If any commit already on main
  mentions FEAT-2643 (an intake or record commit), the guard passes without the merge. I cannot
  check this without a shell, so it goes to the main session as Q-04.

## Open questions (all non-blocking)
- **Q-01.** Use change_type `api` instead of `enhancement`?
- **Q-02.** A malformed item now exits 2 even when github.sync is off. Today such a run is a
  SKIP that exits 0.
- **Q-03.** Keep DEC-138 as is, or amend it to name the exposure grammar?
- **Q-04.** Run `git log --oneline --grep=FEAT-2643 main` now. If it returns any commit, tighten
  the T-01 verify's FEAT-2643 guard before signature.

```yaml
VERDICT: PASS
DIGEST:
  headline: 'FEAT-2682 patch intake is pending signature: a 106-line BRIEF (SC-01..SC-06)
    and plan.yaml with only T-01 (main-session-direct, change_type api, the build
    gated on FEAT-2643). pm reports plan-merge check exit 0. Four questions are open,
    none blocking.'
  open_questions:
  - id: Q-01
    question: The dispatch asked for change_type `enhancement`, but that value is
      not a valid change_type. It is a backlog nature (gh_issue_types.DEFAULT_TYPE_BY_NATURE),
      and DEFAULT_TYPE_BY_CHANGE_TYPE has no such key, so gh-sync open would refuse
      the plan. pm used `api`, and I adopted it after checking the table. Recommend
      keeping `api`; `cross_module` would also fit.
    blocking: false
  - id: Q-02
    question: 'The new refusal runs in main() before load_config, because load_config
      calls gh auth status. As a result, a malformed backlog item exits 2 even when
      github.sync is off; today that case is a SKIP that exits 0. Is that acceptable?
      Recommendation: yes. It is what ''refused before any GitHub call'' requires.'
    blocking: false
  - id: Q-03
    question: DEC-138 and DEC-260 are both marked `keep`, so DECISIONS.md is not edited.
      Do you want DEC-138 amended to name the nature:<exposure>:title grammar? If
      so, T-01 also takes DECISIONS.md and DECISIONS-INDEX.md.
    blocking: false
  - id: Q-04
    question: T-01's verify proves FEAT-2643 merged with `git log -1 --grep=FEAT-2643
      main`. If any commit already on main mentions FEAT-2643 (an intake or record
      commit), that guard passes without the merge. The main session should run `git
      log --oneline --grep=FEAT-2643 main` before signature and tighten the guard
      if it returns anything. I have no shell, so this is not checked.
    blocking: false
  files_touched:
  - .harness/harness/features/FEAT-2682-backlog-exposure/BRIEF.md
  - .harness/harness/features/FEAT-2682-backlog-exposure/plan.yaml
  - .harness/harness/features/FEAT-2682-backlog-exposure/observations/harness-pm.md
  - .harness/harness/features/FEAT-2682-backlog-exposure/runs/2026-11-28-01-plan-product/state.yaml
  expertise_update: []
  team: 'plan (patch lane: draft only)'
  steps_run: 1
  cycles_used: 0
  members:
  - step: draft
    persona: harness-pm
    verdict: PASS
    headline: BRIEF (106 lines, SC-01..06) and the one-task plan.yaml are both pending;
      plan-merge check exits 0.
    files_touched:
    - .harness/harness/features/FEAT-2682-backlog-exposure/BRIEF.md
    - .harness/harness/features/FEAT-2682-backlog-exposure/plan.yaml
    - .harness/harness/features/FEAT-2682-backlog-exposure/observations/harness-pm.md
  must_fix: []
  branch: feat/FEAT-2682-backlog-exposure
  escalations: []
  adequacy_notes:
  - The PASS covers the drafted artifacts only. Under the patch lane, no reader, panel
    or goal-check ran (DEC-225).
  - plan-merge check exit 0 is as reported by pm; this tier has no shell to rerun
    it.
  - 'The change_type deviation (api, not enhancement) was checked at source: gh_issue_types.py
    lines 13-26.'
  - tests/unit/test-issue-types.py is not edited because it never calls the verb.
    SC-04 requires it to pass unchanged.
  sc_status:
  - id: SC-01
    verdict: not_met
    method: automated
    evidence: 'Planned only: test-gh-backlog-issue-types.py CASE J, K1-K6, with red-first
      in the T-01 verify.'
  - id: SC-02
    verdict: not_met
    method: automated
    evidence: 'Planned only: CASE L1-L3 (refused) and N1 (an adversary item is filed).'
  - id: SC-03
    verdict: not_met
    method: automated
    evidence: 'Planned only: CASE M1-M3.'
  - id: SC-04
    verdict: not_met
    method: automated
    evidence: 'Planned only: CASE M4 and N2, the existing cases, test-gh-sync-open.py,
      and test-issue-types.py run unchanged.'
  - id: SC-05
    verdict: not_met
    method: inspection
    evidence: 'Planned only: the reviewer reads gh-sync.py at the review_sha; the
      verify greps for the import and for no literal values.'
  - id: SC-06
    verdict: not_met
    method: inspection
    evidence: 'Planned only: the reviewer reads briefing.md and harness.md at the
      review_sha.'
  needs_approval: true
  severity_max: none
  matrix_ok: none
  coverage_gaps: []
  findings: []
  readers: []
artifact: .harness/harness/features/FEAT-2682-backlog-exposure/runs/2026-11-28-01-plan-product/digest.md
```
