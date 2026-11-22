# Scope review — FEAT-2340 — plan c1

PASS with notes. The mission is proportionate: exactly two operator-set, ordered tasks join prevention guidance to a bounded gate refactor. No implementation is reviewed or approved here.

## Findings

- **reader: scope; scope: none; severity: med; kind: substance — T-02 verification loses timeout evidence and does not enforce its aggregate deadline.** `plan.yaml:95-112` collects every future before printing any result. If one suite exceeds 50 seconds, `TimeoutExpired` escapes `pool.map`; completed suites' receipts and the timed-out suite's captured output never reach the promised evidence. Executor shutdown also waits for remaining work. Per-process timeouts are not an aggregate under-60-second deadline, including process creation, descendant pipe cleanup and output. Keep parallel execution, but make timeout/failure receipts observable and use the Main host's supervised whole-command deadline. No timing measurement was authorized or performed; this is a control-flow finding, not a claim that these suites currently exceed 50 seconds.
- **reader: scope; scope: none; severity: med; kind: form — SC-03 overstates existing multi-cycle coverage.** `BRIEF.md:20` says existing assertions cover `handoff-x-c1-c2.md → notes/handoff-x-c1.md`. The actual enumerated cases at `tests/integration/test-check-domain-post.py:919-921` contain only single-cycle suffixes; the helper at `:933` consumes those supplied cases. The grilling citation does not establish this test. A wrong multi-cycle canonical name is therefore not excluded by that cited regression evidence. Correct the record without rewriting tests: retain the explicit T-02 requirement and make its pinned-content inspection carry this edge. Likewise mixed-case acceptance/refusal coverage is not proof of legacy-versus-shape diagnostic ordering: approval `:304-310` checks exit 2, while grant `:1128-1144` exercises lowercase legacy conversion separately.
- **reader: scope; scope: none; severity: low; kind: form — affected-decision keeps omit directly refactored contracts.** `plan.yaml:26-56` lists five decisions but omits DEC-159 (phase handoff/supersession), DEC-180 (pre/post shape semantics), and DEC-182 (legacy conversion and single-writer denial). These govern the matchers and diagnostic label T-02 changes. Add explicit keep dispositions; no amendment or strike is supported by the planned behavior-preserving change.

## Compliance and architecture

All SCs are traced: T-01 → SC-01/04; T-02 → SC-02/03/04. Dependency order is topological; files are disjoint, and T-02 does not invalidate T-01's presence check. T-02 is the final source-mutating task and owns final integration evidence. Both tasks correctly use Main under DEC-174/179.

Inspection obligations are explicit, not already passed: SC-01 (`plan.yaml:80-83`), SC-02 (`:116-120`), SC-04 (`:83,121`) require pinned-content/baseline and commit-order review. Case-sensitive legacy versus IGNORECASE shape matching, non-greedy phase, lowercased canonical names including multiple suffixes, frozen fixture, bootstrap exceptions, and byte-stable literal declaration shape are carried into T-02.

T-01 docs and T-02 scaffolding are legal matrix values with empty floors. T-02 is specifically a behavior-preserving structural refactor, not new scaffold: the exemption is defensible only while that no-behavior-change constraint holds. Existing integration evidence is additional, not fail-first evidence. No check-domain unit suites exist; do not claim their execution or invent tests to fill an empty floor. SPEC §9, DEC-35/187 and the TDD exemption were consulted.

Concurrency is supported by the existing file-parallel design (`check_domain_support.py:12-16`) and temporary fixture roots (`:70-75`); no shared-fixture collision was identified. This is inspection, not a concurrency run. Architecture improves locality without a new module, adapter or import seam: one handoff matcher, one plan text with deliberate compilation variants, no compatibility aliases. Independent decision-index searches found the three omitted governing entries above; the listed keep dispositions otherwise fit. Product docs are absent as reported; AGENTS maps SPEC/DECISIONS, not an architecture substitute.

## Principles applied

- Delete First: obsolete matcher and alias removal are the refactor's acceptance boundary, not a new abstraction.
- Migrate Callers, Then Delete Legacy APIs: T-02 migrates every named consumer and deletes old symbols in the same task.
- Model the Domain: named captures expose phase/cycle and feature-directory meaning while preserving consumer-specific flags.

Open questions: none. No builds, tests, linters, formatters or implementation diff review performed. Main must run the specified baseline/post integration checks and enforce the bounded receipt-producing invocation before implementation acceptance.
