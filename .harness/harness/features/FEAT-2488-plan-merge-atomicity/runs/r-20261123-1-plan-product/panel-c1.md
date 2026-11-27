# FEAT-2488 independent plan panel — cycle 1

Scope (harness-code-reviewer) requests four substance repairs (three high, one med) and one form repair; should-not-exist (fable-advisor) requests four task-scope proportionality trims (two low, two info), nothing gating; design (harness-ui-reviewer) self-scoped out — no user-facing surface, no prototype required. No `scope: mission` finding: no mission downgrade. Scope note: `notes/review-harness-code-reviewer-plan-c1.md`; design note: `notes/review-harness-ui-reviewer-plan-c1.md` (both under this feature). Advisor findings transcribed verbatim from its terminal return (it self-labelled its persona `second-opinion-advisor`; the dispatched agent is `fable-advisor`). The scope reader labelled its findings `code-reviewer`; they are recorded under its step id `scope`. Severities, kinds, summaries and whys are the readers' own, unchanged.

Lead note on one tension, for pm's disposition at apply: scope endorses running recovery from `guards._resolve_plan` before the lock-free preflight (its note, §"Scope checks and rulings"); should-not-exist finding 1 calls that hook outcome-redundant. pm decides with evidence: keep the hook only if a lock-free preflight refusal (amend / record-amendments re-run) can pre-empt the locked recovery — the draft's own D-02 rationale — and say so in the disposition; otherwise trim it.

```yaml
DIGEST:
  severity_max: high
  readers:
    - reader: scope
      status: ran
      persona: harness-code-reviewer
      reason: Reviewed pending draft scope, traceability, architecture and decision dispositions; ruled OQ-1 (keep approval.py BRIEF rename migration) and OQ-2 (allow one inventory row); repairs below.
    - reader: should-not-exist
      status: ran
      persona: fable-advisor
      reason: Challenged unnecessary work against the grilling ruling, verifying in the PRODUCT checkout; mission proportionate, four task-scope trims, nothing gating.
    - reader: design
      status: ran
      persona: harness-ui-reviewer
      reason: Self-scoped out in Mode A; plan changes file recovery and CLI diagnostics only, no end-user interaction flow, no DESIGN.md or prototype required.
  findings:
    - kind: substance
      scope: none
      severity: high
      reader: scope
      summary: T-01 can replay or unlink a replaced journal generation.
      why: The journal is read before locking, then checked only for existence. If one writer finishes J1 and another dies with J2 pending, a delayed recovery can falsely reject J2 as divergent or unlink it. Validate the current journal under the replay locks and test replacement and disappearance deterministically.
    - kind: substance
      scope: none
      severity: high
      reader: scope
      summary: T-02 reports transaction outcomes from a racy pathname check.
      why: After locks release, another writer can finish recovery before the consumer checks the path, yielding a false 'nothing was written' receipt. The core must report transaction outcome. A post-commit feedback exception also still aborts the CLI before APPLIED; pin that outcome separately.
    - kind: substance
      scope: none
      severity: high
      reader: scope
      summary: T-02 final verification omits three SC-07 suites.
      why: Observations, expertise and inflight-registry run against T-01 or the base but are absent from the terminal verify. Their base or predecessor results do not establish a pass at the final pin.
    - kind: substance
      scope: none
      severity: med
      reader: scope
      summary: Pin a schema-valid feature.json mutation in T-02 case (e).
      why: The proposed unrelated new key is unspecified and the schema rejects unknown top-level fields. A known valid mutation plus an exact assertion proves the ordinary writer proceeds after recovery.
    - kind: form
      scope: none
      severity: low
      reader: scope
      summary: Record DEC-230 as keep.
      why: The changed ledger path implements the amendment judgement premise that INV-40 relies on without changing signed hashes or the invariant. No decision requires amendment or strike.
    - kind: proportionality
      scope: task
      severity: low
      reader: should-not-exist
      summary: T-02's preflight recovery hook (_resolve_plan recover=True, item 3) is outcome-redundant with the recovery already inside locked_update and locked_pair_update and should not be built
      why: >-
        Verified every mutating verb funnels through _locked_plan_update -> harness_merge.locked_update (guards.py:229-233) or write_plan_and_ledger, whose T-01 bodies recover the journal before any transform runs; and every transform recomputes under the lock from the recovered base with its own CAS or compare-and-splice (amend.py:283-285 _require_locked_hash, amendments.py _amended_plan_bytes on `was`, approval.py:321-327 hashes "computed from the very bytes being signed"), so every SC-01 convergence-and-exit-6 outcome lands identically without the preflight call. Building it anyway buys only nicer pre-lock messages (--show, preflight refusals) at the cost of a second production recovery site, a recover= parameter, and a check.py special-case (T-02 item 4) that exist solely to feed it — two recovery entry points to keep consistent forever, and a lock-free call that can race anyway (a journal can appear after it runs, which is exactly why locked_update loops).
    - kind: proportionality
      scope: task
      severity: low
      reader: should-not-exist
      summary: SC-03's mandatory call-recording fsync-ordering unit test over-builds where the grilling explicitly allowed "a test or code anchor cited"
      why: >-
        The grill's SC-03 seed (Q5) sanctions a cited code anchor as sufficient evidence that the journal is fsync'd before the first rename; the BRIEF hardens this into a required monkeypatch test recording the exact sequence of the core's os-level calls plus a QA red-first demonstration. Such a test couples the suite to internal call structure, not behavior: a behaviorless refactor of the write path (e.g. a different fd/fsync idiom) breaks it and costs a maintainer a test rewrite with zero durability information gained, while the torn-state tests of SC-01 already prove the only ordering property a user can observe.
    - kind: proportionality
      scope: task
      severity: info
      reader: should-not-exist
      summary: D-02's broadening of recovery to every harness_merge write in the directory makes a diverged journal block unrelated writers — blast radius beyond the grill's "every acquirer of the plan lock" that the pair's atomicity does not need
      why: >-
        T-01 item 6 runs recover_journal unconditionally before any locked_update in the directory, and the JOURNAL UNREADABLE/DIVERGED refusal states "every harness_merge write in this directory refuses". The grill (Q2) scoped recovery to plan-lock acquirers; the BRIEF extends to feature.json writers (justified — D-02's feature.json-only-writer rationale is real, verified via _record_rework writing feature.json before the plan lock at approval.py:308-313); but the further step means a non-member write in the feature directory (e.g. an observations or notes-file merge living beside plan.yaml) is bricked at exit 5 by a torn amendment it did not create and is not party to, until an operator hand-reconciles. Divergence requires manual tampering so this is rare, but the consequence should be consciously accepted or the refusal narrowed to member writes, not inherited silently from a uniform-rule convenience.
    - kind: proportionality
      scope: task
      severity: info
      reader: should-not-exist
      summary: T-02's six-suite baseline run in the detached base worktree (baseline-t02-regression-base.txt) is receipt ritual duplicating evidence the pin already carries
      why: >-
        SC-07's information content is "these suites pass at the review pin without assertion edits"; re-running test-harness-merge, test-feature-json-merge, test-observations-merge, test-expertise-merge, test-inflight-registry and test-check-state-feat59 inside the base worktree proves only that main was green at 2491336e, which the repo's required CI gates already establish for main [unverified that CI ran at that exact SHA]. The red torn-state runs and SC-04's stdout baseline genuinely need the base worktree (grill-mandated failure-first), but the marginal six-suite replay adds per-task operator minutes and note artifacts with no decision value to the reviewer.
```
