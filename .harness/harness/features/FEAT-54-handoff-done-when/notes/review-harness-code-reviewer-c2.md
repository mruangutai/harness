# Code review — FEAT-54 handoff Done when — c2

**FAIL.** Stage 1 found two new fail-open specification mismatches in the shared validator, and literal SC-04 remains red. The prior containment, probe-admission, pre-Edit, Scope-label/order, and risk-grade findings are otherwise closed. Per the ordered review protocol, Stage 2 code quality was not entered after Stage 1 failed; the mandatory changed-function grade still ran and passed.

Reviewed pinned range: `0ec44965a961d19177de871c3bb1f02b701e646b..53e1745462b75e1c54967b43e2f4fbdfc7037e23`. The complete named 16-file reviewed set was inspected before scoping, and `git diff --name-only 53e1745... -- <named set>` printed nothing, so the inspected worktree bytes match the pin. `git log` over the range contains no `[harness:human]` commit.

## Stage 1 — specification compliance

### F-04 — live — high — literal SC-04 still fails

**Failure scenario.** Entering Harness at this review checkout runs the required root state check and receives exit 1, so the repository cannot satisfy SC-04's exact clean-state condition even though the Done-when corpus itself emits no violation.

**Evidence.** Exact command `bash .claude/skills/harness/bin/check-state.sh` from the repository root exited **1**. Its violations include the previously recorded unrelated FEAT-51 missing `notes/handoff-validate.md` plus five currently present FEAT-54 run-digest contract violations. A search of the complete captured output found **zero** lines naming `Done when`. BRIEF SC-04 at `BRIEF.md:89-101` requires the actual command exit, not merely absence of Done-when lines, so the unrelated lines are neither waived nor replaced with a fixture.

**Owner lane:** Main direct corpus/state reconciliation; any enforcement-script change remains Main direct under DEC-174.

### F-08 — high — a nested or duplicate heading truncates the Done-when block and hides later authorities

**Failure scenario.** Write this otherwise valid body:

```text
## Done when
Scope: validate
Authority: brief-sc:SC-04
### Additional authority
Authority: brief-sc:SC-99
```

The second pointer is dangling and the subheading is prohibited prose, but the write gate validates only the lines before `### Additional authority` and allows the note. The successor sees two authorities while the gate silently treats only the first as part of the logical AND. A duplicate `## Done when` heading has the same hiding effect.

**Evidence.** `_body` treats every stripped line beginning with `##`—including `###` and a second `## Done when`—as the end of the first block, then returns only that prefix (`.claude/skills/harness/bin/handoff_done_when.py:24-32`). `_line_problems` and authority parsing can inspect only the truncated body (`:193-229,253-270`). Existing stray-prose cases append ordinary text and never cover a nested/duplicate heading (`tests/unit/test-handoff-done-when.py:56-65`; `tests/integration/test-check-domain.py:4033-4058`). This mismatches REQ-02's fixed block with no other prose and REQ-03/REQ-06's all-authorities/write-time-resolution obligations (`BRIEF.md:26-39`).

**Owner lane:** Main direct mutation under DEC-174 for the shared validator and its unit/write/state gate cases.

### F-09 — high — approval resolution accepts text that is not a Markdown heading

**Failure scenario.** An approval target containing only `#Approval` or `####### Approval` has no valid ATX Markdown heading named `Approval`, but `Authority: approval:<path>#Approval` resolves and the write is allowed. A handoff can therefore cite an approval gate that does not exist in the required form.

**Evidence.** `_resolve_approval` accepts any line whose whitespace-stripped form starts with `#`, then removes an unlimited number of leading hashes without requiring the Markdown separator or the one-to-six-hash limit (`.claude/skills/harness/bin/handoff_done_when.py:151-162`). The approval tests use only a normal `## Approval` target and a missing-name control (`tests/unit/test-handoff-done-when.py:90-103`; `tests/integration/test-check-domain.py:4061-4079`). D-03 requires “a markdown heading whose text case-insensitively equals the heading” (`plan.yaml:112-115`); these accepted lines are not Markdown headings.

**Owner lane:** Main direct mutation under DEC-174 for the shared resolver and discriminating unit/write-gate cases.

No scope creep was found in the named diff: each changed surface traces to REQ-01–10 or D-01–10, and the two feature handoffs themselves are new, non-baselined five-section notes with non-empty `Scope:` before their `Authority:` lines (`notes/handoff-build.md:33-37`; `notes/handoff-plan.md:52-55`).

## Prior F-01..F-07 reassessment

