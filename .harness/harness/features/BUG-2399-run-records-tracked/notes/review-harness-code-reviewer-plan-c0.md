# Plan scope and architecture review — BUG-2399

PASS — the pending plan matches settled scope; no actionable findings. The **plan mission fits** the coupled installer, fleet-upgrade, lifecycle-evidence and policy change. Approval remains pending; this is not a ship-readiness verdict.

## Specification and sequencing

- SC-01/02 bind T-01 regression evidence to T-02 rule/merger/upgrade changes; SC-03 binds both real lifecycle exposures to T-01 and T-03; SC-04 binds inventory and policy landing to T-02/T-03. No orphan criteria, unknown traces or undocumented scope expansion found (`plan.yaml:43-218`; `BRIEF.md:15-25`).
- Dependencies are topological: T-01 → T-02 → T-03. File ownership is disjoint. T-02 intentionally cannot make all T-01 suites green independently; its focused merger gate is followed by T-03's terminal three-suite gate after documentation edits. Successors therefore do not leave predecessor acceptance stale.
- Removal proof is explicit obsolete-rule check refusal, exact replacement/idempotence and ordinary Git tracking, not merely a green suite. T-01 requires canonical-rule failures independently of the initially absent executable documentation block (`plan.yaml:77-86`).
- **SC-04 inspection:** `plan.yaml:215-218` requires pinned `git show` inspection of policy, unchanged DEC-238, instructions and the build-time inventory receipt. This reviews the inspection contract only; implementation and a review pin do not yet exist.

## Architecture and governing decisions

- The existing merger remains the deep module at the ignore-file seam: preserve project bytes while replacing only exact obsolete Harness rules. The operator procedure owns review/population/hash/staging coordination and calls that merger; it is not a second ignore migrator. Tests cross real process/Git seams and execute the shipped documentation block. No speculative adapter, pass-through layer or new migration service is planned.
- Locality is appropriate: T-02 owns the complete upgrade safety contract, while T-01 tests its effects. Existing distill/removal predicates remain unchanged; fixture changes expose the intended new dirt rather than bypassing gates.
- Independent decision-index search and governing-entry reads support the declared **keep** dispositions: DEC-112 requires deterministic idempotence/check mode, not permanent append-only implementation; DEC-174 requires direct execution; DEC-238 governs retention rather than broad ignoring. D-01 adds tracking without overtaking those clauses. DEC-13's operator-triggered upgrade remains intact. No additional amend/strike is warranted under DEC-188/254; stale SPEC tracking assertions are corrected, not mistaken for a contradictory DEC.

## Principles applied

- Delete First: replace obsolete broad rules and false rationale in the existing merger, rather than layering negations or force-add exceptions.
- Migrate Callers, Then Delete Legacy APIs: both shipped historical rule spellings are migrated in the same change; no live broad-rule compatibility path remains.

## Open questions

None. Read-only plan review; no diff, production grading, builds, tests, linters or formatters run. The reported draft-check result was treated as input, not independently rerun.
