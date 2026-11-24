# Validate c5 (final rework round 4): FEAT-2488 plan-merge atomicity: ESCALATE

**BLUF.** Reviewed at review_sha `45f16cfa9f5ceb063d3d12987e3a6824b5929f35` (base `2491336e`, delta `d4fab731..45f16cfa`).

**MF-11 and MF-12 are closed as the classes the c3 brief defined.** Every lens that probed them measured the closure:
- QA ran unit 68/68 and integration 95/95 once each, with PYTHONUNBUFFERED stripped. The DEC-255 receipts are in `qa/`.
- QA's c4 N-1 wedge probe now passes 6/6. An unreadable real journal still exits 5. QA killed its own mutants.
- The code-reviewer re-ran its c4 fd-1-closed-at-exec probe: rc 0 on both verbs.
- PM reports SC-01..07 met and all three perspectives passing. C4 is untouched and the signature stands.

**Two readers each raised a new high:**
- the code-reviewer's C1 (T-02);
- the security-reviewer's S1 (T-01).

I transcribe both at high, so `severity_max` is high and the gate reads FAIL. No round remains, and a FAIL would route a cycle that does not exist (G-06). This return is therefore **ESCALATE** to fable-advisor.

**My assessment.** I rate both findings med. Neither is a gating instance of the class contracts the terminal condition names. The descope remedies that condition prescribes do not address either finding: the stdio descope would leave C1 in place and would re-open what round 4 closed, and the condition defines no journal descope at all. Both readers' ratings are carried by name (P-04).

## Findings that gate on the readers' ratings (ranked)

1. **C1 · code-reviewer high · lead med · substance · T-02, `plan_merge/guards.py:331-341` (9b19ed55, 9ca2855b).**
   - **What was measured.** The code-reviewer ran `python3 -X warn_default_encoding -W error::EncodingWarning` on real signed `amend` and `record-amendments`, with a feedback checker present. `harness_boundary.py:501` calls `subprocess.run(text=True)` with no encoding, and that call raises EncodingWarning. EncodingWarning is outside `_STDIO_FAULTS`. Both files land once, the journal is removed, no receipt is printed, and the process exits 1.
   - **What I confirmed at source.** `_relay_after_commit` runs the whole relay inside `_emit("stderr", …)`, and the catch is exactly that tuple. `harness_boundary.py:494-501` catches only `(OSError, SubprocessError)`, and that line is unchanged from base.
   - **Why I rate it med:**
     - This is not a stdout or stderr state. The c3 brief's contract is "no state of stdout/stderr may change the exit code". It chose a tuple over `except Exception` on purpose and ruled exceptions from outside the tuple a contract breach by the caller.
     - It is reachable only when the operator opts into warnings-as-errors. A grep finds no `warn_default_encoding`, `PYTHONWARNINGS`, `EncodingWarning` or `-W error` anywhere in `.claude`, `.omp`, `.github` or `tests` in the worktree.
     - The line that raises sits in the unchanged `harness_boundary.py`. It is the same relay that the OQ-3 backlog already names for `feature_json_write.py:227`.
     - At base, the same trigger left a torn pair (rc 2). The pin's behaviour, both files landed and rc 1, is strictly less harmful.
   - **Retry risk.** A caller that sees rc 1 may re-run. That only re-amends if amend is non-idempotent on an already-ledgered amendment, which was not measured.

2. **S1 · security-reviewer high · lead med · substance · T-01, `check-domain.py:2610-2624` (fc69c032).**
   - **The finding.** The two-name denial judges only a Write's final component. A native Write below `plan.yaml.harness-merge.journal/` would implicitly create a directory at the real slot, and `_recover_journal`'s regular-file check then refuses every plan and ledger write at exit 5.
   - **What has been measured.** That the directory slot refuses at exit 5 is measured, by the code-reviewer and in a receipt. That the governed route can create the directory comes from **source inspection only**; nobody executed a governed write.
   - **Why I rate it med.** It meets the advisor's own c3 reconciliation of MF-12 on every axis: availability-only, recovered with one `rmdir`, and the same wedge is reachable through the backlogged Bash route.
   - **It is a different gap from MF-12.** MF-12 was discovery being wider than the producer set, and that is closed by construction. S1 is the general check-domain property that implicit parent creation is never judged. It applies to every name check-domain denies, not only to this journal, which makes it closer to the ruled Bash-route porosity backlog than to a new instance of the journal class.

