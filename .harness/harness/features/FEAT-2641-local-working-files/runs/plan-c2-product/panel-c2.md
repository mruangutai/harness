# Reader fan-in — plan-c2-product cycle 2

One reader ran: the operator authorized exactly one scope re-read (LEAD-01 in
notes/answers-plan-product.md). should-not-exist and design were not re-dispatched this cycle by
operator scope, not by host failure. Findings are transcribed at the reader's own severity and
kind; the reader's note is notes/review-harness-code-reviewer-plan-c2.md.

```yaml
VERDICT: FAIL
DIGEST:
  readers:
    - reader: scope
      status: ran
      persona: harness-code-reviewer
      reason: "operator-authorized single re-read; returned FAIL; note at notes/review-harness-code-reviewer-plan-c2.md"
    - reader: should-not-exist
      status: skipped
      persona: fable-advisor
      reason: "status skipped: not part of the operator's one-reader cycle-2 authorization (LEAD-01); ran in cycle 1"
    - reader: design
      status: skipped
      persona: harness-ui-reviewer
      reason: "status skipped: not part of the operator's one-reader cycle-2 authorization (LEAD-01); ran in cycle 1"
  findings:
    - reader: code-reviewer
      severity: high
      kind: substance
      summary: "T-05/T-09 (D-11/D-12, SC-18): the local decline can silently skip."
      why: "Adding a dispatch arm leaves gh-sync.py's shared config/auth preflight in front of the handler. With sync disabled or unauthenticated gh it exits 0 before recording or cleaning; an exit-only landing report cannot detect that."
    - reader: code-reviewer
      severity: high
      kind: substance
      summary: "T-05 (D-11, SC-18): a failed decline commit still permits cleanup."
      why: "plan.yaml:728 explicitly preserves the nonfatal ship helper and its two-file pathspec. A commit refusal leaves the ledger dirty while cleanup can erase evidence; alternatively a dirty plan.yaml can be committed alongside the decline."
    - reader: code-reviewer
      severity: high
      kind: substance
      summary: "T-03/T-05/T-07 (D-05/D-11, SC-08/09/18): clean can resolve the wrong checkout or fail before deletion."
      why: "plan.yaml:620,624 uses a slugged artifact basename as the worktree ID and calls resolve_root without bin_dir. A supported short-ID linked worktree is not found by exact long-ID path lookup, allowing fallback to the owner and success with the actual evidence left behind."
    - reader: code-reviewer
      severity: med
      kind: substance
      summary: "T-06 (SC-17): post-merge lookup failure can report a merge refusal."
      why: "plan.yaml:763 only specifies catching clean errors, not feature directory or owner resolution. Those errors can escape the landed-merge exit-4 result; the specified diagnostic also omits the instruction not to re-run merge."
    - reader: code-reviewer
      severity: med
      kind: substance
      summary: "T-08 (D-04/D-05, SC-10/15): two amendment reasons still direct obsolete behavior."
      why: "The DEC-253 row says only Expertise is committed, omitting feature.json, and the DEC-238 row says every terminal path cleans, which would include ship before distill. Keep DEC-257's strike and the DEC-230 amendments."
    - reader: code-reviewer
      severity: low
      kind: form
      summary: "T-05/T-07/T-08/T-09/T-10: the task list is not topological."
      why: "T-10 is placed after four tasks that list it in depends_on. The graph is acyclic and all SCs are traced."
```
