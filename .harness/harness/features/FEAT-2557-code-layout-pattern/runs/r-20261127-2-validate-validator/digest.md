# FEAT-2557 · validate c2 · r-20261127-2-validate-validator

**PASS. The c1 must-fix is closed, and nothing regressed.** DEC-259's Because now states that
FEAT-70's `plan-merge.py` split kept one re-export (`signed_task_hash`, loaded by path by
`check_state/ctx.py` `_load_hash_module` for INV-40), and it names that re-export as a finding.
The folded DEC-149 citation is also fixed. `must_fix` is empty and `severity_max` is low. One low
form advisory is left, and it does not gate. Reviewed at `afd20116a2d5b9ffcbd243cb61c1f282e3935318`
(prior pin `5c600680`, base `cf7b422b`).

## Panel

|Step|Persona|Verdict|Note|
|---|---|---|---|
|qa|harness-qa|PASS|`test_matrix.docs.always=[]`, so no kind is required and no receipt was written. At the pin, T-01's verify exits 0, the generator output equals the index, and the anchors check reports 0 failed. `5c600680..afd20116` touches only DECISIONS.md, DECISIONS-INDEX.md and feature records. `plan-merge.py` and `ctx.py` are byte-identical across the two pins (`notes/review-harness-qa-c2.md`)|
|code|harness-code-reviewer|PASS|The raiser measured its own c1 finding closed at source, including the frontmatter `autoloadSkills` lines for all seven agents. It raised one low form advisory (`notes/review-harness-code-reviewer-c2.md`)|
|security|harness-security-reviewer|PASS|Out of scope on a measured census: 34 paths in the full pinned diff and 14 in the c2 delta|
|ui|harness-ui-reviewer|PASS|Out of scope on the same measured census|
|goalcheck|harness-pm|PASS|All three perspectives pass. SC-01..06 are met, with SC-05 met on its letter and on accuracy. D-01→DEC-259 and all six keep rows are met (`notes/research-…-goalcheck-validate-c2.md`)|

## Assessment

- **Closure.** I read DEC-259 at `DECISIONS.md:8789-8801` myself. The Because names the
  re-export, its loader and INV-40. It says removing the re-export "means migrating that loader
  first", and it now cites the agents' frontmatter for autoload and DEC-149 only for origin. Two
  readers measured the closure independently:
  - The code-reviewer raised the c1 finding, and it withdrew the finding on execution (O-08).
  - pm, overruled in c1, re-graded SC-05 on accuracy, and it probed that no other path-loader
    targets `plan-merge.py`.
- **No regression.** SC-06 still holds: outside the feature directory, the full diff contains
  exactly the five files. The c2 delta changes only the two decision docs. The skill, LAYOUT.md
  and AGENTS.md are byte-identical to the c1 pin, so the c1 grades of SC-01..04 still stand.
  DECISIONS.md versus base is still append-only (53 additions, 0 deletions).
- **Census difference noted.** Security and ui counted 34 and 14 paths here, where c1 counted 24.
  The difference is feature records (`runs/`, `notes/`, `feature.json`); every reader that
  checked SC-06 found the non-feature set unchanged at five files.
- **Disagreement resolved: code-reviewer and pm on "with one exception".**
  - pm's reading: the exception count is true for shims. No other re-export or path-load exists.
  - The code-reviewer's reading: the phrase reads as though FEAT-70 conforms to all of Chose
    except the shim. I opened the cited site. `plan_merge/guards.py:1` reads "Destination,
    reload, schema and lock guards shared by every verb", which is a module grouped by kind.
  - Both readings are true, and they measure different things. I adopt the code-reviewer's
    advisory as `form`/low: it is a wording precision point and states no false fact about a
    shim.
  - It does not gate. The skill's Applying-it rule governs review, and DEC-259 calls the one
    deviation it names a finding, not a precedent.

## Findings, ranked

1. **form · low (code-reviewer) · T-01 · advisory.** `DECISIONS.md:8791` says "with one
   exception", which can read as FEAT-70 being an exhaustive precedent for Chose. FEAT-70 also
   introduced the kind-grouped `plan_merge/guards.py`. Suggested remedy: describe the shared
   entry/package shape without claiming an exception count. This is optional and does not
   require another cycle. If the orchestrator applies it, the change is prose only and needs the
   same index regeneration check.

