# BRIEF — BUG-1290 factory claim resolves the feature repository root

Source: [#1290](https://github.com/mruangutai/harness/issues/1290) (the detailed scope record),
blocking subtask of #496 / FEAT-04. Decision record:
`.harness/notes/grilling-factory-claim-repo-root-2026-09-05.md`. Facts below are its verified
anchors, measured at `eb9d044e`.

## Problem

`factory_claim.py` resolves every claimed issue's plan under one hardcoded root — `FEATURES_ROOT`
at `factory_claim.py:48-50`, consumed once as `_BlockerCache(FEATURES_ROOT)` at `:341`. The factory
can decompose a feature stored under another registered repository's segment, but claim then cannot
read that plan and reports `no_plan`. The live Kaya proof stores FEAT-04 under
`.harness/kaya-ai/features/FEAT-04-pdf-parser-evaluation`, so every claim on that repository is
blocked and the factory lane cannot run end to end for anything but this repository.

## Goal

A claim for an issue on any served fleet repository reads that repository's own plan under
`<harness root>/.harness/<segment>/features/<FEAT>/` and evaluates its blocker gate, with the
segment rule living in exactly one place that both claim and `feature-worktree.py` call.

## Requirements

- REQ-01: A claim for an issue on a served fleet repository whose feature lives under
  `.harness/<segment>/features/<FEAT>` reads that plan and evaluates its blocker gate.
- REQ-02: Two served repositories carrying the same feature id resolve to their own plans; neither
  reads the other's, from disk or from cache.
- REQ-03: A served repository whose `.harness/<segment>/features` root is absent still produces the
  existing `no_plan` refusal, naming the resolved absolute path that was tried.
- REQ-04: A fleet entry whose repository name ends in `harness` — an owner-qualified name such as
  `owner/harness`, whose segment is therefore `harness` — resolves to `.harness/harness/features`.
  This is a fleet repository name, NOT the bare literal `harness` that `feature-worktree.py`
  accepts as a `--repo` form; the two are different inputs and only the first is in scope here.
- REQ-05: The `repo name -> segment` rule has one home, called by `factory_claim.py`,
  `feature-worktree.py:resolve_repo` and `factory_config.workspace_path`; no second
  owner-stripping derivation remains in any of those three files.
- REQ-06: `factory_claim.py` carries no hardcoded features root — no `FEATURES_ROOT` global, no
  alias, no fallback to the old root, and no docstring paragraph describing one (`:26-29`).
- REQ-07: The regression is covered at both boundaries (unit and integration), mutation-proven at
  the unit boundary, and no surviving test pins the deleted default. The `feature-worktree.py`
  edit is covered by the existing `tests/integration/test-feature-worktree.py` suite, which drives
  `resolve_repo` through the CLI as a subprocess — a source scan cannot catch a wrong segment
  there, so that suite must run in the task that edits the file.
- REQ-08: The repository's own layout gate stays green once `factory_claim.py` stops carrying a
  `.harness`/`features` join (`layout_migration.READER_TABLE:92-94` reads that file today; a reader
  matching neither form makes the whole `features` surface `CANNOT_VERIFY`, which `check-state.sh`
  INV-27 reports as a failure at `:2363-2367`). The chosen shape is a MOVE of that reader row onto
  `factory_config.py`, the module that carries the join after the change; the `features` surface
  keeps five reader rows.

## Success Criteria

- SC-01: With a fixture fleet declaring `mruangutai/kaya-ai` and a plan at
  `<root>/.harness/kaya-ai/features/FEAT-.../plan.yaml`, a claim reads that plan and reaches the
  blocker gate rather than `no_plan`.
  verify: test — `tests/unit/test-factory-claim.py`
- SC-02: With the same feature id present under two served segments carrying different task DAGs,
  each candidate's verdict is computed from its own plan; a case proves the second candidate does
  not receive the first's cached task.
  verify: test — `tests/unit/test-factory-claim.py`
- SC-03: With the served repository's features root absent, the refusal is the existing `no_plan`
  reason naming the resolved absolute path, and that path carries the repository's segment.
  verify: test — `tests/unit/test-factory-claim.py`
- SC-04: A fixture fleet entry whose owner-qualified name ends in `harness` (`owner/harness`)
  resolves to `.harness/harness/features` (fixture-only; the live fleet omits `mruangutai/harness`
  per DEC-174). Not the bare `--repo harness` literal, which is `feature-worktree.py`'s own CLI
  form and reaches no shared call.
  verify: test — `tests/unit/test-factory-claim.py`
- SC-05: `factory_claim` exposes no `FEATURES_ROOT` attribute after import, and the two module-scope
  cases pinning its default (`tests/unit/test-factory-claim.py:58-68`) are gone rather than
  re-pinned.
  verify: test — `tests/unit/test-factory-claim.py`
- SC-06: No owner-stripping segment derivation survives in `factory_claim.py` or
  `feature-worktree.py` in ANY spelling — a `split`, `rsplit`, `partition` or `rpartition` on a
  slash, or an `os.path.basename`, applied to a repository-named value — and `factory_config.py`
  defines it exactly once, with `factory_claim.py`, `feature-worktree.py:resolve_repo` and
  `factory_config.workspace_path` all reaching the segment through that one definition. The scan
  asserts the BEHAVIOUR rather than one spelling, so a re-derivation written `rsplit` or
  `partition` fails this criterion instead of shipping green; D-03 records the pattern, its
  measurement at `eb9d044e`, and the residue the scan cannot see.
  verify: test — `tests/unit/test-factory-claim.py`, case `BUG-1290 5f`
- SC-07: A `--fleet`-driven end-to-end claim whose feature lives under a non-`harness` segment
  succeeds through the existing integration harness.
  verify: test — `tests/integration/test-factory-integration.py`
- SC-08: The regression is mutation-proven at the unit boundary by
  `tests/unit/test-factory-claim-mutation.py` (T-05), which discards the repository argument at
  the `factory_config.features_root` seam so every candidate resolves to one root — the
  post-change equivalent of the deleted hardcode — re-runs `tests/unit/test-factory-claim.py`
  in-process, and requires cases `BUG-1290 5a`, `5b` and `5c` to print `ok` unmutated and `FAIL`
  under the mutant. Its evidence is the two marker lines `BASELINE 3/3 ok` and
  `MUTATION PROOF: 3/3 cases reddened`, which T-05's verify greps for and the doer records in the
  task receipt. Separately, the same cases are demonstrated failing BEFORE the production change
  by T-01's verify, which requires each of the six new cases' own `FAIL` marker line rather than
  a non-zero suite exit.
  verify: test — `tests/unit/test-factory-claim-mutation.py`
- SC-09: The layout detector's `features` surface is `CLEAN` on the real tree after the reader row
  moves from `factory_claim.py` to `factory_config.py`; no reader is classified `neither`, the
  surface still carries five reader rows with `factory_config.py` among them classified
  `migrated` and `factory_claim.py` absent, and the moved row's legacy pattern still matches a
  legacy control string rather than being dead. `test-layout-migration.py` alone cannot see any
  of that — it is green at `eb9d044e` and stays green if the row is removed — so T-04's verify
  pairs the suite with a reader-row probe that asserts those clauses over the real table and the
  real tree.
  verify: test — `tests/integration/test-layout-migration.py`, plus T-04's reader-row probe

## Verification gaps

- None. Both kinds this brief rests on are active runners in `.harness/harness.json` (`unit`,
  `integration`); no criterion rests on a `cmd: null` kind.

## Constraints

- BUG flow (DEC-139): one engineering squad, no product/design segments, no UAT; `verify: test`
  only. SUPPLIES the route, does not block.
- DEC-174 — `mruangutai/harness` is deliberately absent from `fleet.yaml`, asserted by
  `tests/unit/test-no-distribution.py:178-198`. This is why REQ-04 and SC-04 are fixture-only. It
  BOUNDS the evidence available, and no task may add the harness repository to the live fleet.
- `<harness root>` stays `harness_boundary.resolve_root(_BIN_DIR)` — the checkout hosting the tool,
  never cwd. Unchanged by this bug. SUPPLIES.
- No new refusal path for an unknown repository: `factory_config.repo_entry` and candidate step 4
  already fail closed. BOUNDS the change.
- Out of scope, per the grilling note: migrating `post-merge-sweep.sh:163`, `quarantine.py:109`,
  `worktree_terminal.py:107-129`, `feature_schema.py:231` onto the new resolver; landing
  `.harness/kaya-ai/features/FEAT-04-...` on `main`; populating FEAT-04's `feature.json`
  `factory.issues` map. The one adjacent surface this change FORCES is the layout detector's reader
  row for `factory_claim.py` (REQ-08).
- Disclosure, not a scope choice: after this fix a live claim run from `main` still reports
  `no_plan` for FEAT-04, because that feature tree exists only in the FEAT-04 worktree. Landing it
  is FEAT-04's, not this bug's.

## Approval

status: pending