| Finding | Disposition at `53e1745` | Pinned evidence |
|---|---|---|
| F-01 contained/fail-closed finding and approval paths | **closed** | Absolute/traversal/control paths are rejected in both modes (`handoff_done_when.py:60-72`); resolved reads must remain beneath root and be bounded regular UTF-8 files (`:75-98`); resolver exceptions become problems (`:232-243`), and the write-gate import/call also fails closed (`check-domain.sh:1561-1566`). Unit and gate cases cover unsafe, symlink-escape, special-file, and injected-exception subjects (`test-handoff-done-when.py:75-87,139-159`; `test-check-domain.py:4088-4210`). F-09 is a distinct heading-semantics defect, not a reopening of the former path-containment failure. |
| F-02 safe manual-probe admission / zero calls | **closed** | Admission resolves into the feature handoff tree, rejects final symlinks and non-regular/oversized/unreadable inputs, and returns no admitted note on failure (`probe-handoff-comprehension.py:54-109`). Six focused tests bind outside/traversal/symlink/directory/wrong-name/oversized refusals to zero `ask` calls and retain the valid two-call control (`test-probe-handoff-comprehension.py:53-101`). Post-simplify QA observed all six pass. |
| F-03 PreToolUse Edit refusal before mutation | **closed** | Handoff Edit joins candidate reconstruction before the tool runs (`check-domain.sh:1819-1872`); invalid UTF-8 returns the unreadable sentinel and exit 2 (`:1841-1844,1865-1868`). Gate cases assert invalid candidate exit 2, byte identity after refusal, and non-UTF-8 byte identity (`test-check-domain.py:4114-4166`). |
| F-04 literal root state check | **live** | Exact root command exit **1**; no output line names `Done when`. See finding above. |
| F-05 non-empty Scope label | **closed** | `_scope_problems` trims and refuses an empty value (`handoff_done_when.py:178-184`); unit, write-gate and persisted-state cases cover blank Scope (`test-handoff-done-when.py:68-73`; `test-check-domain.py:4043-4047`; `test-check-state.py:2206-2211`). |
| F-06 ordered Scope before Authority | **closed** | Product ruling `notes/research-FEAT-54-validation-order-c1.md` makes REQ-02 controlling; `_order_problems` requires Scope before the earliest Authority (`handoff_done_when.py:200-206`), with unit/write/state coverage (`test-handoff-done-when.py:68-73`; `test-check-domain.py:4043-4047`; `test-check-state.py:2212-2217`). |
| F-07 changed-function risk grades | **closed** | Exact mandated grader exited **0**, reporting **82 passing** records, no blocking grade and no grade-2 reasoning requirement. |

## Success criteria and inspection evidence

- **SC-01 PASS; SC-02 PASS; SC-03 PASS; SC-05 PASS; SC-06 PASS; SC-09 PASS; SC-12 PASS; SC-13 PASS; SC-14 PASS; SC-15 PASS.** The pinned tests bind their named observable cases at `test-check-domain.py:4033-4223`, `test-check-state.py:2178-2258`, `test-run-unit-tests-kinds.py:21-40,69-98`, and `test-handoff-done-when.py:45-137`. The latest scoped QA evidence, `notes/qa-validation-post-simplify-c2.md`, records configured unit exit 0 with **25 discovered files** and integration exit 0 with **44 discovered files**; this is non-empty discovery, not a zero-test pass. F-08/F-09 are requirement-level gaps outside those enumerated green cases.
- **SC-04 FAIL.** Exact root check exit 1; zero output lines name `Done when`, as recorded above.
- **SC-07 PASS inspection.** At the pin, the write gate imports/calls only the shared `handoff_done_when.problems(..., resolve=True)` at `check-domain.sh:1562-1563`; the state gate imports at `check-state.sh:54` and calls the same function with `resolve=False` at `:1251`. Searches of both full pinned gate sources found no second Done-when block parser or pointer-target resolver.
- **SC-08 PASS inspection.** Current-contract presence is explicit in `SKILL.md:311-316`, `templates/HANDOFF.md:4,37-40`, `check-domain.sh:1547-1558`, `check-state.sh:1069-1070,1212-1251`, and `DECISIONS.md:3701-3727,6698-6701`. The only four-heading gate matches are the authorized FEAT-31 historical measurement/incident at `check-state.sh:1199,1218`; `DECISIONS.md:3765` likewise records the historical first live four-section handoff, not the current contract.
- **SC-10 PENDING UAT.** No operator judgment is claimed or substituted.
- **SC-11 PASS inspection.** `git merge-base main 53e1745...` returned exactly `0ec44965...`; the prescribed `comm -12` primary clause printed nothing. The `comm -23` positive control printed the two FEAT-54 handoff paths, and the added-only arm printed the same two paths. No base-existing handoff was touched.

## Mandatory grade and Stage 2

Exact command:

```sh
python3 .claude/skills/harness/bin/code-grade.py --base 0ec44965a961d19177de871c3bb1f02b701e646b --head 53e1745462b75e1c54967b43e2f4fbdfc7037e23
```

Exit **0**; `PASSING: 82`; `code_grade: pass`. All production records meet bar 4 and all test records meet bar 3. Because Stage 1 fails on F-04/F-08/F-09, discretionary Stage 2 quality review was not entered.

```yaml
VERDICT: FAIL
DIGEST:
  headline: "Literal SC-04 remains red, and the shared validator fails open on hidden Done-when authorities and non-Markdown approval lines."
  severity_max: high
  findings: 3
  must_fix:
    - "F-04: reconcile the root corpus/state so the exact SC-04 check exits 0; do not waive unrelated findings."
    - "F-08: parse exactly one complete Done-when section so nested/duplicate headings cannot hide prose or authorities, with discriminating unit/write/state cases."
    - "F-09: require a real Markdown heading for approval targets, with invalid no-space/overlong-hash controls."
  spec_violations:
    - {kind: mismatch, path: .claude/skills/harness/bin/handoff_done_when.py, ref: REQ-02}
    - {kind: mismatch, path: .claude/skills/harness/bin/handoff_done_when.py, ref: REQ-06}
    - {kind: mismatch, path: .claude/skills/harness/bin/handoff_done_when.py, ref: D-03}
  reviewed: "0ec44965a961d19177de871c3bb1f02b701e646b..53e1745462b75e1c54967b43e2f4fbdfc7037e23"
  human_commits_in_scope: []
  code_grade: pass
  open_questions: []
  files_touched:
    - .harness/harness/features/FEAT-54-handoff-done-when/notes/review-harness-code-reviewer-c2.md
  expertise_update: []
artifact: .harness/harness/features/FEAT-54-handoff-done-when/notes/review-harness-code-reviewer-c2.md
```
