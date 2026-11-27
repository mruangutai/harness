# Distill — validator squad — FEAT-2488 plan-merge atomicity: PASS

**BLUF.** Four personas distilled, 13 ops applied in 6 batches, every section count at or under its cap. No diff was reviewed and no suite was run (distill mission).

| Persona | Tier | Ops | Batch | Counts before → after |
|---|---|---|---|---|
| harness-qa | craft | replace P-11, P-07, G-09, G-11 | ea6bdcfb… | P 15→15, G 15→15, O 10→10, Open 1→1 |
| harness-qa | repo `harness` | add G-14 | 76aafb91… | G 13→14 |
| harness-code-reviewer | craft | replace P-08, O-04, G-07 | 0a485827… | P 15→15, G 15→15, O 10→10, Open 0→0 |
| harness-security-reviewer | craft | replace P-14, O-08 | bef98f3b… | P 15→15, G 15→15, O 10→10, Open 0→0 |
| harness-validator-lead | craft | replace P-04, P-12, G-03 | c1f5b710… | P 15→15, G 15→15, O 10→10, Open 0→0 |

harness-pm goalcheck was not dispatched. Its only relayed candidate (one probe beyond the class contract before saying "closed") is already pm P-19 from the product distill, and pm's log was distilled there.

## Relayed-candidate dispositions (members judged)

- **qa.** Applied: probe beyond the contract (P-11); fixture state inside the contract window (G-09); CI env and interpreter parity (G-11). From its own log: old-blob/pin red (P-07, sharpened) and the BIN override for mutants (repo G-14). Rejected: "run the whole kind" and "prove the env strip load-bearing", both judged already covered by existing G-04, G-03 and P-09.
- **code-reviewer.** All three applied: the class state map plus a boundary probe (P-08); terminal adjacency evidence (O-04); an explicit child environment for exit-status claims (G-07).
- **security-reviewer.** Applied: comparing the discovery, producer and reserved name sets, and checking every implicit path component (P-14); routing evidence for adjacent findings (O-08). Rejected the mandatory execute-before-high rule: live execution is not a severity prerequisite, and its O-04 already separates demonstrated links from inferred ones.

## Lead's own lessons

- **P-04, sharpened.** The c5 escalation was decidable because both ratings were carried by name, and the lead also showed that the prescribed descope remedied neither finding. The ruling adopted both points.
- **P-12, generalized.** A must-fix for a defect class hands down the full state matrix and asks for a discriminating mutant per cell. Under instance-scoped briefs, both classes closed only one member per round.
- **G-03, sharpened.** My c3 to c5 digests said "CI is green" when the evidence was receipts from host runs. CI on Python 3.14 later failed, because the host's colour env had masked the failure. Host receipts should be reported as host runs.

## Assessment

- Every member applied ops within its caps, and each displacement carries a reason.
- QA's repo G-14 names env-var overrides and a scratch layout. That is close to a recipe, but it points at living overrides (test-plan-merge.py and check_domain_support.py), so I accept it as a repository fact. I did not open the member files beyond the receipts; the counts come from tool results.
- Nothing gates.

