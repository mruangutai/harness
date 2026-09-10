last_run: planpanel4-validator
cycle: 0
severity_max: high
note: >-
  Adversarial plan panel planpanel4-validator FAILED this signature draft at severity_max high:
  9 findings, 3 high / 5 low / 1 info, and NOTHING WAS DISMISSED ON MERIT. THE HEADLINE RESULT IS
  THE DISPOSITION ANSWER: all nine of the operator's batched findings (F-01..F-09) are genuinely
  ANSWERED in the written artifacts, verified independently by both readers against plan text and,
  for F-06, against merge-gate.py source - the "recorded answered but not answered" trap does NOT
  fire. Four prior findings (F-10 med, F-11/F-12/F-13 low) were never in the operator's Q1-Q4 batch,
  are genuinely NOT answered, and stay honestly open; each maps forward to a maintained finding
  below. The full previous-cycle disposition is carried in prior_cycle. No reader was skipped: scope
  (harness-code-reviewer) and should-not-exist (fable-advisor) both ran and both returned FAIL. The
  three highs (VL-01, VL-02, VL-03) reach the operator's batched signature review UNRESOLVED: no
  agent in this chain risk-accepted one and none may; risk acceptance is approval.rulings, the main
  session's write alone. TWO severities were reconciled UPWARD from the reader's own rating and both
  are recorded by name with their reason in severity_reconciliations; one finding (VL-04) was
  deduplicated across both readers; no severity was lowered and nothing was averaged. VL-04 is a
  panel RULING rather than an open defect. Fix-order relationships change what is being decided and
  are carried per row in fix_order; the rank order of the findings list IS the fix order. For the
  concrete change per finding, and for the assessed-and-not-re-raised set, read
  runs/planpanel4-validator/digest.md.
transcription_rule: >-
  Each PF- id is computed once by pm with panel_findings.py id --reader <reader> --summary <summary>,
  taking the row's own reader and summary values verbatim as recorded here. Severities, reporters and
  dispositions are the panel digest's; nothing was re-ranked, re-worded into a different claim, merged
  or given a disposition the digest does not state.
severity_reconciliations:
  - finding: VL-02
    from: med
    to: high
    raised_by: lead (planpanel4-validator)
    reason: >-
      The reader (should-not-exist, finding 2) marked the CI-is-shallow premise [unverified]. The lead
      verified it at source: .github/workflows/tests.yml:50 is actions/checkout@v4 with NO fetch-depth,
      so the default depth-1 shallow clone applies, and the job id integration is the SOLE required
      branch-protection context.
  - finding: VL-03
    from: med
    to: high
    raised_by: lead (planpanel4-validator)
    reason: >-
      It makes N-12's own verify unpassable for a correct implementation of N-06 - the unmeetable-census
      shape the previous panel rated high and the operator's own measurement confirmed.
  - finding: VL-04
    from: none
    to: none
    raised_by: lead (planpanel4-validator)
    reason: >-
      Not a severity change: VL-04 was DEDUPLICATED across both readers (should-not-exist finding 3 and
      scope Point 7 ruling), which rule the same way. Across this panel no severity was lowered and
      nothing was averaged.
readers:
  - reader: scope
    persona: harness-code-reviewer
    status: ran
    verdict: FAIL
    artifact: notes/review-harness-code-reviewer-planpanel-c1.md
  - reader: should-not-exist
    persona: fable-advisor
    status: ran
    verdict: FAIL
    findings_returned: 8
    artifact: runs/planpanel4-validator/digest.md
    note: >-
      No write grant: it resolved on this host and returned the required findings shape, so on_fail
      never applied, but its eight findings are transcribed in runs/planpanel4-validator/digest.md and
      here rather than in an artifact of its own.
