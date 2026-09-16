# Scope and architecture review — FEAT-1774 — plan c0

## BLUF

**FAIL.** The three tasks all serve live success criteria and their traces are valid, but the plan never ships or establishes the local Hindsight service that the chosen fail-closed path requires. On a machine with this repository but no separately installed Hindsight container, the committed OMP configuration points at an absent `localhost:8888` service and the first distinct observation is refused, so the operator cannot reach the destination described by the authority. T-01 through T-03 otherwise form a coherent, local architecture around existing seams.

## Gating finding

1. **High · substance · omission — no task establishes the required local Hindsight deployment.** The operator selected “local Docker on this Mac for now” as the server, and the BRIEF says the present deployment is local Docker (`BRIEF.md:42`). SC-01 requires successful synchronous retention before disk write (`BRIEF.md:17`), while SC-02 intentionally fails closed when the server is absent (`BRIEF.md:19`). Yet T-01 explicitly tests without Docker (`plan.yaml:50`), T-02 only writes/checks client configuration (`plan.yaml:60-77`), and no task owns a container definition, installation/start procedure, persistence, readiness proof, or operator-facing setup. Concrete failure: on a checkout where no Hindsight container has independently been created, `memory.backend` points to `http://localhost:8888`; every new observation exits 10 and remains absent from disk, so the feature's operator destination cannot work. The VPS/Tailscale/second-machine exclusion does not exclude the selected local deployment (`BRIEF.md:51`). **Must fix:** add a criterion/task and verification that establish the local Docker service (including durable storage and readiness), or explicitly identify and verify an existing separately operated local service as a prerequisite in the signed scope.

## Advisory observations

1. **Low · proportionality · task — the task DAG serializes disjoint work without an artifact dependency.** T-02 depends on T-01 and T-03 depends on both (`plan.yaml:66,85`), but their declared file sets do not overlap (`plan.yaml:43-46,68-71,87-91`) and each verify block exercises only its own files. Concrete consequence: a T-01 implementation failure prevents the independent config and skill-contract work from running, increasing repair latency without protecting a gate. Retain only dependencies needed for runtime acceptance; otherwise make these three implementation tasks siblings and perform end-to-end acceptance after all three.

2. **Info · substance — T-03's static text check is not evidence for SC-05's ordering requirement.** Its inline assertions only establish that four literals exist (`plan.yaml:93-108`); moving both recall instructions after Expertise judgment would still pass that task check. SC-05 is correctly marked `verify: inspection` (`BRIEF.md:25-26`), so this is not a missing acceptance gate, but the build receipt must not claim the inline script proves ordering. The pinned review must cite the procedure lines showing both recalls precede judgment and the canonical-headline instruction.

## Trace and topology audit

- **No orphan criteria:** SC-01–SC-03 map to T-01; SC-04 to T-02; SC-05–SC-06 to T-03; SC-07 is shared by all three. Every traced ID exists in the BRIEF.
- **No task without a live requirement:** T-01 supplies dual-write/backfill/fail-closed behavior; T-02 supplies the committed global untagged OMP configuration; T-03 supplies distillation recall and the mid-run authoring contract.
- **No shared planned file overlap:** the three declared file sets are disjoint. Therefore no successor can overwrite an earlier task's implementation or invalidate its file-local verify block.
- **Topology is acyclic and topological as written**, but the advisory above identifies unnecessary serialization rather than an invalid order.
- **SC-07 remains an inspection criterion:** task-local tests cannot prove repository-wide absence of a new Hindsight authority reader. Its pinned-diff inspection must cover all changed paths, not infer compliance from the declared file lists.

## Architecture grade

- **Deep modules:** T-01 extends the existing `observations-merge.py` interface with retention and backfill while sharing parsing, item construction, identity, and error handling. That concentrates provenance and idempotency rules rather than duplicating them across callers.
- **Seams and adapters:** the existing observation writer is the correct single write seam; the Hindsight HTTP client is its adapter. The existing OMP configuration checker is also the correct enforcement seam, avoiding a second validator. No hypothetical public seam is proposed solely for tests.
- **Locality:** live append and corpus backfill intentionally share the same content/metadata/document-ID builder, and OMP drift stays in the existing config checker. This is strong locality.
- **Lifetime/operations gap:** the client seam is specified, but the local server adapter's deployment and persistence lifetime are absent. That is the gating omission above, not a request for a new abstraction.

## Open questions

None. The local-service omission can be resolved by adding the selected deployment to scope or by making an existing operated service an explicit, verified prerequisite; operator input is not required to identify the gap.

```yaml
VERDICT: FAIL
DIGEST:
  headline: "Plan traces cleanly and uses strong existing seams, but it does not establish the local Hindsight service required for any fail-closed append to succeed."
  severity_max: high
  findings:
    - kind: substance
      scope: task
      severity: high
      reader: code-reviewer
      summary: "No task ships or verifies the selected local Docker Hindsight deployment."
      why: "With no separately installed service at localhost:8888, every distinct observation exits 10 and remains absent from disk."
    - kind: proportionality
      scope: task
      severity: low
      reader: code-reviewer
      summary: "The task DAG serializes three disjoint file-local changes without an artifact dependency."
      why: "A T-01 failure unnecessarily blocks independent config and skill-contract work."
    - kind: substance
      scope: task
      severity: info
      reader: code-reviewer
      summary: "T-03's literal-presence script does not prove SC-05 recall-before-judgment ordering."
      why: "Both required recall strings could move after Expertise judgment while the task check remains green; pinned inspection must supply the proof."
  must_fix:
    - "Add and verify the selected local Docker Hindsight deployment, including persistence and readiness, or explicitly declare and verify an already-operated local service as a prerequisite."
  spec_violations:
    - kind: omission
      path: ".harness/harness/features/FEAT-1774-observations-hindsight/plan.yaml"
      ref: "SC-01"
  code_grade: n_a
  reviewed: "plan:/Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-1774-observations-hindsight/.harness/harness/features/FEAT-1774-observations-hindsight/plan.yaml"
  human_commits_in_scope: []
  open_questions: []
  files_touched:
    - ".harness/harness/features/FEAT-1774-observations-hindsight/notes/review-harness-code-reviewer-plan-c0.md"
  expertise_update: []
artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-1774-observations-hindsight/.harness/harness/features/FEAT-1774-observations-hindsight/notes/review-harness-code-reviewer-plan-c0.md
```
