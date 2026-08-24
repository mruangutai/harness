# Receipt — harness-dev-ops — T-04 (FEAT-33, run c1)

**Verdict: built and green.** `board_lifecycle.py provision` exists, TDD RED→GREEN confirmed for
every new case, all three disaster-guard/anti-vacuum properties proven to redden against the
exact mutants the plan warns about, and `run-unit-tests.sh --kind all` is clean on every file
this task owns. One flagged plan gap (below) — worked around minimally and read-only, not
silently.

## Files
- `.claude/skills/harness/bin/board_lifecycle.py` (new)
- `.claude/skills/harness/bin/test-board-lifecycle.py` (new)
- `.claude/skills/harness/bin/test-factory-integration.py` (added case (J) + one new stub branch)
- `.claude/skills/harness/bin/run-unit-tests.sh` (added `"test-board-lifecycle.py"` to `UNIT_SCRIPTS`, the one mandated line)

## `provision`, step by step
1. Resolve root via `factory_config.harness_root()`; resolve the board via `_resolve_board`:
   no `--repo`/`--repo == own repo` → `gh_board.load_board(root)`; a fleet member →
   `factory_config.board_for(fleet, repo)`; neither → `factory_cli.refuse` (exit 2, names the
   repo + both sources tried, zero gh calls).
2. `board is None` (explicit `github.board: null`) → print, exit 0, zero gh calls.
3. `factory_gh.project_resolve(owner, number)` — the ONLY signal trusted to call
   `project_create`. Any other `GhError` here propagates unhandled, zero mutations.
4. `resolved is None` → `project_create` + `project_link_repository`, print the new number,
   `sys.exit(3)`.
5. Otherwise discriminate "field absent" vs "field exists, not single-select" via `_field_probe`
   (see gap below) — absent → `project_single_select_create` with all six declared stations in
   declared order; wrong type → `factory_cli.refuse` (exit 2, names field + real type, zero
   mutations).
6. Single-select → `existing = factory_gh.project_field_options(...)`, `missing =
   _missing_options(declared, existing)` (byte-for-byte, case-sensitive, order-preserving); empty
   → "nothing to do", exit 0; else `project_single_select_extend(project_id, field_id, existing +
   missing)` — existing options first, additions after, never the reverse.

## The option union
`_missing_options(declared_stations, board_option_names)` = `[v for v in declared_stations if v
not in board_option_names]`. Called once, then `existing + missing` is what gets sent to
`project_single_select_extend` — never `missing` alone.

**Proof it can go red:** mutated the call site to `project_single_select_extend(project_id,
field_id, missing)` (dropping `existing`). The "sends existing options first... " check reddened
immediately, showing the mutation would have sent only `["Review", "Done"]` — i.e. would have
deleted `Backlog/Plan/Ready/Building` from the operator's board. Reverted, confirmed byte-identical
via `diff`, re-ran green.

## SC-08's discriminating assertion, verbatim
```python
check("SC-08: no argv the fake receives contains the string 'Abandoned'",
      r.returncode == 0 and log and not any("Abandoned" in l for l in log),
      repr(log))
```
Run against the missing-options fixture (a real mutation happens, so the check is not vacuous —
not the "nothing to do" path). **Proof it can go red:** mutated `_declared_stations` to append
`"Abandoned"` to the returned list. The check reddened, showing `"Abandoned"` appearing inside a
real `updateProjectV2Field` mutation argv. Reverted, confirmed byte-identical, re-ran green.

## Each new case's red-proof
- **Disaster guard (i)** ("project exists, field absent → `project_create` not called"):
  constructed M3's exact disaster — replaced the `project_resolve`+`_field_probe` discrimination
  with a broad `except factory_gh.GhError: create a new project` around `project_field_options`,
  fed it a field-absent-shaped `options` response. Guard reddened (`rc=3`, a `createProjectV2(`
  call recorded) exactly as the plan predicts for "the cheap wrong implementation."
- **Disaster guard (ii)** ("field wrong type → exit 2, zero mutations"): same class of mutant —
  broadly catching `GhError` and unconditionally calling `project_single_select_create` — reddened
  both the exit-code and the zero-mutations checks for the wrong-type fixture.
