# Goal-check — BUG-1290 factory claim resolves the feature repository root

**All nine success criteria are MET, every clause of every multi-clause criterion included.** Graded
against the delivered code at the pinned `review_sha` 76e26386 (HEAD e93a59c7 adds notes only; the
bug's own source diff is exactly the plan's nine files — `git diff --stat 4e52d2e3 76e26386`). Every
verdict below rests on a command I ran in this worktree, not on a prior agent's report. One advisory
test-only residue, no gating gap, no emergent criterion.

Commands cross-checked verbatim against plan.yaml `:420` (T-03), `:491-507` (T-04), `:566` (T-05) —
no mismatch. All runs prefixed `env -u HARNESS_AGENT_TYPE`.

## Suite-level evidence (run by me)

| Command | Result |
|---|---|
| `python3 tests/unit/test-factory-claim.py` | exit 0, `124/124 checks passed.` |
| `python3 tests/integration/test-factory-integration.py` | exit 0, `131/131 checks passed.` (9.1s) |
| `python3 tests/integration/test-feature-worktree.py` | exit 0, `PASS test-feature-worktree.py` |
| `python3 -c "... 'FEATURES_ROOT' in factory_claim.py ..."` | exit 0 (absent) |
| `python3 tests/integration/test-layout-migration.py` | exit 0, `ok - case 22: real root's harness/features surface is CLEAN with migrated evidence` |
| T-04 reader-row probe (verbatim) | `READER ROW PROBE: ok 5 {...factory_config.py: 'migrated'...}` exit 0 |
| `python3 tests/unit/test-factory-claim-mutation.py` | `BASELINE 3/3 ok` / `MUTANT ACTIVE` / `MUTATION PROOF: 3/3 cases reddened`, verify rc 0 |
| `python3 tests/unit/test-no-distribution.py` | `ALL PASS` (incl. `case3_absence_harness_is_not_a_fleet_member`) |

## Per-criterion verdicts

- **SC-01 MET** — `ok    BUG-1290 5a: served non-harness repository reaches its own segment's blocker
  verdict, not no_plan`. Case asserts `"unresolvable blocker" in err` AND `"no plan could be read" not
  in err` (pinned test `:1170-1173`).
- **SC-02 MET, both clauses.** (a) per-plan verdicts: `ok BUG-1290 5b`, asserting claimed issue 952
  (harness segment, T-77 clear) while 951 (kaya-ai, T-77 → unresolvable T-88) is refused. (b) no cache
  bleed: I did not take the case name on trust — I ran an in-process mutant probe
  (`/tmp/bug1290_cacheprobe.py`) re-keying `_BlockerCache._plan` on feature alone: `M1
  plan-cache-bleed: {5a: ok, 5b: FAIL, 5c: ok}`. 5b genuinely discriminates the cached-task clause.
- **SC-03 MET, both clauses** — `ok BUG-1290 5c`. The refusal is the existing `no_plan` reason
  (`"no plan could be read" in err`) and the asserted string is the resolved absolute path built with
  the repository's own segment `zzz-missing-segment` (pinned test `:1219-1225`).
- **SC-04 MET** — `ok BUG-1290 5d`; the case calls the *production* `fc.features_root("owner/harness")`
  unpatched and compares to `<root>/.harness/harness/features`. Fixture-only by DEC-174: the live
  `.harness/factory/fleet.yaml` at the pin names only `mruangutai/kaya-ai` and
  `mruangutai/harness-factory-smoke`, and no task touched it (fleet.yaml is absent from the diff stat).
