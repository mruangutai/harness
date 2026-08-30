# FEAT-43 pinned security review — FAIL

**BLUF:** The pinned change has one deterministic, must-fix Tampering gap: both diff-mode graders parse Git's line-oriented, quoted pathname output, so a contributor can hide a changed Python file from the mandatory grade gate by giving it a tab or newline-bearing name. Owner-manifest selection, subprocess construction, review-policy failure handling, secrets, and rendered output otherwise close cleanly.

## Pin and complete-file census

Both requested objects resolve: base `df63193f7ec9798d9660904e0e4e7c78d52358f5`; review `1ac1bd03fc73c004fdde4b684ac8a18d3bd43f2c`. `git diff --name-only df63193..1ac1bd03fc73c004fdde4b684ac8a18d3bd43f2c` returns exactly 48 paths. Every path was examined before scoping:

- **Agent delivery (12; instruction injection surface, only the declared skill-list addition):** `.claude/agents/{harness-ai-dev,harness-backend-dev,harness-code-reviewer,harness-data-engineer,harness-dev-ops,harness-frontend-dev}.md`; `.omp/agents/{harness-ai-dev,harness-backend-dev,harness-code-reviewer,harness-data-engineer,harness-dev-ops,harness-frontend-dev}.md`.
- **Human/agent interpreted guidance (3):** `.claude/skills/harness-code-review/SKILL.md`, `.claude/skills/harness-code-risk-grading/SKILL.md`, `.harness/glossary.md`.
- **Runtime/enforcement (6; in scope):** `.claude/skills/harness/bin/{check-plan-routes.py,code-grade.py,code_grade.py,gate_policy.py,run-unit-tests.sh,validate-digest.py}`.
- **Targeted tests (5):** `.claude/skills/harness/bin/{test-check-plan-routes.py,test-code-grade-cli.py,test-code-grade.py,test-gate-policy.py,test-validate-digest.py}`.
- **Configuration/contract (3):** `.harness/harness.json`, `.harness/harness/features/FEAT-43-code-risk-grading/answers/Q1-t09-owner-resolver.md`, `.harness/harness/features/FEAT-43-code-risk-grading/plan.yaml`.
- **Evidence outputs (19; data-exposure/rendering surface):** feature notes `qa-build-qa{,-rerun}.md`; `receipt-harness-backend-dev-{T-01-c0,T-01-c1,T-02-c0,T-02-c1,T-06-c0,T-07-c0,T-07-c1,simplify-apply,simplify-efficiency,simplify-reuse}.md`; `receipt-harness-dev-ops-{T-03-c0,T-03-c1,simplify-altitude,simplify-simplification}.md`; `research-T-10-t10-product.md`; and `ship-review-t06-eng.{html,md}`.

## Must-fix finding

### SEC-01 — med — Git pathname quoting lets a contributor omit changed Python from the grade gate

- **Pinned evidence:** `.claude/skills/harness/bin/code-grade.py:76-78` consumes `git diff --name-only` with `splitlines()` and then requires the rendered line to end in `.py`. `.claude/skills/harness/bin/code_grade.py:303-312` independently consumes `git diff --name-status` with `splitlines()` and `split("\t")`. Neither invocation requests `-z`, and neither parser handles Git's C-quoted pathname representation.
- **Attacker/input/state → wrong outcome:** a contributor who can add a file to a proposed commit names an executable Python file with an embedded newline or tab and gives it a newly introduced grade-1 function. Git quotes that pathname in the default line-oriented output. The CLI preflight no longer sees a string ending in `.py`, while the library either omits or mis-splits it; the file is never parsed, never appears under `UNGRADED`, and the grading command can exit clean. The contributor bypasses the review gate for that file. This does not itself grant code execution beyond the submitted change, so the unusual pathname precondition and limited impact keep severity at `med`, but it defeats REQ-04/REQ-07's mandatory enforcement and is `must_fix`.
- **STRIDE:** Tampering with the changed-file census; repudiation follows because the report asserts cleanliness without recording the omitted path.
- **Remedy constraint:** both Git consumers must request and correctly parse NUL-delimited output (`-z`), including rename records, and a targeted repository fixture must prove a tab/newline-bearing `*.py` path is graded or loudly ungraded. Fixing only one parser leaves the other fail-open.
- **Owner route:** `harness-eng-lead` to `harness-dev-ops` for `code-grade.py` and `harness-backend-dev` for `code_grade.py` plus their focused tests.

## Other boundary results

- **Subprocess/git:** every new subprocess uses list-form argv with `shell=False`; repository refs in the documented review command are immutable SHAs, closing shell and flag-injection reachability for the shipped path. No credentials enter argv or URLs.
- **Owner/worktree manifest:** `check-plan-routes.py:55-84,704-724` resolves a legitimate linked worktree through `harness_boundary.worktree_owner`, invokes the owner's fixed `check-domain.sh`, refuses an unknown/unreadable owner, and makes branch/owner divergence non-zero. Route strings remain data arguments, not shell text.
- **Policy/digest:** `gate_policy.py:29-64` rejects missing, unreadable, malformed, and unknown gate policy; `validate-digest.py:466-476,768-786,962-977` makes `code_grade` mandatory for the exact code-reviewer persona and returns blocking exit 2 on `GatePolicyError`. The generic internal-error pass-through is pre-existing; the new policy's ordinary failure modes are converted to `GatePolicyError`, so no reachable new fail-open was established.
- **Outputs/secrets:** the full diff contains no credential-, token-, private-key-, or password-shaped value. Several evidence receipts commit the workstation username and absolute checkout path; this is low-value local metadata, not a credential or cross-user data disclosure, and is recorded as assessed rather than raised. The added HTML is static, has no script, and entity-escapes rendered prose.
- **Dependencies/requests/auth:** no dependency, network request, route, session, credential, tenant-data access, redirect, or SSRF surface is introduced.

No open questions.