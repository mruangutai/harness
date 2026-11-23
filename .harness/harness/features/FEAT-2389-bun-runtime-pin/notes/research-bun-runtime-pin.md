# Bun runtime pin — intake ready for signature

The 46-line BRIEF and pending one-task plan implement the settled three-file patch scope without implementation changes. T-01 traces SC-01 through SC-04 and routes main-session-direct under DEC-174; local verification and PR CI evidence are separate.

## Evidence and choices

- Baseline checkout and control-plane HEAD: 9eb07b4f3cd235c234a10edddbfe5542c1e85fba, observed via git rev-parse. package.json has no packageManager and retains @types/bun 1.4.5; its typecheck script invokes tsc --noEmit -p tsconfig.json.
- Settled input: /Users/molchairuangutai/GitHub/harness/.harness/notes/grilling-bun-runtime-pin-2026-11-22.md, Settled and Done when. Host version and setup-bun fallback precedence are advisor-verified settled inputs, not independently measured in this run.
- Workflow checks.steps Install Bun is input-free; Typecheck runs bun run typecheck. README.md, Development / TypeScript typecheck, already distinguishes the pinned compiler/dependencies and their Dependabot updates. Add only the requested runtime-policy sentence.
- Governing control-plane DECISIONS.md: DEC-174 ruling requires direct enforcement-layer implementation; DEC-225 supplies one-task patch scope; DEC-228 excludes patch panel. No decision is amended or struck. Routine reversible config/prose choices need no D-NN.
- Product docs/spec.md, docs/decisions.md and docs/architecture.md do not exist in this checkout (ls exit 2). Missing guidance question: what broader product contract would apply? None is inferred; the settled bounded runtime contract is sufficient for this intake, and these missing docs are disclosed in BRIEF and task intent.
- Config test matrix has no unconditional kind; integration is conditional on touches_config_shape. Active typecheck command is bun run typecheck. No affected null-runner surface is introduced. SCs use inspection of pinned content, captured local receipts and PR CI results rather than mislabeling the equality assertion as an existing test kind.
- Backlog intake read from configured mruangutai/harness; issue #2389 matches the settled scope. An initial repository-name attempt failed and was corrected using harness.json github.repo.

## Verification and remaining work

plan-merge apply returned APPLIED and seeded pending approval; plan-merge check resolved T-01's three anchors with zero failures. wc -l reported 46 brief lines. No implementation assertions, typecheck, tests, builds, linters or formatters were run. Main must capture the pre-edit equality failure, then execute the literal local verify block under Bun 1.3.14 and collect separate review-pin PR CI evidence for both Install Bun steps and every green job.

The apply hook also reported expected unsigned brief/pending plan and absent Build-entry receipt; subsequent signature owns those transitions. It noted mismatched historical run attribution/directory naming in feature.json versus runs/2026-11-22-1-product; intake did not change lead-owned run records. No APPROVAL-RESET receipt occurred and no remote status mutation was made.

## Open questions

No blocking product questions. Subsequent advisor/operator signature remains required; lead should reconcile the hook's run-record attribution note through its own run lifecycle.
