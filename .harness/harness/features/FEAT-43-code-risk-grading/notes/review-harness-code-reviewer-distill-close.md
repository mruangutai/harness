# Code-reviewer Expertise distillation — FEAT-43 close

**BLUF: PASS, three displacements landed.** All three relay candidates (C1/C2/C3) are accepted on
their merits and now live in the DURABLE checkout's `.harness/expertise/harness-code-reviewer.md`
(`/Users/molchairuangutai/GitHub/harness/...` — absolute, per the lead's correction; the FEAT-43
worktree copy is unmodified since it is slated for removal). Zero own-note candidates cleared the
bar.

## Why the first attempt in this same run said "unapplied"

`expertise-merge.py apply` is additive union only — no replace/drop primitive. Confirmed live,
twice: on a scratch copy, and again directly against the durable file immediately before editing
(both times: same-id proposal -> `CONFLICT ... EXIT=7`, new-id proposal into a full section ->
`CAP EXCEEDED ... EXIT=8`, file byte-identical after either refusal). `harness-distill`'s own ops
vocabulary names `op: replace`, but the tool cannot execute one when the target section is at cap
— this is a known, previously-recorded gap (`FEAT-36-merge-gitignore-coverage/notes/review-harness-code-reviewer-distill-validator-c1.md`
closed the identical situation as PASS/not-permitted).

**Lead correction, mid-run:** `Feat43ValidationDistill` supplied the resolution procedure the SKILL's
exit-7 handling ("resolve it yourself") always implied but never spelled out mechanically, already
in live use by sibling members this same feature (qa's diff on the durable checkout shows the same
same-id replacement pattern): (1) run `expertise-merge.py apply` against the exact durable path to
get the `CONFLICT`/exit-7 confirmation as evidence — applies nothing; (2) resolve with one targeted
edit confined to the conflicting line(s), never a reconstructed whole-file payload guessed from a
prior read — done here as a Python string-substitution pass that asserts each old line occurs
exactly once, replaces it, and asserts the resulting line-count and the exact set of changed line
indices before writing, so an unrelated line moving would abort the write rather than silently land;
(3) `check-expertise.sh` on the result. Also corrected: write the DURABLE checkout absolutely, not
the worktree — the worktree is merged and slated for removal, and a write there (confirmed live for
`harness-dev-ops.md`: durable byte-identical to HEAD, worktree copy carrying real edits) is
orphaned the moment the worktree is deleted.

## Empirical trail

```
$ python3 expertise-merge.py apply --file <durable>/harness-code-reviewer.md --entries entries.md
CONFLICT section=Patterns id=P-07 / P-09; CONFLICT section=Outcomes id=O-07
EXIT=7          # applies nothing; file md5 unchanged (89f8879e...)

# targeted edit: read, assert each old line's exact text occurs exactly once, replace,
# assert 45 lines before == 45 lines after, assert changed line indices == {8, 10, 40}, write.

$ check-expertise.sh <durable>/harness-code-reviewer.md
OK
EXIT=0

$ git diff HEAD -- .harness/expertise/harness-code-reviewer.md
# exactly 3 changed lines (P-07, P-09, O-07); everything else byte-identical
$ git status --porcelain
# harness-code-reviewer.md is the only file this run touched, among several siblings' concurrent edits
```

## Candidate dispositions

### Relay (3 candidates, 3 accepted, 0 rejected — all landed)

