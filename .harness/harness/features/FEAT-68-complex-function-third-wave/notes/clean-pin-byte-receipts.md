# FEAT-68 — clean-checkout implementation-pin receipts

Written 2026-09-27T18:04:15+00:00, AFTER the pin it names; this file is not inside `9ab1813e`.

- implementation pin: `9ab1813e86067ca4a21a84f49364cf4f453055b4`
- baseline: `e655f14a56a14bf1777cae55a19195c9af10505d` (the signed plan; = origin/main at the signed plan)
- pin checkout: `/Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/feat68-cleanpin-9ab1813e` (detached, `git status --porcelain` empty)
- baseline checkout: `/Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/feat68-base-e655f14a` (detached)
- baseline receipts: captured in the clean detached baseline checkout (`git status --porcelain` empty) (`/tmp/feat68-baseline.py` → `/tmp/feat68-baseline.json`); exit status and sha1 of stdout/stderr per suite.

## Owning suites at the pin vs baseline (SC-02)

Compared after replacing each checkout's own absolute root with `<checkout>` on both sides: one stderr line in each of three suites names a fresh `mkdtemp()` directory (normalised to `<tmpdir>`), `test-artifact-accessors.py`'s unittest footer carries a wall-clock (`Ran N tests in <t>s`), and three `ok` lines in
`test-validate-digest.py` print the agent file's absolute path, which names the checkout that ran the suite and nothing else.
The sha1 columns are of the raw bytes and so differ for that one suite; the `identical` column is the normalised comparison.

