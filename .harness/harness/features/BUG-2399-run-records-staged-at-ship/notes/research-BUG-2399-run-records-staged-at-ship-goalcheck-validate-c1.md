# BUG-2399 — goalcheck, validate c1

**FAIL: SC-02 and DEC-238 land; SC-01 and SC-03 are partial.** Ordinary-tree staging works, but a retained subtree can be silently omitted. The approved historical-removal clause also has no removal to demonstrate. No fixes, replanning or tests were performed by PM.

Review pin: `9db1ba98209df49017e73fae13da56f3e240086c`; base: `9eb07b4f3cd235c234a10edddbfe5542c1e85fba`. Paths below are relative to the assigned PRODUCT checkout; evidence notes are feature-local.

## Perspective outcomes

- **PARTIAL — operator (SC-01, SC-02; T-01):** automatic staging, missing-path reporting and nonmutating previews pass for ordinary readable trees. QA's pinned unit receipt and named assertions prove those behaviors; silent traversal errors leave the promise of every retained record unmet (`notes/review-harness-code-reviewer-c1.md:17`; pruner `:183`).
- **PARTIAL — code maintainer (SC-03; T-01):** red-first staging/refusal regressions, preserved pruning/safety code and matching automatic-staging instructions are evidenced, but literal removal of a manual force-add cannot be demonstrated because none existed at base (`.omp/commands/harness-ship.md`, base `:1-54`, pin `:43-59`).

## Criterion evidence

- **SC-01 partial (automated):** QA DIGEST names `tests/unit/test-prune-run-evidence.py:194,204,320`; its unit manifest records the pin, runner exit 0 and this completed file. `notes/review-harness-qa-c1.md:9-18` reports 36 passing checks. `notes/red-first-T-01.md:15-24,53-84` records genuine base assertion failures; PM measured matching SHA-256 identities for base pruner, pinned pruner and pinned test. **Substance / T-01 / SC-01:** a recorded run with a readable digest but an unenumerable surviving qa/ directory can return success after staging other files, omitting its manifest. `_run_files` uses `os.walk` without `onerror` (pin pruner `:176-188`); reviewer independently identifies this exact scenario (`notes/review-harness-code-reviewer-c1.md:17`). QA confirmed no executed traversal-error case. This is an inspection-supported counterexample, not a PM-executed probe. Reviewer calls it medium/advisory; that severity is unchanged, but an ordinary-tree pass does not discharge the criterion's universal outcome. Remediation belongs to main-session-direct T-01, not an owning dev; evidence gap returns to QA after any authorized repair.
- **SC-02 met (automated):** QA DIGEST names `evidence_refused` at test `:239` (both normal and dry-run, two missing paths, unchanged files/index) and `evidence_complete` at `:248`. Same pinned unit receipt and red-first note bind green and genuine red evidence. Pruner `:163-167,216-220` checks absence on disk before mutation and names all missing paths.
- **SC-03 partial (inspection):** reviewer evidence `notes/review-harness-code-reviewer-c1.md:11-13` and the pinned base diff show unchanged keep/pin/explicit-keep selection, existing refusal and symlink deletion logic; dry-run exits before Git. Pin ship command `:43-59` preserves both invocations and the existing human commit, adding automatic records. Only DEC-238's ship bullet changes in DECISIONS.md; index changes are subsequent +4 line offsets. **Form / T-01 / SC-03, requiring explicit scope disposition:** base ship command has no manual force-add instructions; the patch adds guidance, not their removal. Reviewer/QA treat this as already-satisfied absence, but that does not establish the literal approved removal action. I retain partial rather than silently narrowing it. No production defect or production rerun is alleged for this clause; Main/operator must explicitly dispose of its false historical premise.

## Decision dispositions

**DEC-238 amend met — inspection:** plan `decisions_affected[0]`, clause “Ship keeps the record and drops the rest”, successor D-01, owner T-01. At `9db1ba98209df49017e73fae13da56f3e240086c:.harness/harness/docs/DECISIONS.md:8058-8070`, the replacement ship bullet describes all non-UI retention, automatic force-staging and exit-2 missing-evidence refusal. The pinned diff changes no other decision bullet; Abandon remains at `:8054-8057`. DEC-174/179/225/254/187 are keep rows and are not landing-graded (DEC-254).

## Evidence boundaries and stated claims

- QA source: terminal DIGEST plus `notes/review-harness-qa-c1.md`; receipt: `runs/2026-11-23-02-validate-validator/qa/manifest-unit.json` (`tested_commit` is the pin; `runner_exit: 0`). PM collected evidence only.
- QA subsequently reported the exact second T-01 verify command, `python3 .claude/skills/harness/bin/gen-decisions-index.py --stdout | diff - .harness/harness/docs/DECISIONS-INDEX.md`, with empty output/diff exit 0 at `3fa183eb6e4efa39dab012280bd42cfbf541d536`, not at the pin. PM inspected an empty pin-to-that-commit diff for the docs and generator. This is transferred-input evidence, not claimed re-execution at the pin; QA's original artifact omits this later receipt.
- Inspected claims: failed Git add returns 1, evidence refusal 2 (`pruner:48-50,198-202`); unsafe run ids are excluded (`:170-173`); only top-level run ui/ is excluded, so nested qa/ui/ remains eligible (`:183-187`); missing means disk-file absence, not invalid hash (`:163-167`). QA explicitly reports these edge claims lack dedicated executed coverage (`notes/review-harness-qa-c1.md:20-29`); no extra criterion or new scope is invented for them.
- PRODUCT `docs/spec.md`, `docs/decisions.md`, `docs/architecture.md` are absent on disk and absent at the pin. No contents or substitute product guidance are assumed. Governing Harness decisions were consulted for the declared Harness surfaces. `notes/simplify-pass.md` reports four empty reader findings, not behavioral verification.

## Open questions

- **Main/operator, blocking full SC-03 completion:** what explicit disposition should replace or waive the approved removal action whose target never existed at base? No authority change has been made by this goalcheck. The substantive SC-01 omission is separately routed to T-01 and cannot be repaired by that wording disposition.
