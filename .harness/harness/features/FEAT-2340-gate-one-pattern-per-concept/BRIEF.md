# BRIEF — FEAT-2340 Gate one pattern per concept

## Problem

Maintainers of check-domain.py must keep overlapping path matchers and opaque flag aliases synchronized. BUG-2295 exposed the resulting drift risk; the current inventory finds two same-file path-concept pairs and eight uses of the flag alias. Existing simplify guidance does not explicitly ask both prevention questions.

## Done when — by perspective

**code maintainer** — I can recognize a path concept and a constant's meaning without decoding aliases, while retaining the gate's deliberate bootstrap independence.

**operator** — I can rely on the same gate decisions and diagnostic names after the cleanup, with prevention guidance landing before the gate refactor and no expansion into other files.

## Success criteria

- SC-01 (code maintainer): At git show <review_sha>:<path>, the existing REUSE angle asks whether the diff adds a second matcher, constant or helper for an existing concept; SIMPLIFICATION asks whether a new name hides behaviour behind an alias or abbreviation. The three naming bullets have their single home beside the naming paragraph in model-the-domain.md: spell flags out, use one pattern per path concept with named variants, and name constants for their meaning. Explicit bootstrap respellings remain permitted. Only those three existing guidance files change in T-01.
  verify: inspection
- SC-02 (code maintainer): At git show <review_sha>:.claude/skills/harness/bin/check-domain.py, the alias declaration and all eight executable uses are removed in favor of explicit re.IGNORECASE wherever a flag argument remains; its explanatory comment is updated. One RE_HANDOFF handles non-greedy phase and optional cycle, preserving handoff-x-c1-c2.md becoming notes/handoff-x-c1.md and lowercased mixed-case canonical diagnostics. One plan path text with named feature_dir is compiled twice with the original flag asymmetry, preserving legacy-versus-shape diagnostic ordering for mixed-case Plan.yaml beside PLAN.md. VERB has a mode-neutral meaningful replacement throughout live code, and the stale test comment names test-check-domain-artifact.py. The protected literals and unrelated symbols in Constraints remain unchanged except the two permitted trailing flag substitutions. Inspect these edge cases in pinned pattern and consumer content against the baseline; existing tests do not establish multi-cycle canonicalization or legacy-versus-shape diagnostic ordering.
  verify: inspection
- SC-03 (operator): Every existing tests/integration/test-check-domain*.py suite exits 0 without FAIL output after T-02, without test rewrites. Existing assertions provide single-cycle handoff refusal/acceptance and canonical-name, mixed-case plan exit-status, and deliberate pattern-text equality regression evidence. Multi-cycle canonicalization and case diagnostic ordering are carried by SC-02 inspection, not claimed as existing test coverage. This is regression evidence for a semantics-preserving refactor, not a claim that these already-green suites fail against the unmodified gate.
  verify: automated evidence: integration
- SC-04 (operator): Comparing git show <review_sha>:<path> with baseline e239d88156c508c948d49cd31238ea13b3b39865 shows production edits confined to the three T-01 guidance files and T-02 check-domain.py. The commit history shows T-01 prevention landed before the dependent T-02 refactor; no new implementation document, file, test or mechanical lint lands.
  verify: inspection

## Verification gaps

No affected null-runner kind. Integration is active with a runnable command and discovers tests/integration/test-check-domain*.py. There are no check-domain unit suites; SC-03 does not claim unit coverage. Guidance and source topology use pinned-content inspection (SC-01, SC-02, SC-04), not a new lint. Functional/eval are excluded under DEC-187 and do not carry these criteria; component, ui and typecheck unresolved runners do not cover this Python/guidance-only surface. No UAT criterion requires the operator personally.

The suite invocation uses existing run_pool.py under Main's supervised aggregate deadline of less than 60 seconds. Runtime has not been measured; completion inside that budget is not guaranteed. The runner emits completed-suite combined stdout/stderr and exit receipts, but buffers each suite until it finishes. On timeout Main retains available output and the host timeout receipt, identifies incomplete suites as unverified, and does not claim their partial output was recovered or that SC-03 passed. A timeout is a failed verification requiring remediation, not permission to add files, rewrite tests or silently extend the budget.

## Constraints

- Settled operator decisions: /Users/molchairuangutai/GitHub/harness/.harness/notes/grilling-gate-naming-one-pattern-2026-11-22.md, sections Destination and Settled. Exactly T-01 then T-02 with depends_on [T-01].
- DEC-174 BLOCKS team execution of check-domain.py; both tasks are main-session-direct because the three guidance paths resolve to NOBODY (DEC-179 SUPPLIES plan-time resolution). Main owns orchestration for this entirely direct plan.
- DEC-195 SUPPLIES existing simplify-angle homes and does not authorize writes to unowned guidance. DEC-235 SUPPLIES the existing craft leaf; do not change frontmatter or generated indexes. DEC-234 SUPPLIES the accepted no-import-seam duplication exception, not a mandate to consolidate bootstrap code.
- DEC-159 SUPPLIES phase handoff/supersession semantics; DEC-180 SUPPLIES pre/post shape-report semantics; DEC-182 SUPPLIES legacy-plan conversion and single-writer denial. All remain unchanged.
- Preserve RE_STATE_YAML and RE_RUN_DIGEST pattern literals, original declaration-line placement and aligned assignment spacing; only replace their trailing _I flag. Preserve _FEATURE_ID_RE verbatim equal to dispatch-guard.py FEATURE_RE. Do not import these deliberate bootstrap respellings.
- Preserve _FEATURE_DIR_RE, STAMP, SWEEP_WINDOW_S, RE_FEATURE_JSON, RE_STATE_MD and RE_CLAUDE_MD except replacing their _I arguments where applicable; preserve RE_RUN_IDENTITY including its fallback. Do not edit fixtures/prior-check-domain.fixture or other files.
- Retain the case-sensitive legacy plan route and IGNORECASE shape route. Handoff phase must remain non-greedy; cycle refusal canonical names and messages remain exact.
- PRODUCT docs/spec.md, docs/decisions.md and docs/architecture.md are absent. AGENTS.md explicitly maps specification and decisions to .harness/harness/docs/SPEC.md section 4.2 and DECISIONS.md; no architecture substitute is invented.

## Out of scope

- Cross-file consolidation (groups F, J, Y, O, E, S, G; the strict feature-slug pair; the distill-token triple; the shell-assignment prefix; the perspective-heading, expertise-section and persona matchers; DEC-id matchers). These become backlog issues at ship, each overlap group as its own issue and later sequential patch, not tasks or open success conditions here.
- Short-name renames outside check-domain.py (SEV, OPS, SEP, RAW, _WHAT, PIN, …), which are later patches.
- A mechanical lint for aliases or duplicate matchers, deferred to a future issue.

## Approval

status: pending
approved-by:
date:
