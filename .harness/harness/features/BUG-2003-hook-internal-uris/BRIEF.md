# BRIEF — BUG-2003-hook-internal-uris — Internal URI domain checks

## Problem

Governed OMP agents cannot reliably send messages or report tooling defects: the write hook
forwards internal URIs to the file-domain checker as checkout paths. FEAT-495 reviewers were
refused on `agent://Main` and `xd://report_issue` (intake evidence at e0bb9814), obstructing
coordination and defect reporting without protecting a real file.

## Done when — by perspective

**operator (governed agent)** — I can send agent messages and report tooling defects without
those operations being mistaken for checkout-file writes. Ordinary file-write permissions and
the main session's behavior remain unchanged.

**security/harness owner** — I can rely on unapproved URI destinations being refused explicitly,
including destinations that could change real files. Switching from write to edit cannot evade
that refusal.

**code maintainer** — I have regression evidence that distinguishes the repaired behavior from
the defect and protects ordinary file-domain enforcement.

## Success criteria

- SC-01 (operator): For governed `write` and `edit`, `agent://<id>` and exactly
  `xd://report_issue` proceed without invoking `check-domain.py` in `preDomain` or with `--post`.
  Unit cases assert both hook stages; their failing state before the fix is demonstrated.
  verify: automated        evidence: unit
- SC-02 (security/harness owner): Every other `scheme://` destination is refused by name with a
  clear message, never resolved to a real path or forwarded to `check-domain.py`. This includes
  other `xd://` devices (`ast_edit`, `lsp`, `recall`, `reflect`), `conflict://`, `local://`,
  `vault://`, `ssh://`, and an unknown scheme, through write and edit, including edit MV targets.
  The URI refusal regression cases must be demonstrated failing before the fix.
  verify: automated        evidence: unit
- SC-03 (operator): Real out-of-domain file writes and edits retain today's domain-check
  payloads and refusal, including an edit combining an allowed URI with a forbidden file;
  allowed URI destinations do not exempt sibling file targets. Main-session write/edit behavior
  remains unchanged. Demonstrate the mixed-target regression failing before the fix and retain
  passing ordinary-file/main-session controls.
  verify: automated        evidence: unit
- SC-04 (security/harness owner): One scheme decision governs write and edit targets in both
  `preDomain` and `postDomain`; there is no edit bypass or independent permissive scheme branch.
  Inspect `git show <review_sha>:.omp/extensions/harness-hooks.ts`, at `preDomain`, `postDomain`
  and their shared decision, rather than an uncommitted working-tree copy.
  verify: inspection
- SC-05 (code maintainer): `tests/unit/omp-hooks.test.ts` contains automated coverage for allowed
  URIs, refused URIs, and real out-of-domain files, exercising write/edit pre/post callbacks and
  mixed edits. Record failing-before-fix and passing-after-fix receipts with discriminating
  cases named; unchanged controls alone are not fail-first evidence.
  verify: automated        evidence: unit

## Verification gaps

None for this surface: the active `unit` kind discovers `tests/unit/test-omp-hooks.py`, whose
Bun invocation executes `tests/unit/omp-hooks.test.ts`. No UAT or prototype is required for this
internal enforcement-only fix. Runtime regression tests have not been run during draft intake.

## Constraints

- Settled intake: the allowlist is only `agent://<id>` and the exact URI `xd://report_issue`.
  All other `scheme://` targets fail closed; one scheme decision covers write and edit.
- Preserve existing runtime lineage/claim checks, real-file checks, and main-session behavior;
  bypass only file-domain checks for the allowed URI targets, not all tool-call enforcement.
- DEC-174 BLOCKS team execution of the active OMP enforcement adapter and its co-changed test;
  T-01 is main-session-direct, overriding the patch lane's default team route.
- DEC-225 SUPPLIES the bounded patch intake: at most 120 brief lines and exactly one task.
  DEC-228 BLOCKS a pre-build panel or goal-check for this patch. Approval remains pending.
- Implementation touches only `.omp/extensions/harness-hooks.ts` and
  `tests/unit/omp-hooks.test.ts`; no new public interface, schema, or enforcement surface.

## Out of scope

- An `agent://` messaging policy: a deliberate rule of its own, later.
- Resolving file-backed schemes (`conflict://`, `local://`, `vault://`, `ssh://`) to real paths:
  refused by name instead. Resolving them would couple the hook to OMP's URI resolution.
- Read-only `xd://` devices (`lsp`, `recall`, `reflect`) for governed agents.
- The Claude Code host, which has no internal URIs.

## Approval

status: pending
approved-by:
date:
