# Plan review — FEAT-1928 — c0

**BLUF:** FAIL. The draft captures the hard cut, parity, historical reads, null-yield live probe, census, supersessions, and DEC-174 routing, but it does not define or gate the cross-language schema projection seam strongly enough to prove provider compatibility. The canonical loader also combines three independently changing responsibilities.

## Findings

1. **[high · substance · task · code-reviewer] The provider-compatibility claim has no executable gate.**
   - **Consequence:** A ref-free bundle can satisfy the local keyword whitelist yet be transformed or rejected by one configured OpenAI or Anthropic model tier; dispatch then fails in production although T-01 and T-02 both pass their signed `verify:` blocks.
   - **Evidence:** BRIEF SC-03 requires configured OpenAI and Anthropic provider compatibility cases. `plan.yaml` T-01 verifies only `test-digest-schemas.py` plus the canonical-reader self-test; T-02 says to keep OMP's canonical provider suites as evidence, but its verify runs only repository-local hook/digest/reader suites and the receipt verifier. No provider normalization/conversion suite or exact command is named. Add the actual provider-suite commands to the last task that can change injection/projection, with explicit OpenAI and Anthropic cases.

2. **[high · substance · task · code-reviewer] The in-process TypeScript hook → canonical Python schema provider seam is unspecified.**
   - **Consequence:** When a Harness dispatch arrives, an implementation can either spawn Python on every dispatch (avoidable process cost and a new fail-closed runtime dependency) or duplicate persona resolution/projection in TypeScript (violating the single canonical contract); both satisfy the current prose “resolve … through digest_schema.py” without a defined interface, lifetime, or error contract.
   - **Evidence:** Intent artifact settles in-process injection in `harness-hooks.ts`; T-01 exposes Python loader/projection functions; T-02 requires the TS handler to resolve through that Python module but names no adapter, serialization interface, cache lifetime, startup/dispatch behavior, or failure semantics. Specify the one cross-language adapter, when bundled schemas are loaded/cached, and how load/projection failure refuses dispatch. Its owning test must exercise the real adapter rather than a fixed fake.

3. **[med · substance · task · code-reviewer] `digest_schema.py` is planned as three shallowly related modules collapsed into one file.**
   - **Consequence:** A historical fenced-YAML parsing change can perturb the hook-critical provider projection/import surface, while schema projection changes force historical state readers through the same broad module; maintainers must understand unrelated durable-record and live-dispatch behavior to change either side.
   - **Evidence:** T-01 assigns one module canonical schema validation/persona resolution, provider dereferencing/projection, JSON CLI decoding, and reverse-scanning historical `digest.md`. The natural seams are schema source/validation, provider projection, and durable-record reading; only the first two share the live schema contract. Keep one canonical schema authority, but give provider projection and historical record loading narrow interfaces/modules (or explicitly justify a single deep interface that hides all three and name its callers).

4. **[low · form · task · code-reviewer] Traceability understates T-01 and overstates T-03.**
   - **Consequence:** Plan records will attribute the historical-reader implementation only to SC-03 and imply the documentation task implements the runtime persona object contract, weakening later omission review.
   - **Evidence:** T-01 implements the last-fenced historical loader required by SC-07 but traces only SC-03. T-03 traces SC-02 although its files are decisions/operator docs; SC-02's eight agent definitions and three skills are wholly T-02. Add SC-07 to T-01 and remove SC-02 from T-03 unless a concrete SC-02 deliverable is named there.

## Coverage audit

- **Scope/hard cut:** covered by T-02, including parser/renderer/fallback/echo/hollow-repair deletion, census, parity, real null-yield retry, and no compatibility alias.
- **Historical corpus:** covered through final-fenced mapping reads and byte-stability for all 30 tracked digests.
- **Decision supersession/docs:** covered in topological successor T-03; DEC-208 is explicitly preserved.
- **Dependency/overlap:** `plan-merge.py check` exited 0 with 3 tasks, 58 anchors, and no overlap lines. T-03 touches only docs after T-02, so it does not invalidate T-02's code gates.
- **DEC-174:** every enforcement source, schema/config surface, probe/parity receipt, and owning test is assigned `main-session-direct`. The team task is limited to doctrine and operator documentation; no team task executes an enforcement-layer edit or owning test.
- **Pre-cutover self-validation:** D-05 and the BRIEF constraint correctly keep validation teams under the main checkout's pre-cutover hook; the fresh disposable process is correctly reserved for exercising the new hook.

## Principles applied

- **Migrate Callers, Then Delete Legacy APIs:** the plan correctly migrates live callers and deletes the text parser, fallback, repair, and renderer in the same cutover wave.
- **Delete First:** finding 3 rejects a broad catch-all module where narrower seams preserve locality without adding duplicate contract sources.

```yaml
VERDICT: FAIL
DIGEST:
  headline: "Provider compatibility and the TS-to-Python schema seam are not yet specified or gated strongly enough to sign."
  severity_max: high
  findings:
    - {kind: substance, scope: task, severity: high, reader: code-reviewer, summary: "SC-03 provider compatibility has no executable OpenAI/Anthropic provider-suite gate.", why: "A locally valid bundle can still be rejected or transformed by a configured provider while every signed verify command passes."}
    - {kind: substance, scope: task, severity: high, reader: code-reviewer, summary: "The in-process TypeScript hook to canonical Python schema provider seam lacks an interface, lifetime, and failure contract.", why: "The plan permits either per-dispatch Python spawning or a duplicated TypeScript contract without violating its current wording."}
    - {kind: substance, scope: task, severity: med, reader: code-reviewer, summary: "The planned digest_schema.py combines schema authority, provider projection, CLI decoding, and historical-record parsing.", why: "Unrelated historical and live-dispatch changes lose locality and share one broad import surface."}
    - {kind: form, scope: task, severity: low, reader: code-reviewer, summary: "T-01 omits SC-07 tracing and T-03 carries an unsupported SC-02 trace.", why: "The historical reader is SC-07 work, while all concrete SC-02 runtime surfaces are in T-02."}
  must_fix:
    - "Name and run the real configured OpenAI and Anthropic provider compatibility suites in the terminal injection/projection verify block."
    - "Define the single TS-to-Python schema adapter, cache lifetime, and fail-closed error behavior, with a real-adapter owning test."
  spec_violations:
    - {kind: omission, path: ".harness/harness/features/FEAT-1928-digest-object-contract/plan.yaml", ref: SC-03}
    - {kind: mismatch, path: ".harness/harness/features/FEAT-1928-digest-object-contract/plan.yaml", ref: SC-07}
    - {kind: mismatch, path: ".harness/harness/features/FEAT-1928-digest-object-contract/plan.yaml", ref: SC-02}
  code_grade: n_a
  reviewed: "plan:/Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-1928-digest-object-contract/.harness/harness/features/FEAT-1928-digest-object-contract/plan.yaml"
  human_commits_in_scope: []
  open_questions: []
  files_touched: []
  expertise_update: []
artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-1928-digest-object-contract/.harness/harness/features/FEAT-1928-digest-object-contract/notes/review-harness-code-reviewer-plan-c0.md
```
