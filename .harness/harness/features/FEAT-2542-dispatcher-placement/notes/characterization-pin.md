# FEAT-2542 T-01 characterization pin

The receipt for T-01 Steps 2 and 4: the predicted red set at base source, the observed base run,
and each pin run. Graded by T-01 verify at HEAD.

dec_number: DEC-258
base_sha: 2e7a2c77d61e3ae93180dc6d71a355ff7b85d8f8

## Row inventory

Every assertion plan.yaml T-01 (b) to (e) marks red at base; every other assertion is green.

predicted_red: c38/distill/distill:exit
predicted_red: c38/distill/distill:claim
predicted_red: c38/distill/distill:receipt
predicted_red: c38/distill/missing:cause
predicted_red: c38/distill/other:cause
predicted_red: c38/distill/foreign-feature:cause
predicted_red: c38/distill/no-tree-root:cause
predicted_red: c38/distill/foreign-tree-root:cause
predicted_red: c38/distill/run-reads:run-reads
predicted_red: c38/fail-persona-mismatch/plan:cause
predicted_red: c38/fail-persona-mismatch/plan:remedy
predicted_red: c38/fail-not-found/missing:cause
predicted_red: c38/fail-not-found/missing:remedy
predicted_red: c38/fail-ambiguous/distill:cause
predicted_red: c38/fail-ambiguous/distill:remedy
predicted_red: c38/fail-unreadable-owner/conflicting:cause
predicted_red: c38/fail-unreadable-owner/conflicting:remedy
predicted_red: c38/fail-unreadable-linked/other:cause
predicted_red: c38/fail-unreadable-linked/other:remedy
predicted_red: c38/fail-escaped-unreadable/distill:cause
predicted_red: c38/fail-escaped-unreadable/distill:remedy
predicted_red: c38/fail-escaped-oserror/plan:cause
predicted_red: c38/fail-escaped-oserror/plan:remedy
predicted_red: c39/eng/persona-mismatch/bound:exit
predicted_red: c39/eng/persona-mismatch/bound:claim
predicted_red: c39/eng/persona-mismatch/bound:cause
predicted_red: c39/eng/persona-mismatch/bound:remedy
predicted_red: c39/eng/persona-mismatch/exploit:exit
predicted_red: c39/eng/persona-mismatch/exploit:claim
predicted_red: c39/eng/persona-mismatch/exploit:cause
predicted_red: c39/eng/persona-mismatch/exploit:remedy
predicted_red: c39/eng/not-found/bound:exit
predicted_red: c39/eng/not-found/bound:claim
predicted_red: c39/eng/not-found/bound:cause
predicted_red: c39/eng/not-found/bound:remedy
predicted_red: c39/eng/not-found/exploit:exit
predicted_red: c39/eng/not-found/exploit:claim
predicted_red: c39/eng/not-found/exploit:cause
predicted_red: c39/eng/not-found/exploit:remedy
predicted_red: c39/eng/ambiguous/bound:exit
predicted_red: c39/eng/ambiguous/bound:claim
predicted_red: c39/eng/ambiguous/bound:cause
predicted_red: c39/eng/ambiguous/bound:remedy
predicted_red: c39/eng/ambiguous/exploit:exit
predicted_red: c39/eng/ambiguous/exploit:claim
predicted_red: c39/eng/ambiguous/exploit:cause
predicted_red: c39/eng/ambiguous/exploit:remedy
predicted_red: c39/eng/unreadable-owner/bound:exit
predicted_red: c39/eng/unreadable-owner/bound:claim
predicted_red: c39/eng/unreadable-owner/bound:cause
predicted_red: c39/eng/unreadable-owner/bound:remedy
predicted_red: c39/eng/unreadable-owner/bound:bytes
predicted_red: c39/eng/unreadable-owner/exploit:exit
predicted_red: c39/eng/unreadable-owner/exploit:claim
predicted_red: c39/eng/unreadable-owner/exploit:cause
predicted_red: c39/eng/unreadable-owner/exploit:remedy
predicted_red: c39/eng/unreadable-owner/exploit:bytes
predicted_red: c39/eng/unreadable-linked/bound:exit
predicted_red: c39/eng/unreadable-linked/bound:claim
predicted_red: c39/eng/unreadable-linked/bound:cause
predicted_red: c39/eng/unreadable-linked/bound:remedy
predicted_red: c39/eng/unreadable-linked/exploit:exit
predicted_red: c39/eng/unreadable-linked/exploit:claim
predicted_red: c39/eng/unreadable-linked/exploit:cause
predicted_red: c39/eng/unreadable-linked/exploit:remedy
predicted_red: c39/eng/escaped-unreadable/bound:exit
predicted_red: c39/eng/escaped-unreadable/bound:claim
predicted_red: c39/eng/escaped-unreadable/bound:cause
predicted_red: c39/eng/escaped-unreadable/bound:remedy
predicted_red: c39/eng/escaped-unreadable/exploit:exit
predicted_red: c39/eng/escaped-unreadable/exploit:claim
predicted_red: c39/eng/escaped-unreadable/exploit:cause
predicted_red: c39/eng/escaped-unreadable/exploit:remedy
predicted_red: c39/eng/escaped-oserror/bound:exit
predicted_red: c39/eng/escaped-oserror/bound:claim
predicted_red: c39/eng/escaped-oserror/bound:cause
predicted_red: c39/eng/escaped-oserror/bound:remedy
predicted_red: c39/eng/escaped-oserror/exploit:exit
predicted_red: c39/eng/escaped-oserror/exploit:claim
predicted_red: c39/eng/escaped-oserror/exploit:cause
predicted_red: c39/eng/escaped-oserror/exploit:remedy
predicted_red: c39/validator/not-found/bound:exit
predicted_red: c39/validator/not-found/bound:claim
predicted_red: c39/validator/not-found/bound:cause
predicted_red: c39/validator/not-found/bound:remedy
predicted_red: c40/not-found/distill-run:cause
predicted_red: c40/not-found/distill-run:remedy
predicted_red: c40/not-found/plan-run:exit
predicted_red: c40/not-found/plan-run:claim
predicted_red: c40/not-found/plan-run:cause
predicted_red: c40/not-found/plan-run:remedy
predicted_red: c40/persona-mismatch/distill-run:cause
predicted_red: c40/persona-mismatch/distill-run:remedy
predicted_red: c40/persona-mismatch/plan-run:exit
predicted_red: c40/persona-mismatch/plan-run:claim
predicted_red: c40/persona-mismatch/plan-run:cause
predicted_red: c40/persona-mismatch/plan-run:remedy