| suite | exit base→pin | stdout sha base / pin | stderr sha base / pin | identical |
|---|---|---|---|---|
| `tests/integration/test-anchor-directions.py` | 0→0 | 91340aa4ad88 / 91340aa4ad88 | da39a3ee5e6b / da39a3ee5e6b | yes |
| `tests/integration/test-bash-write-guard.py` | 0→0 | 949649a8098b / 949649a8098b | da39a3ee5e6b / da39a3ee5e6b | yes |
| `tests/integration/test-board-lifecycle.py` | 0→0 | f2846c1baf3b / f2846c1baf3b | da39a3ee5e6b / da39a3ee5e6b | yes |
| `tests/integration/test-branch-create-gate.py` | 0→0 | 070f38e3ccb1 / 070f38e3ccb1 | da39a3ee5e6b / da39a3ee5e6b | yes |
| `tests/integration/test-check-domain-approval.py` | 0→0 | 058ca85441ab / 058ca85441ab | da39a3ee5e6b / da39a3ee5e6b | yes |
| `tests/integration/test-check-domain-artifact.py` | 0→0 | 192c92446a82 / 192c92446a82 | da39a3ee5e6b / da39a3ee5e6b | yes |
| `tests/integration/test-check-domain-claims.py` | 0→0 | 1810b823ba32 / 1810b823ba32 | da39a3ee5e6b / da39a3ee5e6b | yes |
| `tests/integration/test-check-domain-grant.py` | 0→0 | 1e6c60523185 / 1e6c60523185 | da39a3ee5e6b / da39a3ee5e6b | yes |
| `tests/integration/test-check-domain-post.py` | 0→0 | 8b05b2b516ca / 8b05b2b516ca | da39a3ee5e6b / da39a3ee5e6b | yes |
| `tests/integration/test-check-domain-worktree-parity.py` | 0→0 | 7d5700af43df / 7d5700af43df | da39a3ee5e6b / da39a3ee5e6b | yes |
| `tests/integration/test-check-domain-worktree.py` | 0→0 | 5eb8753b929f / 5eb8753b929f | da39a3ee5e6b / da39a3ee5e6b | yes |
| `tests/integration/test-check-domain.py` | 0→0 | 9f3a2d504473 / 9f3a2d504473 | da39a3ee5e6b / da39a3ee5e6b | yes |
| `tests/integration/test-check-plan-routes.py` | 0→0 | 7de338d7b1b0 / 7de338d7b1b0 | da39a3ee5e6b / da39a3ee5e6b | yes |
| `tests/integration/test-check-state-entry.py` | 0→0 | d6ff164f5622 / d6ff164f5622 | da39a3ee5e6b / da39a3ee5e6b | yes |
| `tests/integration/test-check-state-feat59.py` | 0→0 | 5a34329ad6ed / 5a34329ad6ed | da39a3ee5e6b / da39a3ee5e6b | yes |
| `tests/integration/test-check-state-handoff.py` | 0→0 | d68dca455607 / d68dca455607 | da39a3ee5e6b / da39a3ee5e6b | yes |
| `tests/integration/test-check-state-inv26.py` | 0→0 | edd834ea9673 / edd834ea9673 | da39a3ee5e6b / da39a3ee5e6b | yes |
| `tests/integration/test-check-state-plans.py` | 0→0 | 7c9b05df131a / 7c9b05df131a | da39a3ee5e6b / da39a3ee5e6b | yes |
| `tests/integration/test-check-state-records.py` | 0→0 | 82b3967fbc2d / 82b3967fbc2d | da39a3ee5e6b / da39a3ee5e6b | yes |
| `tests/integration/test-check-state-table.py` | 0→0 | 66f526ae3414 / 66f526ae3414 | da39a3ee5e6b / da39a3ee5e6b | yes |
| `tests/integration/test-check-state-worktrees.py` | 0→0 | 72b810ba8d6f / 72b810ba8d6f | da39a3ee5e6b / da39a3ee5e6b | yes |
| `tests/integration/test-check-state.py` | 0→0 | bb5b723f03a6 / bb5b723f03a6 | da39a3ee5e6b / da39a3ee5e6b | yes |
| `tests/integration/test-factory-integration.py` | 0→0 | 6e856f9f78d3 / 6e856f9f78d3 | da39a3ee5e6b / da39a3ee5e6b | yes |
| `tests/integration/test-factory-issue-types.py` | 0→0 | 9dc36a8aaee5 / 9dc36a8aaee5 | da39a3ee5e6b / da39a3ee5e6b | yes |
| `tests/integration/test-feature-worktree.py` | 0→0 | 0dd7a9273f7f / 0dd7a9273f7f | da39a3ee5e6b / da39a3ee5e6b | yes |
| `tests/integration/test-gen-decisions-index.py` | 0→0 | 01f61699a09f / 01f61699a09f | da39a3ee5e6b / da39a3ee5e6b | yes |
| `tests/integration/test-gh-close-gate.py` | 0→0 | 07b10820c47f / 07b10820c47f | da39a3ee5e6b / da39a3ee5e6b | yes |
| `tests/integration/test-gh-sync-abandon.py` | 0→0 | 52c345685393 / 52c345685393 | da39a3ee5e6b / da39a3ee5e6b | yes |
| `tests/integration/test-gh-sync-open.py` | 0→0 | e1786bdb4e7f / e1786bdb4e7f | da39a3ee5e6b / da39a3ee5e6b | yes |
| `tests/integration/test-gh-sync-record.py` | 0→0 | 771343fa68b7 / 771343fa68b7 | da39a3ee5e6b / da39a3ee5e6b | yes |
| `tests/integration/test-gh-sync-ship.py` | 0→0 | 99076664d68d / 99076664d68d | da39a3ee5e6b / da39a3ee5e6b | yes |
| `tests/integration/test-gh-sync-start-task.py` | 0→0 | 455f467d39e6 / 455f467d39e6 | da39a3ee5e6b / da39a3ee5e6b | yes |
| `tests/integration/test-harness-yaml.py` | 0→0 | 7aab10214ebe / 7aab10214ebe | c0659f251557 / ab7ba7d5aa2d | **NO** |
| `tests/integration/test-inflight-registry.py` | 0→0 | 174c3796f75b / 174c3796f75b | 1e3e411e9bdb / 1e3e411e9bdb | yes |
| `tests/integration/test-inject-expertise.py` | 0→0 | 8407d740b416 / 8407d740b416 | da39a3ee5e6b / da39a3ee5e6b | yes |
| `tests/integration/test-layout-migration.py` | 0→0 | a045494df541 / a045494df541 | da39a3ee5e6b / da39a3ee5e6b | yes |
| `tests/integration/test-plan-merge.py` | 0→0 | 331296f544b1 / 331296f544b1 | da39a3ee5e6b / da39a3ee5e6b | yes |
| `tests/integration/test-plan-sign-gate.py` | 0→0 | 51d2ea2e7ca5 / 51d2ea2e7ca5 | da39a3ee5e6b / da39a3ee5e6b | yes |
| `tests/integration/test-plan-team.py` | 0→0 | ba36622a80c4 / ba36622a80c4 | da39a3ee5e6b / da39a3ee5e6b | yes |
| `tests/integration/test-post-merge-sweep.py` | 0→0 | d34c03d22688 / d34c03d22688 | da39a3ee5e6b / da39a3ee5e6b | yes |
| `tests/integration/test-run-unit-tests-kinds.py` | 0→0 | bd6faeed0f45 / bd6faeed0f45 | da39a3ee5e6b / da39a3ee5e6b | yes |
| `tests/integration/test-run-unit-tests-layout.py` | 0→0 | 0942f7b5f217 / 0942f7b5f217 | da39a3ee5e6b / da39a3ee5e6b | yes |
| `tests/integration/test-validate-digest.py` | 0→0 | 72e2cffb6855 / c75206100a62 | da39a3ee5e6b / da39a3ee5e6b | yes |
| `tests/integration/test-validate-feature-json.py` | 0→0 | 3fb3ca62430b / 3fb3ca62430b | da39a3ee5e6b / da39a3ee5e6b | yes |
| `tests/integration/test-worktree-terminal.py` | 0→0 | 1704dcb63d55 / 1704dcb63d55 | da39a3ee5e6b / da39a3ee5e6b | yes |
| `tests/unit/test-artifact-accessors.py` | 0→0 | da39a3ee5e6b / da39a3ee5e6b | f784a74d59f0 / 8f25ab8ab73c | **NO** |
| `tests/unit/test-config-shape-matrix.py` | 0→0 | 849446963b7b / 849446963b7b | da39a3ee5e6b / da39a3ee5e6b | yes |
| `tests/unit/test-factory-claim.py` | 0→0 | dad0a9479a29 / dad0a9479a29 | da39a3ee5e6b / da39a3ee5e6b | yes |
| `tests/unit/test-factory-config.py` | 0→0 | 1827616bffd7 / 1827616bffd7 | da39a3ee5e6b / da39a3ee5e6b | yes |
| `tests/unit/test-factory-workspace.py` | 0→0 | f156c4404161 / f156c4404161 | da39a3ee5e6b / da39a3ee5e6b | yes |
| `tests/unit/test-gh-board.py` | 0→0 | c7d324c4b552 / c7d324c4b552 | da39a3ee5e6b / da39a3ee5e6b | yes |
| `tests/unit/test-gh-cost-log.py` | 0→0 | 7ecc739a6f4e / 7ecc739a6f4e | da39a3ee5e6b / da39a3ee5e6b | yes |
| `tests/unit/test-handoff-done-when.py` | 0→0 | 866c66363614 / 866c66363614 | da39a3ee5e6b / da39a3ee5e6b | yes |
| `tests/unit/test-harness-boundary.py` | 0→0 | 4207e374f3e6 / 4207e374f3e6 | ee9111cf9ddb / 5ff995e518a6 | **NO** |
| `tests/unit/test-no-distribution.py` | 0→0 | 87f31e1d378d / 87f31e1d378d | da39a3ee5e6b / da39a3ee5e6b | yes |
| `tests/unit/test-suite-independence.py` | 0→0 | 221f3ce81707 / 35d3f42454b0 | 0ba9a268e611 / c1dcd42b75e3 | **NO** |
| `tests/unit/test-wayfind.py` | 0→0 | d9e7c19eee65 / d9e7c19eee65 | da39a3ee5e6b / da39a3ee5e6b | yes |

