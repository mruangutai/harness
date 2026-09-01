# BUG-1081 plan panel — main-session record

The main session ran four read-only reviews over the pending BRIEF.md and plan.yaml: goal alignment (`harness-pm`), implementation feasibility (`harness-code-reviewer`), enforcement-boundary threat modeling (`harness-security-reviewer`), and an independent should-not-be-built challenge (`fable-advisor`). This manual panel was used because issues #1075 and #1080 currently prevent the standing plan-panel flow from recording a pending-plan run unaided.

## Initial result

FAIL, severity high. The initial plan had two build-blocking defects: its shared bar classification depended on configuration absent from the specified fixtures, and it extended repository base derivation to every grade without recording or testing the new availability consequence. The architecture review also found dead verification commands and later found that the first correction introduced two repository-root bases.

## Corrections applied

- One feature-bound repository root now governs every Git operation, review OID, Python diff, grading call, and test-kind configuration read.
- Missing or degenerate default-branch derivation is deliberately fail-closed for every grade, with explicit fixtures and remediation-bearing errors.
- The shared classifier receives parsed `test_kinds`; it never discovers configuration from ambient cwd.
- Unit and integration evidence are separated correctly and both are run where the shared API changes.
- The CLI subprocess alternative is explicitly rejected, mutation evidence is required, and semantic independence from the one grader is not claimed.
- Docs-only, deletion-only, mixed fail/grade-2, syntax-error, plan-mode, and real-hook exit-code boundaries are pinned.
- Deleted `check-docs.sh` and unsupported `gen-decisions-index.py --check` commands were removed.
- GitHub `Done` remains a post-merge ship-gate step rather than an impossible pre-merge success criterion.

## Final result

PASS. The goal re-review reported no remaining high or critical finding. The architecture re-review reported PASS with one low root/config ambiguity, which was then resolved by requiring `test_kinds` to come from the same feature-bound root and never from `review_config_path()`. Security and independent reviews had no blocking findings; their substantive medium findings were folded into the corrections above.

The source reviewer artifacts remain under this notes directory. Findings are retained in plan.yaml as resolved panel entries rather than erased.