findings:
  - id: PF-f0281057320f2984492f8fba14508156
    label: VL-01
    severity: high
    reader: scope
    reporter: scope (NEW-01); premises re-verified by lead at source
    lands_on: N-11 PART 1 + PART 5, REQ-08, SC-15
    summary: >-
      N-11 PART 1 orders the hardlink scan to REFUSE when the corpus root cannot be resolved and N-10
      specifies corpus_root() to RAISE, but _hardlink_plan wraps only os.stat in try/except at
      check-domain.sh:1907-1922, the glob line N-11 rewrites sits outside it, and _plan_route's sole
      caller at :1949 is bare, so the raise propagates uncaught, Python exits 1, and the file's own
      header at :14 states that only exit 2 blocks while exit 1 is a NON-blocking error and the write
      proceeds - the very write SC-15 exists to deny. No case in N-11 PART 4/5 exercises it, unlike
      N-07 PART 4(d) and N-10 PART 5 which both force it for their sites, and it fires precisely when
      st_nlink >= 2, the hardlink case itself.
    fix_order: >-
      rank 1 of the digest fix order; independent of VL-02 and VL-03 and one edit
    disposition: >-
      open - unresolved and carried to the operator's batched signature review. No agent in this chain
      risk-accepted it and none may; risk acceptance is approval.rulings, the main session's write alone.
  - id: PF-9e4a874e461968f2eb1d6be6e7f759b5
    label: VL-02
    severity: high
    reader: should-not-exist
    reporter: >-
      should-not-exist (finding 2, at med with the CI premise [unverified]); premise resolved and
      severity reconciled UP to high by the lead
    lands_on: N-09 PART 3 clauses 2-3, SC-12, SC-13, D-13
    summary: >-
      The pinned form is durable against F-05's failure but not against object availability. Measured,
      not inferred: .github/workflows/tests.yml:50 is actions/checkout@v4 with no fetch-depth, so the
      default depth-1 shallow clone applies, and that job runs run-unit-tests.sh --kind integration
      where test-nonregression-baseline.py lands. Clause 3 runs git diff --name-only
      pre_change_sha..review_sha against the real repository and asserts exit status 0, and clause 2
      asserts pre_change_sha is an ancestor of review_sha; neither object exists in a depth-1 clone, so
      both fail red. The SELF-SCOPE skip cannot save it because it fires only when a literal is absent
      or not 40 hex, never when the literal is present but unresolvable. The job id integration is the
      sole required branch-protection context with enforce_admins true, so this reds every PR in the
      repository including FEAT-58's own, and it falsifies SC-12's own claim that a CI runner behaves
      exactly as today and the existing suites gain no failure.
    fix_order: >-
      rank 2 of the digest fix order; independent of VL-01 and VL-03 and one edit
    disposition: >-
      open - unresolved and carried to the operator's batched signature review. No agent in this chain
      risk-accepted it and none may; risk acceptance is approval.rulings, the main session's write alone.
  - id: PF-06cff062432fa2a378c86f484546aa67
    label: VL-03
    severity: high
    reader: should-not-exist
    reporter: should-not-exist (finding 1, at med); severity reconciled UP to high by the lead
    lands_on: N-06 PART 2, N-12, SC-14
    summary: >-
      Two tasks give contradictory orders about one comment. N-06 PART 2 mandates the marker
      corpus-scope: owner-root on the linked_worktrees fix in harness_boundary.py, a site N-12's
      narrowed subject cannot detect because it enumerates .git/worktrees with no features segment, and
      harness_boundary.py is absent from the measured 8-file census list. N-12 then asserts that every
      owner-root marked site sits in a file that NAMES feature_corpus, a different quantifier from its
      own preceding every-detected-site clause. Under the natural marker reading HALF 1 reds on
      harness_boundary.py with no authorised fix, since feature_corpus imports harness_boundary so the
      reverse naming is circular and deleting the marker defies N-06 - the unmeetable-census shape GC-01
      was just fixed for, reintroduced. Under the detected-sites reading the mandated marker is
      wrong-vocabulary decoration no test ever reads.
    fix_order: >-
      rank 3 of the digest fix order; independent of VL-01 and VL-02 and one edit, but it MUST land
      before any implementer opens N-12 because it changes what that task's test asserts
    disposition: >-
      open - unresolved and carried to the operator's batched signature review. No agent in this chain
      risk-accepted it and none may; risk acceptance is approval.rulings, the main session's write alone.
  - id: PF-5d6b94e681529c8c10a29ace089faf1b
    label: VL-04
    severity: low
    reader: both
    reporter: >-
      both readers - should-not-exist (finding 3) and scope (Point 7 ruling), deduplicated by the lead
    lands_on: N-12, SC-14
    summary: >-
      PANEL RULING on the question pm invited, given independently by both readers and deduplicated into
      one finding. check-domain.sh:1052-1062's _SWEEP_PATTERNS is a list of pattern strings consumed
      through a for-loop binding, and N-12 resolves one level of assignment indirection only, so the
      canonical checkout-local instance falls outside HALF 1 by construction. Both readers rule the same
      way, ACCEPTABLE AS SCOPED: build no list-indirection resolver and leave the site undetected and
      unmarked, because D-02 already rules that site correctly checkout-scoped and untouched and a
      resolver is machinery for one hypothetical future site. The single requirement carried by the
      ruling is that the accepted blind class - list-valued and for-loop pattern indirection - be named
      in N-12's intent, in the artifact the operator signs, because any future narrowing enumeration
      written in that spelling escapes HALF 1 silently.
    fix_order: >-
      rank 4 of the digest fix order; folds into the SAME N-12 edit as VL-03 - one visit to that task
      discharges both
    disposition: >-
      ruling, not an open defect - both readers independently ruled the _SWEEP_PATTERNS list-indirection
      blind class ACCEPTABLE AS SCOPED: build no resolver, leave the site unmarked. The ruling's one
      requirement is outstanding: name the accepted blind class in N-12's intent, in the artifact the
      operator signs.
  - id: PF-20fa406d84f713a4a16e046acaa5180f
    label: VL-05
    severity: low
    reader: should-not-exist
    reporter: should-not-exist (= F-10 maintained, reduced)
    lands_on: N-09 change_type
    summary: >-
      F-10 maintained and reduced. N-09's parser cases are now behavioral - none-vs-absent, verbatim
      compare, 40-hex guard - which retires the pins-internals half of the original finding. What stands
      is that N-09 carries change_type: cross_module with zero production files in its files:, the label
      that manufactures the unit-kind requirement the parser file exists to satisfy, while N-08 was
      relabelled from config to scaffolding for exactly that shape in the same batch, so the plan applies
      its own rule inconsistently across two adjacent tasks.
    fix_order: >-
      rank 5 of the digest fix order; one of the four unaddressed prior findings, mutually independent
    disposition: >-
      open - F-10 maintained. Never in the operator's Q1-Q4 batch, so it is still honestly owed; low,
      and it does not gate this panel.
  - id: PF-e73f4795ba116f730872c14a973d41d8
    label: VL-06
    severity: low
    reader: should-not-exist
    reporter: should-not-exist (= F-11 maintained)
    lands_on: N-01 EXCLUSION 1
    summary: >-
      F-11 maintained. N-01 EXCLUSION 1 still embeds runtime plan.yaml parsing, the list-equals-plan set
      comparison, and non-strict PENDING accounting into f58_sparse_fixture.py, baking the plan's
      location and task-file schema into the one module every integration test imports, to deliver what
      a literal list plus a --strict existence failure already delivers.
    fix_order: >-
      rank 6 of the digest fix order; one of the four unaddressed prior findings, mutually independent
    disposition: >-
      open - F-11 maintained. Never in the operator's Q1-Q4 batch, so it is still honestly owed; low,
      and it does not gate this panel.
  - id: PF-f0a7225dad2cb03b19e82094f4e51448
    label: VL-07
    severity: low
    reader: should-not-exist
    reporter: should-not-exist (= F-12 maintained, premise re-verified)
    lands_on: D-10, N-02 scope guard
    summary: >-
      F-12 maintained, premise re-verified. The DoD note states verbatim that a QA probe worktree now
      gets stripped automatically without QA knowing. N-02's _ID_RE scope guard no-ops on any basename
      that is not a feature id and probe trees are named qa-*, so they keep the full replicated corpus.
      The guard is right; the residual is recorded in neither D-10's because nor N-02's scope-guard
      block, so the operator is asked to sign a sentence the plan deliberately does not deliver.
    fix_order: >-
      rank 7 of the digest fix order; one of the four unaddressed prior findings, mutually independent
    disposition: >-
      open - F-12 maintained. Never in the operator's Q1-Q4 batch, so it is still honestly owed; low.
      Only the operator can amend or knowingly keep the DoD sentence.
  - id: PF-f7a5ff34454ade8140ab5219a5b26687
    label: VL-08
    severity: low
    reader: should-not-exist
    reporter: should-not-exist (= F-13 maintained; GC-03 concurs)
    lands_on: SC-01, SC-09, SC-11, SC-13, SC-14, SC-15
    summary: >-
      F-13 maintained, GC-03 concurring. Test-construction language survives against the operator's own
      shape rule and grew with the two new criteria - demonstrated first, asserted by the invocation it
      records, never as one aggregate, BOTH the stdout and the exit status asserted - across SC-01,
      SC-09, SC-11, SC-13, SC-14 and SC-15. Each clause already exists verbatim in the owning task's
      intent, so the SC copies constrain nothing and give a future amendment two places to drift.
      Coverage-safe: the previous panel verified each survives in N-05, N-06 PART 3, N-04 PART 2 and
      N-09 clause 3.
    fix_order: >-
      rank 8 of the digest fix order; one of the four unaddressed prior findings, mutually independent,
      and the only one carrying an accept-it-explicitly-in-approval.rulings arm, which is the operator's
      to take and not this chain's
    disposition: >-
      open - F-13 maintained. Never in the operator's Q1-Q4 batch, so it is still honestly owed; low.
      Its second arm - recording F-13 as explicitly accepted in approval.rulings instead of striking the
      clauses - is the operator's alone and is not taken here.
  - id: PF-00b183e742cf12a05cc19b0c25adce83
    label: VL-09
    severity: info
    reader: should-not-exist
    reporter: should-not-exist (finding 8); verified by lead
    lands_on: this cycle's panel record and the signature packet
    summary: >-
      RECORD ACCURACY, and it corrects this panel's own dispatch premise. The dispatch stated that the
      goal-check has been re-run and is clean; it had not been.
      notes/research-FEAT-58-goalcheck-plan-c3.md is the PRE-fix grade and carries GC-01 at high and
      GC-02 at med as live findings, fixgoalcheck-product then applied both remedies, so NO goal-check
      has graded the post-fix draft. Substance is not in question: the panel verified both remedies
      landed at source - N-12 and SC-14 carry the narrowed subject, and .harness/corpus is in
      REQUIRED_PATHS, N-05 group 2 and SC-01, each as its own named assertion - so only the record's
      lineage is wrong. The record must state that lineage precisely rather than re-run clean.
    fix_order: >-
      rank 9 of the digest fix order; it changes no task - it changes what the signature packet says
      about itself
    disposition: >-
      open - record correction, carried so the signature packet states its own lineage honestly:
      goal-check c3 FAILED GC-01/GC-02 on the pre-fix draft, both remedies were verified landed at
      source by this panel, and no post-fix goal-check has run.
