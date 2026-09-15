# Ship review — BUG-285 canonical artifact readers

## Decision

The signed feature is complete and the final fix-team panel is clean at review SHA `5be21a432b87ed648c0bed50fbf9a2642c84e0a9`. The permanent AST audit reports 120 canonical rows, 42 justified exemptions, zero migrations, and zero unresolved reader sites across 69 Python files. No PR was created, merged, or closed.

## Done when — by perspective

| Perspective | Signed outcome | Verdict | Criteria and evidence |
| --- | --- | --- | --- |
| Operator | Every classified dispatchable and enforcement reader uses the canonical seam without behavior drift. | Met | SC-04: T-03/T-04 signed gates and historical red proof in `notes/receipt-harness-backend-dev-fix-c1.md`. SC-05: the 29-program normalized enforcement comparison passed byte-for-byte before retirement and its negative control failed as expected in `notes/receipt-main-session-fix-c1.md`; final T-07 gate passed. |
| Code maintainer | One dependency-light accessor module owns the readers, and one AST guard names bypasses and remedies. | Met | SC-01/02/03: final QA and two-stage code review pass in `notes/review-harness-qa-c1.md` and `notes/review-harness-code-reviewer-c1.md`; the accessor-module raw-parser mutant has genuine red evidence, the final audit is zero-drift, and strict JSON/YAML/error contracts pass targeted gates. |
| Reader / reviewer / QA | Semantic and mechanical work are separately inspectable with fail-first evidence and retained inverse coverage. | Met | SC-06: separate T-03 semantic, T-04 relocation, T-06 semantic, and T-07 ownership commits/receipts. SC-07: issue 285's comment-bearing permissive-YAML/strict-JSON inverse and historical red proof are in `tests/unit/test-feature-json-reader.py` and `notes/receipt-harness-backend-dev-fix-c1.md`. Final fix-team digest has `matrix_ok: true`, no coverage gaps, and no must-fix findings. |

The validation goal-check initially graded all three perspectives unmet because F-01 through F-04 were open. Fix round c1 resolved all four; QA re-ran the correct repository-policy matrix and the code reviewer completed both stages over tip `5be21a43`. Per the two-grade limit, PM goal-check was not run a third time.

## What landed

- Planning: the refreshed nine-task plan covered all Python surfaces exposed by PR #1688, retained issue #1682 hardening, and kept semantic migrations separate from mechanical relocation.
- Accessor layer: `artifact_accessors.py` is the sole public owner of feature JSON, harness JSON, plan, fleet, manifest-domain, frontmatter, OMP-config, hook-payload, and GitHub JSON readers, plus the canonical harness JSON writer. Legacy reader/error definitions were removed without aliases, re-exports, or duplicate bodies.
- Strictness: duplicate keys, non-standard JSON constants, malformed data, non-UTF-8 bytes, wrong nested GitHub record shapes, and caller-specific absence/error behavior have targeted unit and integration coverage.
- Manifest handling: the existing `manifest_domains` seam supports all-role aggregation and an immutable typed view without exposing raw mappings or adding a second accessor; macOS system Python 3.9 import compatibility is pinned.
- Enforcement: all PR #1688-converted hooks, gates, and validators use the accessor layer. The temporary 29-case byte-comparison harness was retired only after a 29/29 pass; the permanent AST audit includes discriminating raw-call, alias, discovery, routing, and state-reader mutants.
- Documentation: DEC-174 now includes `branch-create-gate.py`; its generated index matches.
- Simplify: four independent angles found one safe cleanup, the stale migration-history comment in `factory_decompose.py`; exact T-02 verification remained green.
- Validation: the first panel found four substantive issues. Direct and backend fixes landed genuine fail-first evidence, restored the comment-bearing inverse fixture, and closed the AST fail-open shortcut. Final QA, code, security, and UI reviews all pass; UI correctly self-scoped out.

## Verification

Targeted signed gates for T-01 through T-09 passed. The final fix-team panel reviewed repository-policy range `8c3143bd5668ce11186a2a1f8dbe784ff9639d88..5be21a432b87ed648c0bed50fbf9a2642c84e0a9` and reports:

- test matrix: PASS; unit and integration satisfied; no coverage gaps;
- code review: PASS, specification stage then quality stage;
- security: PASS, with SEC-01 assessed and dismissed as outside the signed nested-field contract;
- UI: not applicable after a 152-path census;
- permanent audit: zero unresolved reader sites across 69 Python files;
- project-wide suites, formatters, linters, and builds were intentionally not run.

UAT is not required: this feature changes internal reader, gate, validator, test, and decision-record surfaces, with no rendered or interactive user interface.

## Spend and limits

- Runs: 28, against informational `max_total_runs: 20`. The eight-run overage earned its place: three live-interface gaps were stopped and signed rather than hidden, two downstream regressions were corrected at their owning task, and one validation round closed four findings.
- Wall-clock across recorded runs: 492 minutes.
- Rework: 1 of 3 approved rounds, 64 of 135 approved minutes.
- Rework cycles: 10 of 10. The final permitted cycle ended clean; no further fix cycle is available without an operator-approved raise.
- Tokens: unmeasured, not zero.
- Judgements recorded: 18.

## Questions and residuals

There are no blocking questions. These non-gating residuals are proposed backlog items; unselected rows may be struck by ID.

| ID | Nature | Residual |
| --- | --- | --- |
| B-1 | chore | Make `observations-merge.py` create the per-feature observations parent directory before its first append. |
| B-2 | bug | Repair the governed backend route to `xd://report_issue`; T-09 observed the required report path denied by check-domain. |
| B-3 | bug | Let fix-team handoff validation recognize the run's governed `head_sha`/`tip_sha` until the orchestrator performs the required post-return `review_sha` repin. |
| B-4 | bug | Make governed product-run checkpoint writes reliably mint and preserve `run_uid` plus `.run-identity.json`; the T-07 amendment reproduced a silent missing side effect. |
| B-5 | enhancement | Separately decide whether present top-level `github` or `factory` non-mapping values should be rejected. Validation's SEC-01 was dismissed because the signed scope covered nested parent/issues fields only. |

## Branch state and next gate

The branch has not integrated later `main` changes such as merged PR #1700; that PR changes only BUG-1507's historical `STATE.md` and is unrelated to this feature. The feature branch remains intentionally unmerged. The next gate is the operator's ship-review decision; this run will not merge or close a PR.

## Source disclosure

No report round was spawned. This briefing was assembled from every recorded run digest:

- `runs/2026-09-13-plan-product/digest.md`
- `runs/2026-09-13-plan-apply-c1-product/digest.md`
- `runs/2026-09-14-plan-refresh-product/digest.md`
- `runs/2026-09-14-t09-eng/digest.md`
- `runs/2026-09-14-t02-t04-eng/digest.md`
- `runs/2026-09-14-t03-eng/digest.md`
- `runs/2026-09-14-t03-amend-product/digest.md`
- `runs/2026-09-15-t02-text-eng/digest.md`
- `runs/2026-09-15-t03-eng/digest.md`
- `runs/2026-09-15-t03-amend2-product/digest.md`
- `runs/2026-09-15-t02-shapes-eng/digest.md`
- `runs/2026-09-15-t03-final-eng/digest.md`
- `runs/2026-09-15-t03-amend3-product/digest.md`
- `runs/2026-09-15-t02-manifest-eng/digest.md`
- `runs/2026-09-15-t03-resume2-eng/digest.md`
- `runs/2026-09-15-t02-verify-eng/digest.md`
- `runs/2026-09-15-t04-eng/digest.md`
- `runs/2026-09-15-t05-amend-product/digest.md`
- `runs/2026-09-15-t03-marker-fix-eng/digest.md`
- `runs/2026-09-15-t06-contract-eng/digest.md`
- `runs/2026-09-15-t06-contract-amend-product/digest.md`
- `runs/2026-09-15-t02-manifest-view-eng/digest.md`
- `runs/2026-09-15-t02-pycompat-eng/digest.md`
- `runs/2026-09-15-t07-ownership-amend-product/digest.md`
- `runs/2026-09-15-t08-product/digest.md`
- `runs/2026-09-15-simplify-eng/digest.md`
- `runs/2026-09-15-validate-validator/digest.md`
- `runs/2026-09-15-fix-c1-validator/digest.md`
