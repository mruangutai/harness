# FEAT-2557 · validate c1 · r-20261127-1-validate-validator

**FAIL. One must-fix: DEC-259 calls FEAT-70's split of `plan-merge.py` an example of a shape
that forbids re-export shims, but `plan-merge.py` still re-exports `signed_task_hash` for
check-state INV-40.** The fix is one prose qualification in DECISIONS.md, which T-01 owns. Every
other gate is clean. Reviewed at `5c600680e7f46af124fa3281392fa7b25623e982` (base `cf7b422b`).

## Panel

|Step|Persona|Verdict|Note|
|---|---|---|---|
|qa|harness-qa|PASS|`test_matrix.docs.always=[]`. No kind was required, so no receipt was written. T-01's verify re-ran green and its guards are non-vacuous; it found 6 low weaknesses (`notes/review-harness-qa-c1.md`)|
|code|harness-code-reviewer|FAIL|1 high substance finding and 2 low form findings. Stage 2 was not reached (`notes/review-harness-code-reviewer-c1.md`)|
|security|harness-security-reviewer|PASS|Out of scope on a measured 24-path census (+995/−0, no guard weakened)|
|ui|harness-ui-reviewer|PASS|Out of scope on the same census|
|goalcheck|harness-pm|PASS|Three perspectives met, SC-01..06 met, D-01→DEC-259 and six keep rows hold. Two low OQs (`notes/research-…-goalcheck-validate-c1.md`)|

## Assessment

**Contradiction resolved: code-reviewer (SC-05 mismatch) over pm (SC-05 met).** I verified it
at source myself. `plan-merge.py` line 141 reads `from plan_merge.approval import signed_task_hash
# noqa: E402,F401  INV-40's import`, and its docstring calls the entry "the import surface
check-state's INV-40 loads `signed_task_hash` from". `check_state/ctx.py` `_load_hash_module`
loads `plan-merge.py` by path and reads that attribute.

DEC-259 Chose says a split "leaves no re-export shim". Its Because says FEAT-70 split
`plan-merge.py` "in this shape". Both statements are in the same entry, and the second is false
for one symbol. pm graded the letter of SC-05 (provenance recorded, three homes, index exact), and
that letter holds. The defect is in the accuracy of what the record states (DEC-205, current
truth). So: SC-05 is met on its letter and partial on accuracy. I gate on the accuracy.

The code-reviewer rated it `high`, and I transcribe that rating unchanged. I would rate it
`med`. It is reversible, one sentence long, and the new skill rule and its Applying-it bullet
already name a shim as a finding. I do not escalate the split (P-04 does not apply): T-01
(main-session-direct) can apply the remedy inside its own files, so a fix cycle costs less than a
ruling.

**Remedy bounds.** Qualify DEC-259's Because so that FEAT-70 demonstrates the entry/package layout
but kept one re-export (`signed_task_hash`, loaded by path by check-state's INV-40). Change prose
only:
- Do not change `plan-merge.py` or `check_state/ctx.py`. A code change would break SC-06, and
  removing the import without migrating the path-loader raises AttributeError at checker startup.
- DEC-259 is the last entry, so its heading line (8758) and the generated index anchor stay put.
  Re-run `gen-decisions-index.py --stdout` and diff it against the index anyway.
- The qualification adds to the T-01 intent's dictated Because text without contradicting it. It
  amends neither SC-05 nor the signed intent, so it is a fix, not a plan amendment (G-06 judged).

## Findings, ranked

1. **substance · high (code-reviewer) · T-01 · MUST-FIX.** DEC-259 presents FEAT-70 as
   conformant to the no-shim rule; it is not.
2. **form · low (code-reviewer F2 + pm OQ-2, deduplicated).** DEC-259 Because cites DEC-149 for
   current specialist autoload, but DEC-149 says doers get the skill by dispatch, not preload.
   The claim itself is true by the agents' frontmatter. *Fix order:* the same Because paragraph
   as #1, so fold it into the same edit (cite the frontmatter for current delivery and DEC-149
   for origin). Advisory, not gating. The DEC-149 rewrite pm raised is a pre-existing backlog
   question.
3. **form · low (code-reviewer F3 + pm OQ-1, deduplicated).** The new Layout section carries no
   DEC-259 pointer, which DEC-158's "rule + why + DEC pointer" asks for. Advisory. Whether a
   cross-repository skill should point into Harness's DECISIONS.md is a fair question, so I leave
   it open (non-blocking).