## Assessed, not gating

- **Code med (T-02; residue pre-existing at base).** If fd 1 is closed after CPython has initialized `sys.stdout`, both verbs exit 120 after landing. `_silence` opens /dev/null as fd 1, dup2s it onto itself, then closes fd 1. Base also exits 120 in this case. This is the "MF-9 buffered-exit residue" that the c3 ruling already prices as acceptable risk.
- **QA G-1 (low).** No suite test runs a `_die` refusal under a None or broken stderr. QA's probe shows the pin is correct, while the 8f948c52 blob regresses. A regression lock belongs in the backlog.
- **QA G-2 (info).** Five joint stdio states are missing from `_STDIO_MATRIX`. QA ran all five through `_stdio_case`: 42 checks, 0 FAIL. EPIPE mid-write is unreachable because receipts are under 3.1 KB [INFERENCE, QA's].
- **PM OQ-c5-1 (form).** The verbatim OQ-3 wording says `feature_json_write.py:227` is "outside T-01's and T-02's files". However, T-02's files include `feature_json_write.py#write_feature_json`. The relay line itself is unchanged from base, so the ruling's substance holds; the wording needs correcting before the backlog ticket is filed.
- **SC-07.** Preservation discrimination is still unshown (a baseline lock only).
- **Not re-raised:** the ruled backlog (`feature_json_write.py:227` OQ-3, cited verbatim in the dispatch), Bash-route porosity, the c1 advisories, linked-worktree hardlink detection, and `RE_PAIR_JOURNAL` `$` vs `\Z`. D1 and D2 are as ruled.

## Adequacy

- QA's `suite: pass` rests on `qa/manifest-unit.json` (68) and `qa/manifest-integration.json` (95). Both ran with PYTHONUNBUFFERED stripped, with non-zero and unchanged discovery counts.
- QA re-ran the round-4 natural reds itself: 18 FAILs at the 8f948c52 guards.py and 27 FAILs plus one raise at the 8f948c52 harness_merge.py.
- PM and QA called both classes closed without probing C1's trigger or S1's route. The code-reviewer and security-reviewer probed outside the stated class contracts and found the two adjacent members (P-06).

## Decision for fable-advisor

The choices are:
- **(a)** Rule C1 and S1 not gating instances, backlog both, and ship. This is the lead's recommendation.
- **(b)** Apply the terminal descope. As written, it does not remedy either finding.
- **(c)** Stop.

Per-member artifacts: `notes/review-harness-{qa,code-reviewer,security-reviewer,ui-reviewer}-c5.md` and `notes/research-FEAT-2488-plan-merge-atomicity-goalcheck-validate-c5.md`.

```yaml
VERDICT: ESCALATE
artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2488-plan-merge-atomicity/.harness/harness/features/FEAT-2488-plan-merge-atomicity/runs/r-20261124-6-validate-validator/digest.md
DIGEST:
  headline: 'ESCALATE to fable-advisor at 45f16cfa. MF-11 and MF-12 are closed as
    the classes the c3 brief defined. CI is green with PYTHONUNBUFFERED stripped (unit
    68, integration 95), SC-01..07 are met and C4 is untouched. Two readers raised
    new highs, which I rate med: C1, where under an opt-in -W error::EncodingWarning
    the relay exits 1 after the commit (T-02), and S1, where the governed Write route
    could create a directory at the real journal slot, wedging writes at exit 5 (T-01,
    unexecuted). Neither is a stdio-state or discovery-class instance, and neither
    is remedied by the terminal descope.'
  files_touched:
  - .harness/harness/features/FEAT-2488-plan-merge-atomicity/runs/r-20261124-6-validate-validator/state.yaml
  - .harness/harness/features/FEAT-2488-plan-merge-atomicity/runs/r-20261124-6-validate-validator/qa/manifest-unit.json
  - .harness/harness/features/FEAT-2488-plan-merge-atomicity/runs/r-20261124-6-validate-validator/qa/manifest-integration.json
  team: validate
  steps_run: 5
  cycles_used: 0
  members:
  - step: qa
    persona: harness-qa
    verdict: PASS
    headline: Unit 68 and integration 95 green, each run once with PYTHONUNBUFFERED
      stripped. The N-1 wedge is closed 6/6 and an unreadable real journal still exits
      5. Natural reds reproduce at 18 and 27 FAIL, and QA's own mutants were killed.
      Two coverage gaps, neither gating.
    files_touched:
    - .harness/harness/features/FEAT-2488-plan-merge-atomicity/runs/r-20261124-6-validate-validator/qa/manifest-unit.json
    - .harness/harness/features/FEAT-2488-plan-merge-atomicity/runs/r-20261124-6-validate-validator/qa/manifest-integration.json
  - step: code
    persona: harness-code-reviewer
    verdict: FAIL
    headline: 'MF-12 closes and the c4 fd-1-closed probe now returns rc 0. A new high:
      an EncodingWarning raised as an error escapes the post-commit relay, so the
      verb exits 1 after both files land. A med: fd 1 closed after startup gives exit
      120, as it also did at base.'
    files_touched: []
  - step: security
    persona: harness-security-reviewer
    verdict: FAIL
    headline: 'Foreign-name discovery is closed. New high S1: a governed Write''s
      implicit parent creation could occupy the real journal slot as a directory,
      wedging writes at exit 5. Established by source inspection only.'
    files_touched: []
  - step: ui
    persona: harness-ui-reviewer
    verdict: PASS
    headline: 'Mode B scoped out by census: no UI among 187 paths changed from base
      or the 27 in the delta.'
    files_touched: []
  - step: goalcheck
    persona: harness-pm
    verdict: PASS
    headline: All 3 perspectives pass and SC-01..07 are met. Both classes are closed
      and round 4 stayed in scope. C4 is untouched and the signature stands.
    files_touched: []
  must_fix:
  - 'C1 (T-02, code-reviewer high, lead med, substance; guards.py:331-341, changed
    in 9b19ed55 and 9ca2855b): with python3 -X warn_default_encoding -W error::EncodingWarning
    and a feedback checker present, the call at harness_boundary.py:501, subprocess.run(text=True)
    with no encoding, raises EncodingWarning. That falls outside _STDIO_FAULTS, so
    both verbs land once, remove the journal and exit 1 without receipts. No round
    remains, so route to fable-advisor. The lead recommends a backlog ruling: it is
    not a stdout/stderr state, it needs an opt-in interpreter config that no harness
    surface sets, it is raised in unchanged harness_boundary.py (the same relay as
    OQ-3), and at base it left a torn pair at rc 2. The prescribed stdio descope does
    not remedy it.'
  - 'S1 (T-01, security-reviewer high, lead med, substance; check-domain.py:2610-2624,
    fc69c032): the two-name denial judges only a Write''s final component, so a native
    Write below plan.yaml.harness-merge.journal/ could implicitly create a directory
    at the real slot. Every plan and ledger write then refuses at exit 5. Governed
    reachability rests on source inspection only. Route to fable-advisor. The lead
    recommends a backlog ruling: it is availability-only, recovered by one rmdir,
    reachable on the Bash route as well, and it is a general check-domain property
    (implicit parent creation is never judged) rather than a discovery-class instance.
    The terminal condition defines no journal descope.'
  branch: none
  open_questions:
  - id: OQ-1
    question: 'Round 4 closed MF-11 and MF-12 as the c3 brief defined them, but two
      readers raised new highs. C1 (T-02): under an opt-in -W error::EncodingWarning,
      the relay exits 1 after the commit. S1 (T-01): an implicit parent directory
      created by Write could occupy the real journal slot and wedge writes at exit
      5. The lead rates both med and judges neither a gating instance of the stdio-state
      or discovery class. The terminal descope as written remedies neither: reverting
      to print-only leaves C1 and re-opens what round 4 closed, and no journal descope
      is defined. Options: (a) rule both not gating instances, backlog them, and ship
      (the lead''s recommendation); (b) apply the descope; (c) stop.'
    blocking: true
  - id: OQ-2
    question: The verbatim OQ-3 backlog wording says feature_json_write.py:227 lies
      'outside T-01's and T-02's files', but T-02's files include feature_json_write.py#write_feature_json
      (pm OQ-c5-1). The relay line itself is unchanged from base, so the substance
      holds. Should the wording be corrected before the backlog ticket is filed, and
      should that ticket also cover C1's harness_boundary.py:501 encoding?
    blocking: false
  escalations:
  - id: E-1
    raised_by: harness-code-reviewer
    question: 'C1: does an EncodingWarning raised as an error in the post-commit relay
      (rc 1 after commit, opt-in interpreter config) count as a gating instance of
      the stdio class under the terminal condition?'
    domain: FEAT-2488 terminal ruling (answers-2026-11-24-validate-c3.md)
    routed_to: harness-orchestrator -> fable-advisor
    resolution: pending
    decided_by: pending
    recorded_as: runs/r-20261124-6-validate-validator/digest.md C1
  - id: E-2
    raised_by: harness-security-reviewer
    question: 'S1: does a governed Write creating a directory at the real journal
      slot via implicit parent creation count as a gating instance of the journal
      class, given that it is unexecuted and has Bash-route parity?'
    domain: FEAT-2488 terminal ruling / check-domain.py enforcement
    routed_to: harness-orchestrator -> fable-advisor
    resolution: pending
    decided_by: pending
    recorded_as: runs/r-20261124-6-validate-validator/digest.md S1
  expertise_update: []
  adequacy_notes:
  - 'QA''s suite: pass rests on the DEC-255 receipts qa/manifest-unit.json (68) and
    qa/manifest-integration.json (95). Both ran once at 45f16cfa under env -u PYTHONUNBUFFERED,
    and the discovery counts are non-zero and unchanged.'
  - 'MF-11 closure was measured by the lens that raised it (the code-reviewer''s c4
    probe, rc 0 on both verbs) and by QA reproducing the 8f948c52 reds (18 FAIL).
    MF-12 closure was measured by its raisers: QA''s N-1 wedge 6/6, and security''s
    foreign-name trace.'
  - 'The lead confirmed C1''s sites in the worktree: _emit''s catch tuple at guards.py:270,
    the relay inside _emit at :331-341, and harness_boundary.py:494-501 catching only
    (OSError, SubprocessError). A grep of .claude, .omp, .github and tests finds no
    warn_default_encoding, PYTHONWARNINGS, EncodingWarning or -W error.'
  - 'Severity reconciliation: per the shape-only rule, reader highs are transcribed
    unchanged and severity_max is high. The lead''s med ratings, and the reasons for
    them, are carried alongside the readers'' ratings by name (P-04).'
  - QA and pm called both classes closed without probing C1's trigger or S1's route.
    The adjacent members were found only by the code-reviewer and security-reviewer
    probing outside the stated class contracts.
  - 'Non-gating: code med (fd 1 closed after startup gives exit 120, as it did at
    base; the MF-9 residue the c3 ruling priced as acceptable risk), QA G-1 (no regression
    lock for _die under a None or broken stderr), and QA G-2 (five joint states absent
    from the matrix, all 42 probe checks green).'
  - 'UI scoped out by a measured census: 187 paths base..pin and 27 in the delta,
    none of them UI.'
  sc_status:
  - id: SC-01
    verdict: met
    method: automated
    evidence: 2488/a, n and o, plus the unit journal matrix (202/202), are green in
      QA manifest-integration.json and manifest-unit.json at 45f16cfa with PYTHONUNBUFFERED
      stripped. The code-reviewer contests the advisory-after-commit clause under
      -W error::EncodingWarning (C1).
  - id: SC-02
    verdict: met
    method: inspection
    evidence: _emit and _silence only open, dup2 and close devnull; no mkstemp, os.replace
      or journal access (pm, code)
  - id: SC-03
    verdict: met
    method: inspection
    evidence: The locked_pair_update fsync ordering is untouched in the delta (harness_merge.py:538-597)
  - id: SC-04
    verdict: met
    method: automated
    evidence: 2488/g green at the pin; the code-reviewer independently measured exact
      receipt bytes
  - id: SC-05
    verdict: met
    method: inspection
    evidence: The test-plan-merge.py delta is +204/-0 and the successors are unchanged
  - id: SC-06
    verdict: met
    method: inspection
    evidence: The lock order plan.yaml.lock -> feature.json.lock is kept and documented
  - id: SC-07
    verdict: met
    method: automated
    evidence: The six suites are unedited base->pin and all green at the pin. Discrimination
      is unshown.
  needs_approval: true
  severity_max: high
  matrix_ok: true
  coverage_gaps:
  - No test runs the post-commit relay under -W error::EncodingWarning (C1)
  - No test covers a governed Write that creates a directory at the real journal slot
    via implicit parents (S1)
  - No regression lock runs a _die refusal under a None or broken stderr (QA G-1)
  - Five joint stdio states are absent from _STDIO_MATRIX; QA probed them green (G-2)
  - SC-07 preservation discrimination is unshown
  findings:
  - kind: substance
    scope: none
    severity: high
    reader: harness-code-reviewer
    summary: 'C1 T-02: an EncodingWarning raised as an error in the post-commit relay
      exits 1 after both files land (guards.py:331-341, harness_boundary.py:501)'
    why: 'Measured on both verbs. EncodingWarning is outside _STDIO_FAULTS. The lead
      rates it med: it is not a stdio state, needs an opt-in config that no harness
      surface sets, is raised in an unchanged module, and base left a torn pair.'
  - kind: substance
    scope: none
    severity: high
    reader: harness-security-reviewer
    summary: 'S1 T-01: implicit parent creation by a governed Write could occupy the
      real journal slot as a directory, wedging writes at exit 5'
    why: 'check-domain.py:2610-2624 judges only the final component. Reachability
      rests on source inspection only. The lead rates it med: availability-only, recovered
      by one rmdir, Bash parity, and a general check-domain property.'
  - kind: substance
    scope: none
    severity: med
    reader: harness-code-reviewer
    summary: 'T-02: fd 1 closed after startup gives exit 120 after landing (guards.py:280-288
      self-dup2 then close)'
    why: Base also exits 120. This is the MF-9 buffered residue the c3 ruling priced
      as acceptable risk. Not gating.
  - kind: substance
    scope: none
    severity: low
    reader: harness-qa
    summary: 'G-1: no regression lock for a _die refusal under a None or broken stderr'
    why: Behaviour at the pin is correct by QA's probe, and the 8f948c52 blob regresses.
      Backlog.
  - kind: form
    scope: none
    severity: low
    reader: harness-pm
    summary: The OQ-3 backlog wording says feature_json_write.py is outside T-02's
      files, but T-02 files include write_feature_json
    why: The relay line is unchanged from base, so the substance holds. Correct the
      wording before the backlog ticket is filed.
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
