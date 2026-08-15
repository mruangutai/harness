# BRIEF — FEAT-21-features-layout-migration

Unit 3 of the multi-repo control-plane sequence (map #336, "#339 resolution" as amended 2026-08-14).
Unit 0 — the detector — shipped as FEAT-20. This is the first unit that moves files.

## Problem

Every feature record in the control plane sits at `.harness/features/<FEAT>/`, a path with no room
for a second repository. The destination the operator ruled is `.harness/<repo>/features/<FEAT>/`,
with harness itself one repository among them — its segment is `harness`, from `harness.json`
`github.repo` = `mruangutai/harness`. Until that segment exists, four things the sequence depends on
cannot be built at all: per-repository write grants (unit 7), per-repository config resolution
(unit 5), the expertise split (unit 6), and a live proof against a second repository (unit 8).

The move itself is not the hard part. The hazard is that the mechanisms which resolve a feature path
**fail silently when a segment is inserted** (issue #344, measured): `check-state.sh`'s fifteen
discovery sites return empty and the gate reports a healthy tree; `check-domain.sh`'s four shape
regexes and its `SWEEP_GLOBS` stop enforcing anything while still advancing the shape-sweep stamp;
CI's plan-route guard is defeated by exactly the shape a repo segment produces. Split the cluster
across commits and the tree is either one where every write is denied, or — worse — one whose shape
gate is silently off. Two of the failures are loud instead: after the move, `team-config.yaml`'s
grants no longer match, so every agent loses its own artifact paths, and `branch-create-gate.sh`
denies the creation of a branch for any feature.

## Goal

Move every feature directory to `.harness/harness/features/<FEAT>/` in ONE commit, together with
every mechanism mechanically coupled to that path, so that at no landed commit is the tree half
moved. The detector shipped in FEAT-20 is the instrument: green before, green after, and a red
detector at a landed commit is a stop rather than a note.

## Scope

**In:** the physical move of every directory under `.harness/features/`; `team-config.yaml`'s write
grants; `check-domain.sh`'s `SWEEP_GLOBS` and its four shape regexes; `check-plan-routes.py`'s
discovery; `check-state.sh`'s fifteen discovery sites; the test suites whose fixtures or literal
expectations are pinned to the old path; the guard-enforced instruction paths that tell an agent
where to write its receipt, its observations and its per-feature notes; `branch-create-gate.sh`'s
flow lookup; this repository's own `.gitignore` run-dir rule; the three mechanisms that resolve a
feature path by arithmetic over its depth rather than by a literal — `test-factory-cli.py`'s
module-scope plan read, `gh-sync.py`'s root derivation and `validate-feature-json.py`'s discovery
glob; the two present-tense texts in `.github/workflows/tests.yml` that describe those pulled-forward
steps to a CI reader and to an operator; and the parity test of issue #387, which lands first as its
own commit.

**Out — settled elsewhere, not re-judged here:**

- The DOCS surface. `docs/harness/**`, `factory_config._PROBE`,
  `harness_boundary.HARNESS_CONTROL_PLANE`, `gen-decisions-index.DOCS_DIR` — unit 4, its own atomic
  unit, no ordering tie to this one. The two mixed-forever items FEAT-20 accepted stay mixed.
- `mruangutai/harness` stays absent from `.harness/factory/fleet.yaml` (#355, DEC-174 am.1). The
  detector derives harness's segment from `harness.json` independently of the fleet, so the
  post-move scan raises no undeclared segment. Re-adding a fleet entry would be a decision, not a
  convenience.
- `factory_claim.py`, the shipped `templates/gitignore.snippet`, `merge-gitignore.sh` and
  informational prose — unit 9, landing anytime. `gh-sync.py` and `validate-feature-json.py` were
  on this list and have moved into scope: both fail **silently** after the move, and the BRIEF's own
  severity ordering puts silent above loud. The two `.github/workflows/tests.yml` texts move with
  them for the same reason — they describe the pulled-forward steps, and left behind they would tell
  a CI reader and an operator that the sweep globs a path nothing occupies. The dated measurement
  comments in that same file stay as they are: they record commands that were run and what they
  returned, so they are true as taken.
- The cross-repository **key collision** in `check-state.sh`. Its feature dictionaries key on the
  bare directory name, so two repositories holding a same-named feature collapse last-write-wins.
  It cannot fire while one repository exists. Only the finding *label* is fixed here; the keying is
  unit 5's or unit 8's, where a second repository actually lands.
- Issue #356 proper. Its remaining work is unruled (see Constraints).

## Requirements

- REQ-01: Every feature directory that was under `.harness/features/` is under
  `.harness/harness/features/`, and nothing remains at the old location — including files git does
  not track.
- REQ-02: Every mechanism that discovers or authorises a feature path finds features at the new
  location. No gate evaluates over an empty set and reports health.
- REQ-03: The tree is never half moved at a landed commit: the coupled cluster and the move share
  one commit.
- REQ-04: An agent following its own written instructions can still write its receipt, its
  observations and its per-feature notes after the move, and a branch can still be created for a
  feature.
- REQ-05: The docs surface is untouched, and the sanctioned state of features-migrated with
  docs-legacy is reported as healthy.
- REQ-06: The two renderings of the detector's finding — the CI one and the session-entry one —
  are held to name the same reader set by a test (#387).
- REQ-07: A reader can see, from the record, what the detector said at the commit before the move
  and at the commit that made it.

## Success Criteria

- SC-01: On the repository as it stands at the landed move commit, the layout detector exits 0, and
  the unit case that scans the real repository root and asserts non-zero examined counts passes.
  verify: automated      evidence: unit
- SC-02: The detector's output at the landed move commit reads `features: CLEAN — evidence
  migrated` and `docs: CLEAN — evidence legacy`, and its summary line reads `0 mixed, 0
  cannot-verify`. The output at the parent commit reads `features: CLEAN — evidence legacy`,
  `docs: CLEAN — evidence legacy` and the same summary line. Both captures are committed with their
  commit sha. No criterion here counts feature directories: this feature's own directory is created
  under the legacy layout and moves with the rest, so any count is stale within one cycle.
  verify: inspection
- SC-03: `check-state.sh` exits 0 and emits no INV-27 finding at the landed move commit.
  verify: automated      evidence: integration
- SC-04: The full unit and integration suites pass at the landed move commit, including
  `test-check-state.py`, `test-check-domain.py`, `test-check-plan-routes.py`,
  `test-bash-write-guard.py`, `test-harness-yaml.py` and `test-no-distribution.py`.
  verify: automated      evidence: integration
- SC-05: No path under `.harness/features/` exists on disk after the move — tracked, untracked or
  git-ignored — and the check that establishes this asserts the search's exit status rather than a
  line count.
  verify: automated      evidence: integration
- SC-06: `check-domain.sh --resolve` on a post-move feature artifact path
  (`.harness/harness/features/FEAT-21-features-layout-migration/notes/receipt-harness-backend-dev-x.md`)
  names `harness-backend-dev`, and the same path under the pre-move shape names nobody. The write
  gate moved with the files rather than being widened to accept both.
  verify: automated      evidence: unit
- SC-07: Every occurrence of the literal `.harness/features/` that instructed an agent where to
  write or read a per-feature artifact — in agent files, skills, team definitions and the harness
  command — names the new path, and the only survivors of that literal outside the shipped
  `templates/` directory are ones a reviewer can name and justify individually.
  verify: inspection
- SC-08: `branch-create-gate.sh` allows creating a branch named for a feature that exists at the new
  location, and still denies one naming a feature that exists nowhere.
  verify: automated      evidence: integration
- SC-09: Run directories at the new location are git-ignored, so a team run does not find a dirty
  tree.
  verify: automated      evidence: integration
- SC-10: A test constructs surface reports and asserts that the CI rendering and the session-entry
  rendering name the same reader set and the same cause for the same input (#387). It reddens if
  either rendering is changed alone.
  verify: automated      evidence: unit
- SC-11: The docs surface is unmodified by this feature: no file under `docs/harness/` and none of
  the three DOCS-surface readers is changed.
  verify: inspection
- SC-12: Beyond this feature's own planning record, everything it changes lands in exactly two
  commits — the parity test alone, then the cluster and the move together. In the plan's task terms,
  stated identically wherever it is stated: exactly one commit carrying T-02 through T-08, T-10 and
  T-09; T-01 is its own earlier commit.
  verify: inspection
- SC-13: The two mechanisms that derive the control-plane root or its feature glob by path
  arithmetic still resolve it at the new layout, each proven by a test case that stages a feature
  at the migrated depth: the GitHub mirror resolves a repository root instead of skipping, and the
  execution-state validator reports a non-zero file count instead of a clean zero.
  verify: automated      evidence: integration (the mirror case) and unit (the validator case)
- SC-14: Every operator-facing message emitted by `check-plan-routes.py` or
  `validate-feature-json.py` that names where a scan looked names the path actually scanned. None
  names the pre-move shape, and each still names a path — a message that stopped naming one at all
  does not satisfy this. There are three, and all three are test-backed:
  `check-plan-routes.py`'s scan line, by the existing case that asserts that line verbatim;
  `check-plan-routes.py`'s unreadable-path message, by the existing case that already stages an
  unreadable feature directory and reads the resulting stderr — that case gains an assertion on the
  path text, which it does not have today; and `validate-feature-json.py`'s scan line, by the added
  case that stages a feature at the migrated depth and reads stderr, which gains the same kind of
  assertion. One further operator message names a scanned path — the plan-route step's error string
  in `.github/workflows/tests.yml` — and it is covered by a form check in its task's verify rather
  than by a suite, because no test executes that workflow line.
  verify: automated      evidence: integration (the two `check-plan-routes.py` messages) and unit
  (the `validate-feature-json.py` scan line)

## Verification gaps

None of the null-runner test kinds (`component`, `ui`, `eval`, `typecheck`, and `functional`, which
is signed excluded under DEC-187) covers a surface this feature touches: the work is shell and
Python gate code plus a directory rename, covered by the `unit` and `integration` runners, both
active. SC-02, SC-07, SC-11 and SC-12 rest on a reviewer reading a captured artifact or a diff rather than
on a runner; that is stated here rather than dressed as automation.

## Constraints

- **One commit for the cluster.** The grants, both `check-domain.sh` sites,
  `check-plan-routes.py`'s discovery, `check-state.sh`'s discovery sites and the physical move are
  mechanically coupled — `check-plan-routes.resolve_agents` shells out to `check-domain.sh
  --resolve`, which reads `team-config.yaml` and calls `harness_boundary.matches`.
- **DEC-174 applies to most of this feature.** `check-state.sh` and `check-domain.sh` are named
  carve-outs; `layout_migration.py` is one by content on the FEAT-20 precedent;
  `team-config.yaml`, `.gitignore`, the agent files and the skills all resolve to NOBODY. Every
  task here is main-session-direct.
- **This feature's own record moves mid-feature.** Its `BRIEF.md`, `plan.yaml`, `feature.json`,
  `STATE.md` and `notes/` are created at `.harness/features/FEAT-21-features-layout-migration/`
  and are at `.harness/harness/features/FEAT-21-features-layout-migration/` from the move commit
  onward. Every dispatch, grant and gate reference after that commit uses the new path.
- **Issue #356 is not folded in.** Two of its five relative-path families name
  `.harness/features/...`, and those literals are re-anchored here because the write guard denies
  them otherwise. Its actual defect — a relative path in prose resolves against the agent's working
  directory, which in a factory workspace is not the control plane — is orthogonal to which literal
  the prose names, and its design is explicitly unruled on the ticket: which mechanism carries a
  resolved control-plane root to an agent, what the check is, and whether a doer standing in a
  product may read harness's skills at all. No factory worker has ever run, so nothing regresses by
  leaving it open. #356 stays open and whole.
- **Issue #387 is folded in, first.** The validator recommended it before unit 3 leans on the
  detector's blame text, and it is a test-only change to one file.
- **Reader edits are scoped by the pattern rule** in `layout_migration.py`'s module docstring: a
  legacy pattern is the weakest fragment every stale site necessarily contains, re-audited against
  the real file at the base commit before the row's edit is written. The four FEATURES rows were
  audited at `88b1182`, two commits behind this base; the re-audit at `62fef85` is quoted per row in
  the plan.
- **The detector's residual bound is inherited.** It proves per-file form agreement, never per-site
  completeness. A file migrated so thoroughly that no legacy fragment survives, yet holding a stale
  site the pattern was too narrow to name, is not caught — which is why `check-state.sh`'s fifteen
  sites are enumerated by code fragment in the plan rather than trusted to the detector.
- **The dangerous sites carry no `.harness/features/` literal at all**, and units 4 through 7 face
  the same shape. Three of this feature's own findings were of that class: a fixed climb of `..`, a
  comma-joined path tuple, a glob over a root variable. A literal sweep cannot see them and neither
  can the detector, by the residual bound above. **The sweep that finds them is for path-depth
  arithmetic, and it is run alongside the literal one, not instead of it.** This feature runs it
  once and commits the command, the hits and each hit's disposition to its boundary note, so the
  next unit inherits a worked example rather than rediscovering the class.

## Approval

status: approved
approved_by: operator (Mike Ruangutai), via main session
date: 2026-08-14
notes: Q1 unit-9 override confirmed; Q2 tests.yml main-session-direct; Q3 count-based verify
  clauses added (proven red pre-build); Q8 anchors taken including the compelled correction of
  the already-false 8->19 figure. Rulings at notes/answers-2026-08-14-signature.md.
