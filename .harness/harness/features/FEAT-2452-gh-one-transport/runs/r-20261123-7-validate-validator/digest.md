# Validate — FEAT-2452 — rework c2 (last signed round) — r-20261123-7-validate-validator

**ESCALATE** at review_sha `caeebc7cb24b7205bb5d5ad5191cd6541fc3519a` (base `b788e9da`, fix delta `3465716a..caeebc7c`).

M1 and M2 are closed, and the fix delta introduced no regression. Suites are green with DEC-255 receipts: unit 67 and integration 95. QA reproduced the c2 reds itself at 3465716a: wayfind 115 FAIL and factory-gh 17/345. Every T-01..T-05 verify exits 0.

One **new, pre-existing** finding class is rated high by the code-reviewer. wayfind trusts a related issue's number and discards its repository. Under `gates.review: advisory_unless_high` that rating blocks. However, the signed rework budget is spent, and the class sits outside SC-03's signed text. Routing a FAIL would aim a fix cycle that does not exist, so the operator decides.

## Readers
| step | persona | verdict | note |
|---|---|---|---|
| qa | harness-qa | PASS | `notes/review-harness-qa-c3.md`; receipts `qa/manifest-{unit,integration}.json`; the EMU accept case discriminates under a mutant |
| code | harness-code-reviewer | FAIL | `notes/review-harness-code-reviewer-c3.md`; M1 and M2 measured closed by execution; new high (R1); code-grade pass (137 base..pin) |
| security | harness-security-reviewer | PASS | `notes/review-harness-security-reviewer-c3.md`; M1 fails closed, no ReDoS, no new leak; two low advisories |
| ui | harness-ui-reviewer | PASS | scoped out on a measured census: 0 UI paths in 201 (fix delta 26) |
| goalcheck | harness-pm | PASS | `notes/research-…-goalcheck-validate-c3.md`; both perspectives pass; SC-03 and SC-06 now met |

## c1 must-fix — disposition
- **M1 closed.** The raiser, code-reviewer, confirmed it by execution. `[{}]`, an `unknown` state, an integer state, and missing, null or string assignees each exit 1 with a typed `wayfind:` diagnostic and make no ticket-view call. Valid mixed-case states, `[]` and a confirmed 404 are unchanged.
  - Security confirmed the same closure independently.
  - QA reproduced the 115 reds and the green controls.
  - Code-reviewer's P2 retires the regression risk of the stricter checks. The map body is read through the GraphQL CLI export, where an empty body is `""`, not REST's `null`, so the new strictness does not refuse a real empty map. I confirmed the frontier and resolve reads at source in `wayfind.py` (`frontier`, `checked_issue`, `parent_of`).
- **M2 closed** for the defect it named, the close-failure path, per code-reviewer and pm. A narrower residual remains as advisory V1.
- **B1/B3 folded and closed.** The EMU owner `_` is accepted. Query and fragment characters, dot segments and out-of-range ports are refused.

## Escalated finding
**R1 · high (code-reviewer) · substance · T-04 · wayfind discards relationship repository identity.**
- **What it does.** `frontier` uses a sub-issue's `number` against the local repo. `resolve` uses `parent_of`'s `number` against the local repo.
- **Scenario 1.** A foreign child `other/repo#11` makes frontier advertise local `#11`.
- **Scenario 2.** A foreign parent `other/repo#2` makes `resolve --apply` comment on and close the ticket, then edit local `#2`'s body. It exits 0, and the real map never gets its gist.
- **Where I confirmed it.** At source in `wayfind.py` `sub_issues`, `frontier`, `parent_of` and the resolve branch. The reviewer measured it offline and found it already present at base (`wayfind.py:130–146,308–315`).

**Lead's rating: med, backlog.** The reader's high is transcribed unrevised, and both ratings travel by name (P-04).
- **Scope.** The class is not in SC-03's signed text. SC-03 covers 404-only absence, typed failures, invalid JSON, dry-run and gist stdin. No c0 or c1 remedy named it.
- **Origin.** It predates the feature.
- **Preconditions for the wrong write.** A human-made cross-repo relationship on a wayfinding map, and a same-numbered local issue that carries a `## Decisions so far` heading. Without that heading, `append_gist` refuses.
- **Reversibility.** The impact can be undone: a close and a body edit, both in GitHub history.
- **Related.** Security's low S2 (T-01) is the same class at another site: a foreign owner/repo in the create URL is not bound to the create argv. Pair the two in one backlog item.

