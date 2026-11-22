# Receipt — simplification angle — r-20261121-2-simplify-eng-simplification

BLUF: 2 findings (both fold-in/briefing-row, med/low), 1 low leave. Nothing applied.

## S-1 (med, fold-in) Extension-side applicability duplicates narrow-gate matching
- File/line: plan.yaml:123 (T-01 intent, "The extension must likewise determine applicability before a missing executable or spawn error can be treated as a closed failure"); BRIEF.md:50.
- Summary: When the gate script cannot spawn, the extension (.omp/extensions/harness-hooks.ts:1439-1442 runs all three narrow gates as scripts) can only know applicability via its own matcher — a TS second spelling of gh-close/branch-create/plan-sign command semantics, which the same intent forbids ("no second general-purpose shell parser").
- Cost: two matchers for one rule that drift (nested/quoted/split/indirect spellings are exactly what the Python tests protect); an under-matching TS copy fails open on the spawn-failure path, an over-matching one blocks unrelated Bash.
- Alternative: fold into T-01 a bounded rule so no TS matcher is needed: classify spawn/missing-executable failure of a narrow gate as closed only for the Bash call, using a conservative command-token prefilter limited to the gate's verb names (gh close/api, branch/checkout -b/worktree, feature-record sign verbs) taken from one constant, or state explicitly that extension-side start failure of a narrow gate refuses the Bash call and unrelated-Bash bypass is guaranteed only for in-gate failures. Either way, name which, so the build-design choice is not left open to produce a second parser.

## S-2 (low, fold-in) New runtime suite re-covers SC-06 dispatch checks already owned by test-dispatch-guard.py
- File/line: plan.yaml:125 ("...and cover each remaining dispatch check listed in SC-06" inside test-omp-native-gate-runtime.py), while plan.yaml:109 retains test-dispatch-guard.py and says "retain all unchanged refusal cases".
- Summary: same dispatch refusals asserted in two suites (existing integration + new runtime), same for missing-identity/absent-digest_object controls vs test-validate-digest.py (:113).
- Cost: two places to keep in lockstep for one fact; adds to the 60s budget.
- Alternative: the new suite covers only adapter/unavailable behavior; SC-06's discrimination of refusal-from-crash stays in test-dispatch-guard.py (one crash-vs-refusal case each), with SC-06 verify pointing there.

## S-3 (low, leave) D-01 contract restated in T-01, T-03, SC-01, SC-07
- Fields/phrases ("nothing was checked", no dedup, deny precedence) appear in 4 places; T-03 says "Record D-01's exact fields". Drift risk is small since D-01 is the signed source; leave, optionally have T-03 reference D-01 by id rather than re-listing.

## Not flagged
Settled items per dispatch; T-03 cumulative verify rerunning T-01/T-02 suites is explicitly the cumulative-verify owner.
