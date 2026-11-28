# BUG-2565 plan run 2026-11-27-03-plan-product — FAIL, plan pending, T-01 still not signable

**BLUF:** The operator's answers landed (SC-03 explicit, org.html on T-06, case_30 docstring on T-02), and the bounded scope re-read closed two of the three cycle-1 findings: T-04's typed drift equality (PF-64c3…) and T-02/T-03's failure behaviours (PF-3425…), both now `resolved`. T-01 did not close. The cycle-1 refusal-probe finding is PARTIAL (PF-cbf8…, open), and the re-read raised two new high substance findings against T-01 plus one med against T-02's SC-03 coverage. The panel is recorded as cycle 2. `plan-merge.py check` reports 0 failures, and approval stays `pending`.

## Steps
- answers (pm) PASS: SC-03 now says the host `task` call is not rewritten and the normalized dispatch-guard input stays its own interface (BRIEF.md:21). T-06 owns `.harness/harness/docs/org.html`, and pm also added org.html to SC-09's "no longer tell" clause so the edit traces to a criterion (Q-A1). T-02 owns the case_30 docstring. Check: 36 anchors, 0 failures, no APPROVAL-RESET.
- scope (code-reviewer) FAIL: a valid reader return (`notes/review-harness-code-reviewer-plan-c2.md`). I checked the threshold finding against the source, plan.yaml T-01 intent. The extension refuses "while a per-process counter of yield calls is below PROBE_REFUSE" and logs a "1-based per-process yield count". Under that wording, PROBE_REFUSE=3 can refuse only attempts 1–2, while Run C needs 1–3 refused. The receipt-gate finding also holds at source: the verify uses `re.search("(?m)^key: value$")` over the whole note, so a matching Evidence line can satisfy a key that the Result section contradicts.
- apply (pm) PASS: the form fix is applied in place on T-02 (host call unrevised, normalized target to the guard, and a presence check paired with the absence grep). record-panel `--cycle 2` exited 0 and added 4 PF ids. set-panel resolved the two CLOSED findings, and check exited 0. Map: `notes/research-panel-c2-apply.md`.

## Lead assessment
- **T-01 keeps failing more narrowly, one mechanism at a time (O-09).** Cycle 1 found an unobserved refusal. Cycle 2 found an off-by-one threshold and a receipt parse that whole-note grep can satisfy. Another apply-then-reread round that patches only these two items risks a third narrower finding. Recommendation: pm re-keys T-01 on what the receipt guarantees. That means a single parsed Result block, with exactly one line per key and duplicates refused. The extension contract should say "refuse exactly the first N yield calls". Every refused attempt in every A/C invocation, deviated ones included, must be matched to its transcript result before any classification. Then one bounded scope re-read of T-01 and T-02 only.
- PF-120f… (med, T-02 SC-03 coverage) is real but does not block alone. It should be folded into the same pm pass.
- Not resolved by this run: PF-dc87… (c1 T-06 form, applied in run 02, never re-read by design) and PF-09df… (c2 form, applied here). Both are open but do not gate signature because they are med/low.
- pm left a value file at `notes/panel-c2-set-panel.yaml`. It is a throwaway used as set-panel input and can be deleted before signature.
- Prototype gate: unchanged from run 02. There is no end-user surface, the call is mine, and the operator can override it.
- No proportionality finding has `scope: mission`, so I make no downgrade recommendation.
- Cycles: I issued 0 send-backs. The scope FAIL is a valid reader verdict, and the dispatch scoped apply to form only, so it was not looped back.

