# FEAT-67 — clean-checkout implementation-pin receipts

Written 2026-09-27T14:54:19+00:00, AFTER the pin it names; this file is not inside `e9ed16de`.

- implementation pin: `e9ed16de7d685acbdd7d59255530537ad987e97d`
- baseline: `00c7219e4026081e70614647f3f98726afb2c381` (the signed plan; = origin/main at the signed plan)
- pin checkout: `/Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/feat67-cleanpin-e9ed16de` (detached, `git status --porcelain` empty)
- baseline checkout: `/Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/feat67-base-00c7219e` (detached)
- baseline receipts: captured at the baseline in the feature worktree before any production edit (`/tmp/feat67-baseline.py` → `/tmp/feat67-baseline.json`); exit status and sha1 of stdout/stderr per suite.

## Owning suites at the pin vs baseline (SC-02)

Compared after replacing each checkout's own absolute root with `<checkout>` on both sides: three `ok` lines in
`test-validate-digest.py` print the agent file's absolute path, which names the checkout that ran the suite and nothing else.
The sha1 columns are of the raw bytes and so differ for that one suite; the `identical` column is the normalised comparison.

| suite | exit base→pin | stdout sha base / pin | stderr sha base / pin | identical |
|---|---|---|---|---|
| `tests/integration/test-check-domain.py` | 0→0 | 9f3a2d504473 / 9f3a2d504473 | da39a3ee5e6b / da39a3ee5e6b | yes |
| `tests/integration/test-check-domain-artifact.py` | 0→0 | 192c92446a82 / 192c92446a82 | da39a3ee5e6b / da39a3ee5e6b | yes |
| `tests/integration/test-check-domain-claims.py` | 0→0 | 1810b823ba32 / 1810b823ba32 | da39a3ee5e6b / da39a3ee5e6b | yes |
| `tests/integration/test-check-domain-grant.py` | 0→0 | 1e6c60523185 / 1e6c60523185 | da39a3ee5e6b / da39a3ee5e6b | yes |
| `tests/integration/test-check-domain-post.py` | 0→0 | 8b05b2b516ca / 8b05b2b516ca | da39a3ee5e6b / da39a3ee5e6b | yes |
| `tests/integration/test-check-domain-worktree-parity.py` | 0→0 | 7d5700af43df / 7d5700af43df | da39a3ee5e6b / da39a3ee5e6b | yes |
| `tests/integration/test-check-domain-worktree.py` | 0→0 | 5eb8753b929f / 5eb8753b929f | da39a3ee5e6b / da39a3ee5e6b | yes |
| `tests/integration/test-check-domain-approval.py` | 0→0 | 058ca85441ab / 058ca85441ab | da39a3ee5e6b / da39a3ee5e6b | yes |
| `tests/integration/test-bash-write-guard.py` | 0→0 | 949649a8098b / 949649a8098b | da39a3ee5e6b / da39a3ee5e6b | yes |
| `tests/integration/test-check-omp-port.py` | 0→0 | dcc345eb29fb / dcc345eb29fb | da39a3ee5e6b / da39a3ee5e6b | yes |
| `tests/integration/test-validate-digest.py` | 0→0 | fafde967deed / bee5dae881b1 | da39a3ee5e6b / da39a3ee5e6b | yes |

All identical (normalised): **yes** (11/11).

### Raw-byte differences, exact lines (ledger: the ruled checkout-root normalisation, FEAT-66 D-09)

`tests/integration/test-validate-digest.py`:
```
-ok    [severity_max enum] /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-67-complex-function-second-wave/.omp/agents/harness-code-reviewer.md
-ok    [severity_max enum] /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-67-complex-function-second-wave/.omp/agents/harness-security-reviewer.md
-ok    [severity_max enum] /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-67-complex-function-second-wave/.omp/agents/harness-ui-reviewer.md
+ok    [severity_max enum] /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/feat67-cleanpin-e9ed16de/.omp/agents/harness-code-reviewer.md
+ok    [severity_max enum] /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/feat67-cleanpin-e9ed16de/.omp/agents/harness-security-reviewer.md
+ok    [severity_max enum] /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/feat67-cleanpin-e9ed16de/.omp/agents/harness-ui-reviewer.md
```

## SC-01: the plan's inline grade assertion (T-01 verify) at the pin — green

run in the pin checkout → exit 0
```
FEAT-67 grades [('.claude/skills/harness/bin/check-domain.py', 'approval_guard', 4), ('.claude/skills/harness/bin/check-domain.py', '_matching_grants', 4), ('.claude/skills/harness/bin/check-domain.py', '_approval_guard_applies', 5), ('.claude/skills/harness/bin/check-domain.py', '_approval_grants', 5), ('.claude/skills/harness/bin/check-domain.py', '_approval_disk_text', 5), ('.claude/skills/harness/bin/check-domain.py', '_governed_fragment', 4), ('.claude/skills/harness/bin/check-domain.py', '_deny_fragment', 5), ('.claude/skills/harness/bin/check-domain.py', '_approval_write_rule', 5), ('.claude/skills/harness/bin/check-domain.py', '_write_key_rule', 5), ('.claude/skills/harness/bin/check-domain.py', '_write_heading_rule', 4), ('.claude/skills/harness/bin/check-domain.py', '_approval_edit_rule', 4), ('.claude/skills/harness/bin/check-domain.py', '_edit_overlap_limb', 4), ('.claude/skills/harness/bin/check-domain.py', '_signature_child_keys', 4), ('.claude/skills/harness/bin/check-domain.py', '_edit_introduce_limb', 2), ('.claude/skills/harness/bin/check-omp-port.py', 'check', 5), ('.claude/skills/harness/bin/check-omp-port.py', 'agents_md_errors', 5), ('.claude/skills/harness/bin/check-omp-port.py', 'config_errors', 2), ('.claude/skills/harness/bin/check-omp-port.py', 'agent_files_errors', 4), ('.claude/skills/harness/bin/check-omp-port.py', 'agent_file_errors', 2), ('.claude/skills/harness/bin/check-omp-port.py', 'agent_skills_errors', 5), ('.claude/skills/harness/bin/check-omp-port.py', 'provider_errors', 5), ('.claude/skills/harness/bin/check-omp-port.py', 'provider_file_errors', 4), ('.claude/skills/harness/bin/check-omp-port.py', 'skills_link_errors', 4), ('.claude/skills/harness/bin/check-omp-port.py', 'extension_errors', 4), ('.claude/skills/harness/bin/check-omp-port.py', 'door_errors', 5), ('.claude/skills/harness/bin/validate-digest.py', 'parse_digest', 4), ('.claude/skills/harness/bin/validate-digest.py', '_digest_body', 4), ('.claude/skills/harness/bin/validate-digest.py', '_next_field', 4), ('.claude/skills/harness/bin/validate-digest.py', '_inline_value', 5), ('.claude/skills/harness/bin/validate-digest.py', '_spanning_value', 4), ('.claude/skills/harness/bin/validate-digest.py', '_block_list', 4), ('.claude/skills/harness/bin/validate-digest.py', '_block_list_step', 4), ('.claude/skills/harness/bin/validate-digest.py', '_continued_item', 5)]
```

## SC-01 / SC-04 red-first: the same assertion run in the baseline checkout — red

run in the baseline checkout (the three retained drivers grade 1 there) → exit 1
```
FEAT-67 grades [('.claude/skills/harness/bin/check-domain.py', 'approval_guard', 1), ('.claude/skills/harness/bin/check-omp-port.py', 'check', 1), ('.claude/skills/harness/bin/validate-digest.py', 'parse_digest', 1)]
```

## Test kinds at the pin (change_type cross_module: unit + integration both required)

Run in the feature worktree at `e9ed16de` via the configured runner
(`.agents/skills/harness/bin/run-unit-tests.py`): `--kind unit` exit 0 (42 files, 747 PASS lines,
no FAIL outside the mutation-proof harness's own expected reddening in
`test-factory-claim-mutation.py`, which itself PASSes); `--kind integration` exit 0 (70 files,
`0 failure(s)`).
