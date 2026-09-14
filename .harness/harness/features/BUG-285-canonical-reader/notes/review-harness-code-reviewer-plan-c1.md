# Scope recheck — BUG-285-canonical-reader — plan c1

**PASS.** The applied plan concretely closes all four substance scenarios in this targeted recheck and is sound enough for signature on those concerns. The four proportionality findings remain open for operator routing and are neither reclassified nor resolved here.

## Substance clearance

1. **Complete live-derived migration ownership and amendment-on-drift:** T-01 makes one checked-in classification artifact exactly match the live AST file-and-symbol set, assigns every migratable row to T-03–T-07 with a targeted test, and makes missing classification, ownership, test, or plan-file projection fail with `PLAN AMENDMENT REQUIRED` before migration (`plan.yaml:83-99`). Every migration task repeats that artifact-as-authority and stop-before-edit contract (`plan.yaml:183-186,231-234,257-260,280-283`). This resolves the former fixed-list fail-open.
2. **Concrete omissions assigned semantically:** T-03 now names `factory_gh.py`, `handoff_done_when.py`, `inflight_registry.py`, `merge-settings.py`, and `sync-agent-adapters.py` plus their targeted tests (`plan.yaml:155-181`), and its intent explicitly assigns both handoff plan reads, all four factory GitHub parse envelopes, both merge-settings reads, both inflight-registry reads, and `parse_canonical` to semantic cutover (`plan.yaml:183-186`). Those assignments match the live sites at `handoff_done_when.py:127,257`, `factory_gh.py:171,543,644,928`, `merge-settings.py:244,266`, `inflight_registry.py:71,302`, and `sync-agent-adapters.py:142-145`.
3. **Byte-identical legacy gate proof:** T-07 creates a legacy-case inventory and requires exact equality of return code plus raw stdout/stderr bytes, ordering, and violation membership; new canonical-reader audit cases are a disjoint inventory and a missing or moved legacy case fails (`plan.yaml:286-288`). Its verify command exercises the dedicated byte comparison before the classification, full integration, and live-audit checks (`plan.yaml:283-284`). This now proves pre-existing `check-plan-routes.py` behavior independently of added audit cases.
4. **Authoritative route-table carrier without brittle API:** SC-02 identifies the module contract docstring as the authoritative complete route table and explicitly forbids exporting it as runtime API (`BRIEF.md:22-24`). T-02 specifies the table fields and required sanctioned routes, forbids a runtime table mapping and prose assertions, and instead binds exhaustive ownership to T-01's classification plus AST integration checks while behaviorally exercising every public route (`plan.yaml:120-122`). This covers readers, writers, `plan-merge.py`, `sync-agent-adapters.py`, main-session-owned files, writer callbacks, and the sole `state.yaml` trip-wire without turning prose into an executable interface.

## Traceability and approval

All SCs remain traced: SC-01 by T-01/T-03/T-05/T-06/T-07; SC-02 by T-02/T-04/T-07; SC-03 by T-02/T-03; SC-04 by T-03/T-04; SC-05 by T-01/T-05/T-06/T-07/T-08; SC-06 by T-04/T-05/T-06/T-07; SC-07 by T-02/T-03; and SC-08 by T-07/T-08 (`plan.yaml:74,103,149,190,211,237,264,292`). Every T-01–T-08 traces at least one SC. Approval remains unsigned and pending (`plan.yaml:3-5`), with `feature.json` still carrying `review_sha: "none"`.

The stored four proportionality findings remain `disposition: open` in `plan.yaml`; this targeted recheck makes no judgment on them.

Open questions: none.

```yaml
VERDICT: PASS
DIGEST:
  headline: Applied scope fixes close all four targeted substance failures without weakening the live operator intent.
  severity_max: none
  findings: []
  must_fix: []
  spec_violations: []
  code_grade: n_a
  reviewed: "plan:/Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-285-canonical-reader/.harness/harness/features/BUG-285-canonical-reader/plan.yaml"
  human_commits_in_scope: []
  open_questions: []
  files_touched:
    - /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-285-canonical-reader/.harness/harness/features/BUG-285-canonical-reader/notes/review-harness-code-reviewer-plan-c1.md
  expertise_update: []
artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-285-canonical-reader/.harness/harness/features/BUG-285-canonical-reader/notes/review-harness-code-reviewer-plan-c1.md
```
