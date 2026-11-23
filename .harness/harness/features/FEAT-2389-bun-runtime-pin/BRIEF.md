# BRIEF — FEAT-2389 Pin Bun runtime

## Problem

CI's input-free setup-bun steps float to the latest Bun while the production OMP host uses 1.3.14, so an upstream release can change hook-test and typecheck behavior without a repository change (settled grilling, issue #2389).

## Done when — by perspective

**operator** — I can rely on CI using the production host's Bun version and on the complete PR check run staying green before merge.

**code maintainer** — I can find the single runtime pin and understand when to bump it without confusing runtime updates with dependency updates.

## Success criteria

- SC-01 (operator): At the review pin, package.json packageManager is exactly bun@1.3.14; main captures the equality assertion failing before editing and passing afterwards, and captures bun --version equal to 1.3.14 followed by a successful bun run typecheck under that runtime. Review inspects the recorded red/green command output and pin identity.
  verify: inspection
- SC-02 (code maintainer): git show <review_sha>:.github/workflows/tests.yml shows exactly one added comment sentence at the first Install Bun step naming package.json packageManager as the version source; both setup-bun invocations remain input-free and executable workflow content is unchanged.
  verify: inspection
- SC-03 (code maintainer): git show <review_sha>:README.md shows one added sentence stating that the package.json Bun runtime pin tracks the production OMP host and is bumped manually only when that host is upgraded, never by Dependabot.
  verify: inspection
- SC-04 (operator): The PR CI run for review_sha has both Install Bun step logs reporting bun-v1.3.14 and every job green, including the hook tests and typecheck; review cites the run URL, commit SHA and step/job results.
  verify: inspection

## Verification gaps

No affected null-runner kind: this configuration-only patch has no browser, component, service or model-evaluation surface. Local typecheck cannot prove setup-bun resolution or complete CI health: SC-04 remains outstanding until PR CI runs. SC-01 uses recorded command inspection, not a claim that existing tests detect a missing packageManager field; the explicit equality check supplies red-first evidence. No UAT is required.

## Constraints

- DEC-174 BLOCKS team execution of changes to CI enforcement: main implements directly, with all relative-path edits confined to this feature worktree.
- DEC-225 and DEC-228 SUPPLY the patch lane: at most 120 brief lines, exactly one task, no panel or goal-check. DEC-174 supplies the main-session-direct exception to the default team route.
- DEC-120 SUPPLIES pending approval; this intake does not sign either artifact.
- Implementation touches only package.json (add packageManager: bun@1.3.14), .github/workflows/tests.yml (one comment sentence), and README.md (one sentence). No workflow bun-version input or second runtime pin.
- Preserve @types/bun 1.4.5, TypeScript, bun.lock, workflow commands and .github/dependabot.yml. Runtime bumps are manual when the production host upgrades.
- Product docs/spec.md, docs/decisions.md and docs/architecture.md are absent in the assigned checkout. Settled grilling supplies this bounded runtime contract; no broader product behavior or architecture is inferred from that absence.

## Out of scope

- A github-actions Dependabot ecosystem for floating action tags — a different problem.
- Downgrading @types/bun — the registry's 1.3 line ends at 1.3.9, so exact alignment with runtime 1.3.14 is unavailable (settled grilling).

## Approval

status: approved
approved-by: fable-advisor
date: 2026-11-22