All identical (normalised): **NO** (53/57).

### Raw-byte differences, exact lines (checkout-root normalisation only; every other difference is ledgered)

`tests/integration/test-harness-yaml.py (stderr)`:
```
-PyYAML is not importable and the bootstrap marker at /var/folders/y3/nd_jssrd5dq8lbds73f0fy5m0000gn/T/tmpkbvkh756/.harness/.pyyaml-bootstrap could not be written ([Errno 13] Permission denied: '/var/folders/y3/nd_jssrd5dq8lbds73f0fy5m0000gn/T/tmpkbvkh756/.harness/.pyyaml-bootstrap'), so a one-time grant cannot be recorded — failing closed rather than granting one that never expires.
+PyYAML is not importable and the bootstrap marker at /var/folders/y3/nd_jssrd5dq8lbds73f0fy5m0000gn/T/tmpae99yjt5/.harness/.pyyaml-bootstrap could not be written ([Errno 13] Permission denied: '/var/folders/y3/nd_jssrd5dq8lbds73f0fy5m0000gn/T/tmpae99yjt5/.harness/.pyyaml-bootstrap'), so a one-time grant cannot be recorded — failing closed rather than granting one that never expires.
```

`tests/integration/test-validate-digest.py (stdout)`:
```
-ok    [severity_max enum] /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/feat68-base-e655f14a/.omp/agents/harness-code-reviewer.md
-ok    [severity_max enum] /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/feat68-base-e655f14a/.omp/agents/harness-security-reviewer.md
-ok    [severity_max enum] /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/feat68-base-e655f14a/.omp/agents/harness-ui-reviewer.md
+ok    [severity_max enum] /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/feat68-cleanpin-9ab1813e/.omp/agents/harness-code-reviewer.md
+ok    [severity_max enum] /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/feat68-cleanpin-9ab1813e/.omp/agents/harness-security-reviewer.md
+ok    [severity_max enum] /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/feat68-cleanpin-9ab1813e/.omp/agents/harness-ui-reviewer.md
```

