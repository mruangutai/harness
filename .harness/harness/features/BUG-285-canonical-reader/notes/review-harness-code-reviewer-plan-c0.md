# Scope review — BUG-285-canonical-reader — plan c0

**FAIL.** The architecture is directionally sound, but the task graph cannot deliver the live operator ruling: its fixed migration surfaces omit current Python parse sites that the new guard is required to reject, and its final enforcement-layer relocation lacks the required byte-identical proof. It is not sound enough for signature.

## Ranked findings

1. **HIGH · substance · omission — the live AST work list has no complete migration task.** T-01 says its live output defines the work, and T-07 permits only the accessor layer, `harness_yaml`, canonical writer callbacks, and the sole `state.yaml` reader (`plan.yaml:46-58,211-220`). But T-03 narrows execution to findings “represented by these current symbols” and its fixed list omits current categories/sites, including both bare `plan.yaml` reads in `handoff_done_when.py:127,257`, additional GitHub-output parses in `factory_gh.py:543,644,928`, and JSON reads in `merge-settings.py:244,266` and `inflight_registry.py:71,302`. With the plan as written, those sites either remain and make T-07's required zero audit impossible, or are edited outside any task's declared files/verification. This violates SC-01/SC-04 and D-02. Make the T-01 classification artifact an explicit input to migration tasks and require those tasks' file scopes and targeted tests to be amended from that artifact before execution; do not preserve the present list as a ceiling.

2. **HIGH · substance · omission — T-07 changes an enforcement gate without SC-05's byte-identical proof.** T-07 relocates `check-plan-routes.py` and changes its audit mode, but its verify block only runs the integration test and live audit (`plan.yaml:202-220`). Unlike T-05/T-06, it does not capture and compare the gate's complete pre/post violation output. A relocation could therefore reorder, drop, or rewrite an existing violation while both commands remain green. Require a pre/post byte comparison for all pre-existing `check-plan-routes.py` cases, with only the newly introduced audit cases accounted separately. This violates SC-05 and DEC-174's direct-work proof contract.

3. **MED · substance · omission — the complete accessor/writer/read table is asserted but never delivered or checked exhaustively.** SC-02 requires the complete route table, including sanctioned writer callbacks and main-session-owned files (`BRIEF.md:22-25`). T-02 only requires exported names and tests individual behaviors (`plan.yaml:61-76`); it names no table carrier and no exhaustive assertion binding every row, including the deferred `state.yaml` trip-wire and source/write routes for hook payloads and GitHub JSON. A maintainer can receive all functions while still lacking the promised single answer for ownership, or a row can disappear while membership-style tests stay green. Specify the authoritative table location and an exact-key-set test covering every read and write/source route.

## Scope and architecture assessment

- **No proportionality downgrade is warranted.** The AST guard, central accessor module, semantic/mechanical split, and direct gate lane all serve live requirements; no task is orphaned solely for excess scope.
- **Sound elements:** one dependency-light artifact layer above `harness_yaml` is a deep module with useful locality; AST inspection is the correct enforcement seam; writer callbacks and the sole `state.yaml` reader are narrow syntactic exemptions; T-03/T-04 and T-06/T-07 keep semantic bypasses separate from mechanical relocations; `.sh` is explicitly excluded without claiming token/heredoc coverage; the #285 inverse fixture is centralized in T-02; no stale numeric baseline or ticket line number is imported as acceptance.
- **Not sound enough for signature:** the closed task file lists conflict with the live-derived inventory, and the last DEC-174 edit is not proven byte-identical.

## Dismissed candidates

- T-08 is not scope creep: the live #1594 ruling explicitly requires `branch-create-gate.sh` in DEC-174's enumeration.
- The linear dependencies are topological and preserve checker → accessors → semantic dispatchable → mechanical dispatchable → semantic direct → mechanical direct → documentation.
- SC-06 and SC-08 are not orphaned: T-03/T-04 and T-06/T-07 establish separate review units, while T-07/T-08 pin the Python-only boundary.

Open questions: none.
