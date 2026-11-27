# plan-product (cycle 1) — FEAT-2581 team digest

**BLUF.** BRIEF.md and plan.yaml are drafted and still `pending`. The panel is recorded, with 3 readers and 9 findings. `plan-merge.py check` exits 0, and the goal-check passes both perspectives on re-grade. Two decisions block the signature:
- **PF-7999 (high):** the D-02 diagnostic repoint. The operator must rule on it.
- **Re-panel:** the five substance findings pm applied should be re-read over T-01 and T-03 before signature, per `plan-phase.md` ("Only a `substance` finding re-panels, and only over the tasks it names, in a new run directory"). That is the orchestrator's call. My recommendation is to re-panel.

No reader raised a `scope: mission` finding, so I do not recommend downgrading the mission.

## Steps

| step | persona | verdict | note |
|---|---|---|---|
| draft | harness-pm | PASS | 3 tasks: T-01 atomic move, T-02 DECISIONS, T-03 FEAT-70-style pin. `check` exit 0 |
| scope | harness-code-reviewer | FAIL (findings) | 7 findings. A valid return, so it was routed to apply, not loop_back. Note: `notes/review-harness-code-reviewer-plan-c1.md` |
| should-not-exist | fable-advisor | PASS | Resolved and ran. 2 findings, which I transcribed into `panel-c1.md` |
| design | harness-ui-reviewer | PASS | Mode A self-scoped out; the plan has no user-facing surface |
| apply | harness-pm | PASS after 1 send-back | Sent back on goal-check GC-01..03. 7 findings now resolved, 2 open. `record-panel` and `check` exit 0 |
| goalcheck | harness-pm | FAIL → PASS on re-grade | Note: `notes/research-FEAT-2581-feature-record-package-goalcheck-plan.md`. The first grade stays in the note; the re-grade is appended |

Cycles: 1 send-back (apply). Steps run: 6, plus 1 re-dispatch each of apply and goalcheck.

## Readers

- scope: ran, harness-code-reviewer.
- should-not-exist: ran, fable-advisor.
- design: ran, harness-ui-reviewer (self-scoped out).
- goalcheck: ran, harness-pm.

## Findings and dispositions

Severity and kind are the readers' own. Ids were computed by record-panel.

| id | reader | sev | kind | summary | disposition |
|---|---|---|---|---|---|
| PF-ccd4ca98 | scope | high | substance | T-03 excludes copied-bin CLI invocation from SC-05 | resolved_by T-03 (recorder keys on basename; per-class zero-count FAIL) |
| PF-e7dd0045 | scope | high | substance | T-03 PASS text not bound to measured evidence / review pin | resolved_by T-03 (inputs unchanged pin→HEAD, script sha256, grade re-run, all divergences RULED) |
| PF-d91cba6c | scope | high | substance | INV-40 observer left on old load seam | resolved_by T-01 (observer retargeted, live-seam probe in verify). pm measured that (61.b) was already vacuous at baseline; GC-04 backlog question |
| PF-7999938a | scope | high | substance | D-02 diagnostic exception not operator-authorized or exhaustive | **open**. D-02 now authorizes source text only; an 11-item inventory is measured or recorded UNREACHED as divergence records that must be ruled; operator ruling needed |
| PF-aaf45b29 | scope | med | substance | module map omits spend_for → _runs dependency | resolved_by T-01 (`_runs` moves to read.py) |
| PF-2782df09 | scope | med | form | T-01 verify is a smoke check | resolved_by T-01 (handler binding, AST sweep, labelled smoke; corpus is T-03) |
| PF-dc97f9a2 | scope | med | form | decisions_affected omits governing rules | resolved_by T-01 (keep rows DEC-180/190/191/229/230) |
| PF-d35d903d | should-not-exist | med | proportionality (task) | drop T-03's bun ledger leg | **open**. Kept, because Settled Q3 covers "every feature-record.py CLI call in the test corpus" and omp-hooks.test.ts is in that corpus. Narrowing a settled ruling is the operator's call |
| PF-b3de0ad1 | should-not-exist | low | substance | drop the fixture-root normalization token | resolved_by T-03 (one fixed fixture root on both sides; only checkout roots normalized) |

## Assessment

- **The send-back was warranted.** The first goal-check found three problems:
  - T-03 graded per file where Settled Q3 says "the same pre-existing test cases".
  - The D-02 diagnostics never reached any measured ledger.
  - Every applied finding was still open on the panel.

  One pm spawn closed all three. The re-grade checked both directions and found no criterion broken.
- **Premise corrections the signer must see** (Settled text vs source):
  - D-01: canonical-reader remedies move with the loader, beyond the "file and id only" rule.
  - D-02: diagnostics that name deleted files are repointed, beyond "byte-identical"; every measured byte stays red until ruled.
  - The grilling's classification-row counts were `grep -c` line counts, not rows.
- **Prototype gate:** the design reader self-scoped out and the plan has no end-user interaction, so no prototype is required. The operator can override this.
- **Not yet specified, settled at source by pm:**
  - No `artifact_accessors.py` row moves.
  - No `copy_executable_package` delegate is needed; two selective copies in test-check-plan-routes also copy the package.
- **Out of scope:** none touched. pm also explicitly left `docs/invalid-states-audit.html` and `prior-check-domain.fixture` alone.
- **Verification I did not run:** I hold no shell. The `check` exit 0 is pm's report, and so is pm's baseline test census.

`plan-merge.py check`, as pm reported it at the re-grade (exit 0):

```text
OK T-01 11 anchor(s) resolved | OK T-02 2 anchor(s) resolved | OK T-03 1 anchor(s) resolved | CHECK .../FEAT-2581-feature-record-package/plan.yaml against /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2581-feature-record-package: 3 task(s), 14 anchor(s) resolved, 0 failure(s)
```

Panel recorded from `panel-c1.md` lacks the `goalcheck` reader; the orchestrator re-records from this digest (`plan-phase.md`).

```yaml
VERDICT: FAIL
DIGEST:
  headline: 'FEAT-2581 BRIEF and plan.yaml are drafted and still pending. The panel
    is recorded (3 readers, 9 findings), plan-merge check exits 0, and the goal-check
    passes both perspectives on re-grade. The team verdict is FAIL on worst-wins:
    the scope reader failed, and its 4 high substance findings were applied by pm
    but never re-read. Fix: re-panel T-01 and T-03 in a new run dir; separately, PF-7999
    (D-02) needs an operator ruling. No mission downgrade.'
  open_questions:
  - id: PL-01
    question: 'Ruling on PF-7999 / D-02 (high, open). Should the import-failure diagnostics
      that name deleted files (check-domain x3, INV-23/26/37/40) point at the module
      that is actually loaded? Signing approves only the source text. T-03 then measures
      each of the 11 inventory items, or records it UNREACHED, as a divergence record
      that stays red until it is ruled in divergence-rulings.json. Recommendation:
      sign D-02 through an approval.rulings overrule and rule the measured records
      after the build. The alternative keeps literals that point at deleted files.'
    blocking: true
  - id: PL-03
    question: 'Premise correction D-01. The Settled text says classification rows
      change only file and id. But 24 caller rows'' remedies and the canonical_reader_audit
      keys must become feature_record.read.load_feature_json, because the audit matches
      a row only when callee equals remedy. Two test expectations change with them.
      Accept? Recommendation: yes. The only alternative reverses Q1 b.'
    blocking: false
  - id: PL-04
    question: 'PF-d35d903d (proportionality, scope task, open). fable-advisor recommends
      dropping the bun omp-hooks.test.ts leg from the CLI ledger. pm kept it because
      Settled Q3 covers every feature-record.py call in the test corpus. Will the
      operator narrow Q3? Recommendation: keep the leg. Zero-count FAILs guard each
      process class, and the bun JUnit run stays either way for case identity.'
    blocking: false
  - id: PL-05
    question: Who rules T-03's measured divergences, and can that be delegated as
      in FEAT-70? Expect at least the relocated traceback frames in test_an_unexpected_defect_stays_loud_and_nonzero.
    blocking: false
  - id: PL-06
    question: 'Should the (61.b) gap be backlogged? test-check-state-feat59 case (61.b)
      has never tested stale INV-40 registration, not even at baseline e12381fd. Fixing
      it needs a new test seam, which the Settled imports-only test rule forbids.
      Recommendation: backlog it as a separate chore.'
    blocking: false
  - id: PL-07
    question: 'Harness defect candidates from pm, for the harness owner:

      (a) The INV-41 heuristic in check_state/brief.py _inv41_invocation flagged an
      SC that only named check-state.py as a captured process.

      (b) DEC-191 names bin/feature-schema.json, which does not exist; the schema
      is at schemas/feature.json.

      (c) The Harness product checkout has no docs/spec.md, docs/decisions.md or docs/architecture.md,
      so pm used DECISIONS.md and bin/LAYOUT.md. Is that the intended mapping?'
    blocking: false
  files_touched:
  - /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2581-feature-record-package/.harness/harness/features/FEAT-2581-feature-record-package/BRIEF.md
  - /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2581-feature-record-package/.harness/harness/features/FEAT-2581-feature-record-package/plan.yaml
  - /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2581-feature-record-package/.harness/harness/features/FEAT-2581-feature-record-package/notes/research-feature-record-package.md
  - /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2581-feature-record-package/.harness/harness/features/FEAT-2581-feature-record-package/notes/research-FEAT-2581-feature-record-package-goalcheck-plan.md
  - /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2581-feature-record-package/.harness/harness/features/FEAT-2581-feature-record-package/notes/review-harness-code-reviewer-plan-c1.md
  - /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2581-feature-record-package/.harness/harness/features/FEAT-2581-feature-record-package/notes/review-harness-ui-reviewer-plan-c1.md
  - /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2581-feature-record-package/.harness/harness/features/FEAT-2581-feature-record-package/observations/harness-pm.md
  - /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2581-feature-record-package/.harness/harness/features/FEAT-2581-feature-record-package/runs/plan-product/state.yaml
  - /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2581-feature-record-package/.harness/harness/features/FEAT-2581-feature-record-package/runs/plan-product/panel-c1.md
  - /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2581-feature-record-package/.harness/harness/features/FEAT-2581-feature-record-package/runs/plan-product/acceptance-criteria.md
  expertise_update: []
  team: plan
  steps_run: 6
  cycles_used: 1
  members:
  - step: draft
    persona: harness-pm
    verdict: PASS
    headline: 'Drafted the BRIEF and a 3-task plan: T-01 atomic move, T-02 DECISIONS
      amendments, T-03 FEAT-70-style pin, with D-01..D-03. check exits 0'
    files_touched:
    - .harness/harness/features/FEAT-2581-feature-record-package/BRIEF.md
    - .harness/harness/features/FEAT-2581-feature-record-package/plan.yaml
    - .harness/harness/features/FEAT-2581-feature-record-package/notes/research-feature-record-package.md
  - step: scope
    persona: harness-code-reviewer
    verdict: FAIL
    headline: 'Keeps the 3-task shape. 7 findings, 4 of them high substance: T-03
      proof binding, the INV-40 seam, D-02 authorization, and the spend_for dependency'
    files_touched:
    - .harness/harness/features/FEAT-2581-feature-record-package/notes/review-harness-code-reviewer-plan-c1.md
  - step: should-not-exist
    persona: fable-advisor
    verdict: PASS
    headline: '2 findings: drop the bun ledger leg (proportionality, task) and drop
      the fixture-root normalization token (substance, low). The rest is proportionate'
    files_touched: []
  - step: design
    persona: harness-ui-reviewer
    verdict: PASS
    headline: 'Self-scoped out: no user-facing surface'
    files_touched:
    - .harness/harness/features/FEAT-2581-feature-record-package/notes/review-harness-ui-reviewer-plan-c1.md
  - step: apply
    persona: harness-pm
    verdict: PASS
    headline: Applied all 9 findings over one lead send-back. 7 are resolved_by T-01/T-03;
      PF-7999 and PF-d35d stay open for the operator. record-panel and check exit
      0
    files_touched:
    - .harness/harness/features/FEAT-2581-feature-record-package/BRIEF.md
    - .harness/harness/features/FEAT-2581-feature-record-package/plan.yaml
    - .harness/harness/features/FEAT-2581-feature-record-package/notes/research-feature-record-package.md
  - step: goalcheck
    persona: harness-pm
    verdict: PASS
    headline: 'First grade FAIL: the operator perspective was partial (identity proven
      per file, not per case; D-02 bytes unmeasured). Re-grade after the send-back
      passes both perspectives'
    files_touched:
    - .harness/harness/features/FEAT-2581-feature-record-package/notes/research-FEAT-2581-feature-record-package-goalcheck-plan.md
  must_fix:
  - 'Re-panel: run the scope reader over T-01 and T-03 in a new run directory. They
    carry the five substance findings pm applied without re-read: PF-ccd4, PF-e7dd
    and PF-d91c (high), PF-aaf4 (med), PF-b3de (low). plan-phase.md: ''Only a substance
    finding re-panels, and only over the tasks it names, in a new run directory''.
    Fold in goalcheck advisory RG-A2: bound T-03''s baseline_failing exemption to
    the measured set.'
  branch: none
  escalations: []
  adequacy_notes:
  - The FAIL is the worst-wins roll-up of the scope reader's FAIL, which no reader
    has re-read since apply. The draft itself is complete and pending. Once the re-panel
    clears, only PL-01 (the operator ruling on PF-7999) remains for signature.
  - runs/plan-product/digest.md prose was written before the worst-wins correction,
    and its BLUF reads as pass-pending. The fenced block that validate-digest appends
    after it carries this FAIL and wins (DEC-156). check-domain refused rewriting
    the prose.
  - 'plan-merge.py check exit 0 is pm''s report, verbatim: ''OK T-01 11 anchor(s)
    resolved | OK T-02 2 anchor(s) resolved | OK T-03 1 anchor(s) resolved | CHECK
    <plan.yaml> against <worktree>: 3 task(s), 14 anchor(s) resolved, 0 failure(s)''.
    I hold no shell and did not run it.'
  - panel.readers was recorded from panel-c1.md, which has no goalcheck reader. Per
    plan-phase.md, the orchestrator re-records it from runs/plan-product/digest.md.
  - The digest carries scope none on every non-proportionality finding, as the contract
    requires. That includes fable-advisor's low substance finding, which arrived tagged
    scope task; record-panel drops scope for such findings anyway. No severity or
    kind was changed.
  - 'Prototype gate: the design reader self-scoped out and the plan has no end-user
    interaction, so no prototype is required. The operator can override this either
    way.'
  - 'Not-yet-specified items were settled at source by pm: no artifact_accessors row
    moves, and no copy_executable_package delegate is needed. The grilling''s row
    counts were grep -c line counts; by row they are 2/6/1/4/1.'
  - Out-of-scope items are untouched, no code under .agents/ was edited, and nothing
    is signed.
  sc_status:
  - id: perspective:code maintainer
    verdict: met
    method: inspection (goalcheck re-grade)
    evidence: SC-01, SC-07 (T-01, T-03 audit); SC-02 (T-01 regrade, T-03 grade-assert);
      SC-09 (T-02)
  - id: perspective:operator
    verdict: met
    method: inspection (goalcheck re-grade)
    evidence: SC-03/04/05/06/08/10 carried by T-01 and T-03; T-03 verify requires
      every divergence RULED
  needs_approval: true
  severity_max: high
  matrix_ok: none
  coverage_gaps: []
  findings:
  - kind: substance
    scope: none
    severity: high
    reader: scope
    summary: T-03 excludes a real copied-bin CLI invocation from SC-05.
    why: "test-feature-record.py:1402\u20131422 runs mbin/feature-record.py, outside\
      \ the checkout-path selector in plan.yaml:204. Both ledgers can omit the same\
      \ invocation and pass; capturing it exposes a deliberate traceback whose moved\
      \ frames are not a root-only difference."
  - kind: substance
    scope: none
    severity: high
    reader: scope
    summary: T-03 accepts PASS text without binding measured evidence to the review
      pin.
    why: "plan.yaml:184\u2013196 accepts hand-written PASS markers and any qualifying\
      \ ancestor with a bin diff. It checks no measurements or unresolved divergence\
      \ and stops its tree comparison at the receipt commit. The receipt cannot exist\
      \ at the earlier implementation SHA; distinguish it from review_sha and verify\
      \ measured inputs through review time."
  - kind: substance
    scope: none
    severity: high
    reader: scope
    summary: "T-01 leaves INV-40\u2019s registration observer on the old load seam."
    why: "test-check-state-feat59.py:612\u2013623 replaces plan-merge.py and asserts\
      \ the absence of an import failure. Once Ctx imports plan_merge.approval, the\
      \ assertion can pass even though the observer never runs and stale registration\
      \ is no longer tested."
  - kind: substance
    scope: none
    severity: high
    reader: scope
    summary: "D-02\u2019s diagnostic exception is not operator-authorized or exhaustive."
    why: Accurate paths are warranted but literal wording is a choice, and the settled
      rule keeps differences red pending a ruling. INV-7 and harness_config also render
      RepoModuleError, whose embedded module name changes automatically; the five
      named branches and their literals do not bound the output delta.
  - kind: substance
    scope: none
    severity: med
    reader: scope
    summary: "T-01\u2019s directed module map omits spend_for\u2019s dependency on\
      \ _runs."
    why: feature-record.py:124,708 puts a live helper in runs.py while the plan disallows
      spend importing it. A literal move breaks spend with NameError; sharing the
      record-read helper through read.py preserves locality without duplication.
  - kind: form
    scope: none
    severity: med
    reader: scope
    summary: "T-01\u2019s verify block is a smoke check, not a structural or corpus\
      \ proof."
    why: It never binds argparse handlers to package imports, misses from artifact_accessors
      import load_feature_json, and runs two test files rather than the baseline-passing
      corpus. Keep the live audit and grade commands; strengthen the structural predicate
      and distinguish smoke from full evidence.
  - kind: form
    scope: none
    severity: med
    reader: scope
    summary: decisions_affected omits rules governing the checker, schema, and signed-hash
      surfaces.
    why: "DEC-180, DEC-190/191, and DEC-229/230 govern mechanisms T-01 touches; declare\
      \ keep for the operative rules. DEC-259\u2019s layout rule survives removal\
      \ of its exception, so amend rather than strike; the DEC-150/220 pointer amendments\
      \ are also justified."
  - kind: proportionality
    scope: task
    severity: med
    reader: should-not-exist
    summary: T-03's bun leg (omp-hooks.test.ts run plus a --preload patching node
      mkdtempSync) adds near-zero discriminating power and should be dropped from
      the CLI ledger.
    why: "The bun test's real feature-record.py spawns (omp-hooks.test.ts:3341, 3487,\
      \ 3539) exercise only spend, stamp-tokens and run-end \u2014 verbs the Python\
      \ corpus already ledgers \u2014 and the TS hook code building their argv is\
      \ byte-identical on both sides, so the leg only reproduces divergences the Python\
      \ ledger catches while adding the untried bun mkdtempSync preload, whose leaked\
      \ temp paths would each be a spurious red divergence. Does not reverse Settled\
      \ Q3 (a) if 'the test corpus' means the Python suites; if the operator meant\
      \ to include the TS suite, this asks the operator to narrow it."
  - kind: substance
    scope: none
    severity: low
    reader: should-not-exist
    summary: The second normalization token (fixture root alongside checkout root)
      should not exist; use one shared fixed fixture root on both sides, as FEAT-70
      did.
    why: FEAT-70's driver used one identical fixture path on both sides, cleared per
      execution, so only checkout-root bytes were normalized. T-03's extra fixture-root
      substitution is a channel where a real byte difference can be silently rewritten
      before comparison, which Settled Q3 (a) exists to forbid; a shared fixed root
      removes it at zero cost.
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
artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2581-feature-record-package/.harness/harness/features/FEAT-2581-feature-record-package/runs/plan-product/digest.md
```
