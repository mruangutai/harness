# BRIEF — FEAT-24 Config responsibility split

Implements issue #493, unit 5 of effort #336; the execution record is #498, "Execution — Multi-repo
control plane", which holds the unit table and the Destination criteria and is where this effort's
completion is read. #336 is a question ledger whose 18 questions are all closed, so it reports
finished while four units remain unbuilt; #498 is the artifact that says whether the effort is done.
The authorities are #350's resolution comment and
#336's "Decisions so far"; this brief **indexes** them and restates nothing.

## Problem

One concept — a repository's project board — is declared under two schemas in two files, and the
two loaders that read them disagree about failure. `factory_config._validate_board` raises loudly;
`gh_board.load_board` returns `None` **silently** on the same condition, at which point station
writes are skipped, INV-26 compares nothing, and every gate stays green. Harness's own board record
has no `stations` key at all, so `gh_board.derive_station` hardcodes `"Building"` and `"Review"` and
`check-state.sh`'s INV-26 hardcodes `"Building"`, `"Done"` and `"Backlog"` — a reader cannot tell
what harness's columns are without knowing DEC-192 by heart. Meanwhile kaya-ai's own `harness.json`
on `master` still pins `project_id`, `status_field` and `in_progress_option`, the pre-FEAT-18 flat
keys that do nothing at all, silently, when fed to a loader. The cost is the exact class FEAT-18 was
built to remove: a typo disables the operator's view of the factory and nothing says so.

## Goal

Each file carries only what it is responsible for. `fleet.yaml` says which repositories the factory
serves, where their checkouts go, and what branch they are cut from — nothing else. Each
repository's own `harness.json`, on that repository's own default branch, carries its board, its
stations, its tests, its gates and its budgets. Exactly one loader validates a board, wherever the
board came from, and it fails loudly with the file and the offending key named. Every station name a
gate or a factory tool resolves comes from a declaration, not from a literal in code. And kaya-ai's
config stops being stale, so the new loud error cannot fire on a foreign config months from now.

## Requirements

- REQ-01: A repository's board is declared in exactly one file, and no value is declared in both
  `fleet.yaml` and any `harness.json`.
- REQ-02: Every board that a factory tool or a gate resolves declares its station names explicitly,
  and no station name a tool or gate resolves is a literal in code.
- REQ-03: A board declaration that is present but unusable stops the operation with a message
  naming the file and the offending key. No station write is skipped in silence.
- REQ-04: Harness can obtain a fleet member's configuration when no checkout of that repository
  exists on this machine.
- REQ-05: A repository's checkout can still be created, and its branch cut and its pull request
  based, without reading anything that only exists inside that checkout.
- REQ-06: kaya-ai's own configuration is valid under the new shape on its default branch, and
  carries none of the pre-FEAT-18 pinned identifiers.
- REQ-07: Every surface that read a value which moved reads it from its new home, and no surface
  reads a key that no longer exists.
- REQ-08: The recorded decisions state what is true after this change wherever they previously
  stated the opposite.
- REQ-09: A project that genuinely has no board can still be onboarded and operated.

## Success Criteria

- SC-01: `.harness/factory/fleet.yaml` at head declares only `schema`, `repos[].name`,
  `repos[].default_branch` and `workspace_root`; a fleet declaration carrying `repos[].board` is
  rejected by a message naming that key and where the board moved to.
  verify: automated      evidence: unit
- SC-02: Each of the five station keys code resolves — `backlog`, `ready`, `building`, `review`,
  `done` — is read from the board's declared `stations` map, proved by five independent
  assertions, one per key, each of which fails if only that key's lookup is reverted to a literal.
  verify: automated      evidence: unit
- SC-03: Neither `gh_board.derive_station` nor `check-state.sh`'s INV-26 block contains a station
  name as a string literal, asserted per file with a positive control that proves the search runs.
  verify: automated      evidence: integration
- SC-04: Every malformed board shape — not a mapping, missing `owner`, missing or non-integer
  `number`, missing `station_field`, missing `stations`, a `stations` map whose key set is not the
  five, and a station whose value is empty — raises with the file path and the offending key in the
  message, one case per shape, through **each of the validator's two entry points**: `load_board`,
  which reads a project's own `harness.json` from disk, and `board_for`, which reads a fleet
  member's config from its remote. The same eight shapes are driven through both, so neither
  caller can be loud while the other is silent.
  verify: automated      evidence: unit
- SC-05: A board declared as an explicit `null` is accepted, writes no station, and is the only
  non-error path; a board key that is absent entirely from a fleet member's config is an error.
  Both asserted separately.
  verify: automated      evidence: unit
- SC-06: `board_for` on a fleet member returns that repository's board with **no checkout present**
  on disk, and a failed remote read — missing file, unparseable JSON, `gh` unauthenticated —
  raises naming the repository, the path and the ref, and never falls back to a checkout, a cached
  value or a default.
  verify: automated      evidence: unit
