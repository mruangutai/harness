# FEAT-2489 — plan apply c2 (r-20261124-3-plan-product)

**BLUF: PASS.** pm applied both cycle-2 substance remedies. BRIEF.md and plan.yaml now carry both, approval stays pending, and pm reports `plan-merge.py check` at 4 tasks, 17 anchors resolved and 0 failures. Three findings stay open until a reader re-reads them; the signer must also accept or refuse the disclosed SC-02 departure.

## Member
- apply (harness-pm): PASS. Files: BRIEF.md, plan.yaml, notes/research-plan-routes-split.md, observations/harness-pm.md.

## Lead assessment against sendback-criteria.md (written before dispatch)
- PF-2411 class rule: SC-02 adds a fifth item (`BRIEF.md:32`). It states the rule by class: any diagnostic, on either stream and in any mode, that is formatted from a field items 1–3 rewrite. The text says "not a list of producers". The disclosed departure sits in Verification gaps (`BRIEF.md:61`), beside complete-install, and says it derives from items 1–3.
- Mechanical evidence: T-02 builds its relocation map from the base and head inventories, for exactly the changed rows (`plan.yaml:280`). The perturbed sample blanks the reason on the relocated `_classification_document::json_file#1` row (`:289`). The comparison maps the old lines and then requires them to be equal (`:313`). T-04's receipt requires MAP lines and never `MAP none` (`:477`).
- PF-6efa binding: T-01's verify asserts `merge-base --is-ancestor <recorded HEAD> HEAD` and that `rev-parse <HEAD>:<test>` equals the recorded BLOB (`plan.yaml:180-182`). It never compares the live file. It also asserts that the recorded HEAD predates the move and postdates the T-01 test change. The receipt is recorded after the T-01 commit (`:223`).
- Ruled scope untouched: SC-01..SC-05, 4 tasks, no new task.
- Adequacy note: the relocation map covers the rewrites of inventory rows. A diagnostic formatted from the re-keyed T07 key or from a scanned_files entry is covered by the SC-02 class, but T-02 does not sample one. That is acceptable: the class is the contract and the samples are evidence.

## Dispositions at exit (plan.yaml panel)
- open: PF-241126189d3c3d16550a5f09c7532ff3 (applied, awaiting re-read), PF-6efa88c834c89ca43eea0322509703d9 (applied, awaiting re-read), PF-5dbe6b5eecda5efa44c6d9624e826e1a (its residual is PF-6efa and it closes with it)
- resolved: PF-b25f62af28d7aa5f31cd38d635041a54, PF-0e9128df11c14ad97669b28ff451a725 (both confirmed closed by class at c2), PF-b963b10c2511cecf9ad0f6103be427ea, PF-29a7e86075e97f550fb37781a3eb389f (the c2 info records of those closures), PF-9bc751c71f94a87fdd29e84578ce6c1e, PF-293c2789a0a14408ae4b9f3ca8df9efb, PF-2f032ea4ded9ab191d46672327dac011, PF-0dad747f115c481968d48fdfed6ec1e1 (c1 proportionality and form, trimmed at c1 apply)

## Open questions
- OQ-c2-1 (non-blocking): the signer accepts or refuses SC-02's fifth item, a disclosed departure from Q3's "exactly these, nothing else".
- OQ-c2-2 (non-blocking, possible harness defect): `record-panel` stored the scope reader's reason as `none`, although the c2 digest carried a substantive reason.