`tests/unit/test-artifact-accessors.py (stderr)`:
```
-Ran 24 tests in 0.122s
+Ran 24 tests in 0.105s
```

`tests/unit/test-harness-boundary.py (stderr)`:
```
-harness_boundary: discarding HARNESS_PROJECT_DIR='/var/folders/y3/nd_jssrd5dq8lbds73f0fy5m0000gn/T/tmpc63ro8j0' — it does not carry .harness/team-config.yaml. Falling back to the derived root '/var/folders/y3/nd_jssrd5dq8lbds73f0fy5m0000gn/T/tmpenh3yza9'.
+harness_boundary: discarding HARNESS_PROJECT_DIR='/var/folders/y3/nd_jssrd5dq8lbds73f0fy5m0000gn/T/tmpujmk9hky' — it does not carry .harness/team-config.yaml. Falling back to the derived root '/var/folders/y3/nd_jssrd5dq8lbds73f0fy5m0000gn/T/tmp17b9a1kl'.
```

`tests/unit/test-suite-independence.py (stdout)`:
```
-root /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/feat68-base-e655f14a
-discovered 112
+root /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/feat68-cleanpin-9ab1813e
+discovered 111
```

`tests/unit/test-suite-independence.py (stderr)`:
```
-ERROR could not resolve scan root above /var/folders/y3/nd_jssrd5dq8lbds73f0fy5m0000gn/T/tmp9sv7_pg1
+ERROR could not resolve scan root above /var/folders/y3/nd_jssrd5dq8lbds73f0fy5m0000gn/T/tmpf59d0rrb
```

## SC-01: the plan's inline grade assertion (T-01 verify) at the pin — green