- **Integration case (J)** ("provision against a complete board exits 0, zero mutations"): this
  assertion alone is **exactly the vacuous-assertion trap** the harness expertise warns about — an
  `__main__` block that forgets to dispatch also exits 0 with an empty call log, passing both
  checks for the wrong reason. Verified this live: commented out the
  `if __name__ == "__main__":` dispatch line, re-ran — the exit-0 and zero-mutation checks stayed
  green (confirming the vacuity), so I added two anti-vacuum assertions ("reports its own verdict
  on stdout", "at least one gh call was recorded") mirroring this same file's existing `(H)`
  anti-vacuum convention. Re-ran the mutant: both new assertions correctly reddened. Reverted,
  confirmed byte-identical, re-ran green (120/120 in `test-factory-integration.py`).
- All other new unit cases (no-project/exit-3, field-absent/create-in-order, missing-options/
  extend-once, null-board, unknown-repo) were written before any implementation existed and
  observed genuinely RED (module-not-found, `rc=2`) before the implementation made them GREEN —
  the standard TDD proof, not a separate mutation.

## The field-ID gap — plan defect, not worked around silently
T-04's dispatch names exactly seven primitives (`project_resolve`, `project_create`,
`project_link_repository`, `project_single_select_create`, `project_single_select_extend`,
`project_workflows`, `project_field_options`). **None of them returns an existing field's node id
or its real GraphQL type name** — `project_field_options` (factory_gh.py:465-467) discards both,
returning option *names* only, and `_project_field_resolve` (the only function that has them) is
private and deliberately collapses "field absent" with "field is not single-select" into one
`GhError` (factory_gh.py:451-457, a documented prior decision). Both `project_single_select_extend`
(needs the field id) and the step-3 disaster guard (must tell absent from wrong-type apart without
guessing) are unreachable through the given primitives alone — verified by grepping factory_gh.py
for every `def project_` and finding no ninth function.

**What I did:** added one **read-only** local helper, `_field_probe`, in `board_lifecycle.py`,
sent through `factory_gh.run_gh` — the same `FACTORY_GH`-indirected seam every primitive in
`factory_gh.py` already uses, so it is exactly as fake-testable. It asks only for the field's
`__typename` and node id via three inline fragments on the `ProjectV2FieldConfiguration` union's
three concrete members. It mutates nothing.

This is a **deviation from the literal primitive list**, made because the alternative — refusing
whenever discrimination is needed — would make D-07's "the harness creates... its Status field"
requirement, and the plan's own required "no-field path creates the field" test case, both
unimplementable. Flagging this for the lead/architect: either fold `_field_probe`'s query into
`factory_gh.py` as an eighth primitive in a follow-up task, or affirm the local, read-only helper
as acceptable. I did not ask-and-block on this because it is cheap and reversible (read-only, no
new mutation, isolated to one private function) — but it does touch the single-seam framing in
`factory_gh.py`'s own docstring, which is the lead's call to ratify or not.

## `run-unit-tests.sh --kind all` — exact result
Command run verbatim: `.claude/skills/harness/bin/run-unit-tests.sh --kind all`.
Exit code: 1 (one failure — not mine, see below). No `MISCONFIGURED` line (drift detector and
kind cross-check both clean). `test-board-lifecycle.py`: **PASS** (20/20 checks).
`test-factory-integration.py`: **PASS** (120/120 checks, including the two new `(J)` checks and
the two anti-vacuum checks).

The one failure: `test-gh-sync.py`, case "custom stations: sets the sub-issue's station to the
DECLARED building option (OPT_DOING), not the hardcoded literal OPT_BUILDING" — this is T-07's own
sibling task on `gh-sync.py`/`test-gh-sync.py`, in flight concurrently in this same worktree, per
this task's own dispatch warning. I touched neither file and take no action on it.

## Change-type enum mismatch (per dispatch instruction)
This task is planned `change_type: feature`. `validate-digest.py:158` gives dev-ops the enum
`{config, scaffolding, infra, ci}` — no `feature` member (issue #778, already filed). Substituting
`infra` for the digest below, per instruction, rather than silently reclassifying to something the
schema accepts without saying so.
