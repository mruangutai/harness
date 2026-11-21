# QA gate (contract repair c1) — BUG-2171-task-structured — pin d3792019 (base b7af829c)

BLUF: PASS, restated as a structured object. This retry executed NO gates, tests, graders, builds or linters. Every measurement below was executed by the prior QA child (history://BUG2171Validate.RattyCamel) and is recorded in `notes/review-harness-qa-c0.md`. The c0 return failed the transport contract (prose PASS, six rejected yields), so c0 prose is not accepted as the structured result. This note is the repair.

## Executed evidence (attributed to prior QA, not re-run here)
- unit: `run-unit-tests.py --kind unit` exit 0, 59 files; test-omp-hooks.py Bun 140 pass / 0 fail. satisfied.
- integration: `--kind integration` exit 0, 85 files; test-check-omp-port.py 31/31 incl. 5 task.structured rows and the integer-1 row at the current pin. satisfied.
- Raw outputs: /tmp/qa-red-green.txt and /tmp/qa-codegrade.txt (ephemeral, written by prior QA); key lines quoted in c0 note and durable receipts `notes/receipts/red-port.txt`, `red-hook.txt`, `green-offline.txt`.

## Fail-first (prior QA's own reproduction, quoted from c0)
- SC-02 (tests/integration/test-check-omp-port.py:169 case_task_structured_required): base gate b7af829c: `FAIL absent / boolean false / string 'true' / integer 1` (assertion red, base exits 0); fixed gate: all 5 ok. Semantic red.
- SC-04 (tests/unit/omp-hooks.test.ts:1716): base hook: `expect(asString.validations).toHaveLength(1)` Expected 1 / Received 0; held-run test refusal text mismatch; 1 pass 2 fail at base, 3 pass 0 fail at pin.

## Finding 1 (original, substance medium, SC-03) — dismissed on PM evidence
Original objection: persisted main-session task args contained the full persona outputSchema, so hook injection was not independently proven. PM goal-check (`notes/research-BUG-2171-task-structured-goalcheck-validate-c0.md`, SC-03 section) inspected installed OMP: agent-session.ts:5638-5660 forwards extension input revisions as args and agent-loop.ts:3155-3163 overwrites toolCall.arguments before persistence; hook schemaControlRefusal runs before injection, so caller-supplied fields would be refused. Persisted args therefore do not discriminate caller vs hook, and success plus strict child init does. I accept that assessment as evidence-supported; I did not inspect OMP source myself in this retry. Original finding retained as recorded in c0 (kind substance, severity medium); disposition: dismissed, not a defect.

## Coverage limits (approved/disclosed scope, not unmet SCs)
- String-data yield path has Bun-handler coverage only; live yields used object data.
- typecheck unresolved (cmd null), not run, not claimed; BRIEF discloses it.
- SC-01 and SC-03 are inspection, not QA-automated; PM/inspection reviewers own them.
