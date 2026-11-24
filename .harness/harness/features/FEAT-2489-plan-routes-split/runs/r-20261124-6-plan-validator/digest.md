# FEAT-2489 plan panel c4 — validator digest (final re-read)

**FAIL (severity_max high). The plan should go to the signer with three decidable questions, not to a fifth re-read.** Two of SC-02's three widenings are now correct and tight: W1 (producer-order exception) and W2 (line shifts for sites that stay in the entry). The class is now keyed on printed site identity, which closes the cycle-3 miss (`_unaccounted_candidate_findings`). W3 is still too narrow: it limits the locator to the first site a diagnostic names, and a Python traceback through moved code names several sites. T-02's matcher is lexical, so it can rewrite input data that merely looks like a locator. On the sampled states this is latent. T-04's saved receipt checks MAP lines by containment, not equality. T-01's guard is closed (it now checks both modules); one sentence of prose is left to fix. No BRIEF.md or plan.yaml edits were made in this run.

Reader: `scope` (harness-code-reviewer), note `notes/review-harness-code-reviewer-plan-c4.md`. should-not-exist and design were skipped (reasons in `panel-c4.md`).

## Per finding (each stated so a signer can decide it without earlier cycles)

1. **PF-241126189d3c3d16550a5f09c7532ff3 / PF-6159b2359da400c4da7dca8dcaa1415e (SC-02 item 5): not closed (substance/high).**
   - **W1, order exception: closed.** The exception is forced: the canonical scan walks files in sorted order, and consolidation sorts by line within each file. It is also tight, because it binds to the producer's own order and allows no arbitrary permutation.
   - **W2, line shift for retained sites: closed.** The exception is forced, because a retained `main` loader-rule hit prints a shifted line. It is also tight: only the exact offset of SC-01's diff is allowed.
   - **W3, "locator = first site named": not closed (too narrow).** It does not admit too much, but it misses a forced change. Lead-confirmed at source: `_classification_document` (`check-plan-routes.py:1254–1262`) checks only that the document is a dict. Set `rows: null` in the inventory, and `_named_plans` (`:1628`, `document.get("rows", [])` returns None) raises TypeError with no guard. The result is a stderr traceback whose frames run from `main` (retained, line shifted) through `_run_canonical_reader_audit`, `audit_canonical_readers` and `_named_plans` (all moved). After the move, every frame's `File "…", line N, in NAME` changes. Item 5 allows a change only at the first site, and it does not describe traceback frame syntax. So SC-02 cannot be satisfied by the move on this tree state, and SC-02 explicitly covers stderr and source-error behaviour.
   - **Signer decision:** should item 5's "first site" become "every site the diagnostic names, in any printed form, traceback frames included"? Frame order and every byte outside the locators would stay fixed. That is forced by the move and admits nothing the move does not produce. Or should crash tracebacks be excluded from SC-02 and disclosed?
2. **PF-b14b5b45525eb18f63e04849c88d3838 (T-02 map): not closed (substance/med, latent).** The map is now derived from the moved names, not from the inventory, and applied to one leftmost locator per line (`plan.yaml` T-02 intent). The quoted-exemption case is fixed. Checking unmodelled line-numbered locators and reorders closed (FAIL rather than PASS) is consistent with SC-02: BRIEF's Verification gaps disclose it, and the probes do not hit it. But the regex is lexical. The plan-read diagnostic `f"{plan}: plan cannot be read: …"` (`:1645`) prints an input value first. A `plan` value equal to `…/check-plan-routes.py::_classification_document` would be rewritten as though it were a code site. **Lead-checked latency:** no inventory `plan` value contains `::` (grep over `canonical-reader-classification.json`; positive control: 2 `plan` rows matched), and both matched trees share inputs. The sampled receipt therefore cannot fire it. **Signer decision:** require format-specific locator fields in T-02, or accept the risk as latent on a one-time notes script whose states are fixed.
3. **New, T-04 receipt binding (substance/med).** The T-04 verify checks `set(maps) <= set(final)` against the saved `equivalence-final.txt`. That is containment, so a receipt carrying an extra `MAP` line (e.g. one for retained `main`) passes. The remedy is one line: require the receipt's ordered MAP block to equal the live run's. My assessment, not a re-rating: this can only be reached through a hand-edited or stale receipt, since tree ids already bind the receipt to the pin. Its practical weight is below the reader's med.
4. **PF-1dd0f7a1329fa5038cc5e6aa8e0c3ecb (T-01 guard): closed (substance); form/low residual.** The verify asserts both modules absent at the recorded commit (`plan.yaml:211–212,254`), but the receipt prose at `:252` names only `canonical_reader_audit.py`. This is form: pm fixes it at apply, with no re-read.