## Base run

python3 tests/integration/test-dispatch-guard.py with dispatch-guard.py byte-identical to base_sha
(git diff --quiet base_sha -- dispatch-guard.py exited 0): 300 of 397 cases passed. Every case 1
to 37 assertion, including the rebound cases 30 and 31, passed; the observed set equals the
predicted set (97 lines each), with no prediction corrected.

head_at_base_run: 08ff7671ef8a0682151487287aaa433035619236
base_run_exit: 1
observed_red: c38/distill/distill:exit
observed_red: c38/distill/distill:claim
observed_red: c38/distill/distill:receipt
observed_red: c38/distill/missing:cause
observed_red: c38/distill/other:cause
observed_red: c38/distill/foreign-feature:cause
observed_red: c38/distill/no-tree-root:cause
observed_red: c38/distill/foreign-tree-root:cause
observed_red: c38/distill/run-reads:run-reads
observed_red: c38/fail-persona-mismatch/plan:cause
observed_red: c38/fail-persona-mismatch/plan:remedy
observed_red: c38/fail-not-found/missing:cause
observed_red: c38/fail-not-found/missing:remedy
observed_red: c38/fail-ambiguous/distill:cause
observed_red: c38/fail-ambiguous/distill:remedy
observed_red: c38/fail-unreadable-owner/conflicting:cause
observed_red: c38/fail-unreadable-owner/conflicting:remedy
observed_red: c38/fail-unreadable-linked/other:cause
observed_red: c38/fail-unreadable-linked/other:remedy
observed_red: c38/fail-escaped-unreadable/distill:cause
observed_red: c38/fail-escaped-unreadable/distill:remedy
observed_red: c38/fail-escaped-oserror/plan:cause
observed_red: c38/fail-escaped-oserror/plan:remedy
observed_red: c39/eng/persona-mismatch/bound:exit
observed_red: c39/eng/persona-mismatch/bound:claim
observed_red: c39/eng/persona-mismatch/bound:cause
observed_red: c39/eng/persona-mismatch/bound:remedy
observed_red: c39/eng/persona-mismatch/exploit:exit
observed_red: c39/eng/persona-mismatch/exploit:claim
observed_red: c39/eng/persona-mismatch/exploit:cause
observed_red: c39/eng/persona-mismatch/exploit:remedy
observed_red: c39/eng/not-found/bound:exit
observed_red: c39/eng/not-found/bound:claim
observed_red: c39/eng/not-found/bound:cause
observed_red: c39/eng/not-found/bound:remedy
observed_red: c39/eng/not-found/exploit:exit
observed_red: c39/eng/not-found/exploit:claim
observed_red: c39/eng/not-found/exploit:cause
observed_red: c39/eng/not-found/exploit:remedy
observed_red: c39/eng/ambiguous/bound:exit
observed_red: c39/eng/ambiguous/bound:claim
observed_red: c39/eng/ambiguous/bound:cause
observed_red: c39/eng/ambiguous/bound:remedy
observed_red: c39/eng/ambiguous/exploit:exit
observed_red: c39/eng/ambiguous/exploit:claim
observed_red: c39/eng/ambiguous/exploit:cause
observed_red: c39/eng/ambiguous/exploit:remedy
observed_red: c39/eng/unreadable-owner/bound:exit
observed_red: c39/eng/unreadable-owner/bound:claim
observed_red: c39/eng/unreadable-owner/bound:cause
observed_red: c39/eng/unreadable-owner/bound:remedy
observed_red: c39/eng/unreadable-owner/bound:bytes
observed_red: c39/eng/unreadable-owner/exploit:exit
observed_red: c39/eng/unreadable-owner/exploit:claim
observed_red: c39/eng/unreadable-owner/exploit:cause
observed_red: c39/eng/unreadable-owner/exploit:remedy
observed_red: c39/eng/unreadable-owner/exploit:bytes
observed_red: c39/eng/unreadable-linked/bound:exit
observed_red: c39/eng/unreadable-linked/bound:claim
observed_red: c39/eng/unreadable-linked/bound:cause
observed_red: c39/eng/unreadable-linked/bound:remedy
observed_red: c39/eng/unreadable-linked/exploit:exit
observed_red: c39/eng/unreadable-linked/exploit:claim
observed_red: c39/eng/unreadable-linked/exploit:cause
observed_red: c39/eng/unreadable-linked/exploit:remedy
observed_red: c39/eng/escaped-unreadable/bound:exit
observed_red: c39/eng/escaped-unreadable/bound:claim
observed_red: c39/eng/escaped-unreadable/bound:cause
observed_red: c39/eng/escaped-unreadable/bound:remedy
observed_red: c39/eng/escaped-unreadable/exploit:exit
observed_red: c39/eng/escaped-unreadable/exploit:claim
observed_red: c39/eng/escaped-unreadable/exploit:cause
observed_red: c39/eng/escaped-unreadable/exploit:remedy
observed_red: c39/eng/escaped-oserror/bound:exit
observed_red: c39/eng/escaped-oserror/bound:claim
observed_red: c39/eng/escaped-oserror/bound:cause
observed_red: c39/eng/escaped-oserror/bound:remedy
observed_red: c39/eng/escaped-oserror/exploit:exit
observed_red: c39/eng/escaped-oserror/exploit:claim
observed_red: c39/eng/escaped-oserror/exploit:cause
observed_red: c39/eng/escaped-oserror/exploit:remedy
observed_red: c39/validator/not-found/bound:exit
observed_red: c39/validator/not-found/bound:claim
observed_red: c39/validator/not-found/bound:cause
observed_red: c39/validator/not-found/bound:remedy
observed_red: c40/not-found/distill-run:cause
observed_red: c40/not-found/distill-run:remedy
observed_red: c40/not-found/plan-run:exit
observed_red: c40/not-found/plan-run:claim
observed_red: c40/not-found/plan-run:cause
observed_red: c40/not-found/plan-run:remedy
observed_red: c40/persona-mismatch/distill-run:cause
observed_red: c40/persona-mismatch/distill-run:remedy
observed_red: c40/persona-mismatch/plan-run:exit
observed_red: c40/persona-mismatch/plan-run:claim
observed_red: c40/persona-mismatch/plan-run:cause
observed_red: c40/persona-mismatch/plan-run:remedy

