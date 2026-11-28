# Panel fan-in — FEAT-2516 plan, cycle 2 (run 2026-11-27-01-plan-product)

One reader ran, by operator ruling 3 (2026-11-27): a single scope re-read of the revised T-03.
should-not-exist and design were NOT run and are recorded `status skipped`, never as ran-and-empty.
Severities and kinds are the reader's own, transcribed unchanged; no PF ids assigned here
(record-panel computes them). Two summaries are byte-identical to cycle-1 findings (PF-d0e16ad5,
PF-3a8e31e4): the re-read holds both OPEN. The reader's `scope: none` on non-proportionality
findings is dropped as a shape artefact (scope is carried by proportionality findings only).

- scope (harness-code-reviewer): FAIL, severity_max high — notes/review-harness-code-reviewer-plan-c2.md
  The same note grades cycle-1 PF-590e7bb6 and PF-92bcdbb1 CLOSED by the revised T-03 text.

No proportionality finding was raised.

```yaml
DIGEST:
  readers:
    - reader: scope
      status: ran
      persona: harness-code-reviewer
      reason: "one T-03 re-read per operator ruling 3; VERDICT FAIL, 3 must_fix, PF-d0e16ad5 and PF-3a8e31e4 OPEN"
    - reader: should-not-exist
      status: skipped
      persona: fable-advisor
      reason: "status skipped - not run: operator ruling 2026-11-27, one scope re-read only"
    - reader: design
      status: skipped
      persona: harness-ui-reviewer
      reason: "status skipped - not run: operator ruling 2026-11-27, one scope re-read only"
  findings:
    - reader: scope
      kind: substance
      severity: high
      summary: "T-03 can attribute a fix round without meeting the receipt contract."
      why: "A.1-C now cover sole-effect counting, exact keys and 40-hex fix_commit in the shared writer/INV-7 path, and F.2 plans a successful composed close. But a receipt-backed FAIL can be rewritten PASS by a same-count bare run-end without invoking _attach_digest, and INV-7 checks the ledger verdict and digest count but accepts a matching receipt over a PASS digest."
    - reader: scope
      kind: substance
      severity: high
      summary: "T-03 resolves fleet fix commits in the central planning repository."
      why: "A.3 correctly selects the fleet member directory, and F.2's product-only positive distinguishes it from the planning tree. But an existing noncheckout product directory nested under planning passes isdir and git -C resolves the enclosing planning repo. The planning-only refusal also needs a fresh fixture and a diagnostic assertion to rule out a replay-conflict false positive."
    - reader: scope
      kind: substance
      severity: high
      summary: "T-03's four-parent lookup rejects valid receipts for unsegmented feature records."
      why: "The writer accepts <repo>/.harness/features/FEAT-.../feature.json, but the moved validator lookup climbs above <repo>. F.2 tests only the segmented shape, so a valid unbound fix commit is refused in a supported layout."
    - reader: scope
      kind: form
      severity: low
      summary: "decisions_affected omits DEC-256's QA repository selection rule."
      why: "A.3 relocates the selector governed by DEC-256's QA review-pin exception D-01. Record keep for the existing rule; DEC-157 is correctly amend, not strike."
```
