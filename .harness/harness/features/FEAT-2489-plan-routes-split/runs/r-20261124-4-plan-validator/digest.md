# FEAT-2489 plan panel c3 — validator digest

**FAIL (severity_max high).** PF-6efa (the T-01 receipt binding) is closed for its class. PF-2411 (SC-02 satisfiability) is closed only for the case it sampled. Its class rule is keyed on fields of the inventory rows, but some diagnostics print the moved code's own location, and the rule misses those. Both applies also introduced one new med substance finding each.

Reader: `scope` (harness-code-reviewer), note `notes/review-harness-code-reviewer-plan-c3.md`. should-not-exist and design were skipped (reasons in `panel-c3.md`). No BRIEF.md or plan.yaml edits were made in this run.

## Per finding

1. **PF-241126189d3c3d16550a5f09c7532ff3: not closed (substance/high).** SC-02 item 5 (`BRIEF.md` SC-02) sanctions a diagnostic only when its text is formatted from a field that items 1–3 rewrite: a row's file or id, the T07 key, or a scanned_files entry. **Lead-checked at source:** `_unaccounted_candidate_findings` prints `candidate['file']::candidate['symbol']`, and `reader_candidates_from_source` sets the candidate's file from the file being scanned. Delete the relocated row from both inventories and the base prints `check-plan-routes.py::…`, while the split prints `canonical_reader_audit.py::…`. No row exists, so nothing is rewritten. Item 3 adds scanned_files entries and rewrites none. The difference therefore falls outside item 5, yet a verbatim move forces it. **The apply was instance-scoped:** it covered the blank-reason producer it sampled. The class is "any diagnostic that names a relocated identity (file::symbol / id of moved code), whether it comes from a row or from a scanned candidate". This is the second round on this finding.
2. **New, T-02 map (substance/med; this is the converse false-PASS).** `plan.yaml` T-02 intent applies `re.sub(re.escape(OLD)+(?![A-Za-z0-9_]))` to the whole line. **Lead-checked:** `_exemption_finding` prints `{exemption!r}` on the same line as the row label. A token equal to an old label in any other field gets rewritten too. In the abstract, then, the comparator can excuse a difference that is not a consequence of items 1–3. The sampled states are fixed, and none of them puts an old label in a non-identity field, so on T-02's own receipt the risk is latent. It is not live.
3. **PF-6efa88c834c89ca43eea0322509703d9: closed (class).** T-01 verify requires `merge-base --is-ancestor` and exact equality with `rev-parse CP:T`. No comparison against the live file is involved. The reader ran the git exit codes read-only.
4. **New, T-01 guard (substance/med).** **Lead-checked:** T-01 verify asserts only that `canonical_reader_audit.py` is absent at the recorded commit. SC-03 (`BRIEF.md`) and T-01's own expected-exit text say "neither new module". `structure_audit.py` is unchecked, so the plan contradicts its own criterion. The fix is one line.

## Fix order

Fix 1 first: restate SC-02 item 5's class by relocated identity rather than by rewritten field. Then derive T-02's map from that same identity set and restrict it to the diagnostic field that carries the identity (finding 2). Done the other way round, fix 2 would have to be redone. Finding 4 is independent.

## Assessment

- The reader's claims were re-derived at source (P-15). All three new or open findings reproduce as described. The reader reasoned them and did not execute them; only the PF-6efa git checks were run.
- Convergence: SC-02's class has now been stated twice by enumerating its producers, and each statement missed a producer. If a third apply also lists producers or fields, expect the same result. The rule has to be stated over relocated identities. If that cannot be made tight, the operator should rule on it at signature (DEC-176). Another cycle would not settle it.