## Adequacy

- Assurance comes from executed checks plus inspection. QA and the code-reviewer each ran T-01's
  verify, the generator diff and the anchors check at the pin. pm ran the generator on a
  `git archive` extract of the pin. Each reader measured the census before scoping out.
- c1's OQ-1, OQ-2 and OQ-3 are still with the operator. No reader re-raised them, and this
  digest does not carry them again.
- Under `gates.review: advisory_unless_high`, an empty `must_fix` at `severity_max: low` does not
  gate the ship.

```yaml
VERDICT: PASS
artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2557-code-layout-pattern/.harness/harness/features/FEAT-2557-code-layout-pattern/runs/r-20261127-2-validate-validator/digest.md
DIGEST:
  headline: 'FEAT-2557 passes validation at afd20116, and nothing regressed. The c1
    must-fix is closed: DEC-259 now names plan-merge.py''s signed_task_hash re-export
    for INV-40 as a finding, and the raiser confirmed this by execution. The DEC-149
    citation is also fixed. must_fix is empty, with one low form advisory on the wording
    ''with one exception''.'
  team: validate
  steps_run: 5
  cycles_used: 0
  members:
  - step: qa
    persona: harness-qa
    verdict: PASS
    headline: 'Docs-only change: no kind is required (test_matrix.docs.always=[]),
      so no receipt was written. T-01 verify exits 0, the index is in sync and anchors
      are clean. The fix touches only DECISIONS.md and DECISIONS-INDEX.md; plan-merge.py
      and ctx.py are byte-identical'
    files_touched: []
  - step: code
    persona: harness-code-reviewer
    verdict: PASS
    headline: DEC-259 now correctly identifies the INV-40 re-export and cites agent
      frontmatter for current autoload. Index and anchors pass; one non-gating wording
      advisory
    files_touched: []
  - step: security
    persona: harness-security-reviewer
    verdict: PASS
    headline: 'No security findings: 34 paths in the full pinned diff and 14 in the
      c2 delta; no new trust boundary and no weakened guard'
    files_touched: []
  - step: ui
    persona: harness-ui-reviewer
    verdict: PASS
    headline: 'Mode B out of scope: 34 paths in the pinned diff and 14 in the c2 delta,
      none of them rendered UI'
    files_touched: []
  - step: goalcheck
    persona: harness-pm
    verdict: PASS
    headline: "All three perspectives pass. SC-01..SC-06 are met, with SC-05 met on\
      \ its letter and on accuracy. D-01\u2192DEC-259 and the six keep rows are met,\
      \ and the c1 must-fix is fixed"
    files_touched: []
  must_fix: []
  files_touched:
  - .harness/harness/features/FEAT-2557-code-layout-pattern/runs/r-20261127-2-validate-validator/state.yaml
  branch: none
  open_questions: []
  escalations: []
  expertise_update: []
  adequacy_notes:
  - Closure was measured twice, independently. The code-reviewer raised the c1 finding
    and confirmed it closed by execution. pm, overruled in c1, re-graded SC-05 on
    accuracy and probed that no other path-loader targets plan-merge.py. The lead
    also read DECISIONS.md:8789-8801 at the worktree pin.
  - 'No regression: the skill, LAYOUT.md and AGENTS.md are byte-identical to 5c600680,
    so the c1 grades for SC-01..04 stand. SC-06 holds with five non-feature files.
    DECISIONS.md versus base is append-only (53 additions, 0 deletions). T-01 verify,
    the generator diff and the anchors check (25 examined, 0 failed) were re-run at
    the pin by qa and code-reviewer.'
  - 'Census difference: c1 counted 24 paths and c2 counts 34 (14 in the delta). The
    added paths are feature records only; the non-feature set is unchanged.'
  - 'The code-reviewer and pm read ''with one exception'' differently. pm''s reading
    is that the count is true for shims. The code-reviewer''s reading is that the
    phrase overstates FEAT-70 as an exhaustive precedent; the lead verified plan_merge/guards.py:1
    as a kind-grouped module. Both readings are true. Recorded as form/low advisory:
    it is optional, needs no further cycle, and is prose only if applied.'
  - c1 OQ-1, OQ-2 and OQ-3 are still with the operator and were not re-raised.
  - gates.review is advisory_unless_high, so an empty must_fix at severity_max low
    does not gate the ship.
  sc_status:
  - id: code maintainer
    verdict: met
    method: inspection
    evidence: 'pm: carried by SC-01, SC-03 and SC-04; byte-identical to the c1 pin'
  - id: reader
    verdict: met
    method: inspection
    evidence: 'pm: carried by SC-02; Applying-it bullet names a re-export shim as
      a finding'
  - id: operator
    verdict: met
    method: inspection
    evidence: 'pm: carried by SC-05 and SC-06; DEC-259 now states the one known deviation
      truthfully'
  - id: SC-01
    verdict: met
    method: inspection
    evidence: 'pm + code-reviewer: SKILL.md:57-74 unchanged since 5c600680'
  - id: SC-02
    verdict: met
    method: inspection
    evidence: 'pm + code-reviewer: SKILL.md:92-96 unchanged'
  - id: SC-03
    verdict: met
    method: inspection
    evidence: 'pm + code-reviewer: LAYOUT.md:3-21 unchanged; both __init__.py present'
  - id: SC-04
    verdict: met
    method: inspection
    evidence: 'pm + code-reviewer: AGENTS.md:25 and :50 unchanged'
  - id: SC-05
    verdict: met
    method: inspection
    evidence: 'pm + code-reviewer + lead: DEC-259 at DECISIONS.md:8758. The Because
      (:8790-8794) names the signed_task_hash re-export, which is true at the pin
      (plan-merge.py:141; ctx.py _load_hash_module). Generator equals index; anchors
      25/0. Met on letter and accuracy; the c1 partial is closed'
  - id: SC-06
    verdict: met
    method: inspection
    evidence: 'qa + pm + code-reviewer: cf7b422b..afd20116 outside the feature dir
      is exactly five files; delete-first, plan-merge.py and ctx.py unchanged'
  - id: DEC-259
    verdict: met
    method: inspection
    evidence: 'pm: DECISIONS.md:8758 heading matches D-01; Record names D-01 and its
      signer'
  - id: DEC-149
    verdict: met
    method: inspection
    evidence: 'pm: keep clause at line 3465, unamended; DEC-259 now cites it for origin
      only'
  - id: DEC-235
    verdict: met
    method: inspection
    evidence: 'pm: keep clause at line 8000'
  - id: DEC-158
    verdict: met
    method: inspection
    evidence: 'pm: keep clause at line 3804'
  - id: DEC-202
    verdict: met
    method: inspection
    evidence: 'pm: keep clause at line 6317'
  - id: DEC-179
    verdict: met
    method: inspection
    evidence: 'pm: keep clause at line 4851; fix main-session-direct'
  - id: DEC-205
    verdict: met
    method: inspection
    evidence: 'pm: keep clause at line 6710; append-only (0 deletions vs base)'
  needs_approval: false
  severity_max: low
  matrix_ok: true
  coverage_gaps: []
  findings:
  - kind: form
    scope: none
    severity: low
    reader: code-reviewer
    summary: 'T-01 / SC-05: ''with one exception'' at DECISIONS.md:8791 can read as
      FEAT-70 being an exhaustive precedent for DEC-259 Chose. Advisory and optional.'
    why: 'FEAT-70 also introduced the kind-grouped plan_merge/guards.py (lead verified
      its :1 docstring), so a reviewer could cite FEAT-70 to accept another kind-named
      bucket. pm''s reading (the count is true for shims) also holds. The suggested
      remedy is prose only: describe the shared entry/package shape without an exception
      count.'
  readers:
  - reader: qa
    status: ran
    persona: harness-qa
    reason: none
  - reader: code
    status: ran
    persona: harness-code-reviewer
    reason: none
  - reader: security
    status: ran
    persona: harness-security-reviewer
    reason: none
  - reader: ui
    status: ran
    persona: harness-ui-reviewer
    reason: none
  - reader: goalcheck
    status: ran
    persona: harness-pm
    reason: none
```