- SC-07: `default_branch` is still resolved from the fleet entry, not from anything inside a
  checkout, at each of its three consumers, with one named assertion per consumer and no two
  consumers sharing one: `factory_land` — its pull request is based on the fleet entry's branch;
  `factory_claim` — its pre-clone `default_branch_sha` call carries the fleet entry's branch;
  `factory_workspace` — its end-to-end run succeeds, which it cannot do if the key has left the
  fleet entry, since that is where it reads the branch it cuts the checkout from. Plus
  `test-no-distribution.py case3_presence_kaya_default_branch_is_master` still passes.
  verify: automated      evidence: unit
- SC-08: `test-no-distribution.py case3_absence_harness_is_not_a_fleet_member` still passes, named
  in the verify by that exact case name.
  verify: automated      evidence: unit
- SC-09: kaya-ai's `.harness/harness.json` on `master` carries a `board` block with the five
  stations and none of `project_number`, `project_id`, `status_field`, `in_progress_option`,
  evidenced by the merged pull request and by the output of a `gh api contents` read at `master`.
  verify: inspection
- SC-10: Every one of the eight files the reader survey classified as reading a moved key is
  migrated, with **one named assertion per file** and no file resting on another's: `gh_board.py`
  and `check-state.sh` by a literal-absence search over the file (or its INV-26 block) with a
  positive control; `gh-sync.py`, `board-station.py` and `factory_config.py` by named behavioural
  cases that can only pass after the migration; `factory_land.py`, `factory_claim.py` and
  `factory_decompose.py` by a named case each pinning the value they now resolve through the new
  source. The four files the survey classified as non-readers — `wayfind.py`,
  `layout_migration.py`, `check-plan-routes.py`, `branch-create-gate.sh` — are searched for every
  moved key, each with its own positive control, and must still match none.
  verify: automated      evidence: integration
- SC-11: The two recorded statements this change falsifies — DEC-174 amendment 2's per-repository
  fleet board, and DEC-196's "no stations map is declared for the harness's own board" — each
  carry an amendment, asserted per entry, and `gen-decisions-index.py --stdout` still matches
  `DECISIONS-INDEX.md` byte for byte.
  verify: automated      evidence: integration
- SC-12: `check-state.sh` completes and reports INV-26 as a violation, rather than aborting or
  reporting clean, when the board declaration is unusable.
  verify: automated      evidence: integration
- SC-13: The full suite passes at the merge commit — `run-unit-tests.sh --kind all` green — and no
  test file was removed to achieve it, asserted by comparing the registered script count before
  and after.
  verify: automated      evidence: unit

## Verification gaps

- `component`, `ui`, `eval` and `typecheck` ship with `cmd: null` in `.harness/harness.json`. **None
  of them detects any file this feature touches** — every changed path is Python, shell, JSON or
  YAML under `.claude/skills/harness/bin/`, `.harness/` or a product checkout, which `unit` and
  `integration` both cover with live runners. No criterion here rests on a null kind.
- **SC-10's non-reader half is a regression guard, not evidence of migration.** All four
  non-readers match zero moved keys today — re-derived at `ada8e99` and again while this brief was
  revised — so that search was green before this feature started and cannot go red because of it.
  It is worth running because it fails loudly if a task quietly adds a board read to one of them,
  but it proves nothing about the migration. The classification itself rests on a
  planning-time grep at `ada8e99`, recorded in `plan.yaml`'s `resolved_but_not_written` block, and
  nothing re-runs that survey.
- The kaya-config criterion is `inspection` rather than `automated` on purpose: the only automatable form would put a
  live network read of a foreign repository inside the unit suite, which makes the suite fail on a
  lost connection. The evidence is a `gh api` capture plus the merged pull request url.

## Constraints

- **`repos[].name`, `workspace_root` and `default_branch` cannot move out of `fleet.yaml`.**
  `harness_boundary.resolve_fleet` needs every name before it can classify any path, and
  `factory_workspace.py:115` reads `default_branch` in order to *create* the checkout. Both are
  forced by availability, not chosen.
- **Placement is in the product's own repository.** kaya's `harness.json` lives on kaya's `master`.
  The 2026-08-14 central-placement ruling is superseded by the 2026-08-18 comment on #493.
- **The config resolver's flag is `--which-config`, never `--resolve`** (#336 D-07).
- **Harness is not in `fleet.yaml`** (#355), and `test-no-distribution.py
  case3_absence_harness_is_not_a_fleet_member` keeps passing.
- **DEC-174 carve-out.** Any task touching `check-state.sh`, `check-domain.sh`,
  `bash-write-guard.sh` or `validate-digest.py` is executed by hand by the operator.
- **DEC-189/DEC-193.** No agent seat can be granted a path under a product checkout's `.harness/`;
  the checkout at `workspace_root/<product>` is nonetheless a sanctioned write location.
- Out of scope: `harness-init`'s rewrite (#206), product boards, `factory_claim.py`'s claim
  mechanics, cloning or running kaya's own code.

## Approval

status: approved
approved_by: operator (Mike Ruangutai), via main session
date: 2026-08-18