## Fix order

Item 1 first (the W3 restatement). If T-02 adopts format-specific locators, define them to match the restated item 5's "every site" form, traceback frames included or explicitly excluded. Items 3 and 4 are independent one-liners.

## Assessment

- Every reader claim this digest relies on was re-derived at source in the worktree (P-15, G-08): `_classification_document`, `_named_plans`, `_classification_task_files`, `main`; plan T-01, T-02 and T-04 text. The reader reasoned; it did not execute.
- **Convergence.** This is the third cycle on SC-02. W1 and W2 converged. W3's miss is not another forgotten producer. It is a shape limit: "first site" against multi-site output. Restating the rule as "every printed site, in any form" closes the class rather than one instance. That is the signer's call (DEC-176). It will not settle through another panel cycle.

```yaml
VERDICT: FAIL
DIGEST:
  headline: 'Final re-read: SC-02''s W1 (order) and W2 (retained line shift) are closed
    and tight, and the class is now keyed on printed site identity. W3 (''first site
    named'') is too narrow, because a traceback through moved code changes every frame,
    so SC-02 is unsatisfiable on a rows:null inventory. T-02''s lexical matcher can
    rewrite lookalike input (latent), and T-04''s receipt checks MAP lines by containment.
    PF-1dd0 is closed, leaving a form fix. All three go to the signer.'
  open_questions:
  - id: PF-241126189d3c3d16550a5f09c7532ff3
    question: 'SC-02 item 5 limits the locator to the FIRST site a diagnostic names.
      Setting `rows: null` in canonical-reader-classification.json makes the canonical
      audit raise an unguarded TypeError in _named_plans. The stderr traceback has
      frames for main (stays in check-plan-routes.py, line shifts) and for _run_canonical_reader_audit,
      audit_canonical_readers and _named_plans (all moved). After the verbatim move
      every frame''s `File "...", line N, in NAME` changes, which item 5 forbids,
      so SC-02 cannot be met on that tree state. Should item 5 say ''every site the
      diagnostic names, in any printed form, traceback frames included'', keeping
      frame order and every other byte fixed? That is forced by the move and admits
      nothing else. Or should crash tracebacks be excluded from SC-02 and disclosed?'
    blocking: true
  - id: PF-b14b5b45525eb18f63e04849c88d3838
    question: T-02's one-time equivalence checker rewrites the leftmost `path.py::symbol`
      token on each line. A plan-read error prints its input `plan` value first. A
      plan value shaped like `.../check-plan-routes.py::_classification_document`
      would therefore be rewritten as if it were a code site. No inventory plan value
      contains '::' and both matched trees share inputs, so the sampled receipt cannot
      trigger this. Should T-02 match only recognized diagnostic locator fields, or
      does the signer accept this as a latent risk on a fixed-state notes script?
    blocking: true
  - id: T-04-receipt-map
    question: T-04's verify accepts the saved equivalence-final.txt if its MAP lines
      CONTAIN the live run's (set(maps) <= set(final)), so a receipt with extra MAP
      lines passes. Should the verify require the receipt's ordered MAP block to equal
      the live run's (a one-line change)? Tree ids already bind the receipt to the
      pin, so reaching this needs a stale or edited receipt.
    blocking: false
  files_touched:
  - .harness/harness/features/FEAT-2489-plan-routes-split/runs/r-20261124-6-plan-validator/state.yaml
  - .harness/harness/features/FEAT-2489-plan-routes-split/runs/r-20261124-6-plan-validator/panel-c4.md
  expertise_update: []
  team: plan
  steps_run: 1
  cycles_used: 0
  members:
  - step: scope
    persona: harness-code-reviewer
    verdict: FAIL
    headline: 'Do not sign as written: SC-02 excludes forced traceback changes, and
      the sample map still confuses input text with a code locator.'
    files_touched:
    - .harness/harness/features/FEAT-2489-plan-routes-split/notes/review-harness-code-reviewer-plan-c4.md
  must_fix:
  - 'PF-241126189d3c3d16550a5f09c7532ff3 (high, BRIEF.md SC-02 item 5): replace ''first
    site a diagnostic names'' with every site it names in any printed form, Python
    traceback frames included, keeping frame order and non-locator bytes fixed. Otherwise
    exclude crash tracebacks explicitly and disclose it. Signer''s call.'
  - 'PF-b14b5b45525eb18f63e04849c88d3838 (med, latent, plan.yaml T-02 intent): restrict
    the rewrite to the locator field of recognized diagnostic formats, not to any
    leftmost lookalike token. Otherwise the signer accepts it as latent.'
  - 'T-04 (med, plan.yaml T-04 verify): bind the saved receipt''s ordered MAP block
    exactly to the live run''s, not by subset.'
  branch: none
  escalations: []
  adequacy_notes:
  - 'Lead re-derived the reader''s claims at source in the worktree. _classification_document
    (check-plan-routes.py:1254-1262) checks only isinstance dict. _named_plans (:1628)
    iterates document.get(''rows'', []), which returns None when rows is null, so
    it raises with no guard. Other paths (classification_task_findings :1606) do guard
    rows. The plan-read diagnostic is f''{plan}: plan cannot be read: ...''. T-04
    verify uses set(maps) <= set(final). All reproduce as reasoned. The reader did
    not execute anything.'
  - 'W1 (order exception) closed: it is forced and bound to each producer''s own order.
    W2 (retained-site line shift) closed: it is forced and limited to SC-01''s exact
    offset. W3 does not admit too much, but it is too narrow.'
  - 'The T-02 lookalike is latent on the receipt. A grep for plan values containing
    ''::'' in canonical-reader-classification.json finds 0 (positive control: 2 plan
    rows found), and the matched trees share every input.'
  - 'Form residual, fixed by pm at apply with no re-read: plan.yaml:252 (T-01 receipt
    prose) names only canonical_reader_audit.py. The verify (211-212, 254) already
    requires both modules absent, so PF-1dd0f7a1329fa5038cc5e6aa8e0c3ecb is closed
    in substance.'
  - 'Lead view on T-04, not a re-rating: tree ids already bind the receipt to the
    pin, so an extra MAP line can only come from an edited or stale receipt. Its practical
    weight is below the reader''s med.'
  - 'Convergence: this is the third cycle on SC-02. W1 and W2 converged. W3''s miss
    is a shape limit (a first-site rule against multi-site output), not another missed
    producer. ''Every printed site, in any form'' closes the class. Route it to the
    signer (DEC-176) rather than run another panel.'
  - 'Fix order: SC-02 W3 restatement first, then the T-02 locator formats defined
    to match it. T-04 and the T-01 prose are independent one-liners.'
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
    summary: W3 leaves SC-02 unsatisfiable by a verbatim move on a malformed but readable
      inventory.
    why: With rows:null, the canonical runner emits a traceback with retained entry
      frames followed by relocated audit frames. BRIEF.md:32 freezes all but the first
      site and does not describe Python frame syntax. W1 producer ordering and W2
      retained line offsets are tight; the former scanned-candidate miss is now covered.
  - kind: substance
    scope: none
    severity: med
    reader: harness-code-reviewer
    summary: "T-02\u2019s lexical matcher still rewrites data rather than a locator\
      \ in a plan-read diagnostic."
    why: A named-plan input equal to ENTRY::_classification_document is printed verbatim
      in the plan-read error. The regex in plan.yaml:315 rewrites it, rejecting the
      unchanged output and accepting an unauthorized change. The disclosed fail-closed
      exclusions for line-numbered locators and reordering do not affect the specified
      samples.
  - kind: substance
    scope: none
    severity: med
    reader: harness-code-reviewer
    summary: "T-04\u2019s final receipt admits MAP entries not present in the restricted\
      \ live map."
    why: "plan.yaml:493\u2013501 checks map shape on the live run but only containment\
      \ in the saved receipt. Adding an extra entry for retained main to a valid receipt\
      \ still passes."
  - kind: form
    scope: none
    severity: low
    reader: harness-code-reviewer
    summary: "T-01\u2019s receipt prose still names only one module."
    why: "plan.yaml:252 names only canonical_reader_audit.py even though the checkpoint\
      \ verification and expected result require both new paths absent at the recorded\
      \ commit (211\u2013212,254). PF-1dd0f7a1329fa5038cc5e6aa8e0c3ecb is closed in\
      \ substance."
  readers:
  - reader: scope
    status: ran
    persona: harness-code-reviewer
    reason: none
  - reader: should-not-exist
    status: skipped
    persona: fable-advisor
    reason: 'not re-run at cycle 4: its cycle-1 findings were proportionality scope
      task plus form, trimmed at apply; the c4 dispatch re-reads only scope''s three
      open findings'
  - reader: design
    status: skipped
    persona: harness-ui-reviewer
    reason: 'not re-run at cycle 4: self-scoped out at cycle 1 (no UI surface); the
      applies added none'
artifact: .harness/harness/features/FEAT-2489-plan-routes-split/runs/r-20261124-6-plan-validator/digest.md
```
