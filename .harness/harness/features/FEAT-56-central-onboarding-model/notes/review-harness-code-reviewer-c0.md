# Code review — FEAT-56-central-onboarding-model — c0

Reviewed: `4b5dbb23..6f34e289` (all files read via `git show 6f34e289:<path>`; working tree HEAD
1e65f995 differs from the pin only by the record commit touching `feature.json` and
`notes/handoff-build.md` — confirmed via `git diff 6f34e289..HEAD`, so plain reads of code paths
match the pin). VERDICT: **PASS** (no must_fix, severity_max = med).

## Stage 1 — spec compliance

### SC-01 — `harness-init/SKILL.md` — **met**

Three elements, in order, one paragraph (`SKILL.md:8-12`):
- default_branch: `SKILL.md:8-9` — "land that repository's own `.harness/harness.json` on its
  `default_branch`"
- fleet.yaml: `SKILL.md:9-10` — "register it in `.harness/factory/fleet.yaml`"
- central tree: `SKILL.md:10` — "then create its central per-segment tree at
  `<control-plane>/.harness/<segment>/`"

No match for `templates/team-config.yaml` (confirmed by direct read of the full 414-line blob;
the only nearby text is `SKILL.md:184`, "instantiate its own `.harness/harness.json` and
`.harness/team-config.yaml` from the templates" — a prose reference, not the literal path).

**Would a follower actually do the right thing?** Read step 2 end to end (`SKILL.md:153-185`):
land config → register → **prove reachable** (`--check-product-configs --repo`) → create central
tree. This is D-04's load-bearing order and it holds.

**Lead 1 (write-access gap) — CONFIRMED, reported as a finding, not gating SC-01.**
`SKILL.md:160-163`: "Land `.harness/harness.json` on that repository's `default_branch`. Harness
has no write route into a product repository... The main session asks the operator for this
commit or PR; do not continue until it is on the default branch." This fails **closed** (nothing
proceeds until the file lands), so it never produces wrong behaviour — but it names no path for
the case where the operator genuinely cannot push (no write access, protected branch requiring
review, a fork). The Preflight section models this exact shape elsewhere ("a denial there is a
stop, not a detour") but step 2 does not restate it. See finding F-1.

**Lead 2 (REQ-05 timing) — dismissed, holds correctly.** `SKILL.md:164-175` (step 2c-2d): the
`--check-product-configs --repo` run sits immediately after fleet registration (2c) and strictly
before central-tree creation (2e) and every later step (interview, dev-ops, manifest, BRIEF,
approval, board, design, final verify). That satisfies D-04 — the member is proved reachable
before anything else in the procedure runs, and step 9 (`SKILL.md:345-355`) repeats the check
fleet-wide with no `--repo` as a second line of defence.

### SC-03 — six executable sites — **met**

One citation each, read individually at the pin:

1. `.claude/skills/harness/bin/check-instruction-paths.py:12-15` — comment: "harness-init is
   excluded here because of the anchor rule, not because of ownership: the anchor rule would
   rewrite its deliberately clone-relative core.hooksPath value" plus the trailing inline comment
   on the tuple entry. Matches the code around it: `_skill_docs` (same file, ~line 28-31) excludes
   `MAIN_SESSION_ONLY` names from the SKILL.md anchor sweep, which is exactly what the rationale
   claims.
2. `.claude/skills/harness/bin/check-state.sh:111` — "harness: no .harness/ here — this clone is
   not an onboarded harness control plane. Run /harness-init in the control-plane clone." The
   other three remedies also correctly name the clone (`:287`, `:407` INV-32 panel_era_start, and
   `:2434-2436` INV-31 rationale) — checked individually, not by a file-global grep.
3. `.claude/skills/harness/bin/check-domain.sh:384-386` — the fail-open message: "no {manifest} —
   enforcement OFF. That path is the control plane's own manifest; a product repository never
   carries one. Run /harness-init in the control-plane clone." Confirmed unchanged around it:
   `_run_domain = False` (a flag, never an exit — T-02's own constraint held).
4. `.claude/skills/harness/bin/upgrade-config.py:4-6` — docstring: "This upgrades the
   control-plane clone's own .harness/harness.json. For a fleet member, it upgrades that member's
   harness.json in a checkout, which must then be committed to the repository's default branch to
   be read at all." Both remedies also corrected (`:191` "this control-plane clone is not
   initialised"; `:233` "a team-config.yaml exists only in the control plane, so this message is
   about this clone").
5. `.claude/skills/harness/bin/gh-sync.py:255-256` — "github.repo is not pinned in this project's
   harness.json; for a fleet member, that file lives in the member's own repository on its default
   branch." `skip()` and the surrounding control flow are byte-for-byte unchanged around it.
6. `.claude/skills/harness/bin/layout_migration.py:122` — "a copy or worktree of the control plane
   carries every reader file, and only the control plane carries the fleet declaration." Matches
   the code: `MARKER = .harness/factory/fleet.yaml` (`:131`) is exactly the file only the control
   plane carries, so the applicability rationale is literally true of the mechanism beside it.

All six read and cited individually; no file was skipped.

### Stage 1b — cross-file consistency sweep

Compared: the "route to /harness-init" trigger condition across `.claude/commands/harness.md`,
`.claude/commands/harness-plan.md`, `.harness/README.md`, `.harness/harness/docs/SPEC.md`,
`.harness/harness/docs/BUILD.md`, `README.md`, `.harness/harness/docs/DECISIONS.md` +
`DECISIONS-INDEX.md`, `org.html`; plus a repo-wide grep (not diff-scoped) for stale per-product
install phrasing (`installs the whole bin`, `copies this to .harness/team-config`, `cp .*
templates/team-config.yaml`, `deploy.sh` as an install mechanism) across every `.md/.py/.sh/.yaml/
.json/.html` file outside `features/**` and the frozen fixture — **zero hits**, so no leftover
"copies .harness/ into the repo" clause survives anywhere live.

**One inconsistency found — second instance of the class the simplify pass already fixed once:**

- `.harness/harness/docs/SPEC.md:145` (the §2.2 routing-table row, edited by T-07):
  "not registered in `.harness/factory/fleet.yaml`, or its own `harness.json` not readable at its
  `default_branch`" — **states only TWO of the model's three elements**, silently dropping the
  central-tree condition.
- `.harness/README.md:83-85` (same "when is a repository not onboarded" question): "absent from
  `.harness/factory/fleet.yaml`, ... `harness.json` is not readable at its default branch, or ...
  no central tree at `<control-plane>/.harness/<segment>/`" — **three conditions**.
- `.claude/commands/harness.md:12-14` also carries the third (central-tree) condition, and
  `harness-plan.md:18-19` now correctly *defers* to harness.md's gate rather than repeating its
  own — that is the fold-in the simplify pass already performed (confirmed: no third condition is
  independently restated there, by design).

SPEC.md's own §3.3 (`SPEC.md:134-137`) states the three-part model correctly a few dozen lines
below its own §2.2 table — so this is not merely a doc-vs-doc drift but an **internal
inconsistency inside SPEC.md itself**. A reader who trusts the §2.2 table (the operational
"what do I do" surface) over the narrative prose in §3.3 will treat a fleet member with a landed
config but **no central per-segment tree** (e.g. onboarding was interrupted after step 2d and
before step 2e) as fully onboarded, and route away from `/harness-init` — straight into the same
unattributed-failure mode REQ-05 exists to close, just for the tree element instead of the config
element. Reported as **F-2**.

I compared 8 files/locations pairwise on this one condition-count axis (the axis the dispatch
named as already-drifted-once); no other pair among them disagreed.

## Stage 2 — code quality

### `factory_config.py` — `product_config_report` / `_check_product_configs` / CLI flag

Checked line-by-line against T-04's `intent:` block (plan.yaml):
- Placement: `product_config_report` sits immediately after `product_config`, before `board_for`
  (`factory_config.py:328`, `:378` respectively at pin) — ✓.
- Declaration order preserved (plain `for entry in fleet["repos"]:` loop, no reordering) — ✓.
- Dict keys exactly `{repo, ref, path, ok, detail}`, `path` = `_PRODUCT_CONFIG_PATH` (module
  constant, not a retyped literal) — ✓ (`factory_config.py:351`).
- `except FleetError` only; every other exception is unhandled inside the function and propagates
  — ✓ as written (see finding F-3 on what actually reaches this branch).
- CLI: single stdout `factory_cli.payload({declared, ok, unreachable, members})` emitted exactly
  once, before the per-member `factory_cli.fail(...)` stderr lines, before
  `sys.exit(factory_cli.EXIT_REFUSED)` gated on `unreachable_count or len(report) !=
  len(fleet["repos"])` — order and shape match the intent block verbatim.
- `--repo` resolves via `repo_entry`, so an undeclared name raises `FleetError`, caught only by
  the outer `factory_cli.run("config", _main, expected=(FleetError,))` trap (confirmed at the
  bottom of the file) — never inside `_main` or `_check_product_configs` — ✓.
- `--check-product-configs` wins over `--show` when both given, with the comment T-04 asked for
  present (`factory_config.py:441-445`, `:453-456`) — ✓.
- No `check-state.sh` change, with the required comment naming the board-audit precedent
  (`factory_config.py:448-452` docstring / `:472-477` argparse comment) — ✓.

**Fail-open hunt, empty-`repos` shape — assessed and dismissed.** `product_config_report` over an
empty `fleet["repos"]` would trivially report `declared=0, ok=0, unreachable=0` and exit 0
("vacuously all-ok" — the exact shape the dispatch named). This cannot occur in practice:
`load_fleet` (`factory_config.py:196-199`) raises `FleetError` on an empty or missing `repos` list
before any caller — CLI or test — can reach `product_config_report` with one. Every call site in
this diff goes through `load_fleet` first.

**Fail-open hunt, `--repo` narrowing the length check — assessed and dismissed, for a reason
worth recording.** With `--repo`, `fleet = dict(fleet, repos=[entry])`, so `len(report) ==
len(fleet["repos"])` trivially by construction — but this is true **with or without** `--repo`:
`product_config_report`'s loop has no path that skips an entry without appending one, so the
length-mismatch half of the exit condition is unreachable today regardless of narrowing. It is not
dead code masking a live gap — it is forward coverage against a future regression that adds a
skip-without-append branch — and it matches the intent block verbatim. No finding.

### Grading (`harness-code-risk-grading`, `code-grade.py --base 4b5dbb23 --head 6f34e289`)

All 10 changed/new functions PASS at their bar; nothing gated:
- `product_config_report` — cyclomatic 3, cognitive 3, ABC 9.7 → **grade 4** (bar 4, PASS)
- `_check_product_configs` — cyclomatic 8, cognitive 7, ABC 15.3 → **grade 4** (bar 4, PASS)
- test helpers (`check`, `run_main`, stubs, fixtures) — grades 4-5, all PASS at bar 3

`code_grade: pass`.

### `tests/unit/test-fleet-product-config.py`

Ran `env -u HARNESS_AGENT_TYPE python3 tests/unit/test-fleet-product-config.py` — **15/15 pass**,
matching the BRIEF's named case count.

No case asserts implementation over observable behaviour: (a)-(c) drive the real
`product_config`/`product_config_report` code paths (the stubs only replace the network boundary,
`factory_gh.file_at_ref`), the shape/order checks read the module's own `_PRODUCT_CONFIG_PATH`
constant (matching T-04's explicit "reuse the constant" requirement, not a disguised
implementation assertion), and the (e) cases exercise `_main()` end-to-end in-process.

**Finding F-3 (reasoned from source, not run — per instruction not to mutate a file in this
worktree).** The suite never distinguishes `except FleetError` from a hypothetically widened
`except Exception`. Every failure stub (`stub_first_gherror_second_ok` raising `GhError`,
`stub_first_not_json_second_ok` returning invalid JSON) triggers a failure that `product_config`
itself **already converts to `FleetError`** before it ever reaches `product_config_report`'s
try/except (`factory_config.py:300-321`, read at pin: `except GhError as e: raise FleetError(...)`,
`except json.JSONDecodeError: raise FleetError(...)`). No stub in this file ever raises, or lets
through, any exception type OTHER than `FleetError` — so a regression that widens
`product_config_report`'s `except FleetError:` to `except Exception:` would not change a single
line of this suite's output. Concrete failure scenario: a future edit widens the clause ("to be
safe"), a real bug in `product_config` (a `KeyError` on a malformed fleet entry, an `AttributeError`
from a typo) starts firing — under the current code it would crash loudly out to
`factory_cli.run`'s catch-all ("unexpected failure: ..."), which is the correct, loud behaviour;
under the widened clause it silently becomes an ordinary "config unreachable" entry for whichever
repo happened to be iterating, misdirecting the operator to fix their product's `harness.json`
while masking a genuine factory-side bug — exactly the failure mode T-04's own intent names
("a report that swallows a bug reports every member as unreachable for the wrong reason") and
exactly the class this review was asked to hunt. Severity: **med** (a real, plan-named defect
class with zero discriminating coverage, not a hypothetical). Task: T-04. File:
`tests/unit/test-fleet-product-config.py`. Lane: squad-writable (`tests/**`, `harness-backend-dev`
/ `harness-qa`).

## Findings summary

| id | file | task | severity | lane | scenario |
|---|---|---|---|---|---|
| F-1 | `.claude/skills/harness-init/SKILL.md:160-163` | T-01 | low | main-session-direct | Step 2b names no remediation path when the operator cannot push to the product's default branch (no write access / protected branch / required review); fails closed (blocks) but leaves the main session with no next action to offer |
| F-2 | `.harness/harness/docs/SPEC.md:145` vs `.harness/README.md:83-85` / `.claude/commands/harness.md:12-14` | T-07 | med | squad-writable (documentor) | SPEC.md's §2.2 routing-table row states only 2 of the model's 3 onboarding conditions (drops "no central tree"), contradicting its own §3.3 and every sibling doc; a reader trusting the table would call a config-landed-but-tree-missing member "onboarded" |
| F-3 | `tests/unit/test-fleet-product-config.py` | T-04 | med | squad-writable (backend-dev/qa) | No case distinguishes `except FleetError` from a widened `except Exception`, because every stub's failure is already FleetError by the time it reaches `product_config_report`; a bug-swallowing regression in the exact shape T-04's intent names would ship silently |

No `must_fix` — F-2 and F-3 are real but neither is a certain-breakage or high-probability-realistic
defect (F-2 requires an unusual interrupted-onboarding read of a secondary doc surface; F-3 is a
coverage gap for a regression that has not happened, not a live bug). `severity_max = med` →
verdict stands at PASS with the three findings recorded for the team to act on or accept.

## Assessed and dismissed (recorded per policy)

- Empty-`fleet["repos"]` vacuous-all-ok shape in `_check_product_configs` — impossible, `load_fleet`
  rejects an empty/missing `repos` list before any caller reaches it.
- `--repo` narrowing making the `len(report) != len(fleet["repos"])` guard unreachable — true, but
  true independent of `--repo` given the loop's unconditional-append shape; forward defensive code
  matching the plan's own spec, not a masked gap.
- `--repo` + `--show` both given — `--check-product-configs` wins, `--show` is skipped, matching
  the required comment and the single-stdout-payload contract; no finding.
- SC-01 lead 2 (REQ-05 timing) — the `--check-product-configs --repo` check sits correctly between
  fleet registration and every later step; D-04 holds.
- `_PRODUCT_CONFIG_PATH`-based shape assertion in the test file — tests constant reuse per T-04's
  explicit instruction, not a disguised implementation assertion; no separate literal-path test is
  owed here.

## Tooling note (not a review finding)

`_grep` returned false-positive hits for three already-corrected strings (`installs the whole
bin/...`, `cp .../templates/harness.json .harness/harness.json`, `copies this to
.harness/team-config.yaml`) at specific line numbers in `.claude/skills/harness-init/SKILL.md` and
`.claude/skills/harness/bin/layout_migration.py` that do not exist in the actual files (confirmed
absent via plain `bash grep`, and via `git diff 6f34e289..HEAD` showing zero change to either
file). Did not affect this review's conclusions — every citation above was independently confirmed
via `git show <sha>:<path>` and/or plain `grep`/`sed` reads of the working tree (which is identical
to the pin for every code path touched). Attempted to log via `xd://report_issue`; blocked by
`check-domain` for this persona, so recorded here instead.