```yaml
VERDICT: FAIL
DIGEST:
  headline: PF-6efa (T-01 receipt binding) closed for its class; PF-2411 (SC-02) closed
    only for its sampled case, because item 5 still misses diagnostics that print
    a moved candidate's file; the applies added two new med findings (T-02 map rewrites
    the whole line, T-01 checks only one module)
  open_questions: []
  files_touched:
  - .harness/harness/features/FEAT-2489-plan-routes-split/runs/r-20261124-4-plan-validator/state.yaml
  - .harness/harness/features/FEAT-2489-plan-routes-split/runs/r-20261124-4-plan-validator/panel-c3.md
  expertise_update: []
  team: plan
  steps_run: 1
  cycles_used: 0
  members:
  - step: scope
    persona: harness-code-reviewer
    verdict: FAIL
    headline: SC-02 still excludes a diagnostic change forced by the verbatim move;
      the receipt comparator can also hide an unrelated change.
    files_touched:
    - .harness/harness/features/FEAT-2489-plan-routes-split/notes/review-harness-code-reviewer-plan-c3.md
  must_fix:
  - 'PF-241126189d3c3d16550a5f09c7532ff3 (high): restate SC-02 item 5''s class by
    relocated identity (file::symbol / id of moved code), covering both row-formatted
    and scanned-candidate-formatted diagnostics (_unaccounted_candidate_findings prints
    candidate[''file'']), not by rewritten field'
  - 'T-02 (med): derive the relocation map from that identity set and apply it only
    to the diagnostic field carrying the identity, keeping exact comparison elsewhere
    (whole-line re.sub also rewrites e.g. an exemption repr)'
  - 'T-01 (med): the checkpoint guard must also assert that .claude/skills/harness/bin/structure_audit.py
    is absent at the recorded commit, matching SC-03''s ''neither new module'''
  branch: none
  escalations: []
  adequacy_notes:
  - 'Lead re-derived every open or new finding at source in the worktree: check-plan-routes.py::_unaccounted_candidate_findings,
    ::reader_candidates_from_source, ::_exemption_finding; plan.yaml T-01 verify and
    T-02 intent. All reproduce as reasoned. The reader executed only the PF-6efa git
    exit-code checks.'
  - 'Convergence: this is the second round on PF-2411. Both applies stated the class
    by listing producers or fields, and each missed one. A third apply in that style
    will not converge. If an identity-keyed rule cannot be made tight, route it to
    the operator at signature (DEC-176) instead of running another cycle.'
  - 'The T-02 whole-line false-PASS is latent on the receipt''s fixed sampled states:
    none of them puts an old label in a non-identity field. It matters for the stated
    contract, not for the current probes.'
  - 'Fix order: SC-02 class first, then the T-02 map (derived from the same identity
    set), then the independent one-line T-01 guard.'
  - 'Scope reader result: FAIL, severity_max high: PF-2411 not closed by class (instance
    covered), PF-6efa closed (class), 2 new med substance findings introduced by the
    applies; note notes/review-harness-code-reviewer-plan-c3.md'
  sc_status: []
  needs_approval: false
  severity_max: high
  matrix_ok: none
  coverage_gaps: []
  findings:
  - kind: substance
    scope: none
    severity: high
    reader: harness-code-reviewer
    summary: PF-241126189d3c3d16550a5f09c7532ff3 is closed for the sampled blank-reason
      finding, not for the class.
    why: Delete the relocated row from both inventories and the unaccounted-candidate
      diagnostic prints the scanned candidate's file. That file changes on the split,
      but no field that items 1-3 rewrite supplies it, so SC-02 forbids an output
      a verbatim move forces (lead-confirmed at check-plan-routes.py::_unaccounted_candidate_findings).
  - kind: substance
    scope: none
    severity: med
    reader: harness-code-reviewer
    summary: 'New: T-02''s whole-line replacement can mask a change outside the sanctioned
      fields.'
    why: The re.sub map rewrites every token on the line, including an exemption repr
      printed beside the label (_exemption_finding), so the comparator can accept
      a difference that is not a consequence of items 1-3. On the fixed sampled states
      the risk is latent.
  - kind: substance
    scope: none
    severity: med
    reader: harness-code-reviewer
    summary: 'New: T-01''s ancestry/blob binding closes PF-6efa88c834c89ca43eea0322509703d9,
      but its checkpoint guard checks only one module.'
    why: T-01's verify asserts only that canonical_reader_audit.py is absent at the
      recorded commit. SC-03 and T-01's expected text require neither new module,
      so a commit that already holds structure_audit.py passes.
  - kind: substance
    scope: none
    severity: info
    reader: harness-code-reviewer
    summary: 'PF-6efa88c834c89ca43eea0322509703d9 closed for its class: the T-01 receipt
      must name an ancestor of HEAD and that commit''s test-file blob; nothing compares
      it against the live file.'
    why: 'Closure record: merge-base --is-ancestor plus rev-parse CP:T equality. The
      reader ran the git exit-code checks read-only.'
  readers:
  - reader: scope
    status: ran
    persona: harness-code-reviewer
    reason: none
  - reader: should-not-exist
    status: skipped
    persona: fable-advisor
    reason: 'not re-run at cycle 3: its cycle-1 findings were proportionality scope
      task plus form, trimmed at apply; the c3 dispatch re-reads only scope''s two
      open findings'
  - reader: design
    status: skipped
    persona: harness-ui-reviewer
    reason: 'not re-run at cycle 3: self-scoped out at cycle 1 (no UI surface); the
      two applies added none'
artifact: .harness/harness/features/FEAT-2489-plan-routes-split/runs/r-20261124-4-plan-validator/digest.md
```