- **C1 — accepted, merged into P-09.** Sharpens P-09 ("enumerate every other route... check each is
  separately gated") with complement-enumeration + grep-verify-absence + checkable-by-tier-above,
  generalized past tool/argv/env-var guards to any guard (structural, regex).
- **C2 — accepted, displaces O-07.** Novel severity-ranking rule: rank a zero-cost strengthening by
  its re-verification cost, not its correctness, when no cycle remains to re-check the change. O-07
  was the narrowest existing Outcome — a single-scenario "inherited defect + newly established
  trigger" rule.
- **C3 — accepted, displaces P-07.** "Watch the watcher": when a guard becomes the sole detector for
  a defect class, check whether a meta-gate/self-grading registry tracks it. P-07 was the narrowest
  existing Pattern — a single-scenario "reproduced count vs. plan's disclosed caveat" rule.

### Own notes (4 candidates considered, 0 accepted, 4 rejected)

Sourced from the 5 most recent own notes (bounded-repair-review, delta-c29, mergedelta, delta-c28,
delta-c27).

1. **Fixture-as-oracle, exit-code-only fail-open** (delta-c27, §C). Rejected — subsumed by G-06
   (test double not reading its own arguments) + P-02 (fail-open before/after the write it guards).
2. **Generic-guard-vs-specific-guards trade-off** (delta-c28, Advisory b). Rejected — narrower
   instance of P-02's fail-open scope; the deletion-test/seam judgment is already available via
   `harness-codebase-design`.
3. **Scope ratification by principle, not literal named site** (delta-c27, §B). Rejected —
   situational to this project's Q-ruling convention; already exercised by the four-question Stage-1
   framework in `harness-code-review` itself.
4. **Self-correct a diff-stat via `--numstat`** (delta-c28, Send-back 1). Rejected — narrower
   instance of G-08 (re-verify anchors before publishing) + O-08 (write a revision honestly).

## Section counts

| Section | Before | After |
|---|---:|---:|
| Patterns | 15 | 15 |
| Gotchas | 15 | 15 |
| Outcomes | 10 | 10 |
| Open | 0 | 0 |

Pure displacement — replace, not add — so counts are unchanged. `.harness/harness/expertise/harness-code-reviewer.md`
(repository layer): not touched — none of the accepted candidates turns on anything specific to this
repository.

## What did not run

No project-wide validation, linter, formatter, or test suite ran. `check-expertise.sh` ran only
against the one changed file, per the assignment's constraint.

```yaml
VERDICT: PASS
DIGEST:
  headline: "Three relay candidates (guard-complement enumeration + verify; rank a strengthening by re-verification cost; who watches the watcher) landed via a lead-supplied resolve procedure after expertise-merge.py's additive-only union refused all three same-id replacements (exit 7, confirmed live on the durable file)."
  severity_max: n/a
  findings: 0
  must_fix: []
  spec_violations: []
  candidates_accepted: { relay: 3, own: 0 }
  candidates_rejected:
    relay: []
    own:
      - { candidate: "fixture-as-oracle exit-code-only fail-open", reason: "subsumed by existing G-06 + P-02" }
      - { candidate: "generic guard vs specific guards null-tolerance trade-off", reason: "narrower instance of P-02's fail-open scope; deletion-test judgment already covered by harness-codebase-design" }
      - { candidate: "scope ratification by principle vs literal named site", reason: "situational to this project's Q-ruling convention; already exercised by harness-code-review's Stage-1 four-question framework" }
      - { candidate: "self-correct diff-stat via --numstat", reason: "narrower instance of existing G-08 + O-08" }
  section_counts_before:
    harness-code-reviewer.md: { Patterns: 15, Gotchas: 15, Outcomes: 10, Open: 0 }
  section_counts_after:
    harness-code-reviewer.md: { Patterns: 15, Gotchas: 15, Outcomes: 10, Open: 0 }
  check_expertise: "OK, exit 0 on /Users/molchairuangutai/GitHub/harness/.harness/expertise/harness-code-reviewer.md"
  reviewed: "FEAT-43-code-risk-grading distillation sources: 5 own notes + 3 lead-relayed candidates (validate-delta-c29-validator/digest.md item 1, 4a, 4b)"
  human_commits_in_scope: []
  open_questions: []
  files_touched:
    - /Users/molchairuangutai/GitHub/harness/.harness/expertise/harness-code-reviewer.md
  expertise_update:
    - { op: merge, target: P-09, section: Patterns, entry: "WHEN reviewing any guard — access-control, structural, or regex — DO enumerate every route, syntactic form, or field it does NOT reach, grep-verify each is absent from the tree, and state the boundary as checkable, not hoped; passing the tested case never proves reachability-completeness.", why: "C1 (relay, validate-delta-c29-validator digest item 1) sharpens P-09 with complement enumeration + grep-verified absence + checkable-by-tier-above, generalized past tool/argv/env-var guards" }
    - { op: replace, target: P-07, section: Patterns, entry: "WHEN a guard becomes the sole automated detector for a defect class DO check whether anything watches the watcher — is the guard's own function tracked by a meta-gate or self-grading registry, so a future edit that weakens it doesn't go unnoticed.", why: "C3 (relay, digest item 4b) displaces the narrowest existing Pattern, a single-scenario rule" }
    - { op: replace, target: O-07, section: Outcomes, entry: "WHEN a proposed fix is measurably correct and zero-cost DO rank it should_fix, not must_fix, if applying it is itself an unverified source change with no review cycle left to re-verify — a measured green artifact outranks an unverified improvement.", why: "C2 (relay, digest item 4a) displaces the narrowest existing Outcome, a single-scenario rule" }
artifact: .harness/harness/features/FEAT-43-code-risk-grading/notes/review-harness-code-reviewer-distill-close.md
```