prior_cycle:
  last_run: planpanel3-validator
  count: >-
    9 of 13 answered, verified independently by both readers in the written artifacts. 4 of 13 (one med,
    three low) genuinely unaddressed and honestly recorded as open; they were never in the operator's
    Q1-Q4 batch and each maps forward to a maintained finding in this cycle.
  carried_because: >-
    This mapping replaced the planpanel3-validator record whose 13 findings all stood at disposition
    open. That disposition is the operator's evidence that their batched answers landed, so it survives
    the replacement here rather than being discarded by it.
  findings:
    - label: F-01
      severity: high
      disposition: ANSWERED
      evidence: >-
        All nine choke points sit in a task with shape stated - N-06 P1 (check-state.sh, narrow+refuse)
        and P2 (harness_boundary.py:151-174), N-07 (merge-gate.py), N-10 four read sites, N-11 two
        gates. The trap is covered: N-11 PART 5 case (c) asserts the branch gate still ALLOWS a legal
        flow Y absent from the worktree, before the deny clause and for that reason.
    - label: F-02
      severity: high
      disposition: ANSWERED
      evidence: >-
        No persisted index survives anywhere - no generator, hook, staleness test, --check or cache.
        Every feature-index mention outside the frozen panel record is D-01's recorded deletion or an
        explicit prohibition (N-07, N-08). The replacement refusal is the deny payload.
    - label: F-03
      severity: high
      disposition: ANSWERED
      evidence: >-
        N-09's verify: carries no inline git diff; PART 3 clause 3 is the single discharge site; every
        Arm A carve-out struck.
    - label: F-04
      severity: high
      disposition: ANSWERED
      evidence: >-
        N-06 PART 3 (c) demoted to a one-time receipt proof under PRE-CHANGE REPRODUCTION; the task
        cannot pass until the heading carries a verdict.
    - label: F-05
      severity: high
      disposition: ANSWERED
      evidence: >-
        N-09 PART 3 clause 3 pins both endpoints to immutable literals and self-scopes with a named skip
        line. Durable against the failure F-05 named - but see VL-02 for a different failure the pinned
        form does not survive.
    - label: F-06
      severity: high
      disposition: ANSWERED, re-verified at source
      evidence: >-
        grep -c sys.exit merge-gate.py = 0; deny() at :144-145 prints the claimed JSON. D-01 and N-07
        assert the payload, never an exit.
    - label: F-07
      severity: med
      disposition: ANSWERED
      evidence: >-
        N-09 PART 1 (b) demoted to AUDIT UNCHANGED, pinned to pre_change_sha; (a)(c)(d) standing.
    - label: F-08
      severity: med
      disposition: ANSWERED (dissolved)
      evidence: >-
        No file is written anywhere, so the cone question has no subject. The raiser concurs with the
        dissolution reasoning as written.
    - label: F-09
      severity: med
      disposition: ANSWERED
      evidence: 'N-06 depends_on: [N-01, N-02].'
    - label: F-10
      severity: med
      disposition: NOT ANSWERED
      forward_maps_to: VL-05
      evidence: >-
        N-09 still change_type: cross_module with the full 4-case parser suite.
    - label: F-11
      severity: low
      disposition: NOT ANSWERED
      forward_maps_to: VL-06
      evidence: >-
        N-01 EXCLUSION 1 still carries the runtime list-equals-plan comparison and non-strict PENDING
        mode verbatim.
    - label: F-12
      severity: low
      disposition: NOT ANSWERED
      forward_maps_to: VL-07
      evidence: >-
        The accepted residual appears nowhere in D-10 or N-02; the only occurrence in plan.yaml was the
        previous panel's own transcription.
    - label: F-13
      severity: low
      disposition: NOT ANSWERED
      forward_maps_to: VL-08
      evidence: >-
        Construction language survives in SC-01/09/11/13 and grew into SC-14/SC-15. GC-03 independently
        re-found it.