## Advisory (not gating), ranked
- **V1 · low · form · T-05 (code-reviewer).** `github-mirror.md:106` still says a closed card "is reseated". Without a configured board no reseat happens, and a BoardError abandons that write. It should say "attempted when configured".
- **V2 · low · form · T-01 (pm).** `tests/unit/test-factory-gh.py:2204`, and the fix note's "Disclosed limit", still state the owner class as `[A-Za-z0-9-]`. The code is `[A-Za-z0-9_-]` (`factory_gh.py:244,251`); I confirmed both lines.
- **S1 · low · substance · T-01 (security).** Host labels are not length-bounded under DNS rules (63/253). No request is made to that authority.
- **S2 · low · substance · T-01 (security).** The create URL's owner/repo is not bound to the create argv. This is pre-existing and pairs with R1.
- **A-2 · low · coverage · T-04 (QA).** `cmd_map` has no test, and the null-payload exit-1 change is unpinned.
- **A-1 · info · coverage · T-04 (QA).** There is no non-string frontier `title` case.

## Assessed and dismissed
- OQ-GC2-1, A2, OQ-QA-2, OQ-QA-3, B2, B4 and the standing disclosures were ruled in `notes/answers-2026-11-23-validate-c1.md`. No reader brought new evidence against them. pm confirms that nothing in the delta claims a per-item close-failure red. C4 still holds: zero enforcement files changed across both ranges (code-reviewer, pm).
- The code-reviewer's pagination note (a successful blocker page followed by a 404) was raised by the reviewer itself as not a gate finding, because no real multi-page flow was established. It is dismissed.

## Adequacy
- QA's green rests on receipts with non-zero discovery and on independent red reproduction, not on the builder's files.
- The security lens is reasoning plus isolated execution. It did not look at relationship identity in wayfind; R1 came from the code lens alone.

## Open questions
- **OQ-VC3-1 (blocking).** Rule on R1.
  - (a) Ship with R1 and S2 as one backlog issue (repository identity of related and created issues). The lead recommends this.
  - (b) Authorize an extra rework round to make wayfind refuse foreign or unverifiable relationships before advertising or writing.
- **OQ-VC3-2.** V1, V2, A-1 and A-2: backlog at ship, or ride with (b)?
- **OQ-QA-c3-2 (harness defect, for the harness owner).** bash-write-guard refuses a redirect whose target contains a shell variable.
- **Ship record (pm OQ-GC3-1).** It must carry the C5 cut of SC-04 (e), the OQ-GC2-1 narrowed reading, the backlog items with A2's disclosure class, the standing disclosures, and the issue_types_live probe stdout.