## Pin run
tested_sha: d23f372898d0129b4e89efe49a1bc87e6e300a73
pin_run_exit: 0
397 of 397 cases passed
test-lead-start-return_exit: 0
test-lead-start-preflight_exit: 0
test-broad-catch-census_exit: 0

## Fix round c1 row inventory

Validate c0 ruling (notes/answers-2026-11-26-validate-c0.md): cases 42 and 43, predicted before
the base run. At base the dispatcher's claim feature is read by `_dispatcher_feature`, so a null
or empty feature finds no distill run: the bound child is refused by the unbound-marker rule
(exit and claim green) and the exploit child proceeds. The omitted feature is LEGACY_FEATURE at
base and at the pin (green), as is the ordering witness c43/ok. At base c43/not-found is refused
by the registered-run preflight, never by placement.

predicted_red: c42/null-feature/bound:cause
predicted_red: c42/null-feature/bound:remedy
predicted_red: c42/null-feature/exploit:exit
predicted_red: c42/null-feature/exploit:claim
predicted_red: c42/null-feature/exploit:cause
predicted_red: c42/null-feature/exploit:remedy
predicted_red: c42/empty-feature/bound:cause
predicted_red: c42/empty-feature/bound:remedy
predicted_red: c42/empty-feature/exploit:exit
predicted_red: c42/empty-feature/exploit:claim
predicted_red: c42/empty-feature/exploit:cause
predicted_red: c42/empty-feature/exploit:remedy
predicted_red: c43/not-found/run-preflight:cause

