# Security review — BUG-1898 validate-c1

**PASS.** The pinned lifecycle diff has a real security surface (hook payload identity, cross-run claim ownership, registry mutation, child-release recovery commands, and corrupt-state handling), but I found no exploitable security defect in the canonical range or focused c1 delta.

## Scope and evidence

- Reviewed `merge-base(origin/main, 81dbd81d21b04b6fdcba2435d2e73a12ec72fd2e)..81dbd81d21b04b6fdcba2435d2e73a12ec72fd2e` and `84c3a6cbe74c7c27337d4372a68be60fca834118..81dbd81d21b04b6fdcba2435d2e73a12ec72fd2e`, including `validate-digest.py`, registry interfaces, and both claim-preservation test surfaces. The worktree HEAD was later than the review pin, but these four reviewed implementation/test files were byte-identical between pin and HEAD.
- Exact binding is fail-closed: non-BLOCKED governed returns lacking either a trimmed string `harness_feature` or `harness_agent_id` are refused, and no lookup or release occurs. Releases additionally constrain persona, feature, and runtime agent id; child lookup constrains exact `parent_agent_id` and feature.
- Corrupt/unreadable registry state is checked through strict reads before any writer. Dispatch-capable leads/orchestrator cannot return a non-BLOCKED result when child state is unknowable. Leaves are not denied merely because they cannot hold children, and neither path mutates the unreadable file. A BLOCKED parent retains the operator escape without claiming successful completion.
- Recovery output uses argv-safe shell quoting and names the individual child by feature, agent id, and claim id; it does not recommend persona-wide or bulk release. No shell interpolation, user-controlled URL, credential material, new dependency, PII/log disclosure, or authorization widening was introduced.
- Targeted evidence: `python3 tests/integration/test-validate-digest.py` passed all cases, including 81/81 BUG-1898 exact-release checks; `python3 tests/integration/test-suite-claim-preservation.py` passed and proved every unrelated seeded claim byte-identical after the real suite run. These tests exercise missing identity, cross-worktree ownership, parent/child isolation, corrupt-state immutability, exact recovery targeting, and leaf non-denial.
- SC-07 remains a pending operator-only live OMP merge gate. No receipt was observed or fabricated, and this is not a panel finding.

## Threat model

| Boundary | STRIDE | Result |
|---|---|---|
| Hook payload identity → claim selector | S/T/E | Mitigated by exact feature + runtime-id binding and refusal without both values. |
| Registry read → release mutation | T/I/D | Mitigated by strict pre-read, lock-backed exact release, and preservation on unreadability. |
| Parent return → live child ownership | T/E/D | Mitigated for dispatch-capable personas; unknown state blocks successful return while BLOCKED remains available. |
| Recovery diagnostic → operator command | T/E | Mitigated by exact claim identifiers and shell-safe argv rendering; no broad release appears. |
| Test hook executions → live checkout registry | T/D | Mitigated by isolated roots; preservation reproduction shows unrelated live rows unchanged. |

Findings: none. Severity maximum: **info** (scoped in, no defect found). Must-fix: none. Open questions: none.
