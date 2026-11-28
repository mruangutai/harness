# repanel2-product cycle 3 — reader fan-in (lead)

Cycle 3 is a re-read of the substance text pm applied in cycle 2: T-01, T-03, D-02.choice, and BRIEF SC-02, SC-03, SC-05..08, SC-10 and the disclosure. It ran in two reads.

**First read.** Three readers read the same text in one wave:
- **scope** (harness-code-reviewer): FAIL, 2 findings (1 high substance, 1 med substance). Note: `notes/review-harness-code-reviewer-plan-c3.md`.
- **should-not-exist** (fable-advisor): resolved and ran. PASS, 2 proportionality findings, both `scope: task`. Nothing should be deleted.
- **design** (harness-ui-reviewer): judged itself IN scope, because the operator-facing disclosure is a text-only surface. FAIL, 1 high substance finding. No DESIGN.md is needed. Note: `notes/review-harness-ui-reviewer-plan-c3.md`.

pm then applied those findings: T-03 verify and intent, plus one BRIEF disclosure sentence. The routing is in `runs/repanel2-product/apply1-changes.md`.

**Second read** (send-back 1 of 1 per reader, cycles_used 1). Each reader re-read only the text changed for its own findings:
- **scope**: FAIL. Both routed findings are closed, and it raised 3 new med substance findings. Note: `notes/review-harness-code-reviewer-plan-c3-reread.md`.
- **should-not-exist**: PASS. Both findings are closed, with no new findings and nothing newly broken.
- **design**: FAIL. The high finding is closed, and it raised 1 new med substance finding. Note: `notes/review-harness-ui-reviewer-plan-c3-reread.md`.

Per the dispatch, a substance finding raised by the second read is **not applied**. It stays open, and the run returns FAIL.

Every severity, kind and summary below is the reader's own, unchanged. I assigned no PF- ids. Two readers labelled themselves by persona: the scope reader as `code-reviewer` and the design reader as `ui-reviewer`. I recorded each under its team step id, as panel-c2.md did. fable-advisor has no write grant, so I transcribed its findings from its returns.

## Verdicts on the open cycle-2 substance findings

| cycle-2 id | verdict | read | worktree pointer |
|---|---|---|---|
| PF-14c27514 (restates PF-e7dd0045) | **closed** | 2nd (1st: not closed) | plan.yaml:339–340, 360, 368, 370; BRIEF.md:41, 43. Each kind's exact stream-key set is checked before comparison, so `{}` or an omitted stderr fails |
| PF-c36ed89c | **closed**: the inventory bounds the delta (authorization was not judged) | 1st | plan.yaml D-02.choice :152; T-03 intent :372–376; BRIEF.md:47, 98–102 |
| PF-c82fdafb | **closed** | 1st | T-01 intent plan.yaml:286; SC-03 BRIEF.md:35 |
| PF-390fdc3e | **closed** | 1st | T-03 verify :335–336, 347–349; intent :364; SC-10 BRIEF.md:51 |

## Verdicts on this cycle's first-read findings (second read)