```yaml
VERDICT: FAIL
artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-2565-digest-frontmatter-contract/.harness/harness/features/BUG-2565-digest-frontmatter-contract/runs/2026-11-27-03-plan-product/digest.md
DIGEST:
  headline: 'BUG-2565 plan pending but not signable: re-read closed T-04 and T-02
    findings, T-01 refusal probe still fails (c1 partial + 2 new high: off-by-one
    refuse threshold, whole-note receipt grep); answers applied, panel cycle 2 recorded,
    check 0 failures'
  open_questions:
  - id: Q-R3-1
    question: 'T-01 is open on three high substance findings (PF-cbf8dece partial;
      PF-9a0f853d refuse threshold refuses attempts 1-2 not 1-3 under ''below PROBE_REFUSE''
      with a 1-based count; PF-25a87adf verify regex-searches the whole note so an
      Evidence line can satisfy a key the Result contradicts). Recommendation: one
      pm pass re-keying T-01 on what its receipt guarantees (single parsed Result
      block, one line per key, duplicates refused; ''refuse exactly the first N yield
      calls''; every refused attempt in every A/C invocation incl. deviated ones matched
      to its transcript before classification), folding in PF-120f5374 (T-02 all three
      key combinations in flat and batch shapes, exact per-target tool_input), then
      one bounded scope re-read of T-01/T-02 only. Approve that route, or rule on
      the findings at signature?'
    blocking: true
  - id: Q-A1
    question: pm also added .harness/harness/docs/org.html to SC-09's 'no longer tell
      dispatchers about outputSchema/schemaMode' clause so T-06's org.html edit traces
      to a criterion (not to SC-09's README/BUILD/SPEC 'states' clause). Accept at
      signature, or strike and leave the org.html edit untraced?
    blocking: false
  files_touched:
  - .harness/harness/features/BUG-2565-digest-frontmatter-contract/BRIEF.md
  - .harness/harness/features/BUG-2565-digest-frontmatter-contract/plan.yaml
  - .harness/harness/features/BUG-2565-digest-frontmatter-contract/notes/review-harness-code-reviewer-plan-c2.md
  - .harness/harness/features/BUG-2565-digest-frontmatter-contract/notes/research-panel-c2-apply.md
  - .harness/harness/features/BUG-2565-digest-frontmatter-contract/notes/panel-c2-set-panel.yaml
  - .harness/harness/features/BUG-2565-digest-frontmatter-contract/runs/2026-11-27-03-plan-product/state.yaml
  - .harness/harness/features/BUG-2565-digest-frontmatter-contract/runs/2026-11-27-03-plan-product/criteria.md
  - .harness/harness/features/BUG-2565-digest-frontmatter-contract/runs/2026-11-27-03-plan-product/panel-c2.md
  expertise_update: []
  team: plan
  steps_run: 3
  cycles_used: 0
  members:
  - step: answers
    persona: harness-pm
    verdict: PASS
    headline: 'Q-S2..Q-S4 applied: SC-03 explicit (host call not rewritten, normalized
      guard input its own interface); org.html on T-06 and SC-09; case_30 docstring
      on T-02; check 36 anchors 0 failures'
    files_touched:
    - .harness/harness/features/BUG-2565-digest-frontmatter-contract/BRIEF.md
    - .harness/harness/features/BUG-2565-digest-frontmatter-contract/plan.yaml
  - step: scope
    persona: harness-code-reviewer
    verdict: FAIL
    headline: 'c1 #1 T-01 PARTIAL; #2 T-04 CLOSED; #3 T-02/T-03 CLOSED; new: 2 high
      T-01, 1 med T-02 SC-03 coverage, 1 low form T-02 docstring'
    files_touched:
    - .harness/harness/features/BUG-2565-digest-frontmatter-contract/notes/review-harness-code-reviewer-plan-c2.md
  - step: apply
    persona: harness-pm
    verdict: PASS
    headline: T-02 form fix applied; record-panel cycle 2 added 4 PF ids; PF-64c3
      and PF-3425 resolved; check 0 failures; no APPROVAL-RESET
    files_touched:
    - .harness/harness/features/BUG-2565-digest-frontmatter-contract/plan.yaml
    - .harness/harness/features/BUG-2565-digest-frontmatter-contract/notes/research-panel-c2-apply.md
    - .harness/harness/features/BUG-2565-digest-frontmatter-contract/notes/panel-c2-set-panel.yaml
  must_fix:
  - 'T-01: specify the probe extension refuses exactly the first N yield calls (Run
    C: attempts 1-3 refused, 4 passed) and match every Run C denial to its child transcript
    result (PF-9a0f853dff44e05bcf533eebd405abac)'
  - 'T-01: verify parses one authoritative Result section (one line per key, duplicates
    refused) instead of whole-note regex, and stops on a leaked refused payload in
    any A/C invocation including a deviated one (PF-25a87adffad1fd1f463f52b21ddb5b3e;
    closes partial PF-cbf8dece633693ce07ab5a284be1a0cf)'
  branch: none
  escalations: []
  adequacy_notes:
  - 'Both T-01 high findings verified at source by the lead: the T-01 intent says
    ''while a per-process counter of yield calls is below environment variable PROBE_REFUSE''
    beside a ''1-based per-process yield count'', and the T-01 verify uses re.search
    over the whole note.'
  - Only the scope reader read cycle-2 text (bounded re-read of T-01, T-02, T-04,
    SC-03). Readers should-not-exist, design and goalcheck ran in cycle 1 (run 2026-11-27-02-plan-product)
    and were not re-run by operator order; they are recorded 'ran' with that reason
    in plan.yaml panel because record-panel replaces the readers list wholesale.
  - Cycle-2 reader field normalized to harness-code-reviewer (the reviewer returned
    'code-reviewer') to keep reporter identity stable with cycle 1; severities and
    kinds unchanged.
  - Substance findings were deliberately not applied in this run per the dispatch
    (form only at apply).
  - 'Prototype gate unchanged: no end-user surface; lead''s call, overridable.'
  - 'No scope: mission proportionality finding; no downgrade recommendation.'
  - notes/panel-c2-set-panel.yaml is a throwaway set-panel value file; can be removed
    before signature.
  sc_status: []
  needs_approval: true
  severity_max: high
  matrix_ok: none
  coverage_gaps:
  - T-02 SC-03 witnesses miss flat schemaMode-only and batch both-keys combinations
    and do not assert exact per-target guard tool_input (PF-120f5374d27296822e9d10ea9d8adab9)
  findings:
  - kind: substance
    scope: none
    severity: high
    reader: harness-code-reviewer
    summary: T-01's refusal threshold contradicts Run C's required sequence (SC-11,
      D-03).
    why: 'Open, not applied this run: ''below PROBE_REFUSE'' with a 1-based count
      refuses attempts 1-2 while Run C needs 1-3; a correct build stops on an inconclusive
      receipt.'
  - kind: substance
    scope: none
    severity: high
    reader: harness-code-reviewer
    summary: T-01 can green-light a contradictory or unsupported refusal receipt (SC-11,
      D-03).
    why: 'Open, not applied this run: whole-note re.search lets an Evidence line satisfy
      a key the Result contradicts; a leak in a deviated invocation can be masked.'
  - kind: substance
    scope: none
    severity: med
    reader: harness-code-reviewer
    summary: T-02's tests do not cover the full amended SC-03 dispatch contract.
    why: 'Open: flat singleton-key and batch both-keys refusals could slip past; exact
      normalized guard input not asserted.'
  - kind: form
    scope: none
    severity: low
    reader: harness-code-reviewer
    summary: T-02 case_30 docstring still conflates the host call and normalized guard
      input.
    why: Applied in place by pm (host call unrevised, normalized target to guard,
      presence check paired with absence grep); not re-read by design.
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
```
