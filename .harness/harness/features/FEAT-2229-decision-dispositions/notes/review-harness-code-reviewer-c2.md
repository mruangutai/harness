# FEAT-2229 pinned code review — c2

**PASS with one medium T-01 advisory: the reported creation bypass and original fenced-heading cases are repaired, but fence closing still accepts a non-whitespace suffix.** No must-fix; Python grade passes.

Target: `a8b8df6196c6107b76cbd941bf2266b3e71476d6`; feature range `dfa52536..a8b8df61`; canonical grading range `3dd8bb677bb2936361e3952030fc24f15bf9afc6..a8b8df6196c6107b76cbd941bf2266b3e71476d6` (merge-base with origin/main). Read BRIEF/plan decisions before the diff, completed compliance assessment before quality assessment, and used pinned `git show` source throughout. Full commit list contains no human-tagged commits. Only dirty tracked path was this feature's feature.json; its live pin agrees with dispatch. Pinned feature.json records the preceding c8a8e174 seam; independently diffing c8a8e174..a8b8df61 showed only feature.json/plan.yaml, establishing source equivalence without reviewing c1 again.

## Prior findings — explicit dispositions

- **F1 / substance / high / code-reviewer / T-01 / SC-01: closed by inspection.** `plan_merge/union.py:340-347,381-391` calls the shared public `harness_yaml.validate_decisions_affected` before producing creation bytes and translates schema errors into refusal 5. `harness_merge.py:160-167` cannot write after that exception. Malformed creation/no-file assertions and the valid creation control are present in `tests/integration/test-plan-decision-dispositions.py:436-450`; loader and creation share the same rule (`harness_yaml.py:421,460`). This is control-flow evidence, not a fresh runtime result.
- **F2 / substance / med / code-reviewer / T-01 / SC-02: original plain/nested-fence counterexamples closed; residual below.** `_real_headings` starts at document line zero, retains fence character/length, and `_Authority.section` bounds against those real headings (`plan_merge/check.py:279-320`). Four CLI assertions cover spoof rejection, nested shorter runs, genuine DEC-10 acceptance, and DEC-11 continuation (`test-plan-decision-dispositions.py:249-292`).
- **F-01 / substance / T-02 / SC-07: coverage gap closed by inspection.** `test-plan-team.py:481-489` now independently asserts the successor-justified deletion/repointed-citations alternative against the canonical pm Mode 2 slice (`:439-440`), not other documents. The generic deletion witness at `:502-508` uses that same owner. `notes/red-first-T-02.md` records old-test green/new-test red on deletion; that historical execution is not claimed as mine.

## Ranked new findings

- **F3 — substance / med / reader code-reviewer / owner T-01 / SC-02 mismatch:** `plan_merge/check.py:279-287` closes an open fence whenever a same-character run is long enough, without requiring a whitespace-only remainder. Concrete input: inside DEC-11, open a three-backtick `text` fence, include a literal three-backtick `python` content line, then `## DEC-10` and a spoof clause; close the actual fence and place the genuine DEC-10 later. Markdown keeps the `python` line inside the existing code block, but this checker closes there and selects the example as DEC-10 authority (`:294-320`), accepting a clause absent from the real DEC-10. **REASONED, not executed.** This is the original wrong-section defect class in a narrower, unusual input, so retains medium/nonblocking treatment. Require whitespace-only trailing text for a closing run and add this rejection beside the genuine-section control. Security reader independently raised the same mechanism; one finding, not two.

## Compliance and quality evidence

- **SC-04 inspection met:** `teams/plan.yaml:59-65,103-108`, template `:75-86`, and `references/patch-lane.md:20` retain five fields, independent omissions/empty-list judgment, DEC-188 distinction, drafting check and panel-free patch.
- **SC-05 inspection met:** `.omp/agents/harness-pm.md:64-82` individually grades amend/strike, skips keep, requires pinned evidence and both strike alternatives; `teams/validate.yaml:120` delegates; validator-lead `:104` preserves failed landings and task routing.
- **SC-06 inspection met:** `DECISIONS.md:5290-5338,8253-8326`, `DECISIONS-INDEX.md:237`, `SPEC.md:2009-2041,2287-2302` carry the amendment/new authority and existing sc_status route without general stale detection. No invented absent product docs.
- SC-01/03 implementation retains typed rows, guarded provenance, era-boundary diagnostics and legacy exemptions; SC-02 has the F3 edge above. New runtime tests exercise the real CLI with distinct rejection diagnostics and valid controls. SC-07 assertions are owner-scoped static instruction checks, not proof of agent obedience. No unrelated implementation/scope-creep identified; classification-fixture maintenance supports the new config reader.
- Mandatory `code-grade.py --base 3dd8bb677bb2936361e3952030fc24f15bf9afc6 --head a8b8df6196c6107b76cbd941bf2266b3e71476d6`: **exit 0, PASSING 88**, no high/grade-2 records. All seven changed Python paths included. Source quality review found no additional gating failure.

Preserved dismissals: simplify L-1..L-4 remain leave; B-1/B-2 remain briefing-only, not new findings. D-01/DEC-254, FINISHED_STATIONS use, pm path placeholder, validator gate placement and preexisting landed create:true behavior remain settled. Build/simplify amendments list is empty; no source edits or unowned task scope added.

## Principles applied

Delete First: retained the existing writer/check/Mode 2 seams rather than requesting a parallel audit system. Model the Domain: assessed the fence's character/length state and found its missing closing-line invariant.

Limits/checks: only the mandatory static grader ran; no tests, builds, lint, formatters or mutable probes. Read-only role grants only this report write, so closure and F3 are explicitly inspection/reasoning, not independently measured execution or mutation evidence. QA owns the signed T-01/T-02/T-03 checks at this pin; no redundant suite requested. Open questions: none.
