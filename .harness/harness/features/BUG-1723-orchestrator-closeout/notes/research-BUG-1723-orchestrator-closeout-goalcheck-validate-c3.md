# BUG-1723 goal-check — validate c3

## Conclusion

PASS for the presently applicable goal-check obligations at pinned review SHA `6999227750f68b3ec9c8f77a3ae4f281310742a9`. The complete feature range is `1a1c1925171803db8ac7f7464560a3767fa902a8..6999227750f68b3ec9c8f77a3ae4f281310742a9`. SC-01 through SC-04 are met. SC-05 is not met because its approved post-shipment UAT has not yet run; it is deliberately not applicable to this pre-ship validation and is neither treated as passed nor omitted. Both c2 blocked questions are answered and independently confirmed at the pin. No open finding or question remains, and this conclusion does not recommend another validation round.

## Authority and scope

- `BRIEF.md` and `plan.yaml` are approved at the pin. The plan contains three done tasks and two decisions; every SC-01 through SC-04 has a task trace, while SC-05 is the approved post-shipment UAT.
- QA ran the required unit and integration matrix in a detached checkout at the exact pin. Unit passed 40 files and integration passed 72 files, with no coverage gaps (`notes/review-harness-qa-c3.md:3-20,30-48`). QA's final return is nevertheless `BLOCKED` because a separate return validator repeated c2 Q1 by shell-invoking the Python runner in a later checkout (`notes/review-harness-qa-c3.md:26-33,49-50`). Main's signed answer makes that invocation out of contract for this exact-pin grade; this goal-check uses QA's exact-pin test evidence and did not rerun tests.
- The complete pinned range contains no `[harness:human]` commit. The c3 correction changed the DEC-159 authority and its generated index plus feature records; it did not change the runtime implementation or tests previously graded at c2.

## Perspective grades — exactly one line per declared perspective

- **pass — orchestrator** — SC-01 and SC-04 are met: one public `close-run` invocation composes successful close-out and named first-refusal behavior, while all three pinned playbook files keep `STATE.md`, the handoff note, and the commit as separate writes and quarantine as wake-time work.
- **pass — operator** — SC-03 is met and the permanent authorities consistently expose retrospective succession at every station; SC-05 remains an explicitly future, not-yet-run UAT for the first complete post-shipment plan mission and therefore is not counted as present validation success.
- **pass — code maintainer** — SC-02 is met with exact-pin regression evidence, and the c3 cutover removes the prior DEC-159 contradiction so the decision, ledger, executable, and tests now state one all-stations phase-seam contract.

## Success-criterion status

- **SC-01 — met (automated).** At the pin, `tests/unit/test-feature-record.py:182-212` covers successful one-command close-out, the single spend-bearing output line, paired task/station and judgement inputs, and exact `n_a` handling. QA's exact-pin unit matrix passed and cites the discriminating pre-change receipt (`notes/review-harness-qa-c3.md:7,11-20,37-44`).
- **SC-02 — met (automated).** At the pin, `tests/unit/test-feature-record.py:247-312` covers named station, judgement, and public spend refusals, nonzero authority status, first-refusal stopping, retained earlier writes, absent later writes, and no false success summary. QA's exact-pin unit matrix passed and retains separate fail-first evidence for the original and c2-added arms (`notes/review-harness-qa-c3.md:13,18-20,39,43`).
- **SC-03 — met (automated).** `69992277:.claude/skills/harness/bin/check-state.py:3026-3064` pairs each applicable handoff with its succession and first later run, reports unreadable `at` or `started_at` as CANNOT VERIFY, reports only a later succession as retrospective, and sends every in-era hit to the violation list without a terminal exemption. `69992277:tests/integration/test-check-state-feat59.py:396-458` covers later, earlier, equal, multi-handoff, unreadable, legacy, and both `done` and `review` stations. QA's exact-pin integration matrix passed with the required pre-change red evidence (`notes/review-harness-qa-c3.md:14,20,40,44`).
- **SC-04 — met (inspection).** At `69992277`, `.claude/skills/harness/SKILL.md` under `Adjust and record — ONE command closes the run`, `.claude/skills/harness/references/build-phase.md` under `Every run in this phase closes the same way` and `The seam out of this phase`, and `.claude/skills/harness/references/ledger.md` under `Runs` present `close-run` as the single close command, keep `STATE.md`, handoff, and commit explicit and separate, and place quarantine at wake time (`SKILL.md:66-93`; `build-phase.md:9-12,67-71`; `ledger.md:5-32`).
- **SC-05 — not_met (uat; not presently applicable).** The approved criterion and Verification gaps reserve this UAT for the first complete plan mission after shipment (`BRIEF.md:25-30`), and DEC-159 repeats that timing (`69992277:.harness/harness/docs/DECISIONS.md:3821-3822`). No such mission has occurred and no user UAT has been run, so there is no verdict yet on the at-most-eight calls per dispatch, median context below 100,000 tokens, or zero retrospective succession thresholds. This future obligation must remain open after ship rather than being represented as validation success.

## C2 questions independently resolved at the pin

