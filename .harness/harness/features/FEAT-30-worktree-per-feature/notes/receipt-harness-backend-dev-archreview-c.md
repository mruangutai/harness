# FEAT-30 archreview S-C — worktree lifecycle altitude

## BLUF

D-01 stands: a standalone CLI is the right altitude. Its stated REASON is directionally correct but
overstated — it names "fleet-scoped modules" as the obstacle when the real, verified obstacle is
narrower and stronger: the existing factory_ **entry points** are fleet-scoped by deliberate design
(one of them documents itself as excluding the harness checkout), and merging worktree-lifecycle
exit codes into them would collide with `factory_cli.py`'s four-value contract, which is a concrete
cost D-01's own text never names.

## Q1 — inventory

All four factory_* entry points (`factory_workspace.py`, `factory_claim.py`, `factory_land.py`,
`factory_decompose.py`) are CLIs whose argparse requires `--repo`/`feature_dir --repo`, resolved
through `factory_config.repo_entry(fleet, name)`, which raises `FleetError` when the name is not in
`fleet["repos"]` (`factory_config.py:229-239`). None accepts a bare "harness" form. That makes them
**fleet-scoped as entry points** — genuinely, not merely fleet-aware — confirmed by code, not
inferred. `factory_workspace.py`'s own docstring states this as an explicit design choice: "a ready
checkout of a repository the harness does not live in" (`factory_workspace.py:1`), "the harness is
not installed into the target repository in this increment" (`factory_workspace.py:3`).

`factory_cli.py` is a pure library (no entry point, no side effects at import,
`factory_cli.py:18-19`) implementing one fixed exit-code contract: 0 ok / 1 nothing-to-do / 2 refused
/ 3 lost-race (`factory_cli.py:10-13`). It is fleet-agnostic, not fleet-scoped, and not the thing D-01
is arguing about.

`factory_config.py`'s functions (`load_fleet`, `repo_entry`, `workspace_path`) are **fleet-aware**,
not fleet-scoped: they take a fleet dict as an argument and place no restriction on what that dict
contains. Nothing in the library layer refuses a synthetic or harness-only fleet. The fleet-scoping
is a property the four CLIs impose on top of this library through their argparse contracts, not a
property of the library itself.

## Q2 — `workspace_path()`

Docstring, verbatim (`factory_config.py:334-339`): "Return the absolute checkout path: workspace_root
joined with the repository name AFTER the owner. This is the one place that derivation exists —
factory_workspace.py and factory_land.py both call it rather than restating the rule." Current
callers, grepped: `factory_workspace.py:117`, `factory_land.py:56`, `harness_boundary.py:158`
(`get_fleet_bases`), plus test files. T-01 adds `feature-worktree.py` as a fourth production caller
(the docstring already undercounts — `harness_boundary.py` is a real caller today, uncited).

Effect of a third/fourth caller: the general claim — "the one place that derivation exists" —
**stays true**: `feature-worktree.py`, per its intent (plan.yaml lines 253-255), calls
`workspace_path()` rather than re-deriving `workspace_root + name-after-slash`, which is legitimate
reuse of the seam, not duplication. The **enumeration of callers goes stale/misleading** — T-01's
file list (plan.yaml:218-220) does not include `factory_config.py`, so nobody updates the docstring's
name-list to add `feature-worktree.py` (or to correct the pre-existing omission of
`harness_boundary.py`). Not a blocker; a real, checkable documentation-debt finding.

## Q3 — seam and depth

Interface: 4 verbs (`create/list/path/remove`), 2 flags (`--repo`, `--id`), fixed stdout/exit
contract. Behind it: two-form repo resolution, `dest_for()`, branch-reuse detection, `git worktree
add`, porcelain-based dirty-tree detection, and cross-checkout artifact verification via `git
hash-object`/`rev-parse`. Small interface, substantial behaviour — this is a deep module by the
glossary's test.

Deletion test: if this lived as a mode of `factory_workspace.py` instead, two concrete things
reappear, not abstractions:
1. A fleet/non-fleet branch would have to be added inside a module whose docstring explicitly
   states the opposite design ("a repository the harness does not live in" —
   `factory_workspace.py:1`), reopening the exact case D-07 already refused to widen for
   bash-write-guard.sh.
2. The lifecycle's own exit codes (2 bad-id, 3 destination-exists/not-a-worktree, 4 dirty-tree/git
   failure, 5 artifacts-not-landed) do not fit `factory_cli.py`'s fixed four-value contract
   (`factory_cli.py:10-13`, specifically `EXIT_RACE=3` already means "another agent owns the issue,"
   a different fact from "destination exists"). Reusing `factory_cli.run()` would force either a
   contract violation or growing `factory_cli.py`'s enum to carry meanings it wasn't built for —
   a cost D-01's stated reason never mentions but that is real and checkable.

No existing seam duplicates this behaviour (see Q4).

## Q4 — falsification check

`grep -n worktree factory_*.py` returns **zero** hits — no factory_ module creates, lists, or manages
worktrees today. `grep -n '"harness"' factory_*.py` finds no repo-entry special case for "harness"
anywhere; the only "harness" hits are label strings and `harness_root()` derivation, unrelated to
fleet membership. D-01's premise is not merely plausible, it is directly confirmed: nothing already
does this, and nothing already treats harness as a non-fleet repo inside a factory_ module.

## Q5 — one derivation site or two

Grepped for the literal `.claude/worktrees` and for `WORKTREES_SEGMENT` across `bin/*.py` and
`bin/*.sh`. Existing sites that touch `WORKTREES_SEGMENT` (`harness_boundary.py:33,37,424,445-446`;
`bash-write-guard.sh:432,441,450,465,473,562`; `check-domain.sh:433,499,603,644`) all compute a
**boundary/membership test** — "is this write inside the worktrees area" — never a create
**destination** of the form `owner_root/segment/id`. `bash-write-guard.sh:465`'s `_legal` is the
closest, and it stops at `owner_root/WORKTREES_SEGMENT` (no id component), by design (D-07: this door
"stays fleet-unaware and unchanged"). T-01's `dest_for(owner_root, segment, id)` is the **only** site
in the repo that computes the full three-part creation destination. The derivation stays in exactly
ONE place; the four/five existing `WORKTREES_SEGMENT` sites are a different concern (enforcement) and
are not duplicated by it.

## Recommendation

D-01 stands. The standalone CLI is the right altitude: the behaviour is deep, nothing existing
duplicates it, and folding it into a factory_ entry point would either violate that entry point's own
documented non-harness design or collide with `factory_cli.py`'s exit-code contract.

**But the stated REASON is overstated.** "The factory_ modules are fleet-scoped" reads as an
intrinsic property of the whole layer; measured, only the four **CLI entry points** are fleet-scoped
(by argparse-required `--repo` resolved through `repo_entry`), and the underlying library
(`factory_config.py`) is merely fleet-aware. The correct and stronger justification — verified, not
supplied by the plan — is: (a) `factory_workspace.py` explicitly documents itself as excluding the
harness checkout, so adding harness-awareness there reopens a design choice D-07 already refused
elsewhere, and (b) the lifecycle's exit codes don't fit `factory_cli.py`'s fixed four-value contract.
Recommend the plan's `because:` text for D-01 be tightened to cite these two checkable facts rather
than the broader, slightly false "fleet-scoped modules" framing — a right choice resting on an
imprecise justification is still a finding worth recording.
