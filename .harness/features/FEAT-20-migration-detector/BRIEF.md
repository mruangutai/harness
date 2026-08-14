# BRIEF — FEAT-20-migration-detector

Unit 0 of the multi-repo control-plane sequence (map #336, "#339 resolution"). The detector lands
before anything moves.

## Problem

Nothing in the tree can tell a half-migrated layout from a healthy one, and the two mechanisms that
look like they would are the two that go quiet. `check-state.sh` discovers features with fixed-depth
globs — `glob(join(H, "features", "*", …))`, 15 sites at `88b1182` — so inserting a repository
segment makes every one match nothing, every invariant evaluate over an empty set, and the gate that
`/harness` entry runs report a healthy tree. `check-domain.sh`'s four shape regexes and its
`SWEEP_GLOBS` fail the same way, silently, while still advancing the shape-sweep stamp. CI's
plan-route gate is defeated by exactly the shape a repo segment produces — `examined > 0, plans == 0`,
a case its own comment names as uncaught (issue #344). Units 3 through 7 each move roughly 800 code
sites across two migrations; every intermediate state in that sequence would hide its own mistakes.

## Goal

Ship one detector that fails loud on a half-migrated tree, before any file moves. It passes on the
tree as it stands today, passes on a fully migrated tree, passes on the intermediate states the
sequence sanctions, and reddens on the mixtures that indicate a migration went half-done. It is
proven able to redden by perturbation before it lands, because a check that cannot fail is issue
#148 — and shipping one inside the fix for it would be that defect twice.

## Scope — the detector only

No file moves, no layout change, no config split. Those are units 3 through 7 and are later
features. The only files this feature changes are the detector, its tests, its two call sites, the
test registration, and the decision record.

## Requirements

- REQ-01: A mixture within one coupled surface is reported as a failure, loudly, with the
  disagreeing surface and reader named.
- REQ-02: The tree as it stands today, all-legacy, passes.
- REQ-03: A fully migrated tree passes.
- REQ-04: The intermediate states the sequence sanctions — features migrated with docs not, docs
  migrated with features not — pass.
- REQ-05: A state the detector cannot judge is reported as cannot-verify, distinct from clean, at
  both call sites.
- REQ-06: The detector runs at session entry and in the required CI job, without anyone choosing to
  invoke it.
- REQ-07: Each failure mode has a sandboxed fixture that shows the detector actually reddening on
  it, and the green cases have fixtures too.
- REQ-08: A tree that is not a harness control-plane checkout — an onboarded product repository, or
  a test fixture — is not reported as broken, and is not silently counted as clean either.

## Decisions taken here, restated where they are signed

These four — D-01, D-02, D-03 and D-04 — are rulings this brief asks you to approve. `plan.yaml`'s `decisions:` block is their
formal record.

### D-01 — Failure is judged per coupled surface, over a closed reader set

Two surfaces, judged independently:

**FEATURES** — disk evidence is `.harness/features/*/feature.json` (legacy) against
`.harness/*/features/*/feature.json` (migrated). Coupled readers are exactly unit 3's atomic
cluster: `team-config.yaml`'s write grants, `check-domain.sh`'s `SWEEP_GLOBS` and its four shape
regexes, `check-plan-routes.py`'s discovery join, and `check-state.sh`'s discovery globs.

**DOCS** — disk evidence is `docs/harness/SPEC.md` against `.harness/*/docs/SPEC.md`. Coupled
readers are exactly unit 4's atomic trio: `factory_config._PROBE`,
`harness_boundary.HARNESS_CONTROL_PLANE`, and `gen-decisions-index.DOCS_DIR`.

**Deliberately excluded from both sets**: `gh-sync.py:729`, `branch-create-gate.sh:77`,
`validate-feature-json.py`, `factory_claim.py:43`, the gitignore snippet, and all prose. Map #336
places them in unit 9, landing "anytime". A detector that read them would redden a state the
sequence sanctions.

The alternative — one tree-wide notion of "half migrated" — reddens on features-moved-docs-not,
which map #336 explicitly permits: unit 4 has no ordering tie to unit 3.

### D-02 — The detector is gate code, so building it is main-session-direct

`check-state.sh` computes an invariant verdict from the detector's return value. FEAT-18 ruled the
same shape for `gh_board.py` — granted to `harness-backend-dev` and `harness-dev-ops` by
`--resolve`, and still main-session-direct as a DEC-174 carve-out by content, on FEAT-17's
`harness_boundary.py` precedent. This feature follows it: the module, its unit test,
`check-state.sh`, `test-check-state.py` and the runner registration are all main-session-direct.

The cost, stated rather than argued away: two of the four tasks, and five of the eight files this
feature touches, are built by hand rather than dispatched. The alternative — invoking the detector only from CI to keep a team lane — was rejected
because session entry is the higher-value call site, and `check-state.sh` going quiet is the
defect this feature exists to prevent.

The one team task is the CI step in `.github/workflows/tests.yml`, which `--resolve` grants to
`harness-dev-ops` and which is not one of DEC-174's four named scripts. Recorded because a reader
may assume every gate-adjacent file is a carve-out.

### D-03 — A reader matching neither form is cannot-verify, never clean

The migrated form of each reader is anticipated, not observed; nothing has moved yet. So the form
table is data, one pair per reader, and units 3 and 4 update their own rows inside their one atomic
commit — and are not done until the detector exits 0 on their migrated tree inside that same
commit, which is the only thing that turns an anticipated form into an observed one. A reader file
matching neither form exits 2, which both call sites treat as a violation. Degrading to clean is how
a check passes forever.

**Because the table is data, "clean" requires a non-empty reader set.** "Every reader carries the
same form as the evidence" is *vacuously true* over an empty set, so a later edit that drops a
surface's rows would make this detector report clean forever — issue #148 reappearing inside the
verdict logic of the feature built to eliminate it. A surface with no rows is cannot-verify. The two
surfaces are also a fixed enum declared independently of the table, so a surface can never be
*skipped* before its verdict is computed; a declared surface that goes unjudged is exactly as loud
as one judged cannot-verify.

**Every named reader carries the form it matched** — `[legacy]`, `[migrated]`, `[both]`,
`[neither]` or `[unreadable]` — at both call sites. A reader carrying the legacy form on a migrated
tree needs *finishing*; one carrying the migrated form on a legacy tree needs *reverting*. Those are
opposite remedies, and without the form they are the same line of output.

**Each legacy pattern is the weakest fragment every stale site necessarily contains**, audited
against the real file before the row is written — not the shape of the commonest site. This is not
a style note. The first draft of this plan specified `check-state.sh`'s legacy form with a trailing
wildcard segment; two of that file's fifteen discovery sites carry none
(`os.listdir(os.path.join(H, "features"))` and `os.path.join(H, "features", _f, "feature.json")`),
so a unit-3 pass that updated the thirteen and missed those two would have left the file matching
only the migrated form — **CLEAN, with two broken discovery sites**, which is this feature's own
defect committed inside the fix for it.

**The residual bound, stated where you sign it:** the detector proves per-file **form agreement**,
never per-site **completeness**. It answers whether a file speaks one layout language and the same
one its evidence speaks; it cannot answer whether every site inside that file was updated. A file
migrated so completely that no fragment of the legacy pattern survives, yet still holding a stale
site the pattern was too narrow to name, is not caught. That is why the pattern rule above is a rule
and why later units owe the same-commit acceptance clause. The bound is carried in the module
comment and in the decision entry, so units 3 through 7 read it before they lean on it.

### D-04 — Applicability is decided by one positive control, before any surface is judged

Every coupled reader lives in the harness control plane. `check-state.sh` also runs at session entry
inside onboarded product repositories, and `test-check-state.py`'s existing fixtures are bare
`.harness/` skeletons — neither has any reader file at all. Judged by D-03 alone both would exit 2,
so a healthy product repo and every existing test case would redden the moment this lands.

So: the detector first asks whether the scanned root is a harness control-plane checkout, by the
presence of `.claude/skills/harness/bin/check-state.sh`. If it is not, the whole scan is reported as
not applicable, the examined counts are zero, and the exit is 0.

**What bounds that branch is a unit case, not the CI step, and the difference is worth your
attention.** The branch's danger is that a renamed or moved marker makes the harness tree itself
"not applicable" and the detector goes silent everywhere at once. The control is T-01 **case 1**: it
scans the real repository root and asserts non-zero examined counts, so that failure reddens the
required unit suite. The marker is also invariant across the migration it gates —
`.claude/skills/harness/bin/**` moves in no unit of map #336 — and presence of the marker is a
different property from agreement of the forms, so the control is sound rather than circular.

The CI step's zero-count assertion is a second signal, deliberately **not** presented as the
guarantee: DEC-183 records that whole CI step class as unguarded by owner decision — *nothing
protects the gate, settled* — and no `.py` in the tree reads `.github/workflows/tests.yml` at
`88b1182`, so a bound resting there is one PR deep. Session entry is genuinely unbounded and silent
on "not applicable" by design (SC-12 mandates that silence); case 1 is what keeps the harness tree
from reaching that branch unnoticed.

## Success Criteria

- SC-01: On the repository as it stands, the detector exits 0 and prints how many feature
  directories and reader files it examined, both non-zero.
  verify: automated      evidence: unit
- SC-02: On a fixture whose feature directories are split across the legacy root and a repository
  root, the detector exits 1 and names the FEATURES surface.
  verify: automated      evidence: unit
- SC-03: On a fixture where every feature directory sits under a repository root but at least one
  coupled FEATURES reader still carries the legacy form, the detector exits 1 and names that reader
  file.
  verify: automated      evidence: unit
- SC-04: On a fixture where the docs surface is split the same two ways — evidence split, and
  evidence-versus-reader disagreement — the detector exits 1 and names the DOCS surface.
  verify: automated      evidence: unit
- SC-05: On a fully migrated fixture, with both surfaces moved and every coupled reader carrying the
  migrated form, the detector exits 0.
  verify: automated      evidence: unit
- SC-06: On a fixture where the FEATURES surface is fully migrated and the DOCS surface is fully
  legacy, and on its mirror image, the detector exits 0. The sanctioned intermediate states are not
  failures.
  verify: automated      evidence: unit
- SC-07: On a fixture where a coupled reader file carries neither form, the detector exits 2 and
  says which file it could not judge. Exit 2 is distinct from both 0 and 1 in the same test.
  verify: automated      evidence: unit
- SC-08: `check-state.sh` reports a violation on a tree the detector reddens and on a tree the
  detector cannot judge, and reports nothing on a clean one — proven against fixtures, not against
  the live tree alone.
  verify: automated      evidence: integration
- SC-09: The required CI job runs the detector, fails the step when the detector exits 1 or 2, and
  fails the step when the detector's own summary or examined-count line is missing.
  verify: inspection
- SC-10: No file outside the detector, its tests, its two call sites, the test registration and the
  decision record is modified by this feature. Nothing moves.
  verify: inspection
- SC-11: Every fixture is built and torn down inside a temporary directory by the test itself; no
  test writes into the repository tree.
  verify: inspection
- SC-12: On a fixture holding no harness control-plane marker, the detector exits 0, says the scan
  was not applicable, and reports zero examined counts; and `check-state.sh` reports no INV-27
  finding for it. Paired in the same suite with a case that scans the real repository root and
  asserts non-zero counts, so this branch cannot go silent inside harness without reddening the
  unit suite.
  verify: automated      evidence: unit
- SC-13: On a fixture where one surface's reader rows are empty while its disk evidence shows
  exactly one shape, the detector reports that surface cannot-verify and exits 2 — it does not
  report clean, and it does not omit the surface from its report. The surface count in the summary
  line on the real repository accounts for every declared surface.
  verify: automated      evidence: unit
- SC-14: In the detector's own output, each reader it names carries the form it matched, so that a
  reader needing to be finished and one needing to be reverted are distinguishable — proven on both
  directions in the same suite, not on one.
  verify: automated      evidence: unit
- SC-15: `check-state.sh`'s INV-27 finding carries the same form alongside each reader path it
  names, and ends with an action the reader can take.
  verify: automated      evidence: integration

## Verification gaps

None. Both kinds this brief rests on are `active` in `.harness/harness.json`: `unit` matches
`.claude/skills/harness/bin/test-*.py`, and `integration` names `test-check-state.py` explicitly in
its detect list. No SC rests on `component`, `ui`, `eval` or `typecheck`, all of which are
`unresolved` with a null `cmd`.

## Constraints

- Detector only. No file moves, no layout change, no config split (units 3–7, later features).
- Every step touching `check-domain.sh`, `bash-write-guard.sh`, `validate-digest.py` or
  `check-state.sh` is declared `main-session-direct` and never dispatched (DEC-174).
- Fixtures are sandboxed temporary trees, built and torn down by the test. Fixture creation is not
  a layout change and must not be read as one.
- The check asserts which FORMS appear per reader file. It never asserts a site count and never
  anchors on a line number: the glob-site count was 13 in the dispatch, 14 in map #336 and 15 at
  `88b1182`, and all three readings were made in good faith.

## Approval

status: approved
approved_by: operator (Mike Ruangutai), via main session
date: 2026-08-14
notes: Q1 accepted (unguarded CI step, consistent with DEC-183); Q2 SC-13/14/15 kept; Q5 D-04 signed as designed (single marker, SC-12 silence in product repos).
