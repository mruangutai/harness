# Research — FEAT-20-migration-detector — the coupled-reader survey

Observed at `88b1182`, working tree clean. Everything here is a survey input for the plan; the
instructions live in `plan.yaml`, not here.

## BLUF

Two independently-atomic surfaces, each with a small closed set of coupled readers. The detector
compares the LAYOUT EVIDENCE ON DISK against the FORM each coupled reader is written in, one
surface at a time. Nothing tree-wide, nothing counted, nothing line-anchored.

## Surface FEATURES — unit 3's atomic cluster (map #336, "Unit 3 is ONE COMMIT")

Disk evidence, two disjoint glob shapes:

- legacy: `.harness/features/*/feature.json`
- migrated: `.harness/*/features/*/feature.json`

Disjoint by segment count, so no reserved-name table and no segment list is needed.

Coupled readers, and the literal each is written in at `88b1182`:

| Reader | Legacy form | Where |
|---|---|---|
| `team-config.yaml` write grants | `.harness/features/` prefix, 43 lines carry it | grant globs |
| `check-domain.sh` SWEEP_GLOBS | `.harness/features/*/feature.json` and three siblings | `:597-600` |
| `check-domain.sh` shape regexes | `^\.harness/features/[^/]+/…` (four) | `:663-666` |
| `check-plan-routes.py` discovery | `os.path.join(root, ".harness", "features")` | `:539` |
| `check-state.sh` discovery globs | `glob(join(H, "features", "*", …))`, 15 sites at this sha | throughout |

The count 15 is recorded as an observation only. The dispatch said 13 and map #336 said 14; the
number drifts, which is exactly why the check must assert FORMS PRESENT PER FILE and never counts.

## Surface DOCS — unit 4's atomic trio (map #336, "Unit 4 is its own atomic unit")

Disk evidence:

- legacy: `docs/harness/SPEC.md`
- migrated: `.harness/*/docs/SPEC.md`

Coupled readers:

| Reader | Legacy form | Where |
|---|---|---|
| `factory_config._PROBE` | `os.path.join("docs", "harness", "SPEC.md")` | `factory_config.py:32` |
| `harness_boundary.HARNESS_CONTROL_PLANE` | `"docs/harness/**"` entry | `harness_boundary.py:89-94` |
| `gen-decisions-index.DOCS_DIR` | `os.path.join("docs", "harness")` | `gen-decisions-index.py:20` |

## DELIBERATELY EXCLUDED from every reader set

`gh-sync.py:729`, `branch-create-gate.sh:77`, `validate-feature-json.py`, `factory_claim.py:43`,
the gitignore snippet, and all prose. Map #336 puts them in unit 9, "anytime". Reading them would
redden a state the map sanctions — the false-positive failure reached from the other side.

## The two sanctioned intermediate states

- features migrated, docs not — units 3 and 4 have no ordering tie.
- docs migrated, features not — same.

Both must exit 0.

## The #148 defence

`check-plan-routes.py` and its CI step are the working precedent for a check that can prove it
looked: a summary line, an `examined N` line, and three distinct error messages
(`.github/workflows/tests.yml`, step "Plan-route gate"). The rule this feature inherits: a coupled
reader file matching NEITHER form is CANNOT VERIFY (exit 2), never clean. A wrong or rotted anchor
is the shape that makes a check pass forever.

## Applicability — the finding that changed the design late

Every coupled reader is a harness control-plane file. `check-state.sh` also runs at session entry in
onboarded product repositories, and `test-check-state.py`'s fixtures are bare `.harness/` skeletons
built under `tempfile.TemporaryDirectory` — a shared `make_fixture` helper at `:40` plus many cases
calling `os.makedirs` directly. Neither holds a single reader file. Judged by the cannot-verify rule
alone, INV-27 would exit 2 on a healthy product repo and break every existing check-state case the
moment it landed.

Hence the positive control: `.claude/skills/harness/bin/check-state.sh` present at the scanned root
means the tree is a harness control-plane checkout and is judged; absent means NOT APPLICABLE, zero
counts, exit 0. Inside harness the marker is present by construction. The CI step's zero-count
assertion is the only thing standing between that branch and a silent pass, which is why it is a
criterion and not a comment.

## Lane precedent

FEAT-18's `plan.yaml` lane rows: `gh_board.py` resolved to `harness-backend-dev` and
`harness-dev-ops`, and was still `main-session-direct` because `check-state.sh` imports it and an
invariant computes its verdict from its return value — a DEC-174 carve-out BY CONTENT, on
FEAT-17's `harness_boundary.py` precedent. This feature's module is the same shape.

`check-plan-routes.py` prints `DEVIATION` (not `VIOLATION`, verified at `:214` and `:369`) for a
granted path declared `main-session-direct`, and does not increment the violation count.

## Open

- The MIGRATED form of each reader is anticipated, not observed — nothing has moved yet. The form
  table is data, and units 3 and 4 update their own rows inside their one atomic commit.
