# Code review — FEAT-54-handoff-done-when — c0

Pinned range: `0ec44965a961d19177de871c3bb1f02b701e646b..e75767df4b75e71f2c9b12766604cee5008d94e1`

## Verdict

**FAIL.** Stage 1 found three substantive specification mismatches, two of them fail-open paths in the enforcement layer. The mandatory Python risk grade also fails. Per the two-stage protocol, the discretionary Stage 2 quality review was not entered after Stage 1 failed.

The complete 60-file pinned diff and the full required shared implementation/corpus set were inspected. No commit in the reviewed range has the configured `[harness:human]` prefix.

## Stage 1 — specification compliance

### F-01 — high — an invalid handoff Edit lands before it is reported

**Failure scenario.** Start with a baselined four-section handoff and use `Edit` without adding `## Done when`. The PreToolUse route exits successfully because it reconstructs Edit content only for run digests and run state; every other Edit exits at `.claude/skills/harness/bin/check-domain.sh:1858-1874`. The edit therefore mutates the note. PostToolUse later reads the already-landed file and exits 2 at `check-domain.sh:1877-1897`, but that report cannot undo the invalid edit. A historical note can consequently be changed while still lacking the fifth section, contrary to the requirement that the edit be refused and that a historical note leave the old shape only by becoming compliant.

**Evidence.** `BRIEF.md:35-39` requires unresolved pointers to be refused when written **or edited**, and `BRIEF.md:104-107` (SC-06) requires an edit without the section to be refused. The signed T-03 case (f) says the same at `plan.yaml:333-335`. The purported integration proof pre-writes invalid/valid bytes and invokes only `PostToolUse` (`tests/integration/test-check-domain.py:4063-4076`); it proves post-hoc reporting, not refusal or non-mutation.

**Owner lane.** **Main session direct mutation** — `check-domain.sh` and its gate test are DEC-174 enforcement surfaces.

**Required remedy.** Make the pre-tool Edit path validate the reconstructed candidate handoff and refuse invalid edits before mutation; replace the current post-write-only fixture with an assertion that exercises the pre route and proves the invalid edit does not land.

### F-02 — high — finding and approval pointers can escape the repository

**Failure scenario.** A note uses `Authority: approval:/tmp/claim.md#Approval`, and `/tmp/claim.md` contains `## Approval`. `APPROVAL_RE` accepts the absolute path (`handoff_done_when.py:15`), `root / match.group(1)` discards `root` for an absolute operand (`:90`), and the heading check returns success (`:91-99`). The write gate therefore allows an authority outside the repository. `../` segments create the same escape for either `finding:` or `approval:`. This converts a pointer that the signed decision excludes into a valid completion authority instead of failing closed.

**Evidence.** D-03 requires both path-bearing types to take a **repo-relative path** (`plan.yaml:113-115`). The parser uses unrestricted `(.+)` path captures at `handoff_done_when.py:14-15` and performs no absolute/traversal/containment check before the reads at `:84-99`. The unit pointer table tests only ordinary repo-relative paths (`tests/unit/test-handoff-done-when.py:67-78`).

**Owner lane.** **Main session direct mutation** — `handoff_done_when.py` is imported enforcement logic under DEC-174; its unit and gate tests inherit that lane.

**Required remedy.** Reject absolute paths and any normalized target outside `root` before opening it, for both path-bearing authority types, with unit and real-gate cases for absolute and traversal escapes.

### F-03 — med — the fixed Scope shape accepts a missing label and reversed order

**Failure scenario.** Either of these bodies returns no shape problem when paired with a resolving authority:

```text
Scope:
Authority: plan-task:T-03.verify
```

```text
Authority: plan-task:T-03.verify
Scope: build complete
```

The first leaves the successor with no scope label; the second violates the required `Scope:`-then-`Authority:` fixed shape. In `handoff_done_when.py:111-122`, a line is counted solely by its prefix and line order/value are never checked.

**Evidence.** `BRIEF.md:26-27` (REQ-02) requires exactly one `Scope:` line **carrying a concise action label, then** one to four `Authority:` lines. The template makes the value obligation explicit at `.claude/skills/harness/templates/HANDOFF.md:39-40`. Existing shape cases cover zero/two Scope lines but neither an empty label nor order (`tests/unit/test-handoff-done-when.py:55-65`). The T-02 prose at `plan.yaml:250-254` explicitly declines order enforcement, so the approved task text and binding requirement are inconsistent; the implementation follows the weaker text.

**Owner lane.** **Main session direct mutation** — shared parser and gate tests are DEC-174 enforcement surfaces.

**Required remedy.** Enforce a non-empty trimmed Scope value and the binding Scope-before-Authority order, and align the conflicting T-02 record with REQ-02.

## Mandatory Python risk grade

