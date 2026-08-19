# Research — FEAT-25 · the correct feature root for factory_claim.py

**Observed at `ada8e99`** (`git rev-parse --short HEAD`), working tree of `/Users/molchairuangutai/GitHub/harness`.

## BLUF

**The correct root today is `<harness_root()>/.harness/harness/features` — a FIXED `harness`
segment.** Not because `harness` is the general answer, but because three separate facts each
independently forbid a derived one at module scope, and because every plan the gate can reach
today lives under that path. The residual — a kaya-lane feature would live at
`.harness/kaya-ai/features/` and a fixed root cannot reach it — is real, named below, and belongs
to unit 7, not here.

**The conditional stop does NOT fire.** The answer does not depend on unit 5's config split. See
"Stop condition, disposed" below.

## The defect, reproduced

Live probe, `python3` from `.claude/skills/harness/bin`:

```
FEATURES_ROOT = /Users/molchairuangutai/GitHub/harness/.harness/features   exists: False
alt           = /Users/molchairuangutai/GitHub/harness/.harness/harness/features  exists: True
_BlockerCache(FEATURES_ROOT).task("FEAT-24-config-responsibility-split", "T-01") -> None
_BlockerCache(alt).task(...)                                                     -> T-01
```

`factory_claim.py:43` is the single stale site. `_BlockerCache.task` at `:100-106` swallows the
unreadable plan as `plan = None`, `:108-109` returns `None`, `_blocker_gate:140-142` returns
`("edge_i", task_id)` — blocking. Nothing is claimed. Fails CLOSED (settled; not re-derived).

## Q1 — whose `plan.yaml` does `_BlockerCache` read?

**The reader's root must equal the writer's, and the writer has no root constant at all.**

- `factory_decompose.py` takes the feature directory as an argv positional
  (`factory_decompose.py:4`, "Command line: factory_decompose.py <feature-dir> ..."). It joins
  `feature.json` and `plan.yaml` onto that given dir (`:96`, `:302`) and writes `factory.issues`
  into it (`:390`, `:479`). It never derives a features root. So the writer's root is wherever the
  operator's feature directory actually is.
- The integration suite makes the identity explicit: `test-factory-integration.py:670-675` and
  `:1039-1041` build `<root>/.harness/features/<feat>` and pass that same `feat_dir` to
  `decompose`, with the comment at `:670-671` saying it "lives exactly where factory_claim's
  (import-time) FEATURES_ROOT will look for it". Writer dir and reader constant are hand-kept in
  agreement, and the fixture agrees with the *stale* constant — which is why the suite is green
  over a broken tool.
- On disk, every feature directory a `feature:` label can name lives under
  `.harness/harness/features/` (unit 3, `d033b9d`). The probe above confirms a real plan resolves
  there and nowhere else.

**Whose DAG at unit 8:** `factory_decompose.py:278` attaches `feature:<feat_id>` to every issue it
creates and `:360` to the parent, and issue titles carry `T-NN` (`_TASK_ID_RE`,
`factory_claim.py:45`). So there is no decomposed issue on any repository that bypasses the gate
through D-09's tolerant read. A kaya issue created by `decompose` WILL be gated, and its feature
directory is whatever directory the operator handed `decompose`.

## Q2 — does `factory_config` already expose a per-repository segment derivation?

**Yes, exactly one — and it cannot serve a module-level constant.**

`factory_config.workspace_path(fleet, repo_name)` at `:222-227` is "the one place that derivation
exists": `repo_name.split("/", 1)[-1]` gives the post-owner name (`mruangutai/kaya-ai` ->
`kaya-ai`), joined onto `fleet["workspace_root"]`.

What it does NOT give a module global:

1. **It needs two runtime arguments.** `fleet` comes from `load_fleet()`, a file read; `repo_name`
   comes from the board item being examined (`factory_claim.py:279`). Neither exists at import
   time, and `factory_config.py:20-21` states importing the module reads no fleet file.
2. **It joins onto `workspace_root`, not onto `harness_root()`.** It answers "where is the
   checkout", a different question from "where is the control-plane feature tree".
3. **It cannot produce `harness` at all.** `mruangutai/harness` is deliberately absent from
   `.harness/factory/fleet.yaml` (its own comment block; pinned by
   `test-no-distribution.py:160-163`, `case3_absence_harness_is_not_a_fleet_member`). A
   fleet-derived segment rule therefore has no input that yields the harness's own segment — the
   one segment every plan on disk today actually sits under.

`harness_root()` at `:37-49` is the other half and is already correct: three-tier resolution,
`CLAUDE_PROJECT_DIR` when `.harness/harness/docs/SPEC.md` is readable under it, else derived from
the file's own location. Nothing about the fix touches it.

## Q3 — fixed segment or derived? The answer, and its named residual

**Fixed.** The forcing constraints, in order of strength:

1. No derived rule yields `harness`. The one derivation that exists (fact 3 above) has no input
   that produces the segment: `mruangutai/harness` is deliberately absent from
   `.harness/factory/fleet.yaml`, pinned by `test-no-distribution.py:160-163`
   (`case3_absence_harness_is_not_a_fleet_member`), while every plan on disk sits under exactly
   that segment. Any derived rule would have to special-case the harness itself, i.e. hard-code
   the literal anyway.
