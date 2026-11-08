# Platform scope and architecture review — plan c1

**PASS.** The unsigned draft serves the operator's platform-only destination. No concrete scope, dependency, ownership or architecture defect warrants a finding. This is a reasoned plan assessment, not production approval or compatibility/runtime evidence.

## Target and authority

Reviewed current `BRIEF.md` and `plan.yaml`; product source baseline supplied as `6303f9f`, not a production review range. `feature.json` has no review pin and both approvals are pending. Consulted the grilling intent, Kaya #14, `docs/SPEC.md` prerequisite, `docs/DECISIONS.md` DEC-002/008/009/010/011/012/013 and binding `docs/ARCHITECTURE.md:24-98`. Issue #14's latest-generator, undecided-provider and broad UI-install instructions do not override the accepted decisions and operator's Anthropic selection.

## Stage 1 — scope and execution

- Every task has live SC-01–SC-09 traces; no orphan SC or unrelated product deliverable found. All dependency edges point to predecessors. File lists partition 41 anchors across ten tasks; no shared write path or deleted-file gate assumption found. The research receipt's exact resolution stdout for both QA subsystem test paths and canonical 10-task/41-anchor check were inspected, not independently rerun.
- T-01 checks installed tools, not absent successor modules. T-02 explicitly delivers red assertions; absent-subject loading must fail the behavior assertion, never substitute a fake implementation or claim collection errors as red. Production tasks require those receipts and target predecessor tests. T-06 waits for real composition; T-08 waits for the actual app. T-09 runs the cumulative gate after all executable inputs exist; only documentation follows.
- Shared/ungranted root and application configuration belongs to serialized main-session-direct T-01; `.harness/harness.json` belongs to main-session-direct T-09. The existing product matrix was inspected: required offline kinds currently have null commands and obsolete discovery. The cutover supplies real, mutually exclusive discovery and failure/zero-selection demonstrations; null UI/eval remain explicit gaps, not fabricated passes.
- SC-05 inspection mapping: `plan.yaml:160-167` and T-06 require server-only settings, early bearer denial and safe errors. SC-06: T-01/T-07 enforce the binding workspace and app/server/mastra organization. SC-07: T-04/T-05 require owned non-public storage, TLS, bounded pooling and HMR-safe lifetime. SC-08: T-02/T-09 require real behavioral and terminal runner evidence. SC-09: T-10 requires truthful fresh-clone instructions. These are planned inspection subjects; none is discharged against shipped code here.
- SC-02/03 retain real Anthropic generation, independently recalled user/assistant messages and restart readback without model invocation. SC-04 separately requires actual adapter relations, catalog/default-grant checks and specific Data API non-exposure plus a successful control request. Offline collaborators are not hosted proof. Candidate versions/model remain unproven until exact-release inspection, installation, offline gates and operator UAT.

## Stage 2 — planned architecture and proportionality

The storage module earns depth: pool ownership, initialization, schema and lifecycle concentrate behind generation/recall composition rather than spreading across route and CLI callers. Auth/request guards sit at incoming-data seams; Mastra owns orchestration and memory, not financial logic. Route-level composition preserves the prohibited server-services-to-Mastra direction. External provider/database I/O are real test seams; no speculative adapter hierarchy or one-caller pass-through layer is required. Named process/HMR lifetime and probe-only cleanup reduce resource ambiguity and reader state.

**Mission proportionality:** a new runnable application, server interface and hosted persistence integration justify the plan lane. The static landing, bearer probe and operational SQL support the live platform requirements rather than introducing account/chat/worker/financial scope. No task-level or mission-level proportionality finding.

## Open questions

None. Implementation and operator receipts remain future gates; no product checks, credential reads, source writes or approval changes were performed.
