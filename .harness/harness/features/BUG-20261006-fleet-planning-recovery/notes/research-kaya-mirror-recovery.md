# T-05 — Kaya mirror recovery (#2159; closes #2172)

This was executed on 2026-11-07 by the main session (DEC-174) in the Kaya planning worktree, using the installed tooling (#2177 `4a05030d`), under the separate authorization recorded in T-04's note (`a6ec5e09…`, effect `recover-mirror`).

## Preflight (read-only)

- `recovery_command_for(..., replacement=True)` returned **full**. That is the expected result: runs 4 and 7 are `code_grade: n_a` plan-flow runs, which the fad2e25c fix excludes from "started work".
- `resolve_binding` returned `mruangutai/kaya`, board `{owner: mruangutai, number: 9, station_field: Status}`.
- Provenance problem: "nonempty mirror has no matching github.repo provenance".
- `plan.yaml` sha256 is `1c5d6bfb…`, which matches the authorization.

## Execution

1. `gh-sync.py recover-mirror <FEAT-01 dir> --previous-repo mruangutai/harness --evidence notes/research-fleet-planning-recovery-authorization.md --yes` exited **2**.
   - It created, in mruangutai/kaya: milestone #1, parent #16, and T-01..T-10 as #17..#26, all attached to #16. Recovery was recorded durably as `25a09cc3-…`, `state: in-progress`.
   - It then refused: `ERROR - mruangutai/kaya#17 -> ready: issue carries no item on mruangutai project 9`.
   - Cause: gh-sync never adds board items. It depends on the project's "Auto-add to project" workflow, which Kaya's project 9 lacks. This is tracked as #2181.
2. Remediation, per advisor ruling BoardAutoAddAdvisor: `gh project item-add 9 --owner mruangutai --url …/issues/N` for #16..#26, giving item ids `PVTI_…HnM` through `PVTI_…HqY`. No receipt was edited.
3. The same `recover-mirror` command was rerun unchanged and exited 0. It set every card to ready (#17..#26, #16, #14) and reported `mirror recovery 25a09cc3-… complete in mruangutai/kaya`.
4. A no-op replay of the same command exited 0 and reported `mirror recovery 25a09cc3-… already complete — no writes`. `feature.json` was byte-identical: `900d8fb9…` before and after.

## Resulting state (live, read back)

- Milestone mruangutai/kaya#1 is open and titled "FEAT-01-kaya-platform (recovery 25a09cc3-…)", with 10 open issues.
- Parent #16 has 10 sub-issues: [17..26]. Source #14 is OPEN.
- Project 9: #14 and #16..#26 all read **Ready**.
- `feature.json` `github` holds:
  - `repo: mruangutai/kaya`, `milestone: 1`, `parent: 16`, `issues: T-01..T-10 = 17..26`;
  - `source_issues: [14]`, `build_entry: opened`;
  - `recovery.state: complete`, `plan_sha256 1c5d6bfb…`.
- The wrong-repository objects were left untouched: Harness milestone 100, #2116–#2126 (CLOSED NOT_PLANNED), and Harness #14.

## Feature-scoped checks

The first post-recovery `check-state.py` run crashed with `factory_gh.GhError: Could not resolve to an Issue with the number of 17`. INV-26 had looked up Kaya's numbers in mruangutai/harness. That was fixed by BUG-2180 (#2180, PR #2184, `88f1c4c2`).

After that fix, `check-state.py --feature FEAT-01-kaya-platform` exits 0, with gh authenticated and the planning worktree's stale-worktree INV-29 resolved. One GraphQL read went to mruangutai/kaya only.

## Not done

- **SC-08 / UAT** is operator-executed: confirm in the Kaya board and repository that FEAT-01 is mirrored correctly before any build.

## Landed

The recovered record is on main as `30c06581` (PR #2189). CI was green after BUG-2190 (#2205) applied the operator's DEC-221 amendment. See the T-04 note.
