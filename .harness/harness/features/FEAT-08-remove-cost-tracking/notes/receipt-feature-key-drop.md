Removed 38 key(s) from FEAT-08-remove-cost-tracking's feature.yaml because each had no reader; FEAT-14 closed the key set to eleven. This receipt is the only durable record of their values.

## status collapse (the pre-collapse pair survives only here)

- old status: `awaiting_user`
- old phase: `ship`
- new status: `Review`  (rule)

## value normalization

- `pr`: `'none'` (string) -> `null`

## removed keys, full values

```yaml
amendment_a5:
  discrimination: NEITHER criterion would have failed at ae2443d, and that is correct
    for the class - both are over-removal guards and SC-12 is the signed in-BRIEF
    precedent. Both CAN fail against the delivered tree, measured on ten scratch-only
    mutants, not argued. No criterion that cannot fail was shipped.
  ruling: The user chose AMEND AND RE-SIGN over waiving both criteria. pm drafted
    A-5 through product-lead; pm recommended and did not self-approve. The approved
    SC-05 and SC-06 text is left in place with a pointer, exactly as A-2 and A-4 did.
    Only the main session writes the Approval block.
  three_false_premises: A-5 falsified three claims handed down as fact rather than
    pasting them forward. TWO WERE MINE. Byte-identity holds for the live config but
    NOT the template, whose rationale carries the u2014 escape at ae2443d and a literal
    em dash at HEAD - decoded values are equal, so A-5 asserts decoded equality and
    names the byte difference as a tolerance. My empty-diff suggestion over runs/
    paths is VACUOUS, 0 tracked paths at ae2443d. The third was the lead's own cycle-0
    sign-off of a draft that had silently dropped check-state.sh and SKILL.md from
    SC-05; the lead sent it back and clause 2 returns as SC-05 (c).
baseline:
  answers: none
  base_sha: ae2443d
  briefing: .harness/features/FEAT-08-remove-cost-tracking/notes/ship-review-validate-close.md
  closes_issues: '#58'
  cost_note: 370.53 was the last measurable figure, at 3503d1d before T-03 deleted
    the meter. Everything after 1a69d9d is unmeasurable BY DESIGN and nothing for
    it is invented. Over the 120 budget, reported not hidden. The harness no longer
    meters spend (DEC-178).
  cycles_note: 5 of 10. Two from build; one for the panel's fix round; one for the
    SC-15 re-dispatch. The fifth is the A-5 send-back, which product-lead reported
    against itself - its own cycle-0 sign-off missed that the draft had dropped SC-05's
    file coverage. Rework, so it counts. T-10's re-dispatch added ZERO - forward work
    created by a SIGNED amendment is not rework, which is DEC-157's distinction.
cost_usd: 370.53 at 3503d1d — final measurable figure; T-03 deleted the meter
gate_status:
  distillation: PASS — 12 Expertise files, all check-expertise.sh clean, re-run by
    me
  docs: PASS — check-docs.sh re-run by me, exit 0, 45 patterns across 212 files
  goal_check: FAIL — 13 met; SC-05 and SC-06 amended by A-5, awaiting re-signature
    and re-grade
  qa_gate: PASS — 12/12 scripts, matrix_ok true, qa authored nothing (D-08)
  review: FAIL — 3 must_fix at med; MF-2 and MF-3 FIXED, MF-1 FIXED main-session-direct
  security: PASS — reviewer declared IN SCOPE and executed both suites; 0 findings
  ship_refresh: NOT_RUN — .harness/codebase/ does not exist, decided at ship
  state: PASS — check-state.sh re-run by me, exit 0, zero violations
  uat: NOT_REQUIRED — BRIEF states no uat criterion
  ui: PASS — reviewer LOOKED and declined with a file-extension census; DESIGN.md
    absent
  unit: PASS — re-run by me at the A-5 tip, exit 0
github.closed:
- T-01
- T-02
- T-03
- T-04
- T-05
- T-06
- T-07
- T-08
- T-09
- T-10
- T-11
- T-12
github.perf_row_10: 79
github.q18_ruled: 104
max_cost_usd: 120
open_q:
- A-5 awaits the user's RE-SIGNATURE. Until then SC-05 and SC-06 stay not_met and
  the goal-check stays FAIL.
- Q23 - A-4's AWAITING RE-SIGNATURE preamble is stale; the Approval block already
  records A-4 as signed. Cosmetic, unfixed.
- Q27 - SC-06's hard-coded 67 can false-FAIL on a sanctioned log_retention_days prune
  of a historical run dir.
- Q28 - SC-05 (c) resolves the signed text's undisambiguated SKILL.md to 3 literal
  files out of 20; a future SKILL.md documenting the cycle budget sits outside it.
- Q1 CARRIED - the briefing loses its only size signal. Issue 79 filed, unscheduled.
- Q6 - SC-03 is repo-wide and passes only because FEAT-09 sits in a worktree. Dormant,
  not gone. Re-rooting is FORBIDDEN.
- Full backlog is in the briefing. Anything unlisted there dies silently.
panel_result:
  mf1: FIXED main-session-direct — no agent domain covers .claude/commands/harness.md
  mf2: FIXED at 8958840 — org.html no longer advertises the deleted subsystem
  mf3: FIXED — the stale orchestrator rule is gone; pm's re-grade flipped SC-15 to
    met
  scope_ruling_i_made: All three are REQ-08 violations of ALREADY-APPROVED text, so
    they are fix cycles, NOT scope expansion, and no amendment or re-signature is
    needed. On the record so the user can overturn it.
  verdict: FAIL — four-wide, all four reviewers PASS, the LEAD found three they all
    missed
  what: Three surviving REQ-08 violations that SC-01 structurally CANNOT see, because
    its sweep matches compound tokens while all three use only the plain English word.
    The blind spot's THIRD appearance.
runs[0].cost_usd: 237.73
runs[10].4 ops: null
runs[10].note: dev-ops and lead
runs[11].note: stranded lead ops applied
runs[12].flips to met: null
runs[12].note: SC-15 re-grade
runs[13].4 ops: null
runs[13].note: lead self-distillation
runs[14].note: A-5 drafted
runs[14].one send-back: null
runs[1].note: lane defect
runs[1].resolved by user ruling: null
runs[2].T-10 partial: null
runs[2].note: one send-back
runs[3].note: SC-01 redraft after ruling
runs[4].note: A-3 rows 10 and 11
runs[5].3 must_fix at med: null
runs[5].note: four-wide
runs[6].note: MF-2 org.html fix cycle
runs[7].3 not_met: null
runs[7].note: 12 met
runs[8].25 ops: null
runs[8].note: pm and documentor
runs[9].16 ops: null
runs[9].note: four reviewers
sc_status:
- evidence: sweep returns exactly the 4 amended survivors; 18 at ae2443d
  id: SC-01
  method: automated
  verdict: met
- evidence: both scripts absent; drift detector satisfied
  id: SC-02
  method: automated
  verdict: met
- 8 note lines: null
  evidence: check-state.sh exit 0
  id: SC-03
  method: automated
  verdict: met
  zero violations: null
- evidence: omitting payload accepted; rejected at ae2443d
  id: SC-04
  method: automated
  verdict: met
- evidence: signed clause 2 red on a formatting change; A-5 replaces it with 3 clauses,
    all measured green by me — NOT re-graded
  id: SC-05
  method: automated
  verdict: not_met
- evidence: signed globs rotted; A-5 scopes them to the 7 ae2443d dirs, returns 89
    and 67-of-67 — NOT re-graded
  id: SC-06
  method: automated
  verdict: not_met
- evidence: all 8 keys count 0 in both configs; both parse
  id: SC-07
  method: automated
  verdict: met
- evidence: DEC-148 row correct; generator diff exit 0
  id: SC-08
  method: automated
  verdict: met
- evidence: DEC-178 carries all three mandated parts; index row has a real ruling
  id: SC-09
  method: inspection
  verdict: met
- 45 patterns across 212 files: null
  evidence: check-docs.sh exit 0
  id: SC-10
  method: automated
  verdict: met
- evidence: whole suite exit 0
  id: SC-11
  method: automated
  verdict: met
- all protected prose intact: null
  evidence: verified BY CONTENT; 4 of 12 line anchors dead
  id: SC-12
  method: inspection
  verdict: met
- evidence: plain-word grep over README returns nothing
  id: SC-13
  method: automated
  verdict: met
- evidence: all 6 hits carry the marker on the same line
  id: SC-14
  method: automated
  verdict: met
- evidence: RE-GRADED after MF-3 fixed; 57 hits over all 12 rule files plus agents
  id: SC-15
  method: inspection
  skills: null
  team YAML - zero money: null
  verdict: met
tasks:
  T-01: DONE
  T-02: DONE
  T-03: DONE
  T-04: DONE
  T-05: DONE
  T-06: DONE
  T-07: DONE
  T-08: DONE
  T-09: DONE
  T-10: DONE
  T-11: DONE
  T-12: DONE
verified_by_me:
  a5: I re-ran ALL SIX A-5 clauses verbatim from the BRIEF at my own tier, not relayed.
    SC-05 (a) PASS exit 0; (b) live config EMPTY and template differing solely by
    the u2014 escape; (c) residual EMPTY exit 1. SC-06 (a) 89; (b) 67 and 67; (c)
    EMPTY. I independently confirmed pm's vacuity finding - git ls-tree at ae2443d
    returns 0 tracked paths under any features runs/ dir, so the empty-diff-over-runs
    clause I handed down would have been permanently green. Approval block UNTOUCHED
    - the BRIEF diff is 297 insertions with no line inside it. I corrected one number
    myself - A-5 section 5 said three SC-05 (c) mutants where the table lists four;
    the guard permits my agent_type on BRIEF.md and blocks harness-documentor, which
    is how I checked.
  mf1: 'FIXED main-session-direct at :18 and :83. Two cost mentions remain at :47
    and :80 and STAY - plain English about a trade-off, neither instructing anyone
    to produce a figure. Not an agent write: check-domain.sh BLOCKED documentor, orchestrator,
    dev-ops and pm on that path.'
  numbers: 21 commits and 33 files in ae2443d..942505e — measured, not relayed
  t10: All five verify clauses re-run at 942505e - compound sweep leaves one hit carrying
    the DEC-178 marker; unchanged-count 8 before and 8 after; the new plain-word sweep
    printed exactly the two defect lines mid-flight and prints nothing now; unit 0;
    docs 0. Issue 95 closed.
```
