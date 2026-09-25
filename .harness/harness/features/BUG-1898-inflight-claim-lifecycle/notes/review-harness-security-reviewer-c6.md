# Security review — BUG-1898 validate-c6

**PASS. F-SEC-C5-01 is closed.** At immutable pin `47b345fe65e992e07386de717f43b9f8dd495dc8`, every sampled lineage id under a governed orchestrator is collected by the same any-depth root predicate and every non-direct, wrong-persona, or wrong-parent row is rejected. No singleton/crossed-row escape or other scoped security finding remains.

## Pin, range, and scope

- Exact source reviewed and executed from `git archive 47b345fe65e992e07386de717f43b9f8dd495dc8`.
- Canonical census used `merge-base(origin/main,pin)..pin`. The focused range `7893fe7a23e493dcd1554e439f28e3c9832b4de4..47b345fe65e992e07386de717f43b9f8dd495dc8` contains ten paths; its only executable delta is `tests/manual/probe-inflight-claim-lifecycle.py` (+15/-6), with the other changes limited to feature state/evidence/reviewer records.
- In scope: sampled runtime identity, persona, and parent fields cross into the SC-07 ship oracle. A false acceptance would permit tampered or misattributed lifecycle evidence to support shipment. This surface has prior security review through c5; c6 changes the exact failed assertion.

## Adversarial oracle proof

Pinned behavior at `tests/manual/probe-inflight-claim-lifecycle.py:433-476`:

- `_governing_root` recognizes any-depth descendants by the governed root plus `.` boundary. `nested_ids` applies it to every sampled row, so `Nest.Probe.Deep` cannot disappear from the gathered set.
- `crossed_rows` applies the same governing root. A gathered row is accepted only when it is one non-empty runtime-name segment below the orchestrator, has persona `harness-eng-lead`, and has `parent_agent_id` exactly equal to that orchestrator. Any deeper row is crossed regardless of otherwise-correct persona/parent.
- S3 requires `len(nested) == 1` and `not stray`. Its final no-row selector calls `governed_rows(governed + nested)`, covering the exact singleton it observed.

Independent synthetic execution of the pin produced `(nested count, crossed count)`:

- Former c5 counterexample `Nest.Probe.Deep` / `harness-qa` / parent `Nest.Probe`: **(1, 1)** — positive control catches the former hole.
- Structurally deeper otherwise-well-formed lead `Nest.Probe.Deep` / `harness-eng-lead` / parent `Nest`: **(1, 1)**.
- Direct `Nest.Probe` with wrong persona: **(1, 1)**.
- Direct `Nest.Probe` with wrong parent: **(1, 1)**.
- Mixed valid `Nest.Probe` plus invalid `Nest.Probe.Deep`: **(2, 1)**, failing both singleton and no-crossing predicates.
- Valid direct `Nest.Probe` / `harness-eng-lead` / parent `Nest`: **(1, 0)**.
- Correct top-level governed `Nest` and `Plain` orchestrator rows: **(0, 0)**.
- The no-row selector returned `Nest`, `Nest.Probe`, and `Nest.Probe.Deep` when those exact gathered ids were supplied, excluding only an unrelated row.

A Cartesian search across direct/deep/unrelated ids, four personas, and four parent shapes found no accepted lineage shape except a direct child with the exact lead persona and governing parent. The only syntactic artifact was an empty suffix (`Nest.`), which cannot be emitted by the runtime's non-empty agent-name segment and gives no describable attacker capability; it is not a finding. Thus there is no surviving fail-open row under the governed runtime-id grammar.

## Authorized SC-07 receipt

SC-07 is graded only from the final operator-authorized entry in `notes/live-omp-probe.md`, run `2026-09-25T13:18:49+00:00`: **PASS 29/29**, registry `before: []` and `after: []`. Its observed direct lineage is `Nest.Probe`, persona `harness-eng-lead`, parent orchestrator `Nest` (shown by the lineage and direct runtime lifecycle), matching the pinned oracle's accepted shape. No replacement receipt or live/credentialled probe was created.

## OWASP / STRIDE result

No focused delta adds a dependency, network request/redirect, SQL/shell/template interpolation, export, path traversal, auth route, credential value, PII, or secret logging. Credential handling remains an existence/count check and does not emit values. The relevant Tampering/Repudiation/Elevation boundary is mitigated by the shared root predicate plus exact depth/persona/parent checks. INV-43 late succession for `notes/handoff-validate.md` seq-3 remains a named non-blocking historical residual, not a security finding.

## Cleanup

No source, test, config, plan, brief, feature state, run state, receipt, or other reader artifact was modified. The immutable scratch archive `/tmp/bug1898-security-c6` was removed with main-session assistance after the persona read-only guard correctly blocked direct removal; Main confirmed the path no longer exists. No formatter, linter, project-wide build/suite, or live mode ran.

```yaml
VERDICT: PASS
DIGEST:
  headline: "F-SEC-C5-01 is closed at 47b345f; no singleton/crossed-row escape or other scoped security finding remains"
  in_scope: true
  scope_reason: "The focused probe delta validates untrusted runtime identity/persona/parent observations used as SC-07 ship evidence; c6 repairs the previously demonstrated fail-open lineage boundary."
  severity_max: none
  findings: []
  must_fix: []
  threat_model:
    - { boundary: "sampled governed lineage row -> S3 identity assertion", stride: "T/R/E", mitigated: true }
    - { boundary: "gathered governed ids -> final no-row assertion", stride: "T/R", mitigated: true }
    - { boundary: "credential environment/store -> receipt", stride: "I", mitigated: true }
  open_questions: []
  files_touched: []
  expertise_update: []
artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-1898-inflight-claim-lifecycle/.harness/harness/features/BUG-1898-inflight-claim-lifecycle/notes/review-harness-security-reviewer-c6.md
```