| finding (reader) | verdict | pointer |
|---|---|---|
| scope high: "PF-14c27514 not closed: … missing required measurement streams" | closed | plan.yaml:339–340, 360 |
| scope med: "New: T-03 accepts an audit-count disclosure that disagrees with the committed raw audit" | closed | plan.yaml:346, 374; BRIEF.md:45, 47 |
| design high: "D-02's operator-facing disclosure is not bound to the measured output" | closed | plan.yaml:341, 346, 374, 376 |
| should-not-exist med: Q3(a) exceedance undisclosed | closed (disclosed; whether to amend Q3(a) is the operator's call) | BRIEF.md:104–110 |
| should-not-exist low: two implementations | closed | plan.yaml:376 (end of Compare paragraph) |

Still open for the operator, and no reader's to close: PF-7999938a (authorization), PF-d35d903d and PF-502d3541 (the bun-leg pair, whose facts are unchanged).

```yaml
DIGEST:
  readers:
    - reader: scope
      status: ran
      persona: harness-code-reviewer
      reason: "cycle-3 first read FAIL (2 findings, notes/review-harness-code-reviewer-plan-c3.md); second read of apply-1 text FAIL: both routed findings closed, 3 new med substance (notes/review-harness-code-reviewer-plan-c3-reread.md)"
    - reader: should-not-exist
      status: ran
      persona: fable-advisor
      reason: "resolved and ran twice; first read PASS, 2 proportionality task findings; second read PASS, both closed, no new findings; transcribed by the lead (no write grant)"
    - reader: design
      status: ran
      persona: harness-ui-reviewer
      reason: "Mode A in scope (text-only operator disclosure, no DESIGN.md needed); first read FAIL, 1 high; second read FAIL, high closed, 1 new med substance (notes/review-harness-ui-reviewer-plan-c3-reread.md)"
    - reader: goalcheck
      status: ran
      persona: harness-pm
      reason: ran once at plan exit in run plan-product and re-graded there after the cycle-1 apply; not re-run in cycles 2 or 3 (SC-09); dated addenda in cycles 2 and 3; note notes/research-FEAT-2581-feature-record-package-goalcheck-plan.md
  findings:
    - reader: scope
      summary: "PF-14c27514 not closed: T-03 accepts CLI and replay records missing required measurement streams."
      severity: high
      kind: substance
      scope: none
      why: "plan.yaml:338–343 checks class presence and replay IDs but not required stream keys. If the recorder omits stderr on both sides, no stderr change can enter the recomputed divergence set even though SC-05/06 require it; even streams: {} on both sides passes. Reading the records at review_sha closes the ref-binding gap, not this evidence gap. Second read: closed (plan.yaml:339–340, 360)."
    - reader: scope
      summary: "New: T-03 accepts an audit-count disclosure that disagrees with the committed raw audit."
      severity: med
      kind: substance
      scope: none
      why: "plan.yaml:346 checks the summary line by regex only; a receipt reporting 0 0 passes even when both raw audit summaries contain different nonzero counts. The raw audit:stdout divergence remains bounded, so this does not reopen the inventory finding. Second read: closed (plan.yaml:346, 374)."
    - reader: design
      summary: "D-02’s operator-facing disclosure is not bound to the measured output."
      severity: high
      kind: substance
      scope: none
      why: "BRIEF.md:47,98–102 and plan.yaml:372–376 require exact before/after output in build-divergences.md and the audit count from both runs. T-03 verify (plan.yaml:335–352) checks recomputed IDs and ruling metadata but never reads build-divergences.md and accepts any two numeric audit counts. A missing or stale disclosure can pass while the operator rules on a misrepresented delta. Second read: closed (plan.yaml:341, 346, 374, 376)."
    - reader: should-not-exist
      summary: "T-03's committed raw-measurement store (notes/measurements/{baseline,pin}.jsonl.gz), recorder/sitecustomize.py interception of every Python process, and the divergence-recomputing verify together exceed Settled Q3(a)'s stated bar — 'reusing FEAT-70's receipt-script structure with no new proof framework' — and the plan nowhere discloses that exceedance to the signer."
      severity: med
      kind: proportionality
      scope: task
      why: "git ls-tree a98451c5 shows FEAT-70 committed scripts, summary receipts and divergences only — no raw measurements, no recorder, no preload. The machinery is the ruled price of PF-14c27514, so deleting it would reopen a high finding; but the operator signs text that silently supersedes their own settled constraint. Remedy: one disclosure line or one explicit signature question amending Q3(a) — not removal. Second read: closed by the disclosure at BRIEF.md:104–110; amending Q3(a) stays the operator's."
    - reader: should-not-exist
      summary: "The divergence set is computed by two independent implementations — feat2581-cleanpin.py writes the receipt's divergence lines, and T-03's verify recomputes them with its own root-token/base64 logic and hard-asserts mv==D — so any drift between the two implementations, not any real behaviour difference, voids the receipt."
      severity: low
      kind: proportionality
      scope: task
      why: "A normalization drift between cleanpin.py and the verify would force two fresh full clean-checkout corpus runs with nothing wrong. Keep the duplication; name T-03 intent's comparison paragraph as normative for both. Second read: closed (plan.yaml:376)."
    - reader: scope
      summary: "T-03 accepts invalid base64 as a captured stream."
      severity: med
      kind: substance
      scope: none
      why: "plan.yaml:339–341,360: stderr \"!!!!\" and \"\" both decode to empty under permissive decoding, so an invalid measurement compares equal to a valid empty capture. Raised by the second read; not applied in this run (open)."
    - reader: scope
      summary: "T-03 accepts unrelated source templates for unreached D-02 items."
      severity: med
      kind: substance
      scope: none
      why: "plan.yaml:341,372,376: a valid d02# ID with an arbitrary nonblank file, symbol, old_source, and new_source passes, allowing the operator to rule on the wrong source. Raised by the second read; not applied in this run (open)."
    - reader: scope
      summary: "T-03 can pass without the `divergence:` records SC-08 requires in build-divergences.md."
      severity: med
      kind: substance
      scope: none
      why: "plan.yaml:335,341,376,378 and BRIEF.md:47: valid divergence_entry blocks alone pass; the verifier checks the literal divergence: marker only in the separate generated receipt. Raised by the second read; not applied in this run (open)."
    - reader: design
      summary: "New: T-03 permits an operator-facing disclosure made up only of escaped byte literals."
      severity: med
      kind: substance
      scope: none
      why: "Worktree plan.yaml:376 puts any explanation outside the verified delimiters but does not require it. A multiline or non-ASCII stream is flattened to one escaped line per side, so long entries can hide the change the operator must rule on. Raised by the second read; not applied in this run (open)."
```
