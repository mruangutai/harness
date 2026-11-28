# BUG-2565 ship review: the digest schema lives in the agent definition

**Conclusion.** BUG-2565 is ready to merge with two named residuals, #2593 and #2604, both accepted by the operator. Nothing is merged: the merge is yours.

- **Removed by design.** Dispatchers no longer supply, copy or get refused for `outputSchema`/`schemaMode`. The task tool stops offering them once `task.structured` is off.
- **The barrier.** Each harness agent's frontmatter carries its generated digest schema, and the yield hook refuses any return it could not check.
- **Live proof (T-05).** The generated frontmatter hides both parameters, rejects an off-schema yield and accepts a conforming one on OMP 19.2.1.

**Operational note: restart omp after merging.** A running omp process keeps the hook and config it loaded at start. This session, started before the change, still offered both parameters on its task tool. It attached them to all nine of its own lead dispatches despite intending not to, which is the copy loop this feature removes at the source. BUG-2566 detects such stale processes.

**How this was assembled.** No report round was spawned. This review was assembled from these digests and notes on disk:

- `runs/2026-11-27-01-plan-product/digest.md` … `runs/2026-11-27-05-plan-product/digest.md` (plan)
- `runs/2026-11-27-06-validate-validator/digest.md`, `-07-`, `-08-` and `-09-validate-validator/digest.md` (validate rounds 1–4)
- `notes/research-BUG-2565-digest-frontmatter-contract-goalcheck-validate-c4.md` (final goal-check)
- `notes/receipt-main-session-build.md` (build, with RED evidence and the three fix rounds)
- `notes/answers-2026-11-27-signoff.md`, `-validate-c1.md`, `-c2.md`, `-c3.md` (operator rulings)

## Definition of done, graded (validate goal-check c4)

| Perspective (as signed) | Verdict | Discharged by | Evidence |
|---|---|---|---|
| **operator**: every return reaching a dispatcher was checked by the validator; when it cannot run, the yield is refused, never passed; README, BUILD, SPEC and the decision record describe the contract that runs | met | SC-01, SC-02, SC-09, SC-10, SC-11 | goalcheck-validate-c4.md; `omp-hooks.test.ts` (six validator-failure classes, data-less yield); T-06 verify `decisions ok`; index regenerates byte-equal |
| **orchestrator**: no schema field to supply, copy or be refused for; the child still returns its persona shape | met | SC-03, SC-05 | SC-03 witnesses in `omp-hooks.test.ts`; `notes/research-frontmatter-binding-probe.md` (`task_item_keys: agent, name, solutionSpace, task`; off-schema rejected; conforming accepted) |
| **code maintainer**: change a digest contract by editing its persona schema only; agent copies are generated, and the port check fails on a missing regeneration | met (SC-07 partial for two exotic inputs, accepted) | SC-04, SC-06, SC-07, SC-08 | T-03 verify 16/16 parity; `check-omp-port.py` ok; `test-check-omp-port.py` 39/39; `gen-agent-output.py --check` ok; SC-07 residuals F-3/F-4 in #2604 |

## Lead summaries

- **Plan.** Five product runs (01 BLOCKED, 02–04 FAIL, 05 PASS). The plan was signed with a rework ruling of 2 rounds / 90 minutes. Digests: `runs/2026-11-27-0[1-5]-plan-product/digest.md`.
- **Build.** Main-session-direct under DEC-174. The receipt is `notes/receipt-main-session-build.md`.
  - Tasks T-01 to T-06 were built test-first, with RED recorded per task.
  - The main session ran SIMPLIFY itself and applied one reuse fix.
- **Validate round 1 (run 06): ESCALATE.** Integration was red: index word caps and reader classification. T-03 failed the code grade. One SPEC row contradicted the hook. Operator rulings OQ-1 to OQ-4 followed, and the exit-0 acknowledgement residual became #2593.
- **Validate round 2 (run 07): ESCALATE.** Every round-1 item was closed. F-1: the fix-round generator could delete a dash-prefixed sibling key. The operator authorised a third round.
- **Validate round 3 (run 08): ESCALATE.** F-1 was closed. F-2: a generated-key lookalike inside a multiline value was deleted, because the guard compared keys only. The operator authorised a fourth round.
- **Validate round 4 (run 09): ESCALATE.** F-2 was closed: witnesses RED before and GREEN after, guard-deletion mutants killed. Two older exotic shapes remain (F-3 merge override with an int/bool change; F-4 VT/NEL fence split). The operator ruled to ship with them as residual #2604.

