# FEAT-2225 — SIMPLIFY — r-20261121-5-simplify-eng

**BLOCKED (reader handoff contract), not a source/test failure.** T-01 grade debt is cleared and committed as `f06b2e57d1f6ee38ed901a66885a0f0cb29f0b8b` (`[harness:SIMPLIFY] FEAT-2225: lift T-01 functions to the code-grade bar; share the Expertise path fragment`). All requested checks exit 0. Three readers' outer yield contracts failed after one re-prompt each; their prose receipts are retained, not normalized into PASS. Main/orchestrator must resolve that host defect and finalize bookkeeping before claiming this pass or a clean tree.

Builder: **harness-backend-dev**, because approved T-01 explicitly names that execution_agent; bin/ also grants dev-ops, but ownership follows the plan. Only T-01's three paths changed. Behavior/interfaces/docs/SCs/decisions intentionally unchanged. Initial lift member returned ESCALATE solely for deferred verification; final builder PASS satisfies that deferral. Zero implementation send-backs or restoring fixes.

## Reader results and durable inputs

All paths below are under this feature's `notes/`; all readers judged pinned `594af2a8..fd8ffcdf`, not in-flight lifts.

|Angle|Accepted verdict|Receipt|Findings|
|---|---|---|---|
|REUSE|PASS|receipt-harness-backend-dev-r-20261121-5-simplify-eng-reuse.md|4|
|SIMPLIFICATION|BLOCKED: contract violation|receipt-harness-data-engineer-r-20261121-5-simplify-eng-simplification.md|9 advisory prose findings; no accepted DIGEST|
|EFFICIENCY|BLOCKED: contract violation|receipt-harness-dev-ops-r-20261121-5-simplify-eng-efficiency.md|2 advisory prose findings; no accepted DIGEST|
|ALTITUDE|BLOCKED: contract violation|receipt-harness-ai-dev-r-20261121-5-simplify-eng-altitude.md|6 advisory prose findings; no accepted DIGEST|

The three re-prompts also failed with “must return the digest as an object,” including visibly wrapped payloads; reported to `xd://report_issue`. No further retries or charitable normalization. The failed reader artifacts remain useful finding inputs, not accepted return evidence.

## Every finding disposition (deduplicated; R/S/E/A refer to angles above)

|Finding IDs|Disposition and reason / concrete backlog alternative|
|---|---|
|R-F1|**APPLIED:** share `_EXPERTISE_REL` between TAIL and PATH regexes; original tail capture preserved, new PATH capture unused.|
|S-F6|SKIP: receipt destination consolidation would tighten accepted header grammar; shared `_is_persona`/`_declared_segment` already improve locality. Preserve evidence semantics.|
|R-F2 / S-F3 / A-F3|FLAG-ONLY backlog: centralize distill-token rule/lead tuple in an existing shared module. Guards are main-session-direct; no grant.|
|R-F3|SKIP: git/hash wrappers have distinct refusal classes/timeouts; sharing requires exception translation and wider gate changes, low leverage.|
|R-F4|SKIP: optional shared git-fixture cleanup crosses suites; not required for grade lift. Backlog `git_support` reuse.|
|S-F1 / A-F2|FLAG-ONLY backlog: remove host destination mirror in favor of core receipt destination; host is main-session-direct. Keep direct-execute argument validation until schema guarantees are established.|
|S-F2 / E-F1 / A-F4|FLAG-ONLY backlog: unify receipt reads/matching at core seam; validator ungranted. In-process replacement changes timeout/test seam; deleting `unreported` changes interface, so not applied.|
|S-F4|SKIP: deleting repeated check-expertise removes an integrity check; deliberate boundary checks are not waste and no weakening is authorized.|
|S-F5|FLAG-ONLY backlog: flatten one-caller dispatch helpers while retaining lazy destination loading; guard ungranted.|
|S-F7|FLAG-ONLY backlog: reuse `_split_words` in HEAD-move loop; shell guard ungranted.|
|S-F8|SKIP: foreign-persona guard supplies intentional instructional refusal text; removing/rewording changes observable behavior.|
|S-F9|SKIP: structured cap refusal metadata extends shared exception interface beyond this scope; backlog for next core-interface change.|
|E-F2|SKIP: removing execute-time authorization weakens direct-execute protection; preserve independent authority checks, despite estimated startup cost.|
|A-F1|FLAG-ONLY, routed to main via orchestrator: possible prose-marker versus registered-run distill authority gap. Alternative: symmetric dispatch refusal including legitimate orchestrator authority. Source-derived candidate, not reproduced; main must assess before pinning.|
|A-F5|SKIP/backlog: shared shell-command parser would reshape several guard behaviors, outside build-close scope.|
|A-F6|LEAVE: committed-blob comparison verifies what gh actually merges; working-tree replay is not a substitute.|

## Verification and preservation evidence

Builder's durable evidence: `notes/receipt-harness-backend-dev-r-20261121-5-simplify-eng-final.md`; decomposition map: corresponding `...-lifts.md`. Shell evidence is delegated, not independently executed by this shell-less lead. All subprocess environments unset `HARNESS_AGENT_TYPE`.

