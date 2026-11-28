# repanel3-product cycle 4 — reader fan-in (lead)

Cycle 4 is the one bounded re-read that the operator ordered at PL-11 (a). It covers pm's single rewrite pass: T-03 verify and intent, D-01.because, and BRIEF SC-08, the Verification gaps and the Constraints disclosure. The change list is `runs/repanel3-product/apply1-changes.md`. Each reader read once. There is no second read, and no new finding is applied.

- **scope** (harness-code-reviewer): FAIL. It closes PF-96cdf9f1, PF-3882d444 and PF-cf9cf710. It raised 3 med substance findings, 1 low substance finding and 1 low form finding. Note: `notes/review-harness-code-reviewer-plan-c4.md`.
- **design** (harness-ui-reviewer): FAIL. It closes PF-a37e5b40. It raised 3 med substance findings. Note: `notes/review-harness-ui-reviewer-plan-c4.md`.
- **should-not-exist** (fable-advisor): not dispatched this cycle. The operator's ruling PL-11 (a) names the scope and design readers only. It did not run, so it found nothing.

Every severity, kind and summary below is the reader's own, unchanged. I assigned no PF- ids. Both readers reported the same defect: test_change compares patches after text=True newline translation. Scope rated it low and design rated it med. I kept both entries and both severities as the readers gave them.

## Verdicts on the four cycle-3 findings

| id | verdict | reader | worktree pointer |
|---|---|---|---|
| PF-96cdf9f1 | closed | scope | plan.yaml T-03.verify `cz` strict decode (:396+); see the reader's note |
| PF-3882d444 | closed | scope | plan.yaml T-03.verify TB/`sg`/`SO`, `bd==BODY`; see the reader's note |
| PF-cf9cf710 | closed | scope | plan.yaml T-03.verify `divergence:`…`end_divergence` set equality; BRIEF.md:47 |
| PF-a37e5b40 | closed | design | plan.yaml:409, 416–418, 449 |

Still open for the signature, and no reader's to close: PF-7999938a, PF-d35d903d and PF-502d3541.

```yaml
DIGEST:
  readers:
    - reader: scope
      status: ran
      persona: harness-code-reviewer
      reason: "cycle-4 single read FAIL: closes PF-96cdf9f1, PF-3882d444, PF-cf9cf710; 3 med + 1 low substance and 1 low form new (notes/review-harness-code-reviewer-plan-c4.md)"
    - reader: should-not-exist
      status: skipped
      persona: fable-advisor
      reason: "status skipped: not dispatched this cycle because the operator's ruling PL-11 (a) names the scope and design readers only; it did not run and is not recorded as finding nothing"
    - reader: design
      status: ran
      persona: harness-ui-reviewer
      reason: "Mode A in scope (text-only operator disclosure); cycle-4 single read FAIL: closes PF-a37e5b40; 3 med substance new (notes/review-harness-ui-reviewer-plan-c4.md)"
    - reader: goalcheck
      status: ran
      persona: harness-pm
      reason: "ran once at plan exit in run plan-product; not re-run in cycles 2-4 (SC-09); cycle-4 dated addendum at notes/research-FEAT-2581-feature-record-package-goalcheck-plan.md:315-348"
  findings:
    - reader: scope
      summary: "T-03 reports SAME when a one-summary file's non-marker stdout changes."
      severity: med
      kind: substance
      scope: none
      why: "Worktree plan.yaml:412–413,439 compares whole stdout only for unnamed files. Keeping the PASS marker, exit and source unchanged while changing the separate 0 failure(s) line from tests/integration/test-suite-claim-preservation.py:79–83 produces no cases# record, contrary to BRIEF.md:51,61–65."
    - reader: scope
      summary: "A suite record's claimed file is not bound to its argv or checkout cwd."
      severity: med
      kind: substance
      scope: none
      why: "Worktree plan.yaml:407,410–413,437 checks the set of IDs and stream encodings but never consumes argv or cwd. A recorder that assigns the previous file's completed run to the next ID on both sides can produce a passing receipt without running the next file."
    - reader: scope
      summary: "Replacing the checkout root before JUnit parsing can invalidate otherwise valid Bun evidence."
      severity: med
      kind: substance
      scope: none
      why: "Worktree plan.yaml:408,411–412,439 replaces a root with literal <checkout> before ElementTree parses cases. A testcase attribute containing that root becomes invalid XML, aborting the gate instead of deriving SC-10 identity. This does not dispose of the open Bun CLI-leg findings."
    - reader: scope
      summary: "The new test_change check compares text-translated patches, not exact patch bytes."
      severity: low
      kind: substance
      scope: none
      why: "Worktree plan.yaml:399,419,445 reads Git patch stdout with text=True, which converts CRLF in a changed content line to LF and depends on the host encoding. The path and body checks otherwise cover the changed paths; no CRLF match was found in the scoped Python files. BRIEF.md:47 calls for exact old and new bytes."
    - reader: scope
      summary: "OQ-C4-1: T-01 and the BRIEF retain stale only-language beside the explicit D-01 exception."
      severity: low
      kind: form
      scope: none
      why: "Worktree plan.yaml:350,352–353 and BRIEF.md:97,108–112 still claim only file/id or only imports/targets and D-02 expectations. D-01 and PL-03 explicitly authorize the loader row's remedy and the named expectation changes. This is carried editorial ambiguity, not a new scope change or a reopened ruling."
    - reader: design
      summary: "The mandatory account can obscure whitespace-only and long binary changes."
      severity: med
      kind: substance
      scope: none
      why: "plan.yaml:409,418,449 leaves tabs and spaces literal and diffs whole LF-delimited lines. A trailing tab versus a trailing space can look identical; LF-free binary data becomes two long escaped lines without a changed-byte location. BRIEF.md:47,107–108 promises a readable rendering of what changed."
    - reader: design
      summary: "The newly verified test_change diff is not byte-exact for line-ending changes."
      severity: med
      kind: substance
      scope: none
      why: "plan.yaml:399,419 uses text=True, translating CRLF/CR to LF before equality. The CRLF-to-LF edit can look identical after the diff markers, and a verbatim CRLF-bearing hunk fails the comparison despite plan.yaml:445 and BRIEF.md:47 promising exact old/new bytes."
    - reader: design
      summary: "The BRIEF discloses growth beyond PL-09 but understates what the new suite records retain."
      severity: med
      kind: substance
      scope: none
      why: "BRIEF.md:119–122 lists exit, stdout, stderr and case list; plan.yaml:407,433,437,439 additionally stores argv and cwd per side and exact Bun JUnit XML, not just a case list. The BRIEF correctly avoids claiming prior approval of the growth."
```