```yaml
VERDICT: PASS
artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2489-plan-routes-split/.harness/harness/features/FEAT-2489-plan-routes-split/runs/r-20261124-3-plan-product/digest.md
DIGEST:
  headline: Both cycle-2 remedies are in BRIEF.md and plan.yaml, and approval is still
    pending. SC-02 now states a class rule with a disclosed departure. T-01's receipt
    is bound to its checkpoint by an ancestor check and a blob check. plan-merge check
    reports 0 failures. PF-2411, PF-6efa and PF-5dbe stay open until they are re-read.
  open_questions:
  - id: OQ-c2-1
    question: "Will the signer accept or refuse SC-02's fifth sanctioned item? It\
      \ departs from grilling Q3's 'exactly these, nothing else'. Its rule: a diagnostic\
      \ formatted from a field that delta items 1\u20133 rewrite shows the rewritten\
      \ value and is otherwise identical. It is disclosed at BRIEF.md:61. If it is\
      \ refused, the plan goes back to Plan, because SC-02 cannot be met as ruled."
    blocking: false
  - id: OQ-c2-2
    question: 'Possible harness defect, reported by pm: record-panel wrote panel.readers[scope].reason
      as ''none'', although the cycle-2 digest carried a substantive reason. Is that
      expected record-panel behaviour? The digest validator also requires reason ''none''
      for a reader that ran, which may be the cause.'
    blocking: false
  files_touched:
  - /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2489-plan-routes-split/.harness/harness/features/FEAT-2489-plan-routes-split/BRIEF.md
  - /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2489-plan-routes-split/.harness/harness/features/FEAT-2489-plan-routes-split/plan.yaml
  - /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2489-plan-routes-split/.harness/harness/features/FEAT-2489-plan-routes-split/notes/research-plan-routes-split.md
  - /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2489-plan-routes-split/.harness/harness/features/FEAT-2489-plan-routes-split/observations/harness-pm.md
  - /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2489-plan-routes-split/.harness/harness/features/FEAT-2489-plan-routes-split/runs/r-20261124-3-plan-product/state.yaml
  - /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2489-plan-routes-split/.harness/harness/features/FEAT-2489-plan-routes-split/runs/r-20261124-3-plan-product/sendback-criteria.md
  expertise_update: []
  team: plan
  steps_run: 1
  cycles_used: 0
  members:
  - step: apply
    persona: harness-pm
    verdict: PASS
    headline: Both cycle-2 substance remedies are applied, approval is pending, and
      plan-merge check reports 4 tasks, 17 anchors resolved and 0 failures. PF-2411
      and PF-6efa stay open until they are re-read.
    files_touched:
    - .harness/harness/features/FEAT-2489-plan-routes-split/BRIEF.md
    - .harness/harness/features/FEAT-2489-plan-routes-split/plan.yaml
    - .harness/harness/features/FEAT-2489-plan-routes-split/notes/research-plan-routes-split.md
    - .harness/harness/features/FEAT-2489-plan-routes-split/observations/harness-pm.md
  must_fix: []
  branch: none
  escalations: []
  adequacy_notes:
  - "Checked against the send-back criteria written before dispatch, and all are met.\
    \ (1) SC-02's fifth item states the rule as a class: BRIEF.md:32 says 'not a list\
    \ of producers'. (2) The disclosed departure sits beside complete-install at BRIEF.md:61\
    \ and says it derives from items 1\u20133. (3) T-02 builds a relocation map for\
    \ exactly the changed rows (plan.yaml:280). It samples a relocated row by blanking\
    \ the reason on _classification_document::json_file#1 (:289), and it compares\
    \ by mapping the old lines and then requiring equality (:313). T-04 requires MAP\
    \ lines and never 'MAP none' (:477). (4) T-01's verify checks that the recorded\
    \ HEAD is an ancestor of HEAD and that rev-parse <HEAD>:test equals the recorded\
    \ BLOB. It never reads the live file (plan.yaml:180-182). The receipt is recorded\
    \ after the T-01 commit (:223)."
  - The relocation map rewrites only the identities of relocated inventory rows. A
    diagnostic formatted from the re-keyed T07 key or from a scanned_files entry is
    covered by the SC-02 class, but no T-02 sample exercises one. The class is the
    contract and the samples are evidence, so this is not a defect.
  - 'Dispositions at exit. Open: PF-241126189d3c3d16550a5f09c7532ff3, PF-6efa88c834c89ca43eea0322509703d9,
    and PF-5dbe6b5eecda5efa44c6d9624e826e1a (its residual is PF-6efa and it closes
    with it). Resolved: PF-b25f62af28d7aa5f31cd38d635041a54 and PF-0e9128df11c14ad97669b28ff451a725
    (confirmed closed by class at c2); PF-b963b10c2511cecf9ad0f6103be427ea and PF-29a7e86075e97f550fb37781a3eb389f
    (the c2 info records of those closures); PF-9bc751c71f94a87fdd29e84578ce6c1e,
    PF-293c2789a0a14408ae4b9f3ca8df9efb, PF-2f032ea4ded9ab191d46672327dac011 and PF-0dad747f115c481968d48fdfed6ec1e1
    (c1 proportionality and form, trimmed at c1 apply).'
  - The 0-failure plan-merge check result is pm's own run. This lead holds no shell
    and did not rerun it.
  - 'No prototype gate: the c1 design reader self-scoped out because the feature has
    no UI surface.'
  - No reader ran in this run. The readers entry records only the apply step, which
    the schema allows.
  sc_status: []
  needs_approval: true
  severity_max: high
  matrix_ok: none
  coverage_gaps: []
  findings:
  - kind: substance
    scope: none
    severity: high
    reader: harness-code-reviewer
    summary: 'PF-241126189d3c3d16550a5f09c7532ff3: SC-02''s closed delta list was
      unsatisfiable by the verbatim move. The class rule and the mechanical relocation-map
      evidence are now applied. The finding stays open until it is re-read.'
    why: A diagnostic formatted from a relocated row's file changes text under the
      required move.
  - kind: substance
    scope: none
    severity: med
    reader: harness-code-reviewer
    summary: 'PF-6efa88c834c89ca43eea0322509703d9: T-01''s green receipt was not bound
      to its checkpoint. The ancestor check and the blob-at-recorded-HEAD check are
      now applied. The finding stays open until it is re-read.'
    why: Without the binding, any green transcript with the HEAD/BLOB prefixes passes
      after T-03 makes the live run red.
  readers:
  - reader: apply
    status: ran
    persona: harness-pm
    reason: none
```
