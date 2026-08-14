# STATE

## Current

- feature: FEAT-20-migration-detector
- run: close-out — ship-refresh and distillation dispatched concurrently
- squad: eng + product + validator
- status: closing-out

**All 15 success criteria are MET. The feature's goal is achieved.** The operator ruled on the
one open criterion on 2026-08-14: SC-10 binds the *shipped surface*, which is exactly the eight
files it enumerates; the harness's own per-feature bookkeeping is outside its subject, not a
violation of it. `BRIEF.md`'s text stands as signed — no edit, no re-plan. The ruling and the
evidence it rests on are recorded at `notes/answers-2026-08-14-2-product.md`.

**Built and verified.** Four tasks — `14ca661` T-01, `d3207e7` T-02, `2c35398` T-03, `396f1ad`
T-04 — with every `verify:` re-run in this session rather than read from a receipt. Issues
#361-#364 closed, parent #360 on `Review`. **Blocking qa gate PASS** (matrix union
`{unit, integration}`, both green, both registration greps fired). **Review panel PASS**,
`must_fix: []`, `severity_max: med` under `advisory_unless_high`, so nothing gated.
**Goal-check: 15 of 15**, each verified first-hand at `434307a`.

**Live evidence, re-measured at HEAD.** The detector prints `features: CLEAN — evidence legacy`,
`docs: CLEAN — evidence legacy`, `examined 20 feature dir(s), 1 doc root(s), 7 reader file(s)`,
exit 0. Zero renames across the whole feature. `check-state.sh` exits 0 with zero INV-27 lines.
The feature's own tool confirms the feature stayed in its lane.

**Budget: `cycles_used` 3 of 10** — two from the plan phase, one from qa's in-run send-back. Both
build dispatches, the panel and the goal-check were clean first passes; the operator's ruling is
not rework and added none. **`len(runs)` 7 of 20**, and a floor, since T-01 and T-02 were
main-session-direct and are not runs.

**Next: the CEO briefing**, assembled from every run's digest read off disk — including the plan
phase this orchestrator did not run — with no report round spawned, disclosed in the briefing
itself. Then it returns to the operator for ship acceptance. Merge stays user-gated.

## Open Questions

None blocking. Seven residual items carry to the briefing's backlog:

- **A session-entry path executes files from the tree it scans.** `check-state.sh` runs
  `cd "$root"` before its heredoc, so `sys.path[0]` precedes `PYTHONPATH`; a planted
  `harness_yaml.py` or `layout_migration.py` at `CLAUDE_PROJECT_DIR` runs at every session entry.
  Byte-identical at `88b1182` — pre-existing, not this feature's regression, but RCE-shaped.
- **The approved plan contradicts its own code, and DEC-194 now repeats it.** Both assert every
  finding names the reader path, while the `no-evidence` and `no-rows` causes correctly name none.
  Narrow both, before unit 3 opens — units 3-7 cite DEC-194 as their maintenance contract.
- **The suite is correct-today, not pinned against regression.** First mutation target named:
  `check-state.sh:1302-1318` dispatches INV-27's wording across four `if/elif` branches on
  `_srep.cause` with **no trailing `else`**, and only one cause is rendered by any test.
- **SC-10's wording is deliberately left unimproved** by the ruling and will trip the same way on
  the next feature. The broader question — should containment criteria state an outcome ("nothing
  is renamed, no reader is migrated") rather than enumerate permitted files — is live and unowned.
- **`.github/workflows/tests.yml:110-114` carries a false guard claim**, pre-existing and
  byte-unchanged here. Issue #279 owns it.
- **Harness defect:** `bash-write-guard` refuses redirects whose target is a shell variable, so the
  plan's `verify:` clauses are not runnable verbatim by the agent that must run them.
- **Harness defect:** the playbook says to record the phase in `feature.json` `phase:`, which
  `feature-schema.json` forbids via `additionalProperties: false`.
