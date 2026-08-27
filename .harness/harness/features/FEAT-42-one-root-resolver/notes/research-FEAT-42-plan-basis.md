# Research — FEAT-42 plan basis — 2026-08-26

BLUF: the plan covers all 20 chain sites, 19 tasks, 6 squad / 13 main-session-direct. SC-11 is
downgraded from `uat` to `automated`. One new contradiction was found that nobody has ruled on:
the OMP host feeds the accidental cwd straight back in as `HARNESS_PROJECT_DIR`.

## Verified at 3952814, in this worktree

- **20 occurrences, 16 files.** `grep -rn HARNESS_PROJECT_DIR .claude/skills/harness/bin/ | grep -v
  /test-` returns exactly the operator's list. All 20 are tasked; T-07's invariant counts them to 0.
- **Nine more occurrences live in `test-*.py`** and SET the variable. That is why SC-01 states the
  test exclusion in the criterion instead of hiding it in a test comment.
- **`dispatch-guard.sh`'s chain is at `:83` and `:92`**, not `:75`. `:75` is the `_root_from` def.
- **Callers of the seven deleted names, enumerated** — the delete breaks all of them:
  `harness_root` → `board_lifecycle.py:671,:922,:934,:1034,:1121`, `factory_claim.py:45`,
  `feature-worktree.py:67`, `gh_cost_log.py:111`, `factory_config.py:59`; prose at
  `factory_claim.py:26`, `board_lifecycle.py:158`, `feature-worktree.py:10`, `gh_cost_log.py:109`,
  `worktree_terminal.py:112,:113,:301`; **tests that bind by attribute**
  `test-gh-cost-log.py:40,:45,:52`, `test-factory-claim.py:54`, `test-factory-config.py:780`.
  `_repo_root_from_script` → `context-watch.py:79`. `_root_from` → `dispatch-guard.sh:95`.
  `_resolve_repo_root` → `post-merge-sweep.sh:227` plus prose at `:67,:80,:86`. `wayfind.root` →
  `wayfind.py:57`. All are in T-04, T-02, T-08, T-09, T-18.
- **A test seam already exists for 7 of 9 gates** — `CHECK_DOMAIN_BIN`, `BASH_WRITE_GUARD_BIN`,
  `CHECK_STATE_BIN`, `CHECK_PLAN_ROUTES_BIN`, `DISPATCH_GUARD_BIN`, `VALIDATE_DIGEST_BIN`,
  `INJECT_EXPERTISE_BIN`. Missing on `test-branch-create-gate.py:25` and `test-gh-close-gate.py:15`;
  T-14 and T-15 add it first, because without it am.4's proof cannot be run at all.
- **`run-unit-tests.sh` has a drift detector** (`:47-60`): a `test-*.py` under `bin/` that is not in
  the arrays exits 2. That is why T-01 and T-02 verify their own file directly and T-03 registers
  both before any later task runs the suite. `unit`'s detect glob already matches, so
  `.harness/harness.json` needs no edit.
- **`test-dispatch-guard.py:121-124`'s `_checkout()` makes a bare `.harness` directory** with no
  `team-config.yaml`. Under D-2 that stops being a harness checkout, so every case in the file would
  silently stop exercising the gate. Folded into T-18.

## The identical-violation-set proof, and why it takes the shape it does

Restoring the base-sha gate to `/tmp` and running it there does not work: the old copy resolves its
root through the env chain to the LIVE checkout while the new copy resolves `/tmp`, so the two are
handed different trees and the diff is meaningless. Every gate task therefore builds **two mirror
checkouts**, each carrying `.harness/team-config.yaml`, puts the sha-3952814 copy in one and the
edited copy in the other, sets `HARNESS_PROJECT_DIR` to the respective mirror so both agree, and
drives the gate's own case set through the seam. Each verify also asserts the before-set is
**non-empty** — an empty capture makes `diff` pass on nothing, which is the vacuous-gate shape this
repository has shipped before.

T-13 cannot use it, and says so: it edits `test-check-plan-routes.py` itself, so the two sets are
not comparable. Its substitute is that the three issue-#133 cases pass unmodified and the gate's
output is byte identical run from `/tmp` and from the root.

## Q5 — SC-11 comes off `uat`. The reasoning, not the conclusion

The previous run's argument was that every claim recorded `cwd: <main checkout>` while the worktree
registry did not exist. **That is evidence the DEFECT is real, not that the FIX is verified** —
adopting it as written would have graded the defect. Rejected as stated.

It is settleable anyway, by a different route. `test-dispatch-guard.py` already drives the real
`dispatch-guard.sh` with a synthetic payload, and `_task()` at `:135-142` already carries
`tool_input.prompt`. A case can therefore set payload `cwd` to a fixture MAIN checkout, declare
`HARNESS-FEATURE:` for a fixture worktree, and assert the claim lands in the worktree's registry
while main's is untouched — red first against `dispatch-guard.sh:83`. That is T-18's
`claim_lands_in_declared_worktree`.

What a live operator dispatch would add over that is the **payload shape**, and the shape is already
measured on disk from real spawns: `FEAT-31/notes/probe-hook-payload-identity.md` (the eleven keys,
`tool_input.prompt` absent from a Bash payload) and `FEAT-32/notes/research-FEAT-32-hook-payloads.md`
(a real governed dispatch, `agent_type=harness-orchestrator`). Everything after the payload is
deterministic code this feature edits.

**The residual is stated in the BRIEF rather than buried:** no test can prove a real dispatch prompt
CONTAINS the line. SC-06 pins the machine half — a dispatch without it is refused at exit 2 — which
is what makes the conduct unnecessary to trust.

## The one thing I could not resolve — for the operator

`.omp/extensions/harness-hooks.ts:144` runs every policy script with
`env: { ...process.env, HARNESS_PROJECT_DIR: cwd }`. Under D-2/D-3 a worktree carries
`.harness/team-config.yaml`, so that value PROBES VALID and is honoured — the accidental cwd walks
back in through the override the design keeps. It is outside `.claude/skills/harness/bin/`, so
SC-01 cannot see it and no task touches it. Raised as Q1 in the digest.

## Deliberately NOT scoped

`SINGLE_FLIGHT_AGENTS = ("harness-pm",)` (`inflight_registry.py:32`) — only pm is ever refused. Not
this feature's subject. The `agent_id` → sidecar → `toolUseId` join that would give a claim a real
identity is unbuilt and rests on an undocumented format; D-07 refuses rather than guesses instead.
