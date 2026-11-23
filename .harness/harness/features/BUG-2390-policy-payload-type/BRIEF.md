# BRIEF — BUG-2390 Honest runner payload typing

## Problem

The member-ops hook passes an ops array through a PolicyRunner contract that claims every payload is a Dict. A double cast conceals this mismatch, and the test fixture repeats the false object-only assumption, making the runner seam harder to maintain safely.

## Done when — by perspective

**code maintainer** — I can trust the runner payload contract and narrow object payloads honestly in tests without disguising arrays as objects.

**operator** — I retain existing hook behavior while the type mismatch is repaired, with recorded static red-first evidence and a green hook suite matching main's observed baseline.

## Success criteria

- SC-01 (code maintainer): PolicyRunner, runPolicy, classifyPolicyRun and every affected test runner accept object or array payloads honestly; object-field reads use checked narrowing, member-ops forwards its ops array without an array-as-Dict cast, and the obsolete fixture apology is removed or truthful. Inspect git show <review_sha>:.omp/extensions/harness-hooks.ts and git show <review_sha>:tests/unit/omp-hooks.test.ts; no payload-path double cast remains.
  verify: inspection
- SC-02 (code maintainer): Main first widens test runner payloads and adds an asserted object-narrowing helper while production remains object-only, captures bun run typecheck failing specifically at the runner contract mismatch with the test-only pin, then widens production and records bun run typecheck exiting 0 at the completed pin.
  verify: automated  evidence: typecheck
- SC-03 (operator): Existing object-gate and member-ops array behavior remains unchanged; bun test tests/unit/omp-hooks.test.ts exits 0 with the actual main baseline pass count recorded in notes/research-patch-intake.md, with no removed, skipped or weakened assertions. The static red-first proof required by SC-02 is the discrimination evidence for this semantics-preserving repair, not an invented runtime failure.
  verify: automated  evidence: unit

## Verification gaps

No applicable null-runner gap: unit and typecheck are active and match these TypeScript files. The existing pi/ctx any boundary means typecheck does not prove the real OMP host API; the hook suite carries regression evidence, not a new live-host claim. SC-03 is regression-only and shares SC-02's static fail-first proof; no runtime failure is claimed.

## Constraints

- Settled intake: /Users/molchairuangutai/GitHub/harness/.harness/notes/grilling-policy-payload-type-2026-11-22.md; adopt Dict | unknown[], not a full JSON-value type or separate member-ops runner.
- Implementation files only: .omp/extensions/harness-hooks.ts and tests/unit/omp-hooks.test.ts. Preserve serialization, gate classification, forwarding and observable behavior.
- DEC-174 BLOCKS team execution of hook and hook-test changes; main executes T-01 directly inside the assigned feature worktree.
- DEC-225 SUPPLIES the bounded patch lane: one task, no panel, readers, goal-check or plan-flow simplify.
- DEC-182 SUPPLIES controlled plan authoring; DEC-231 SUPPLIES perspective-tagged criteria; DEC-254 SUPPLIES explicit decision dispositions. No existing decision text changes.
- Approval remains pending for the delegated advisor signature; PM does not sign.

## Out of scope

- Restructuring the member-ops seam or the runner wrappers — settled intake bounds this repair to honest payload typing.

## Approval

status: approved
approved-by: fable-advisor
date: 2026-11-22
