# FAIL — T-01 does not fully satisfy SC-01/SC-02

Reviewed immutable `3dd8bb677bb2936361e3952030fc24f15bf9afc6..21e064c9475e35a4abfdd71b5b5cdd23517c0659`; merge-base confirmed. Current feature.json agrees with dispatch pin. Six commits inspected; no `[harness:human]` commits. Only working-tree modification was feature.json. No checkout created; no tests, grading, lint or builds executed by this reader.

## Stage 1 — acceptance findings

1. **High · substance · T-01 / SC-01:** `.claude/skills/harness/bin/validate-digest.py:2495,2506` excludes legitimate filenames containing whitespace. For example, run_pool emits `MUTATED fixtures/my case.json` verbatim (`run_pool.py:134`; FAIL basenames likewise at :113). If buried above 20 subsequent lines, fullmatch of `\S+` drops the file entirely, recreating the missing diagnosis. Must preserve these producer-valid file lines. The simplify rationale's one-token producer assumption is false; excluding case output cannot weaken SC-01.
2. **High · substance · T-01 / SC-02:** `tests/integration/test-validate-digest.py:6533-6546,6569` has a one-shot in-process timer, not a watchdog independent of child readiness. If timeout forwarding is removed and child initialization is delayed beyond two seconds, its pid file is absent/empty when the timer fires; the exception is swallowed, the timer never retries, and the subsequently started sleeping child hangs the regression indefinitely. No parent probe isolation/process-group kill-and-reap exists. Must make missing-timeout probes bounded regardless of readiness timing. This is acceptance failure, not merely departure from signed HOW.
3. **Low · form · T-01 / SC-01/SC-02:** receipt provenance is weaker than claimed: `notes/receipts/red.txt:1` names build-entry 3769919f and reconstructed base callsites, not an execution against the exact immutable base; green.txt names no immutable fix SHA or separate stderr. Git diff confirms 3769919f's two subject files equal the immutable base, so the observed six `[3,3,3]` reds are meaningful evidence, not missing-helper failures. Preserve that distinction and record exact subjects/commands/streams.

SC inspection: shared 30s rationale and six replacements are present at test lines 1025,3033,3066,3286-3288,3316-3318. Default/0.05/0.10 probes execute all six enclosing-function callsites; six blocking probes retain real subprocess helpers. Supplied green has 14 passing cases; red has gate failure, six observed-budget failures and six blocking failures (several unwind as FileNotFoundError). These are supplied observations, not rerun results. Tail slicing, stdout+stderr concatenation, refusal return 2, rerun selection and 1800s timeout remain unchanged. Classification unchanged, consistent with supplied audit receipt.

## Simplify/amendment judgement

Existing `--only run_bug2253_cases` reuse is approved and acceptance-preserving. Timing only the real helper call appropriately excludes setup latency. Readiness as pid channel alone does not prove the child reached its intentional block: TimeoutExpired can reflect slow startup; the one-shot timer also loses the watchdog guarantee. One-token matching is not acceptance-preserving (finding 1).

## Stage 2 / mechanical evidence / principles

Quality stage withheld because Stage 1 fails. Main subsequently supplied an existing grading result: `code-grade.py --base 3769919f --head 16ec2047`, exit 0, `PASSING: 21`, no `RESULT: FAIL` rows. Main reports commit-content verification that the endpoint differences contain only records (16ec2047..21e064c9 only plan.yaml; 3dd8bb67..3769919f no Python). Thus this is supplied evidence for a byte-equivalent Python grading range, not an exact-endpoint rerun or reader-executed check; code_grade is pass.

Delete First (read this run): no additional abstraction is requested; fixes should stay at the existing diagnostic and probe seams.

## Open questions

None requiring an operator decision. No out-of-scope defect identified. QA owns execution. Must-fixes are findings 1–2.