`python3 .claude/skills/harness/bin/code-grade.py --base 0ec44965a961d19177de871c3bb1f02b701e646b --head e75767df4b75e71f2c9b12766604cee5008d94e1` exited **1** (`code_grade: fail`). Failing functions:

- production: `_body` grade 3/high, `_resolve` grade 1/high, `problems` grade 2/med;
- gate tests: `run_handoff_done_when` grade 1/high and `case_feat54_done_when` grade 1/high;
- locally-run probe: `measure_note` grade 2/med.

For the grade-2 functions, no complexity exception is justified: `problems` mixes section extraction, shape checks, grammar and resolution orchestration, while `measure_note` mixes I/O, scoring, formatting and aggregation. The actual missed containment rule in F-02 is a concrete failure in the grade-1 `_resolve` branch structure, not a theoretical style concern.

**Owner lanes.** Main session direct mutation for `handoff_done_when.py`, `test-check-domain.py`, and `test-check-state.py`; `harness-dev-ops` for the manual probe.

## Required inspection evidence

### SC-04 — met for the Done-when subject

Ran `.claude/skills/harness/bin/check-state.sh` from the repository root. Exit status was **1** because of the unrelated pre-existing `FEAT-51-claude-code-lifecycle-safety` missing `handoff-validate.md` violation. The full 810-line output contains **no** `Done when` line, so no handoff Done-when corpus violation was reported.

### SC-07 — met

The two gates use the shared implementation:

- `check-domain.sh:1562,1567` imports and calls `handoff_done_when.problems(..., resolve=True)`;
- `check-state.sh:54-56,1243-1251` imports and calls the same function with `resolve=False`.

Neither gate contains a second Done-when body parser or pointer-target resolver. `check-state.sh:1215-1242` is the existing parser for the four narrative section bodies only and does not parse the Done-when body or open authority targets.

### SC-08 — met

Current contract surfaces state five sections and name `## Done when`: `.claude/skills/harness/SKILL.md:310-316`, `check-domain.sh:1547-1567`, `check-state.sh:1069-1070,1212-1251`, `templates/HANDOFF.md:4-16,37-40`, and `DECISIONS.md:3698-3727,6696-6724`. The only four-heading claims in the live gate scripts are the two criterion-authorized historical FEAT-31 comments at `check-state.sh:1194-1202` and `:1215-1219`. DEC-160's older four-section wording is historical decision evidence, not a current contract assertion.

### SC-11 — met

`git merge-base main e75767d...` resolved to `0ec44965a961d19177de871c3bb1f02b701e646b`. The base-to-review handoff diff contains exactly two paths, both status `A`:

- `.harness/harness/features/FEAT-54-handoff-done-when/notes/handoff-build.md`
- `.harness/harness/features/FEAT-54-handoff-done-when/notes/handoff-plan.md`

Thus the intersection with base-existing handoffs is empty, and the positive-control set is non-empty and exactly equals the `--diff-filter=A` set. No historical handoff was modified.

### SC-10 — pending

SC-10 remains operator UAT and is not marked met by this review.

## Stage 2 — code quality

Not entered because Stage 1 failed. The mandatory pre-review risk grade is reported above and independently fails.

```yaml
VERDICT: FAIL
DIGEST:
  headline: "Three spec mismatches remain: Edit enforcement is post-hoc, path-bearing authorities escape the repository, and the fixed Scope shape accepts no label/reversed order; mandatory Python risk grading also fails."
  severity_max: high
  findings: 4
  must_fix:
    - "F-01: refuse invalid handoff Edit candidates before mutation and prove non-mutation through the pre-tool route."
    - "F-02: constrain finding:/approval: paths to normalized repo-relative targets beneath root, with escape cases."
    - "F-03: require a non-empty Scope label in Scope-before-Authority order and reconcile T-02 with REQ-02."
    - "F-04: refactor every function reported failing by code-grade.py; no grade-2 exception is justified."
  spec_violations:
    - {kind: mismatch, path: .claude/skills/harness/bin/check-domain.sh, ref: REQ-06}
    - {kind: mismatch, path: .claude/skills/harness/bin/handoff_done_when.py, ref: D-03}
    - {kind: mismatch, path: .claude/skills/harness/bin/handoff_done_when.py, ref: REQ-02}
  reviewed: "0ec44965a961d19177de871c3bb1f02b701e646b..e75767df4b75e71f2c9b12766604cee5008d94e1"
  human_commits_in_scope: []
  code_grade: fail
  open_questions: []
  files_touched:
    - .harness/harness/features/FEAT-54-handoff-done-when/notes/review-harness-code-reviewer-c0.md
  expertise_update: []
artifact: .harness/harness/features/FEAT-54-handoff-done-when/notes/review-harness-code-reviewer-c0.md
```