|Required command|Exit / evidence|
|---|---|
|`python3 tests/unit/test-expertise-ops.py && python3 tests/integration/test-expertise-merge.py`|0; constituents also 0/0; runtime 194/355 passing checks, matching earlier T-01 counts|
|`python3 tests/integration/test-member-expertise.py`|0; 111 passing checks|
|`python3 tests/integration/test-validate-digest.py`|0; ALL PASSED|
|`python3 tests/integration/test-merge-gate.py`|0; ALL PASSED|
|`python3 .claude/skills/harness/bin/code-grade.py --base 594af2a8 --head HEAD`|0 at f06b2e57; 414 PASS, **remaining FAIL lines: none; REASON REQUIRED: none**|
|`python3 .claude/skills/harness/bin/check-plan-routes.py`|0; 0 violations|
|`python3 .claude/skills/harness/bin/check-plan-routes.py --canonical-reader-audit`|0; **0 unresolved** across 100 Python files; `cmd_ops.transform` resolves|

`check-state.py` before commit: 0. No optional apply failure or restoring-fix cycle occurred. JSON classification was not executed as a script.

Assertion expression: `ast.walk`; Call with `func` Name `check`, plus separate Assert count. Predicted and builder-measured before/after: unit **119→119**, integration **255→255**, Assert **0→0** both. Label multisets identical; full argument ASTs differ only a local exception-variable rename and an equivalent binary read helper that closes the file. Lift receipt maps all split cases and preserves registration/state order; runtime counts agree. No assertion weakened, removed or merged. Unit registries remain active; integration retains 26 serial + 13 pooled case registrations.

## Architecture and remaining prerequisites

Local extraction stays behind existing CLI/ops/receipt/replay interface; no new adapter, dependency or persistent resource lifetime. Destination resolution is shared by application/verification; reconstruction remains lazy inside the existing locked writer. Receipt checks and locks remain at the same seam. Grade target met without changing the public contract.

**Tree status: source-only clean; TOTAL TREE NOT CLEAN.** Builder left modified feature.json and six new reader/builder receipts unstaged because they are peer/lead bookkeeping. This digest/checkpoint also require main/orchestrator finalization. Do not claim clean-afterwards or pin review_sha yet. Recommendation: repair/revalidate the three reader handoffs, assess A-F1 on its main-session-only surface, then commit owned bookkeeping and record final clean status. No code-grade reasons remain to author.

## Principles applied

Delete First (`harness-craft/references/delete-first.md`): one path fragment replaces duplicate regex spelling; no new abstraction seam. `harness-codebase-design`: keep pure fixture/receipt decomposition local and retain locked-writer lifetime. These do not waive the blocked handoff contract.

## Open questions

- Blocking: why does the host reject wrapped yields from data/dev-ops/ai readers, including the single repair dispatch? Resolve host acceptance rather than fabricate PASS.
- Main-session decision: does A-F1 require enforcement changes before review pinning? This squad has no write grant there.
- Blocking acceptance prerequisite: main/orchestrator must finalize its bookkeeping and attest the total tree is clean.