2. `FEATURES_ROOT` is a single module global (`factory_claim.py:41-43`) and `_BlockerCache` is
   constructed once per run from it (`:296`) and keyed by feature alone (`:100`, `:119`). A
   per-repository root requires either a per-repo cache key or a root-deriving callable — a
   signature change to `_BlockerCache`, which is general per-repository resolution and unit 7's
   surface (#495).
3. No new `factory_config` API is available to this feature: `factory_config.py` is FEAT-24's T-02
   surface.

The literal is therefore consumed directly, matching the shape every other migrated Python reader
uses (`layout_migration.py:88-89` states the migrated form as
`os.path.join("\.harness", <segment>, "features")`).

### The residual, stated (not deferred silently)

Under DC-4/DC-7 of #498, a kaya feature's directory is `.harness/kaya-ai/features/<FEAT>`. A fixed
`harness` root cannot read it, so `_blocker_gate` would return the no-plan reason and **kaya's
decomposed, `feature:`-labelled issues would still not be claimable**. Since `decompose` labels
every issue it creates, D-09's tolerant read does not rescue this.

Consequence for the operator: #498's table has unit 8 depending on units 5 and **9a**, but not on
unit 7. If unit 8's proof runs against a kaya feature that was decomposed from a plan directory,
9a alone is not sufficient. Two escapes exist and both are the operator's to pick, not the
planner's: run unit 8's first proof against an issue with no `feature:` label (ungated), or place
kaya's first feature directory under `.harness/harness/features/` for the proof and let unit 7
move it. **Non-blocking for this plan** — it changes nothing about what the correct root is today.

## Stop condition, disposed — it does not fire

The root answer does not depend on unit 5's config split (FEAT-24, #493):

- #493's own "Out of scope" list names "Product boards and `factory_claim.py`".
- FEAT-24's open decisions concern where a *product's `harness.json`* lives; D-03 in
  `.harness/harness/features/FEAT-24-config-responsibility-split/plan.yaml` settles it as a remote
  read at the product's default branch, never a checkout. `harness.json` is not read by
  `_BlockerCache`, which reads only `plan.yaml` and `feature.json` under the features root.
- Nothing in FEAT-24's ten decisions moves, renames or re-segments the features tree.

## The diagnostic

`factory_claim.py:162-168`'s `edge_i` text names the issue title and the plan task. The cause here
is an absent directory. `_blocker_gate:140-142` collapses three distinguishable states into one:
(a) the features root does not exist, (b) the feature's `plan.yaml` is absent or unparseable,
(c) the plan loaded and contains no task with that id — the only true edge (i). Splitting (a) and
(b) out with a message naming the attempted absolute path is the fix; stderr only
(`factory_claim.py:12-14`).

## The verification trap

`FEATURES_ROOT` is documented as monkeypatchable (`:41-42`) and **every existing test patches it**:
`test-factory-claim.py:342-343` and `:360` save/patch/restore around every case;
`test-factory-integration.py:25-31` redirects the root through `CLAUDE_PROJECT_DIR` and then plants
its fixture at the stale path. That is precisely why a green suite sat over a dead tool. A new test
that patches the root passes against both broken and fixed code.

The discriminating assertion is on the **unpatched module default**, at module scope before any
case's patch machinery: `claim.FEATURES_ROOT == os.path.join(fc.harness_root(), ".harness",
"harness", "features")` and `os.path.isdir(claim.FEATURES_ROOT)`. The `isdir` half is red today
(probe above) and is a real positive control, since the harness's own features tree exists at
`ada8e99`.

## DEC-194 and the detector

`layout_migration.py:42-44` explicitly excludes `factory_claim.py` from every surface, because
"Map #336 lands them anytime under unit 9". This unit is 9a. Leaving it excluded leaves a coupled
reader that DEC-194 classifies as unverifiable rather than clean. Adding the row closes it.

Pattern-rule audit, run against the real file at `ada8e99` (the table header at
`layout_migration.py:20-25` requires it per row):

```
grep -nE '"\.harness", "features"' factory_claim.py            -> 43 (one site)
grep -nEi 'harness.{0,30}features|features.{0,30}harness' ...  -> 43 only (broader adds nothing)
grep -nE '"\.harness", [^,)]+, "features"' factory_claim.py    -> no match today
  ... same pattern against the fixed line                      -> matches
  legacy pattern against the fixed line                        -> no match (exit 1)
```

So the code-shaped row is exact, adds no prose lines, and does not hold the file MIXED after the
fix. The row's `migrated` pattern contains an unbalanced `)`, so it needs a trailing
`# balance: (` comment — the precedent is `layout_migration.py:89`, and the reason is
`test-check-plan-routes.py` case_20's paren-depth line joiner (`layout_migration.py:81-86`).

## Lane resolution — `check-domain.sh --resolve`, at `ada8e99`

All five surfaces returned `harness-backend-dev`. None is one of the four DEC-174 carve-out
scripts, so every task dispatches normally.

## Open questions carried out

- **Q1 (non-blocking)** — FEAT-24 also edits `.claude/skills/harness/bin/test-factory-claim.py`
  (its `plan.yaml:42` lanes row) and adds one case to it (its T-03 intent, item 1b, at `:560-574`);
  it also edits `test-factory-integration.py`. Both plans are pending, so nothing is blocked, but
  the merges need sequencing.
- **Q2 (non-blocking)** — the unit-8 sequencing gap in "The residual" above.
