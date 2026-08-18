# Research — FEAT-24 config responsibility split

All measurements at `ada8e99` (HEAD of `feat/FEAT-22-docs-layout-migration`) unless stated.

## BLUF

The board can move out of `fleet.yaml` under in-repo placement, but only if harness gains a way to
read a fleet member's `harness.json` **without a checkout** — because `factory_decompose` and
`factory_claim` both resolve a product's board before any clone exists. The answer is a remote read
at `default_branch`. `default_branch` itself **cannot** move: `factory_workspace.py:115` reads it to
*create* the checkout, so moving it into the checkout is circular. It stays in `fleet.yaml`, sole
location, which satisfies ruling 1's actual rule (no value in both files) while #350's enumeration
of it into `harness.json` rested on a premise the 2026-08-18 comment killed.

## The pre-clone readers — the measurement that drives every decision

| Call site | Reads | Runs before a checkout exists |
|---|---|---|
| `factory_workspace.py:114-115,129,130,134` | `entry["default_branch"]` | yes — it *creates* the clone |
| `factory_claim.py:354-355` | `entry["default_branch"]` via `repo_entry` | yes |
| `factory_land.py:44-45,49,67` | `entry["default_branch"]` | no (post-workspace) but reads the fleet |
| `factory_config.py:146` | validates `default_branch` as required | n/a |
| `factory_claim.py:226` | `board_for(fleet, repo)` | **yes** |
| `factory_decompose.py:299,329,399` | `repo_entry`, `board_for`, `board_station(...,"ready")` | **yes** — intake, no issue number yet |
| `factory_land.py:85,90` | `board_for`, then `board["stations"]["review"]` directly | no |

`factory_workspace` is the decisive one. It takes `--repo` and `--issue`, and there is no
issue number at decompose time, so "clone first, then read the config" is not orderable.

## Reader classification — every mission-named candidate, classified

Grep of `board|station|default_branch` over `.claude/skills/harness/bin/` is a superset. Each file
named in the dispatch, classified:

- `board-station.py:132` — **`load_board` consumer** (ruling 3 surface). NOT a `default_branch`
  consumer; it reads `github.repo` and the board only. Confirms DEC-196's "one more call site".
- `wayfind.py` — **no match** for any moved key. Not a reader.
- `layout_migration.py` — **no match**. Not a reader.
- `branch-create-gate.sh` — **no match**. `test-branch-create-gate.py:55` asserts the ABSENCE of
  `project_number`, `project_id`, `status_field`, `in_progress_option` from that script; kaya's
  migration removes the same four keys from kaya's config and does not touch this test.
- `factory_decompose.py` — **board reader** (`board_for`, `board_station`), pre-clone. Above.
- `check-plan-routes.py:336` — the string `"Building"` appears in a **comment** about plan `status:`
  values, not a board read. Not a reader.

Loud-loader surfaces (`load_board` / `derive_station` consumers): `gh-sync.py:139,185`,
`board-station.py:132`, `check-state.sh:1131,1151,1180`.

## The station-name literals in code, and what they must become

- `gh_board.derive_station` returns `"Building"` (`:115`) and `"Review"` (`:117`).
- `check-state.sh` INV-26 `_EXPECT = {"building": "Building", "done": "Done", "pending": "Backlog"}`
  — three more literals, and two of them (`Done`, `Backlog`) are stations the fleet schema's
  three-key set does not cover.
- `factory_decompose.py:399` resolves `"ready"` through `board_station` already — the model to copy.

**Probed live, both boards carry the identical six DEC-192 options** in order:
`Backlog, Plan, Ready, Building, Review, Done` (`factory_gh.project_field_options('mruangutai',2,'Status')`
and `(...,3,...)`, 2026-08-18). So a five-key required set is safe on both.

`plan` is deliberately excluded from the required set: no code resolves it. `board-station.py` takes
the station as a plain CLI string resolved by name at the board (DEC-196), so `/harness-plan`'s
`Plan` needs no declaration. **Every declared key has at least one code reader; every code literal
becomes a lookup.** That is the rule, and it is what keeps the map from being a declaration nobody
reads — DEC-196's own objection.

## Kaya's config today, fetched from the remote

`gh api repos/mruangutai/kaya-ai/contents/.harness/harness.json?ref=master` returns a config whose
`github` block is `{sync, repo, project_number: 2, project_id: PVT_..., status_field: PVTSSF_...,
in_progress_option: 47fc9ee4}` — **no `board` key at all**, and the four pre-FEAT-18 pinned ids D-05
killed. Top-level keys present: `schema_version, cli_min_version, test_matrix, test_kinds,
commit_attribution, dirty_tree_whitelist, log_retention_days, cost_model, budgets, gates, github`.
No `default_branch`, consistent with it staying in `fleet.yaml`.

The remote read works today with no clone and no new dependency — one `gh api contents` call.

## The pen for kaya's file — measured, not argued

`check-domain.sh --resolve` at `ada8e99`:

- `/Users/molchairuangutai/GitHub/harness-factories/kaya-ai/.harness/harness.json` → **NOBODY**
- `.harness/factory/fleet.yaml` → **NOBODY**
- `.claude/skills/harness/templates/harness.json` → **NOBODY**
- `.harness/harness.json` → `harness-dev-ops`
- everything under `.claude/skills/harness/bin/` → `harness-backend-dev` (and `harness-dev-ops`)
- `.harness/harness/docs/DECISIONS*.md` → `harness-documentor`

The NOBODY on kaya's path is forced by DEC-189: in a product checkout, manifest entries whose first
segment is `.harness` or `.claude` are **excluded**, so no seat can ever hold that path. The
checkout location itself is legitimate — DEC-193 names `workspace_root/<product>` as one of the two
places code is written under harness authority. So the route exists; only the pen is missing, and
the main session is the only holder that does not require reversing DEC-189.

## Record statements this feature falsifies (DEC-188, no propagation checker)

1. **DEC-174 amendment 2** (`DECISIONS.md` §"DEC-174 amendment 2"): *"Each `repos:` entry in
   `.harness/factory/fleet.yaml` carries its own `board:` mapping."* False after T-07.
2. **DEC-196** (`DECISIONS.md:6057`): *"No stations map is declared for the harness's own board."*
   False after T-06. Its own text conditions the clause on 350's ruling having no implementing
   ticket — FEAT-24 is that ticket, so this is pre-authorization, not a conflict.
3. `.harness/factory/fleet.yaml` header comment: *"THE BOARD IS PER-REPOSITORY (FEAT-16). There is
   no top-level `board:` any more"* — the second half stays true, the first becomes false.
4. `.harness/harness.json` `github.board._note`: *"Absent or incomplete = station writes are not
   attempted and INV-26 is vacuous."* That is the sentence ruling 3 deletes.
5. `gh-sync.py:118,120` `load_config` docstring: *"A missing board is an ENVIRONMENTAL PRECONDITION
   (D-02), never a reason to skip"*, and `board-station.py`'s EXIT CONTRACT paragraph reserving
   exit 2 for caller mistakes. Both change.

Amendments 1 and 2 are T-10; 3,4,5 ride in the task that edits the file (G-13).

## Traps carried into task intents

- **`load_fleet()` with no argument reads the LIVE `fleet.yaml`** — `FLEET_PATH` binds at import
  (`factory_config.py:52`). Every fixture test must pass an explicit path or it passes for the
  wrong reason. Named in T-02, T-03.
- **Two fake-gh variables.** `factory_gh.run_gh` reads `FACTORY_GH`; `gh-sync.py` reads
  `GH_SYNC_GH`. A test setting one leaves the other hitting the real network. Named in T-04.
- **Registration list.** `run-unit-tests.sh:17-18` holds explicit `UNIT_SCRIPTS` /
  `INTEGRATION_SCRIPTS` arrays; an unregistered new test file fails the whole run's drift check.
  No new test file is added by this plan, so no registration change is needed.

## Baselines, observed at `ada8e99` with the plan pending

- **Registered test scripts (SC-13's "no test file removed"):** `run-unit-tests.sh:17` holds **16**
  `UNIT_SCRIPTS`, `:18` holds **12** `INTEGRATION_SCRIPTS`, **28 total**. This plan adds no script,
  so the number must be 28 at the merge commit.
- **`gh_board.py` quoted station names:** 3 at `ada8e99`. Must be 0 after T-04.
- **`gen-decisions-index.py --stdout` matches `DECISIONS-INDEX.md` byte for byte** at `ada8e99`, so
  T-10's drift check can turn green. There is no `--check` flag; the read-only mode piped into
  `diff` is the documented form.
- **Every task verify was run at `ada8e99` and returns non-zero**, except T-03, whose verify is
  green at head by construction: it discriminates only once T-02 has made a fleet-nested board a
  rejected shape. That exception is labelled in T-03's own intent.

## The four ok-line formats, measured — this cost a rewrite of six verify blocks

Test scripts in this tree do **not** share one passing-line prefix. Measured at `ada8e99`:

| Prefix | Scripts |
|---|---|
| `ok` + 4 spaces | `test-factory-gh`, `test-factory-config`, `test-gh-sync`, `test-factory-land`, `test-factory-claim`, `test-factory-decompose`, `test-factory-integration`, `test-check-domain` |
| `PASS` + 2 spaces | `test-gh-board`, `test-board-station` |
| `PASS` + 1 space | `test-no-distribution` |
| `ok - ` | `test-check-state` |

A verify that greps a literal `ok    <case>` is therefore permanently red against four of these
files, which BLOCKs correct work at the lead's verbatim cross-check. Every verify in this plan
normalises first — `sed -E 's/^(ok|PASS)[ -]+//'` then `grep -qxF` on the exact case text — and the
helper was proved against a real passing line from each of the four formats. `FAIL` is uniform at
line start across all twelve scripts, so the failure grep needs no normalisation.

## Open items handed to the operator

None blocking. The one sequencing constraint is stated in the plan: kaya's PR (T-09) must be merged
before T-07 removes the board from `fleet.yaml`, or every `factory_decompose`/`factory_claim` run
against kaya fails loudly until it is. That window is designed, not discovered.