Final measured state at pin `dca6017d`:

- QA: unit 69 and integration 95 green, `runner_exit` 0.
- Parity: 16/16.
- Production code grade: passes.
- UI: scoped out, since no rendered surface changed.

## Questions and escalations

There are no open questions. These escalations were resolved:

| Run | Question | Ruling |
|---|---|---|
| 06 | OQ-1: who owns `canonical-reader-classification.json` | T-03 owns it (amendment, below) |
| 06 | OQ-2: the yield passes an exit-0 validator answer that carries no positive acknowledgement | Accepted residual, issue #2593 |
| 06 | OQ-3: SC-08 parity evidence | QA's execution accepted |
| 06 | OQ-4: does D-03 cover failure prose | No, task data only; docs and the probe receipt were corrected |
| 07 | F-1 | Third round authorised (budget 3 rounds / 135 min) |
| 08 | F-2 | Fourth round authorised (budget 4 rounds / 165 min) |
| 09 | F-3, F-4 | Ship with residual issue #2604 |

## Spend

`feature-record.py spend`:

- 9 runs, 208 wall-clock minutes.
- Rework: 113 minutes against the final ruling of 165.
- Tokens: not host-measured.

There are 5 judgements in the ledger, and no run budget (`max_total_runs`) is set.

## Amendments

| at | decision | reason | overruled |
|---|---|---|---|
| 2026-11-27T18:23:40Z | T-03.files | Operator ruling OQ-1 (validate run 06): T-03 owns the reader-classification rows for its two new scripts | no |

overrule rate: 0/1

## UAT

No criterion in BRIEF.md or plan.yaml is `verify: uat`. None is required.

## Proposed backlog

Strike any row by ID. Unstruck rows become backlog issues when you accept the ship. B-1 and B-2 already exist as issues.

| ID | Nature | Item | Source |
|---|---|---|---|
| B-1 | bug | The yield refuses any `validate-digest.py` exit 0 that lacks a positive acknowledgement line (#2593) | run 06 OQ-2 |
| B-2 | bug | Generator spans from `yaml.compose` node marks plus a typed compare, closing F-3 (merge override, int/bool) and F-4 (VT/NEL fence split) (#2604) | run 09 |
| B-3 | bug | A recursive alias in frontmatter raises `RecursionError` (exit 1, nothing written) instead of a clean exit-2 refusal | run 09 F-5 |
| B-4 | enhancement | A block scalar (`\|`/`>`) that ends the frontmatter is refused, because the parsed trailing newline changes. No agent uses one today | run 09 F-6 |
| B-5 | bug | Invalid UTF-8 in an agent file crashes with exit 1 before the refusal handler. It writes nothing | run 09 advisory 3 |
| B-6 | bug | A write-phase I/O failure part-way through can leave agents inconsistent across personas. Preflight refusals are already all-or-nothing | runs 07–09 |
| B-7 | enhancement | A multiline flow `output: {…}` closed by a column-0 `}` cannot be regenerated. It fails closed | run 08 advisory 3 |
| B-8 | chore | The `refused()` test helper does not assert the refusal cause | run 09 advisory 4 |
| B-9 | chore | Grade-2 test functions `walk`, `case_generator` and `case_generator_edges` in `test-digest-projection.py` | runs 06–09 |
| B-10 | chore | Bound and redact the validator diagnostics a child can see. They may carry absolute paths or exception text, and base did the same | run 06 security |
| B-11 | chore | SPEC §8.3 cites stale line numbers (`harness-hooks.ts:1108`, `validate-digest.py:2200/:1827`) | run 06 pm |
| B-12 | bug | The validator-lead digest schema forces `findings[].scope` and `readers[].reason` to n/a, so a validate lead cannot record a task scope (DEC-228) | run 06 OQ-5 |
| B-13 | chore | Coverage gaps: a symlink-escape fixture for `digest_projection`; the SC-06 test should assert the `.omp/config.yml` file name | run 06 |