4. **QA verify-guard weaknesses (6 × low; substance ×2, form ×3, proportionality ×1).** All are
   against T-01's one-shot build verify, not shipped prose. The worst one, the delete-first
   `git diff HEAD` line being vacuous after commit, is backstopped by the terminal scope check.
   **Assessed and dismissed:** the verify is a spent build check, and inspection by the panel
   covers each gap (the pinned LAYOUT.md is clean on every inflection QA named).

## Adequacy

- The panel's assurance here is inspection by reasoning plus executed checks. QA executed T-01's
  verify at the pin and positive-injected each guard. The code-reviewer executed the generator
  diff (55,030 bytes matched) and the anchors check (25/0). Both readers measured the census
  rather than assuming it.
- Neither readers nor the verify catch a provenance sentence that is false about code outside
  the diff. Only the code-reviewer's habit of opening the cited example at the pin found #1.
- Weight check: the largest preload is 5,178 of 5,500 words (eng-lead). The skill is 1,056
  words (+247). Non-gating.

## Open (non-blocking)

- OQ-1: Should a backlog item migrate INV-40's loader to `plan_merge/approval.py` and drop the
  re-export, bringing FEAT-70's split into conformance with DEC-259? That is code outside this
  feature's scope.
- OQ-2: Should the Layout section carry a DEC-259 pointer (finding 3)?
- OQ-3: Should DEC-149 be rewritten under DEC-205 to state the current autoload fact (finding 2,
  pm's OQ-2)?

```yaml
VERDICT: FAIL
artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2557-code-layout-pattern/.harness/harness/features/FEAT-2557-code-layout-pattern/runs/r-20261127-1-validate-validator/digest.md
DIGEST:
  headline: 'FEAT-2557 fails validation at 5c600680 on one gate: DEC-259 gives FEAT-70
    as an example of the no-shim shape, but plan-merge.py still re-exports signed_task_hash
    for INV-40. A one-sentence prose fix in DECISIONS.md under T-01 clears it. All
    other gates are clean (matrix_ok; security and ui out of scope; pm met all three
    perspectives).'
  team: validate
  steps_run: 5
  cycles_used: 0
  members:
  - step: qa
    persona: harness-qa
    verdict: PASS
    headline: docs change requires no test kind (test_matrix.docs.always=[]), so no
      receipt was written; T-01 verify re-ran green with non-vacuous guards; 6 low
      guard weaknesses
    files_touched: []
  - step: code
    persona: harness-code-reviewer
    verdict: FAIL
    headline: 'SC-05 fails: DEC-259 presents FEAT-70 as following the no-shim rule,
      but its split retained a re-export that check-state still uses'
    files_touched: []
  - step: security
    persona: harness-security-reviewer
    verdict: PASS
    headline: 'No security findings: measured 24-path prose-only census adds no boundary
      and weakens no guard'
    files_touched: []
  - step: ui
    persona: harness-ui-reviewer
    verdict: PASS
    headline: 'Out of scope: the measured 24-path census has no rendered or interactive
      surface'
    files_touched: []
  - step: goalcheck
    persona: harness-pm
    verdict: PASS
    headline: All three perspectives discharged, SC-01..SC-06 met on inspection, D-01
      landed as DEC-259, six keep rows hold; two low advisory OQs
    files_touched: []
  must_fix:
  - 'T-01 (substance, high, code-reviewer): in .harness/harness/docs/DECISIONS.md,
    DEC-259''s Because must qualify FEAT-70. Its split of plan-merge.py demonstrates
    the entry/package layout but kept one re-export (plan-merge.py `from plan_merge.approval
    import signed_task_hash  # noqa: E402,F401  INV-40''s import`), which check_state/ctx.py
    _load_hash_module loads by path. Change prose only: do not change plan-merge.py
    or check_state/ctx.py (SC-06; dropping the import without migrating the path-loader
    raises AttributeError at checker startup). Afterwards run gen-decisions-index.py
    --stdout | diff against DECISIONS-INDEX.md and check-decision-anchors.py. Fold
    the low form finding on the DEC-149 citation into the same paragraph edit (cite
    the agents'' frontmatter for current autoload, DEC-149 for origin).'
  files_touched:
  - .harness/harness/features/FEAT-2557-code-layout-pattern/runs/r-20261127-1-validate-validator/state.yaml
  branch: none
  open_questions:
  - id: OQ-1
    question: plan-merge.py re-exports signed_task_hash for check-state INV-40's path
      loader, which deviates from DEC-259's no-shim rule. Should a backlog item migrate
      INV-40 to plan_merge/approval.py and drop the re-export? That is code outside
      FEAT-2557's scope.
    blocking: false
  - id: OQ-2
    question: DEC-158 asks for a DEC pointer, but the new language-neutral Layout
      section in harness-codebase-design carries no DEC-259 pointer (raised by code-reviewer
      F3 and pm OQ-1). Should one be added, given that the skill binds every repository
      Harness builds and DEC-259 lives in Harness's DECISIONS.md?
    blocking: false
  - id: OQ-3
    question: DEC-149 says doers receive harness-codebase-design by dispatch, not
      preload, yet five doer agents and product-lead autoload it at the pin. Should
      a backlog item rewrite DEC-149 under DEC-205? (pm OQ-2 and code-reviewer F2)
    blocking: false
  escalations: []
  expertise_update: []
  adequacy_notes:
  - 'Contradiction resolved in favour of code-reviewer over pm on SC-05. I verified
    at source: plan-merge.py line 141 re-exports signed_task_hash, its docstring calls
    the entry INV-40''s import surface, and check_state/ctx.py _load_hash_module reads
    the attribute after loading the file by path. pm graded SC-05''s letter (provenance
    recorded, three homes, index exact), which holds; the defect is in what the record
    states (DEC-205).'
  - The code-reviewer's 'high' is transcribed unchanged. The lead would rate it med
    (reversible, one sentence, and the new rule already names a shim as a finding).
    The rating split is not escalated because T-01 can apply the remedy inside its
    own files.
  - 'Judged against G-06: the qualification adds to the intent''s dictated Because
    text and amends neither SC-05''s wording nor the signed intent, so it is a fix-cycle
    item, not a plan amendment.'
  - QA's six low weaknesses in the T-01 verify guards (substance x2, form x3, proportionality
    x1) are assessed and dismissed. The verify is a spent build check, the panel's
    inspection covers each gap, and the terminal scope check backstops the delete-first
    guard, which is vacuous after commit.
  - 'Preload weight is non-gating: max 5,178/5,500 words (eng-lead); harness-codebase-design
    is 1,056 words (+247).'
  - 'Assurance: QA executed T-01 verify at the pin with positive injection. The code-reviewer
    executed the generator diff (55,030 bytes matched) and the anchors check (25 anchors,
    0 failed). Security and ui measured the census before scoping out. The blocking
    defect concerns code outside the diff, so no verify could catch it; only opening
    the cited example found it.'
  sc_status:
  - id: code maintainer
    verdict: met
    method: inspection
    evidence: 'pm: carried by SC-01, SC-03 and SC-04 at 5c600680'
  - id: reader
    verdict: met
    method: inspection
    evidence: 'pm: carried by SC-02 at 5c600680'
  - id: operator
    verdict: met
    method: inspection
    evidence: 'pm: carried by SC-05 and SC-06 at 5c600680'
  - id: SC-01
    verdict: met
    method: inspection
    evidence: 'pm + code-reviewer: SKILL.md:57 heading, seven clauses cited at :59-:74,
      language-neutral'
  - id: SC-02
    verdict: met
    method: inspection
    evidence: 'pm + code-reviewer: SKILL.md:92-96 Applying-it bullet'
  - id: SC-03
    verdict: met
    method: inspection
    evidence: 'pm + code-reviewer: LAYOUT.md:3-21; named files exist; both __init__.py
      0 bytes'
  - id: SC-04
    verdict: met
    method: inspection
    evidence: 'pm + code-reviewer: AGENTS.md:25 sole path occurrence; AGENTS.md:50
      exact bullet'
  - id: SC-05
    verdict: met
    method: inspection
    evidence: 'pm: DEC-259 at DECISIONS.md:8758; index equals generator; anchors 0
      failed'
  - id: SC-05 (lead)
    verdict: partial
    method: inspection
    evidence: 'Met on its letter. Accuracy defect: DEC-259''s Because says FEAT-70
      split plan-merge.py ''in this shape'', but plan-merge.py:141 keeps a signed_task_hash
      re-export for check_state/ctx.py _load_hash_module; must_fix #1'
  - id: SC-06
    verdict: met
    method: inspection
    evidence: 'pm + code-reviewer: cf7b422b..5c600680 is exactly the five files plus
      the feature dir; delete-first unchanged'
  - id: DEC-259
    verdict: met
    method: inspection
    evidence: 'pm: DECISIONS.md line 8758, heading matches D-01, Record names D-01'
  - id: DEC-149
    verdict: met
    method: inspection
    evidence: 'pm: keep clause present at line 3465'
  - id: DEC-235
    verdict: met
    method: inspection
    evidence: 'pm: keep clause present at line 8000'
  - id: DEC-158
    verdict: met
    method: inspection
    evidence: 'pm: line 3804; history only in DEC-259 (pointer question OQ-2)'
  - id: DEC-202
    verdict: met
    method: inspection
    evidence: 'pm: line 6317; pointer row plus pathless bullet, nothing copied'
  - id: DEC-179
    verdict: met
    method: inspection
    evidence: 'pm: line 4851; T-01 declared main-session step'
  - id: DEC-205
    verdict: met
    method: inspection
    evidence: 'pm: line 6710; pure append'
  needs_approval: false
  severity_max: high
  matrix_ok: true
  coverage_gaps: []
  findings:
  - kind: substance
    scope: none
    severity: high
    reader: code-reviewer
    summary: 'T-01 / SC-05: DEC-259 overstates FEAT-70''s conformance to the new rule.'
    why: "DECISIONS.md:8790 cites FEAT-70 as following the shape defined at :8760\u2013\
      8765. Its split retained plan-merge.py:141's signed_task_hash re-export; check_state/ctx.py:360\u2013\
      372 still loads it. Using the example unqualified can perpetuate shims; dropping\
      \ this import without migrating its caller raises AttributeError during checker\
      \ startup."
  - kind: form
    scope: none
    severity: low
    reader: code-reviewer, pm
    summary: 'T-01 / SC-05: DEC-259 cites DEC-149 for current specialist autoload,
      but DEC-149 says the opposite.'
    why: "DECISIONS.md:8796\u20138798 points readers to DEC-149, whose :3471\u2013\
      3473 describes dispatch-time delivery. The pinned specialist frontmatter confirms\
      \ current autoload; a reader auditing delivery from the reference alone gets\
      \ the wrong answer. (Deduplicated with pm OQ-2.)"
  - kind: form
    scope: none
    severity: low
    reader: code-reviewer, pm
    summary: 'T-01 / SC-01: the new layout rule lacks the DEC-259 pointer required
      by DEC-158.'
    why: "A reader following SKILL.md:57\u201374 reaches delete-first for the split\
      \ trigger but has no direct reference to the signed rationale for review-only\
      \ enforcement. (Deduplicated with pm OQ-1.)"
  - kind: substance
    scope: none
    severity: low
    reader: qa
    summary: 'T-01 verify: delete-first guard `git diff --quiet HEAD` is vacuous after
      commit. Assessed and dismissed: backstopped by the terminal scope check.'
    why: A committed edit to delete-first.md passes that line, but the base..tree
      scope check prints SCOPE DRIFT.
  - kind: substance
    scope: none
    severity: low
    reader: qa
    summary: 'T-01 verify: the size/grade -w guard misses inflections (''sizes rot'',
      ''line-count''). Assessed and dismissed: the pinned LAYOUT.md is clean on inspection.'
    why: LAYOUT.md could gain a size rule and the verify would stay green; inspection
      still covers it.
  - kind: form
    scope: none
    severity: low
    reader: qa
    summary: 'T-01 verify: the ''A split'' heading guard is case-sensitive and needs
      a space. Assessed and dismissed.'
    why: '''## A Split'' would escape; the pinned file has no such section.'
  - kind: form
    scope: none
    severity: low
    reader: qa
    summary: 'T-01 verify: the ''exactly once'' check counts lines, not occurrences.
      Assessed and dismissed: the true count at the pin is 1.'
    why: Two paths on one line would pass.
  - kind: form
    scope: none
    severity: low
    reader: qa
    summary: 'T-01 verify: the DEC-259 extraction runs to EOF. Assessed and dismissed:
      DEC-259 is the last entry at the pin.'
    why: A later DEC-260 could supply the required tokens.
  - kind: proportionality
    scope: task
    severity: low
    reader: qa
    summary: 'T-01 verify: the language-neutral guard covers only the letter of SC-01.
      Assessed and dismissed: acceptable for a one-shot build check.'
    why: '''.PY'' and other-language paths escape the regex.'
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