## Fix round c1 base run

python3 tests/integration/test-dispatch-guard.py (with cases 42 and 43) run with DISPATCH_GUARD_BIN
pointing at an isolated_bin copy whose dispatch-guard.py is `git show base_sha:` of it (cmp equal);
the real dispatch-guard.py was not touched. 337 of 426 cases passed, 89 FAIL lines. The 13 FAIL
lines of cases 42 and 43 are below and equal the c1 predictions. The other 76 are the original
97 minus the 21 escaped-state and run-reads assertions, whose fixtures build their own guard from
an isolated_bin copy of the live bin and so ran the live guard; their base red is the Base run
above. No assertion outside the predicted set failed. Run against the validate c0 pin's guard (the
live file before this round's guard edit), the suite failed exactly the 14 null- and empty-feature
assertions; null-feature/bound proceeded and claimed.

c1_head_at_base_run: 7abee7d9ec596cc59374242a79bcffb4ab7c63a6
c1_base_run_exit: 1
observed_red: c42/null-feature/bound:cause
observed_red: c42/null-feature/bound:remedy
observed_red: c42/null-feature/exploit:exit
observed_red: c42/null-feature/exploit:claim
observed_red: c42/null-feature/exploit:cause
observed_red: c42/null-feature/exploit:remedy
observed_red: c42/empty-feature/bound:cause
observed_red: c42/empty-feature/bound:remedy
observed_red: c42/empty-feature/exploit:exit
observed_red: c42/empty-feature/exploit:claim
observed_red: c42/empty-feature/exploit:cause
observed_red: c42/empty-feature/exploit:remedy
observed_red: c43/not-found/run-preflight:cause

## Pin run (fix round c1)
tested_sha: b27cbcc6e103f058e1e8e060893a5ecc74f9106b
pin_run_exit: 0
426 of 426 cases passed
test-lead-start-return_exit: 0
test-lead-start-preflight_exit: 0
test-broad-catch-census_exit: 0