- **Q2 — resolved: T-03 declaration and re-signature.** `69992277:plan.yaml` declares both `.harness/harness/docs/DECISIONS.md` and `.harness/harness/docs/DECISIONS-INDEX.md` in T-03's `files`, T-03 remains `done`, and approval is `approved` by `mruangutai` on `2026-09-16` (`plan.yaml:3-6,159-180`). The Main-authored re-signature records that `plan-merge.py amend` reset approval before the re-signature and that neither SCs, tasks, nor decisions changed (`notes/answers-2026-09-15-sign.md:5-10`). The former scope question is therefore closed, not waived.
- **Q2 — resolved: all-stations authority consistency.** DEC-159 says a retrospective succession is a violation at every station, `done` included, and unreadable chronology is CANNOT VERIFY (`69992277:.harness/harness/docs/DECISIONS.md:3805-3822`). The generated index resolves DEC-159 to its actual `@3726` heading (`DECISIONS-INDEX.md:163`). Ledger guidance says the same (`ledger.md:52-59`), the executable sends all in-era INV-43 hits to `bad` without checking station (`check-state.py:3056-3064`), and the integration cases assert violations at both `done` and `review` (`test-check-state-feat59.py:437-458`). The c2 contradiction is gone.
- **Q2 — resolved: meaning of the INV-43 census.** The specified census means two retrospective succession judgement records in the single `BUG-285-canonical-reader` feature record, not two feature files and not ignorable terminal noise. The handoffs at `seq-26` and `seq-27` (`BUG-285-canonical-reader/notes/handoff-build.md:1`; `handoff-validate.md:1`) make runs 27 and 28 the first later runs, started at `17:00:04` and `18:07:42` (`BUG-285-canonical-reader/feature.json:253-267`). Their ordinally matched successions were recorded later at `18:53:25` and `20:17:42` (`feature.json:392-403`), so each satisfies INV-43's exact retrospective predicate. The earlier `seq-3` handoff is clean because its succession at `21:48:37` predates the first later run at `23:23:31`; `seq-28` has no later run and therefore nothing for INV-43 to grade. There is exactly one matching feature file in the pinned `.harness/*/features/` census.
- **Q1 — resolved for the exact-pin contract; repeated by the return validator.** The c2 blocker was a caller error: executing the Python runner as a shell script in a later checkout. At c3 QA used `python3 .claude/skills/harness/bin/run-unit-tests.py --kind unit` and `--kind integration` in a detached checkout whose HEAD matched the review SHA; both exited 0 with 40 and 72 files respectively (`notes/review-harness-qa-c3.md:3,9-14`). QA's return validator then repeated the excluded later-checkout shell invocation and QA truthfully returned `BLOCKED` (`notes/review-harness-qa-c3.md:26-33,49-50`). That process blocker does not falsify the exact-pin matrices or reopen the c2 question Main already answered; the exact-pin contract remains unchanged.

## C2 findings and current dispositions

- **C1-V01 — resolved; severity: high; kind: substance; scope: task; task: T-03; owner: main-session-direct.** Before c3, DEC-159 allowed a terminal note while ledger and code required an all-stations violation, risking a maintainer restoring a terminal fail-open exemption. T-03 now declares both decision surfaces, the plan was re-signed, and DEC-159, its index anchor, ledger, implementation, and tests agree at the pin.
- **C1-V02 — closed and unchanged; severity: med; kind: substance; scope: task; task: T-01; owner: main-session-direct.** The judgement- and public-spend refusal cases now have distinct pre-change red evidence, so the tests no longer claim discrimination without demonstrating it (`notes/review-harness-qa-c3.md:18-20,41-44`).
- **C1-V03 — closed and unchanged; severity: med; kind: substance; scope: task; task: T-01; owner: main-session-direct.** The public `cmd_close_run` spend-refusal test exercises the real stage tuple and proves the required `spend` name, ordering, retained earlier writes, propagated exit, and absent success line; a renamed or reordered public stage now has concrete regression impact (`tests/unit/test-feature-record.py:273-312`).
- **Code-grade advisory 1 — accepted; severity: med; kind: substance; scope: task; task: T-02; owner: main-session-direct.** `case_inv43_chronology` remains grade 2 because its cohesive boundary matrix is clearer than extracted assertion helpers; there is no correctness or maintainability gate to fix and no open impact.
- **Code-grade advisory 2 — accepted; severity: med; kind: substance; scope: task; task: T-01; owner: main-session-direct.** The public spend-refusal scenario remains grade 2 because one linear test best exposes ordering and retained state; there is no correctness or maintainability gate to fix and no open impact.
- **QA c2 question Q1 — answered and closed for BUG-1723; repeated process blocker recorded.** The exact-pin c3 matrix invocation establishes that the prior exit 2 belonged to the caller, not the feature. QA's own c3 return remains `BLOCKED` because the return validator repeated the excluded later-checkout shell invocation; that is a validator-process blocker with an existing Main answer, not an unanswered feature question or failed SC.
- **PM/code c2 scope question Q2 — closed.** Main answered it through the declared T-03 surfaces and re-signature, and the pin independently confirms both.
- **Security and UI c2 — no findings.** Security found no exploitable defect across the input, subprocess, mutation, chronology, or diagnostic boundaries; UI correctly self-scoped out because the range has no rendered surface. The c3 authority-only correction introduces neither surface.

## Open findings and questions

- Findings: none.
- Open questions: `[]`.

## Structured status

```yaml
sc_status:
  - id: SC-01
    verdict: met
    method: automated
    evidence: notes/review-harness-qa-c3.md:13,18,37,42
  - id: SC-02
    verdict: met
    method: automated
    evidence: notes/review-harness-qa-c3.md:13,19,39,43
  - id: SC-03
    verdict: met
    method: automated
    evidence: notes/review-harness-qa-c3.md:14,20,40,44
  - id: SC-04
    verdict: met
    method: inspection
    evidence: 69992277:.claude/skills/harness/SKILL.md:66-93; 69992277:.claude/skills/harness/references/build-phase.md:9-12,67-71; 69992277:.claude/skills/harness/references/ledger.md:5-32
  - id: SC-05
    verdict: not_met
    method: uat
    evidence: Approved BRIEF.md:25-30; first complete post-shipment plan mission and user UAT have not occurred
open_questions: []
```