run in the pin checkout → exit 0
```

```

## SC-01 / SC-04 red-first: the same assertion run in the baseline checkout — red

run in the baseline checkout (the five retained drivers grade 1 there) → exit 1
```
Traceback (most recent call last):
  File "<string>", line 1, in <module>
    import importlib.util,pathlib,subprocess,sys; root=pathlib.Path("."); base="e655f14a56a14bf1777cae55a19195c9af10505d"; spec=importlib.util.spec_from_file_location("feat68_code_grade",root/".claude/skills/harness/bin/code_grade.py"); grade=importlib.util.module_from_spec(spec); sys.modules[spec.name]=grade; spec.loader.exec_module(grade); paths=[".claude/skills/harness/bin/check-plan-routes.py",".claude/skills/harness/bin/harness_boundary.py",".claude/skills/harness/bin/board_lifecycle.py",".claude/skills/harness/bin/layout_migration.py",".claude/skills/harness/bin/check-domain.py"]; targets={(paths[0],"process_plan_yaml"),(paths[1],"classify"),(paths[2],"_audit_findings"),(paths[3],"scan"),(paths[4],"domain_check")}; baseline={(p,r.qualname) for p in paths for r in grade.grade_source(subprocess.check_output(["git","show",f"{base}:{p}"],text=True),p)}; records=[(p,r) for p in paths for r in grade.grade_source((root/p).read_text(),p)]; seen={(p,r.qualname) for p,r in records}; assert targets <= seen, sorted(targets-seen); selected=[(p,r) for p,r in records if (p,r.qualname) in targets or (p,r.qualname) not in baseline]; bad=[(p,r.qualname,r.grade) for p,r in selected if r.grade < 4 and r.grade != 2]; assert not bad,bad
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                             ^^^^^^^
AssertionError: [('.claude/skills/harness/bin/check-plan-routes.py', 'process_plan_yaml', 1), ('.claude/skills/harness/bin/harness_boundary.py', 'classify', 1), ('.claude/skills/harness/bin/board_lifecycle.py', '_audit_findings', 1), ('.claude/skills/harness/bin/layout_migration.py', 'scan', 1), ('.claude/skills/harness/bin/check-domain.py', 'domain_check', 1)]
```

## The four non-identical suites

53/57 identical under the one signed normalisation. The four that differ are five ledgered
lines, each with exact old/new bytes above and its ruling in `notes/build-divergences.md`:
D-01 `test-suite-independence.py` `discovered 112 → 111` (the deleted renderer test — the
deletion's consequence); D-02/D-03/D-04 one stderr line each in `test-harness-yaml.py`,
`test-harness-boundary.py`, `test-suite-independence.py` naming the case's fresh `mkdtemp()`
directory; D-05 `test-artifact-accessors.py`'s unittest wall-clock. Exit statuses match in all
57; stdout matches in 56.

## Test kinds at the pin (change_type cross_module: unit + integration both required)

Run in the feature worktree at `9ab1813e` via the configured runner
(`.agents/skills/harness/bin/run-unit-tests.py`): `--kind unit` exit 0 (41 files — one fewer
than the base, the deleted renderer test); `--kind integration` exit 0 (70 files, `0 failure(s)`).
The candidate `0c15bad6` before it failed the unit kind on `test-code-grade.py`'s stale
`process_plan_yaml: 1` exemption (D-13); `9ab1813e` removes it and is the pin.

## SC-05 at the pin

The verify block's html-absence and reference-grep assertions pass at the pin (part of the
T-01 verify run above); no `render-brief` / `md_to_html` reference remains outside notes,
logs, decision records and feature-history dirs.

## History of this receipt

The first version (commit `ae0b41d7`) compared against a baseline captured in the feature
worktree and applied two further normalisations (mkdtemp paths, unittest timing). Validate c0
VF-01 ruled both outside the signed experiment; this version (fix run, after the pin) uses the
detached baseline checkout and the checkout-root normalisation alone.