- **SC-05 MET, both clauses** — `ok BUG-1290 5e` (hasattr assertion, pinned `:1245`). The two
  module-scope cases present at `eb9d044e:tests/unit/test-factory-claim.py:58-68` ("the unpatched
  FEATURES_ROOT default is the migrated harness features tree" / "…names a directory that exists") are
  **gone, not re-pinned or weakened**: `git show 76e26386:tests/unit/test-factory-claim.py | grep -n
  FEATURES_ROOT` returns only lines 1241/1243/1245/1246 — the 5e hasattr case and its comment. The
  docstring sentence was reworded, not deleted wholesale.
- **SC-06 MET, both clauses** — `ok BUG-1290 5f`. I re-measured D-03's regex myself over the pinned
  blobs rather than trusting the case: `factory_claim.py 0`, `feature-worktree.py 0`,
  `factory_config.py 1` — the single hit is `factory_config.py:387 return repo_name.split("/", 1)[-1]`
  inside `segment_of`. Reach: `feature-worktree.py:86 segment = factory_config.segment_of(repo)`,
  `factory_config.py:403 name = segment_of(repo_name)` (workspace_path), `factory_claim.py:95/119/137
  factory_config.features_root(repo)` → `features_root` → `segment_of`. All three reach the segment
  through that one definition, which is SC-06's wording.
- **SC-07 MET** — named lines, not the exit code (the file has one global FAILS counter):
  `ok    (F) claim exits 0` and `ok    (H) claim against the two-board fleet exits 0`, zero FAIL lines.
  Non-vacuous: both fixtures build `os.path.join(root, ".harness", REPO.split("/",1)[-1], "features",
  feat)` with `REPO = "acme/widget"` (pinned `:883`, `:1247`) — a non-`harness` segment.
- **SC-08 MET** — the two marker lines, never the exit code: `BASELINE 3/3 ok` and `MUTATION PROOF: 3/3
  cases reddened`, with `MUTANT ACTIVE` and `FAIL BUG-1290 5a/5b/5c` between them.
- **SC-09 MET, all clauses** — suite (`case 22 ok`) **plus** the probe I ran verbatim: `READER ROW
  PROBE: ok 5`, dict shows five features readers all `migrated`, `factory_config.py` present and
  `migrated`, `factory_claim.py` absent, legacy pattern matching the legacy control and *not* the
  migrated control, migrated pattern matching the migrated control.

## Advisory residue — delivered, unproven (not gating)

The `_issue_maps` half of D-02/REQ-02 is **delivered** (`factory_claim.py:135` keys on `(repo,
feature)`) but **no case can see it**: my probe M2, re-keying `issue_number` on feature alone, reddened
nothing — `M2 issue-map-bleed: {5a: ok, 5b: ok, 5c: ok}` — because both 5b fixtures carry
`{"factory": {"issues": {}}}`. Test-only gap, owner **T-01** (fixture), cost ~2 lines: give one segment
a non-empty issues map. SC-02's own words name the "cached task", which is proven, so this is a note
for the operator, not an unmet criterion.

## REQ-05 wording — a record question for the operator

**My judgement: REQ-05 is MET in intent, and its prose is inaccurate about the code that satisfies it.**
It says the rule is "called by `factory_claim.py`, `feature-worktree.py:resolve_repo` and
`factory_config.workspace_path`". Measured: `segment_of`'s *direct* callers are `features_root`,
`workspace_path` and `feature-worktree.py:86`; `factory_claim.py` reaches the segment **transitively**
through `features_root`. That is exactly the D-01 split the operator signed knowingly, and REQ-05's
second clause (no second owner-stripping derivation in those three files) is measured true (0/0/1).
Recommendation: record a one-line wording correction — "reaches, directly or through `features_root`" —
as an operator ruling on the approved artifact. I edited nothing; the operator decides.

## Disclosures for the ship briefing (neither is an unmet criterion)

1. **REQ-04/SC-04 are fixture-only by DEC-174.** `mruangutai/harness` is deliberately absent from the
   live fleet and its absence is asserted by `tests/unit/test-no-distribution.py` case
   `case3_absence_harness_is_not_a_fleet_member` (ran: ALL PASS). No task added it.
2. **A live claim from `main` still reports `no_plan` for FEAT-04**, because that feature tree exists
   only in the FEAT-04 worktree. BRIEF `## Constraints:128-130` discloses this; landing the tree is
   FEAT-04's work, not this bug's.

## Emergent criteria

**None.** The two surfaces the change forced — the layout reader-row move and the `workspace_path`
rewrite — are already owned by SC-09 and SC-06 respectively; nothing the delivered change makes
necessary sits outside BRIEF.md's nine criteria.
