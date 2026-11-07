# Security review — BUG-2169 — cycle 0

PASS: T-01 preserves the inspected YAML-origin boundary; no actionable security findings.

Reviewed only `c4e8bbc87e858bb2a0320efd766c7036cbcebb8b..6c896d981ed17d2bae528818ecffa56400ae2666`, against BRIEF SC-01–05, the settled operator grilling, SPEC §13 and DEC-174/225.

## Scope and threat model

All 16 changed paths were assessed. In scope: dispatch bootstrap cached imports (Tampering/Elevation), human-interpreted installation advice, CI dependency installation and their regression assertions. The nine feature records/notes/observation paths add governance/evidence, not executable authority; the worktree-terminal delta is documentation only. A full pinned-diff credential sweep found no credential material (the sole token match is run accounting).

- `dispatch-guard.py:57–115`: every loaded `yaml`/`yaml.*` origin must exist, resolve inside a remaining policy search root, and resolve outside per-user site, PYTHONPATH, cwd and bin roots. `realpath` plus `commonpath` handles nested package files, symlink and `..` path aliases without string-prefix sibling matches. One rejected origin rejects the entire YAML namespace, including its C extension. Trusted system-wide modules remain the same objects in `sys.modules`; no forced pure-Python loader.
- `dispatch-guard.py:107–115`: project/bin-origin modules remain purged regardless of name; the YAML exception cannot override that purge. The existing policy path filtering and explicit bin reinsertion remain intact. No new attacker-controlled shell, URL, authorization field, logging disclosure or cross-user data access is introduced.
- `harness_yaml.py:539–566` and `references/checkout-prereqs.md:30–50`: advice is fixed command text, not interpolation or automatic execution; Homebrew's system-modifying installation risk is expressly disclosed. Debian uses apt; per-user YAML is not recommended.

This remains an import-origin policy, not a sandbox for arbitrary Python already executed in phase 1. Forging module metadata or monkeypatching interpreter state requires that pre-existing execution capability; it is not a new privilege delta established by this patch.

## Evidence and limits

- The pinned preflight additions exercise real guard starts/claims and sabotaged user-site/PYTHONPATH packages, including symlink and `..` spellings. `notes/build-evidence-2026-11-07.md:19–24,60–62` records four plant failures under the keep-all-YAML mutant and green fixed results; these are builder receipts, not executions by this reviewer.
- SC-03 inspection: `.github/workflows/tests.yml:79–80,376–377` removes the forced second installation and its distro-blaming comment; no replacement dependency or new credential use.
- SC-05 inspection: `worktree_terminal.py:249–293` retains the MissingDependency-only fallback and malformed-YAML refusal; the added explanation does not alter reclamation behavior.
- No tests, builds, linters, formatters or mutation checks were run here. QA owns fixed-pin gate execution and receipt completeness; code reviewer owns mechanical risk grading.

Findings/must-fix: none. Open questions: none. Source/tests unchanged.