```yaml
VERDICT: ESCALATE
artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2452-gh-one-transport/.harness/harness/features/FEAT-2452-gh-one-transport/runs/r-20261123-7-validate-validator/digest.md
DIGEST:
  headline: 'FEAT-2452 at caeebc7c: M1 and M2 are closed, with no regression from
    the fix and suites green with receipts. The code-reviewer raised a new high finding
    (T-04: wayfind trusts a related issue''s number and drops its repository). It
    predates the feature and falls outside SC-03''s signed text, and no rework round
    is left, so the operator decides.'
  team: validate
  steps_run: 5
  cycles_used: 0
  branch: none
  members:
  - step: qa
    persona: harness-qa
    verdict: PASS
    headline: 'Unit 67/67 and integration 95/95 are green with DEC-255 receipts, and
      every T-01..T-05 verify exits 0. QA reproduced the fix-c2 reds itself at 3465716a:
      wayfind 115 FAIL, factory-gh 17/345. The EMU owner accept case catches a mutant.'
    files_touched:
    - /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2452-gh-one-transport/.harness/harness/features/FEAT-2452-gh-one-transport/runs/r-20261123-7-validate-validator/qa/manifest-unit.json
    - /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2452-gh-one-transport/.harness/harness/features/FEAT-2452-gh-one-transport/runs/r-20261123-7-validate-validator/qa/manifest-integration.json
    - /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2452-gh-one-transport/.harness/harness/features/FEAT-2452-gh-one-transport/observations/harness-qa.md
  - step: code
    persona: harness-code-reviewer
    verdict: FAIL
    headline: The M1 shape cases are closed by execution, but T-04 can advertise or
      edit the wrong issue when a GitHub relationship crosses repositories (pre-existing,
      high).
    files_touched: []
  - step: security
    persona: harness-security-reviewer
    verdict: PASS
    headline: M1 fails closed and the fix adds no security regression. Two pre-existing
      URL validation limits remain advisory (low).
    files_touched: []
  - step: ui
    persona: harness-ui-reviewer
    verdict: PASS
    headline: 'Out of scope: 0 UI paths among 201 changed paths in the full diff and
      26 in the fix delta.'
    files_touched: []
  - step: goalcheck
    persona: harness-pm
    verdict: PASS
    headline: Both perspectives pass. SC-03 and SC-06 are now met, and SC-05 stays
      met on its literal discharge with no per-item red claimed. No enforcement file
      changed.
    files_touched:
    - /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2452-gh-one-transport/.harness/harness/features/FEAT-2452-gh-one-transport/observations/harness-pm.md
  must_fix:
  - 'R1 (T-04, high per code-reviewer, substance; pre-existing at base; outside SC-03''s
    signed text): wayfind frontier and resolve use a related issue''s number against
    the local repo and drop its repository. A foreign sub-issue other/repo#11 makes
    frontier advertise local #11. A foreign parent other/repo#2 makes resolve --apply
    close the ticket and edit local #2''s body with exit 0, and the real map gets
    no gist. Remedy if authorized: refuse foreign or unverifiable relationships before
    advertising or writing. Gating depends on operator ruling OQ-VC3-1, because the
    lead rates it med/backlog and no rework round remains.'
  files_touched:
  - /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2452-gh-one-transport/.harness/harness/features/FEAT-2452-gh-one-transport/runs/r-20261123-7-validate-validator/state.yaml
  - /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2452-gh-one-transport/.harness/harness/features/FEAT-2452-gh-one-transport/runs/r-20261123-7-validate-validator/qa/manifest-unit.json
  - /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2452-gh-one-transport/.harness/harness/features/FEAT-2452-gh-one-transport/runs/r-20261123-7-validate-validator/qa/manifest-integration.json
  - /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2452-gh-one-transport/.harness/harness/features/FEAT-2452-gh-one-transport/observations/harness-qa.md
  - /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2452-gh-one-transport/.harness/harness/features/FEAT-2452-gh-one-transport/observations/harness-pm.md
  open_questions:
  - id: OQ-VC3-1
    question: 'R1 is pre-existing and outside SC-03''s signed text. Code-reviewer
      rates it high; the validator lead rates it med because of the preconditions:
      a human-made cross-repo relationship on a wayfinding map, and a same-numbered
      local issue that carries ''## Decisions so far''. Its impact is a reversible
      close and body edit. The signed rework budget (2 rounds) is spent. Choose: (a)
      ship, and file R1 together with security S2 (create URL owner/repo not bound
      to the create argv) as one backlog issue on repository identity (the lead recommends
      this); or (b) authorize an extra rework round so wayfind refuses foreign or
      unverifiable relationships before advertising or writing.'
    blocking: true
  - id: OQ-VC3-2
    question: 'Non-gating advisories: V1 (T-05 form) github-mirror.md:106 should say
      the Backlog reseat is attempted when a board is configured. V2 (T-01 form) test-factory-gh.py:2204
      and the fix note still state the owner class as [A-Za-z0-9-]. A-1 and A-2 (T-04
      coverage) have no non-string title case and no cmd_map test. S1 (T-01) host
      labels have no DNS length bound. Should these go to backlog at ship, or ride
      with option (b)?'
    blocking: false
  - id: OQ-QA-c3-2
    question: 'Harness defect raised by QA: bash-write-guard refuses a redirect whose
      target contains a shell variable (e.g. > /tmp/x/mut-$m.txt), while literal absolute
      /tmp paths pass. This needs the harness owner''s ruling.'
    blocking: false
  - id: OQ-GC3-1
    question: 'The ship record must carry: the SC-04 (e) cut under C5; the OQ-GC2-1
      narrowed reading (no per-item close-failure red was observed); the backlog items
      A2 (disclosure class: non-public issue body text persisted to the local cost
      log when opted in), OQ-QA-2, OQ-QA-3, B2 and B4; the standing disclosures; and
      the issue_types_live probe stdout.'
    blocking: false
  escalations:
  - id: ESC-VC3-1
    raised_by: harness-code-reviewer
    question: Is R1, where wayfind discards relationship repository identity, a must-fix
      for FEAT-2452 now that the signed rework rounds are exhausted?
    domain: scope / rework budget
    routed_to: harness-orchestrator
    resolution: pending operator ruling (OQ-VC3-1); lead recommends backlog
    decided_by: none
    recorded_as: runs/r-20261123-7-validate-validator/digest.md
  expertise_update: []
  adequacy_notes:
  - M1 closure was measured by the raiser (code-reviewer) by execution and confirmed
    independently by security. QA reproduced the reds at 3465716a (115 FAIL / 123
    PASS; all 50 new input classes red, controls green). pm regraded SC-03 as met,
    citing the case_8c/10c names.
  - 'No false refusal of real payloads: the map body, title and labels are read through
    the GraphQL gh issue view export, where an empty body is "", not REST''s null.
    REST state casing is handled by the lowercase check. Code-reviewer recorded the
    argv and live read-only controls.'
  - 'R1 is transcribed at code-reviewer''s high, unrevised. The lead''s med is carried
    by name rather than reconciled, because the remedy needs a round the signed budget
    does not have. The lead confirmed the number-only reads at source: wayfind.py
    sub_issues, frontier, parent_of and the resolve branch.'
  - Security's S2 (the create URL owner/repo not bound to argv) is the same repository-identity
    class at the T-01 site. Pair the two in one backlog item.
  - Code-reviewer dismissed its own pagination note (a successful blocker page followed
    by a 404) as not a gate finding, because no production multi-page flow was established.
  - 'C4 holds: zero enforcement files changed in both base..pin and the fix delta
    (code-reviewer P5, pm).'
  - 'Gate: .harness/harness.json gates.review = advisory_unless_high. Only R1''s high
    blocks. Every other finding is low/info and advisory.'
  sc_status:
  - id: SC-01
    verdict: met
    method: automated
    evidence: test-factory-gh.py 345/345 at the pin; 17/345 FAIL with the 3465716a
      factory_gh.py (QA and pm reproduced); unit receipt green
  - id: SC-02
    verdict: met
    method: automated
    evidence: untouched in the fix delta; test-gh-sync-open.py:863 green under the
      integration receipt
  - id: SC-03
    verdict: met
    method: automated
    evidence: case_8c/10c/11c red at 3465716a (115 FAIL) and ALL PASS 238 at the pin.
      Met on the signed text; R1 (relationship repository identity) is a reader's
      widened reading escalated as OQ-VC3-1
  - id: SC-04
    verdict: met-with-cut
    method: automated
    evidence: untouched in the delta; c1 grading stands; (e) cut under C5 is a standing
      ship disclosure
  - id: SC-05
    verdict: met
    method: automated
    evidence: literal discharge per the OQ-GC2-1 ruling; label-create red at 15a240bc
      unchanged; nothing claims a per-item red
  - id: SC-06
    verdict: met
    method: inspection
    evidence: github-mirror.md:106 close-failure path matches gh-sync.py; :118 matches
      wayfind validation; residual V1 reseat-when-configured wording is low form
  - id: SC-07
    verdict: met
    method: inspection
    evidence: 'notes/enforcement-backlog.json unchanged; #2468 OPEN'
  - id: DEC-138
    verdict: met
    method: inspection
    evidence: DECISIONS.md:3132 unchanged in the fix delta
  needs_approval: true
  severity_max: high
  matrix_ok: true
  coverage_gaps:
  - 'A-1 (T-04, info): no non-string frontier title case'
  - 'A-2 (T-04, low): no cmd_map test; the null-payload exit-1 change is unpinned'
  - No test for a foreign-repository sub-issue or parent (R1)
  - 'Carried and ruled: B4 (labels seam event); OQ-GC2-1 (per-item close-failure #13
    red never observed)'
  findings:
  - kind: substance
    scope: none
    severity: high
    reader: code-reviewer
    summary: 'T-04: wayfind drops the repository from a valid GitHub relationship
      and trusts the issue number alone (frontier advertises the wrong local ticket;
      resolve --apply closes and edits the wrong map body with exit 0)'
    why: Pre-existing at base and outside SC-03's signed text; escalated as OQ-VC3-1
      with the lead's med rating carried alongside the reader's high
  - kind: form
    scope: none
    severity: low
    reader: code-reviewer
    summary: 'T-05: github-mirror.md:106 still promises a successful Backlog reseat
      after a close'
    why: No reseat occurs without a configured board, and a BoardError abandons it;
      the row should say the reseat is attempted when configured (advisory V1)
  - kind: form
    scope: none
    severity: low
    reader: pm
    summary: 'T-01: test-factory-gh.py:2204 comment and the fix note state the owner
      class as [A-Za-z0-9-], while the code is [A-Za-z0-9_-]'
    why: Doc drift after Main widened the class for EMU; lead confirmed both lines
      (advisory V2)
  - kind: substance
    scope: none
    severity: low
    reader: security-reviewer
    summary: 'T-01: host labels are edge-checked but not bounded to DNS lengths'
    why: 'Advisory S1: the authority is never fetched'
  - kind: substance
    scope: none
    severity: low
    reader: security-reviewer
    summary: 'T-01: a well-formed foreign owner/repo in the create URL is not bound
      to the create argv'
    why: 'Advisory S2: pre-existing, needs faulty or substituted gh output; same repository-identity
      class as R1'
  - kind: substance
    scope: none
    severity: low
    reader: qa
    summary: 'T-04: cmd_map has no test; the null sub-issue payload now exits 1 typed,
      unpinned'
    why: 'Advisory A-2: coverage, outside the fix''s stated frontier/resolve scope'
  - kind: substance
    scope: none
    severity: info
    reader: qa
    summary: 'T-04: no non-string frontier title case'
    why: 'Advisory A-1: weakening title=_string to a not-None check would stay green'
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