```yaml
VERDICT: BLOCKED
DIGEST:
  headline: T-01 grade debt cleared at f06b2e57; all requested gates pass, but three
    reader yield contracts remain blocked and bookkeeping leaves total tree dirty.
  open_questions:
  - id: Q-HANDOFF
    question: Resolve host rejection of wrapped yields from simplification/data, efficiency/dev-ops
      and altitude/ai readers; one re-prompt each failed. Recommend repairing/revalidating
      host acceptance, not normalizing prose receipts into PASS.
    blocking: true
  - id: Q-AUTHORITY
    question: 'Main-session assessment requested for ALTITUDE F1: does prose-marker
      versus registered-run distill authority require enforcement changes before review
      pinning? Concrete alternative: symmetric dispatch refusal while preserving legitimate
      orchestrator distill authority.'
    blocking: false
  - id: Q-CLEAN
    question: Main/orchestrator must commit its feature.json and run receipts/bookkeeping,
      then record total-tree clean status; builder committed only its three owned
      source paths.
    blocking: true
  files_touched:
  - .claude/skills/harness/bin/expertise-merge.py
  - tests/unit/test-expertise-ops.py
  - tests/integration/test-expertise-merge.py
  expertise_update: []
  team: simplify
  steps_run: 6
  cycles_used: 0
  members:
  - step: grade-lifts
    persona: harness-backend-dev
    verdict: ESCALATE
    headline: Implementation completed; initial verification deferral subsequently
      satisfied by final builder PASS.
    files_touched:
    - .claude/skills/harness/bin/expertise-merge.py
    - tests/unit/test-expertise-ops.py
    - tests/integration/test-expertise-merge.py
  - step: reuse
    persona: harness-backend-dev
    verdict: PASS
    headline: Four advisory reuse findings; R-F1 applied, remaining findings explicitly
      skipped or flagged.
    files_touched: []
  - step: simplification
    persona: harness-data-engineer
    verdict: BLOCKED
    headline: Contract violation persisted after one re-prompt; nine prose findings
      retained without accepted DIGEST.
    files_touched: []
  - step: efficiency
    persona: harness-dev-ops
    verdict: BLOCKED
    headline: Contract violation persisted after one re-prompt; two prose findings
      retained without accepted DIGEST.
    files_touched: []
  - step: altitude
    persona: harness-ai-dev
    verdict: BLOCKED
    headline: Contract violation persisted after one re-prompt; six prose findings
      retained without accepted DIGEST.
    files_touched: []
  - step: apply-verify
    persona: harness-backend-dev
    verdict: PASS
    headline: Committed f06b2e57; all required checks exit 0, no grade failures/reasons,
      canonical audit zero unresolved.
    files_touched:
    - .claude/skills/harness/bin/expertise-merge.py
    - tests/unit/test-expertise-ops.py
    - tests/integration/test-expertise-merge.py
  must_fix:
  - Resolve three reader handoff contract failures before marking SIMPLIFY passed.
  - Finalize main/orchestrator bookkeeping and record total-tree clean status.
  branch: feat/FEAT-2225-member-expertise-writes
  escalations:
  - id: E-HANDOFF
    raised_by: harness-eng-lead
    question: Wrapped reader yields rejected even after one repair dispatch each.
    domain: Host yield acceptance
    routed_to: Feat2225Validate3
    resolution: Pending host/main resolution; reported to xd://report_issue; no further
      reader retries.
    decided_by: none
    recorded_as: runs/r-20261121-5-simplify-eng/digest.md#reader-results-and-durable-inputs
  - id: E-AUTHORITY
    raised_by: harness-ai-dev
    question: Potential prose-marker versus registered-run distill authority gap at
      expertise_apply.
    domain: Main-session-direct enforcement
    routed_to: Feat2225Validate3
    resolution: Flag-only; recommend main assessment before review pin. No squad grant
      to alter guards.
    decided_by: none
    recorded_as: notes/receipt-harness-ai-dev-r-20261121-5-simplify-eng-altitude.md#f1
  adequacy_notes:
  - 'Builder pick: harness-backend-dev, following approved T-01 execution_agent despite
    overlapping dev-ops bin grant.'
  - 'Commit: f06b2e57d1f6ee38ed901a66885a0f0cb29f0b8b; prefix [harness:SIMPLIFY] FEAT-2225:.
    Source-only clean; TOTAL TREE NOT CLEAN: feature.json and six receipts require
    main/orchestrator bookkeeping.'
  - 'Builder-reported exits: T-01 combined 0 (unit/integration also 0/0), member-expertise
    0, validate-digest 0, merge-gate 0, code-grade 0, check-plan-routes 0, canonical-reader-audit
    0; HARNESS_AGENT_TYPE unset in subprocess environments.'
  - 'Code-grade at committed f06b2e57: 414 PASS; remaining FAIL lines none; REASON
    REQUIRED none. Canonical audit zero unresolved; cmd_ops.transform resolves.'
  - "Builder AST counts: unit check119\u2192119, integration check255\u2192255; Assert0\u2192\
    0 both. Label multisets preserved; argument AST exceptions limited to variable\
    \ rename and equivalent closing read helper. Runtime passing checks194/355 unchanged."
  - Applied R-F1 shared Expertise path regex fragment. Every skipped/flag-only finding
    and concrete reason is mapped by original angle ID in digest.md; no intended behavior
    or assertions weakened.
  - Zero restoring fixes; three contract-only re-prompts are recorded as redispatches,
    not implementation send-back cycles.
  - Verification evidence is delegated through final builder receipt; shell-less lead
    ran no checks. Docs/changelog intentionally unchanged because behavior/interfaces
    unchanged. No SC/task/decision amendments.
  sc_status: []
  needs_approval: none
  severity_max: high
  matrix_ok: none
  coverage_gaps:
  - Three completed angle prose assessments have no accepted persona DIGEST because
    of persistent host yield-contract failures.
  - Total-tree clean-afterwards acceptance not satisfied; source changes are committed.
  - ALTITUDE F1 is source-derived and not reproduced; main-session assessment pending.
  findings:
  - kind: form
    scope: none
    severity: high
    reader: harness-eng-lead
    summary: Three reader return contracts remain BLOCKED after one re-prompt each.
    why: Required structured returns were rejected; prose artifacts cannot substitute
      for accepted DIGESTs.
  - kind: substance
    scope: none
    severity: med
    reader: harness-ai-dev
    summary: Potential mismatch between tool mission marker authority and validator
      registered-run authority; flag-only.
    why: Source-derived candidate at ungranted main-session-direct surfaces; not reproduced
      or independently adjudicated as a correctness defect.
  readers:
  - reader: reuse
    status: ran
    persona: harness-backend-dev
    reason: none
  - reader: simplification
    status: ran
    persona: harness-data-engineer
    reason: none
  - reader: efficiency
    status: ran
    persona: harness-dev-ops
    reason: none
  - reader: altitude
    status: ran
    persona: harness-ai-dev
    reason: none
  amendments: []
artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2225-member-expertise-writes/.harness/harness/features/FEAT-2225-member-expertise-writes/runs/r-20261121-5-simplify-eng/digest.md
```