```yaml
VERDICT: PASS
artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2488-plan-merge-atomicity/.harness/harness/features/FEAT-2488-plan-merge-atomicity/runs/distill-validator/digest.md
DIGEST:
  headline: 'Validator-squad distill done: qa, code-reviewer, security-reviewer and
    the lead applied 13 ops in 6 batches. All craft counts are unchanged at P15/G15/O10
    (qa Open 1); qa''s repo-tier Gotchas went 13->14. pm was skipped because P-19
    already covers its candidate. No diff reviewed, no suite run.'
  open_questions: []
  files_touched:
  - .harness/expertise/harness-qa.md
  - .harness/harness/expertise/harness-qa.md
  - .harness/expertise/harness-code-reviewer.md
  - .harness/expertise/harness-security-reviewer.md
  - .harness/expertise/harness-validator-lead.md
  - .harness/harness/features/FEAT-2488-plan-merge-atomicity/runs/distill-validator/state.yaml
  expertise_update:
  - persona: harness-qa
    op: replace
    target: P-11
    section: Patterns
    entry: "WHEN reporting a defect class closed DO run at least one probe one boundary\
      \ beyond the stated class contract (adjacent configuration, caller, route or\
      \ write target) and name that boundary in the claim \u2014 measuring only inside\
      \ the contract leaves adjacent members for later rounds and other reviewers\
      \ to find."
    why: 'Lead-relayed (ship ruling Distill): QA called stdio/journal classes closed
      measuring only inside the contract; reviewers found adjacent members outside
      it. Displaces old P-11 (whole-file grep -q), which P-02''s vacuous-substring
      rule and G-05 already cover.'
  - persona: harness-qa
    op: replace
    target: P-07
    section: Patterns
    entry: "WHEN fail-first needs a pre-fix red and source edits are refused DO load\
      \ the old blob (`git show <sha>:<path>`) into a fresh in-process module, or\
      \ check the new tests into an old-SHA pin \u2014 cases spawning subprocesses\
      \ re-import from disk, so only the pin reddens them."
    why: 'Own log: in-process old-blob reproduction matched the builder red except
      the subprocess-probe cases, which re-import the pinned module from disk; sharpens
      P-07 without growing it.'
  - persona: harness-qa
    op: replace
    target: G-09
    section: Gotchas
    entry: "WHEN a fixture imposes hostile state for a windowed contract (e.g. post-commit\
      \ stdio) DO produce it the way real callers can and apply it inside the window\
      \ \u2014 state imposed earlier exercises unrelated phases whose behaviour varies\
      \ by host environment, so the fixture passes locally and crashes elsewhere."
    why: 'Lead-relayed (CI fixture ruling): closing the stream object before startup
      passed locally but crashed CI''s earlier argparse phase. Displaces G-09 (exact
      enum tokens), now enforced by the digest validator itself.'
  - persona: harness-qa
    op: replace
    target: G-11
    section: Gotchas
    entry: "WHEN claiming a run independent of the parent session or equivalent to\
      \ CI DO run every CI interpreter version and pin or diff the environment the\
      \ tooling and interpreter themselves read (project-root vars, colour/TERM, buffering)\
      \ \u2014 stripping one variable leaves host settings that mask failures CI will\
      \ hit."
    why: 'Lead-relayed (CI fixture ruling): host NO_COLOR/TERM=dumb masked a 3.14
      CI crash. Generalizes old G-11 (inherited project-root vars) into one env-parity
      rule, same length.'
  - persona: harness-qa
    op: add
    target: G-14
    section: Gotchas
    entry: "WHEN a mutant or old blob must drive test-plan-merge.py or the check-domain\
      \ integration tests DO set PLAN_MERGE_BIN / CHECK_DOMAIN_BIN to a /tmp scratch\
      \ tree mirroring bin/, schemas/ and .harness/team-config.yaml \u2014 those tests\
      \ honour the overrides, and root resolution needs team-config."
    why: 'Own log: the overrides let mutants run under the pin''s own tests without
      refused source edits; confirmed both env names in tests/integration (test-plan-merge.py:37,
      check_domain_support.py:32).'
  - persona: harness-code-reviewer
    op: replace
    target: P-08
    section: Patterns
    entry: WHEN re-reviewing a fix meant to close a defect class DO map the contract's
      distinct states across phase changes, probe the exception families the guard
      excludes, and test one reachable case beyond the boundary. A passing replay
      of the original failure closes that instance, not the class.
    why: 'Replaces a broad omission prompt with a concrete action for class closure:
      the closed object, buffered shutdown, and missing-at-exec cases survived different
      instance fixes.'
  - persona: harness-code-reviewer
    op: replace
    target: O-04
    section: Outcomes
    entry: WHEN reporting a finding adjacent to a terminal closure class DO separate
      its consequence from class membership. Name the triggering state and its reachability,
      whether the faulting line changed, and what identical input does at base. Route
      the evidence to the ruling tier rather than requesting another fix round.
    why: 'Displaces generic defect-class labeling with the facts that settled the
      final dispute: healthy streams, an opt-in trigger, an unchanged source line,
      and a less harmful pinned outcome.'
  - persona: harness-code-reviewer
    op: replace
    target: G-07
    section: Gotchas
    entry: WHEN a CLI exit-status claim depends on buffering or shutdown DO measure
      the real child through termination with interpreter flags and relevant environment
      explicit. Remove inherited overrides to establish the default case, then measure
      supported overrides separately; an unbuffered green run cannot establish buffered
      shutdown behavior.
    why: Buffered and unbuffered children exited differently after the same write.
      This replaces a deletion-sweep reminder already covered by the retained sweep
      patterns.
  - persona: harness-security-reviewer
    op: replace
    target: P-14
    section: Patterns
    entry: WHEN auditing filesystem recovery discovery DO compare the names discovery
      trusts, the names legitimate producers emit, and the names write authorization
      reserves; check every path component a write can implicitly create, not just
      its final component.
    why: The review exposed successive mismatches across producer, discovery and gate,
      including a reserved name reachable through implicit parent creation. This reusable
      boundary check displaces the narrower credential-sweep reminder.
  - persona: harness-security-reviewer
    op: replace
    target: O-08
    section: Outcomes
    entry: WHEN a terminal review uncovers a finding adjacent to a named class DO
      route it to the ruling tier with the class-defining evidence, impact, recovery
      cost, parity with previously ruled routes, and which links were executed versus
      inferred; do not assume a class-specific remedy applies.
    why: The terminal ruling distinguished the closed discovery contract from an availability-only
      perimeter gap. Explicit routing evidence is more useful than forcing independent
      reviewers to share a severity.
  - persona: harness-validator-lead
    op: replace
    target: P-04
    section: Patterns
    entry: "WHEN you rate a gating finding lower than its raiser and no squad may\
      \ remedy it DO escalate both ratings by name, plus whether each prescribed remedy\
      \ actually remedies it \u2014 the split and the remedy fit are what the tier\
      \ above decides, and reconciling either hides it."
    why: Final-round escalation was decidable only because both ratings were carried
      AND the lead showed the terminal descope remedied neither finding; the ruling
      adopted both points verbatim.
  - persona: harness-validator-lead
    op: replace
    target: P-12
    section: Patterns
    entry: "WHEN ruling a must-fix against a defect class DO hand down the class's\
      \ full state matrix \u2014 every axis the decision consumes, each state a caller\
      \ can produce \u2014 and require a discriminating mutant per cell; an instance-scoped\
      \ remedy closes one member per round, and rounds are budgeted."
    why: Two classes cascaded one member per round until the brief listed the full
      state matrix and demanded discriminating mutants; generalizes the old input-axis
      wording to any defect class.
  - persona: harness-validator-lead
    op: replace
    target: G-03
    section: Gotchas
    entry: "WHEN runner receipts are green DO report them as that host's interpreter\
      \ and environment, never as CI, until every required CI lock and interpreter\
      \ version has run \u2014 host env can mask CI failures; a failure outside the\
      \ verify set is an assurance gap first, then an ownership question."
    why: My digests headlined 'CI is green' from host-run receipts; a CI-only interpreter
      version then failed because host colour env masked it. Sharpens G-03 without
      growing it.
  team: distill
  steps_run: 3
  cycles_used: 0
  members:
  - step: distill-qa
    persona: harness-qa
    verdict: PASS
    headline: 4 craft replaces (batch ea6bdcfb; P15/G15/O10/Open1 unchanged) and 1
      repo add (batch 76aafb91; harness G 13->14). Relayed candidates 1 and 2 applied.
      The 'whole kind' and 'env-strip load-bearing' items were rejected as already
      covered.
    files_touched:
    - .harness/expertise/harness-qa.md
    - .harness/harness/expertise/harness-qa.md
  - step: distill-code
    persona: harness-code-reviewer
    verdict: PASS
    headline: 3 craft replaces, P-08, O-04 and G-07 (batch 0a485827); P15/G15/O10/Open0
      unchanged. All three candidates applied.
    files_touched:
    - .harness/expertise/harness-code-reviewer.md
  - step: distill-security
    persona: harness-security-reviewer
    verdict: PASS
    headline: 2 craft replaces, P-14 and O-08 (batch bef98f3b); P15/G15/O10/Open0
      unchanged. The execute-before-high candidate was rejected as covered by its
      O-04.
    files_touched:
    - .harness/expertise/harness-security-reviewer.md
  must_fix: []
  branch: none
  escalations: []
  adequacy_notes:
  - 'Lead''s own batch is c1f5b71090dbe4041340b23704c8aaf112e9e10011bb47d4200135a761be6542:
    3 replaces (P-04, P-12, G-03); craft P15/G15/O10/Open0 unchanged.'
  - harness-pm goalcheck was not dispatched. Its only relayed candidate (one probe
    beyond the contract before saying 'closed') is already pm P-19 from the product
    distill.
  - Ops and per-section counts were checked against the expertise_apply receipts in
    notes/; the lead did not open the member Expertise files.
  - QA's repo G-14 is close to a recipe, but it points at living env overrides in
    tests/integration, so it is accepted as a repository fact.
  - 'Distill mission: no diff was reviewed and no suite was run.'
  sc_status: []
  needs_approval: false
  severity_max: none
  matrix_ok: n/a
  coverage_gaps: []
  findings: []
  readers: []
```
