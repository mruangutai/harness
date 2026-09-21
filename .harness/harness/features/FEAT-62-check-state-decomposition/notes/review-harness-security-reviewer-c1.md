# Security review — FEAT-62 — cycle 1

BLUF: **PASS.** Exact range `16ee44f0..3d92d38b8882bf6699c4b90a2dfd06489511d085` is security-relevant: it consumes Git-controlled path bytes, statically audits repository-controlled source/argv, derives an executable checkout from canonical writer destinations, and forwards child diagnostics. The 21-path census and OWASP/STRIDE review found no exploitable capability increase, trust-boundary bypass, secret exposure, injection, or cross-user data disclosure. Cycle-1 changes strengthen rather than alter cycle 0's PASS conclusion.

## Complete changed-path census (21)

1. `.claude/skills/harness/bin/check-plan-routes.py` — **in scope:** parses repository source and classifies file, `git:<op>`, `gh:<resource>`, and `gh:board` reads; AST only, no parsed-code execution.
2. `.claude/skills/harness/bin/check-state.py` — **in scope:** parses Git porcelain path bytes and runs fixed list-form Git/GitHub argv; `_dirty_paths` now catches only `OSError`/`SubprocessError` (`:4581-4597`).
3. `.claude/skills/harness/bin/feature_json_write.py` — **in scope:** authorized structured-data write calls advisory feedback only after `locked_update` returns (`:210-211`).
4. `.claude/skills/harness/bin/harness_boundary.py` — **in scope:** canonical-path-derived checkout, fixed `[sys.executable, checker, "--changed"]`, `shell=False` default, bounded timeout, recursion marker, and dropped `HARNESS_PROJECT_DIR` (`:320-365`).
5. `.claude/skills/harness/bin/plan-merge.py` — **in scope:** authorized plan write calls feedback after lock release (`:2486-2487`).
6. `.harness/README.md` — operator guidance only; no credential, executable, or data-export surface.
7. `.harness/harness/features/FEAT-62-check-state-decomposition/BRIEF.md` — signed requirements only; amended SC-01/SC-09 authority, no runtime input.
8. `.harness/harness/features/FEAT-62-check-state-decomposition/STATE.md` — feature record only; no secrets.
9. `.harness/harness/features/FEAT-62-check-state-decomposition/feature.json` — run/commit metadata only; no credential material.
10. `.harness/harness/features/FEAT-62-check-state-decomposition/notes/build-divergences.md` — audit record only; explicitly parks two record anomalies.
11. `.harness/harness/features/FEAT-62-check-state-decomposition/notes/research-FEAT-62-check-state-decomposition-goalcheck-validate-c0.md` — prior validation evidence only.
12. `.harness/harness/features/FEAT-62-check-state-decomposition/notes/review-harness-code-reviewer-c0.md` — prior review evidence only.
13. `.harness/harness/features/FEAT-62-check-state-decomposition/notes/review-harness-qa-c0.md` — prior review evidence only.
14. `.harness/harness/features/FEAT-62-check-state-decomposition/notes/review-harness-security-reviewer-c0.md` — prior security evidence only.
15. `.harness/harness/features/FEAT-62-check-state-decomposition/notes/review-harness-ui-reviewer-c0.md` — prior review evidence only.
16. `.harness/harness/features/FEAT-62-check-state-decomposition/plan.yaml` — approved task/decision record only; no runtime secret.
17. `tests/integration/test-check-plan-routes.py` — isolated-copy resource mutants; fixture input only.
18. `tests/integration/test-check-state-table.py` — selector/Git-path fixtures only.
19. `tests/integration/test-feature-json-merge.py` — temporary fixture checker now proves the sibling writer lock is free (`:430-468`); no production boundary.
20. `tests/integration/test-plan-merge.py` — temporary lock-probe checker and writer cases (`:155-208`); no production boundary.
21. `tests/unit/test-harness-boundary.py` — path/argv/environment fixtures only.

## Trust-surface audit

- **Injection / subprocess / path traversal:** all added production spawns use argv lists, not a shell. Git status is NUL-delimited; rename pairs are consumed, decoded with replacement, rebased from Git top-level, and paths outside the selected root are dropped (`check-state.py:4564-4610`). The feedback executable is admitted only for canonical `plan.yaml`/`feature.json` shapes beneath a checkout carrying both the Harness marker and checker; a repository author able to replace that checkout's checker already has code-execution capability in that checkout, so execution adds no privilege delta. No SQL, template, spreadsheet/export, URL, redirect, or dependency surface exists.
- **Input validation / tampering:** cycle 1 strengthens the declaration guard from binary-level to resource-level. `_spawn_resource` derives `git:<op>`/`gh:<resource>`, recognizes `board_stations_for` as `gh:board`, and `_row_reads_findings` requires exact declarations (`check-plan-routes.py:1949-2055`). Dynamic/unrecognized argv can reduce static-audit coverage, but this is a repository-author control over code that the same author can edit; it grants no attacker capability and is not a security finding.
- **Secrets / auth / data exposure:** no route, principal, session, credential, token, URL, or dependency changes. The secret-shaped-string scan found no credential value. Feedback forwards only checker stdout/stderr after an authorized write; it does not serialize environment or file contents. Dropping `HARNESS_PROJECT_DIR` prevents stale-session redirection.
- **Availability / repudiation:** advisory execution is bounded at 120 seconds and failure remains fail-open only for non-authoritative edit-loop feedback; authoritative hooks/workflows/pre-commit remain full-check paths. Cycle 1's narrow catch prevents unrelated programming errors from being silently converted to a conservative run. Writer suites now observe `lock=free`, closing the deadlock regression gap without changing production behavior.

## Cycle-0 dispositions

Cycle-1 changes do **not** alter cycle 0's security conclusion. `CR-01`/`GC-01` are discharged by the operator-approved SC-01 amendment admitting D-1/D-3; `CR-02` is discharged by restoring the exact 47-to-47 broad-handler census and narrowing `_dirty_paths`; `GC-02` is discharged by exact git/GitHub/board resource declarations plus three wrong-resource mutants; `GC-03` is discharged by both writer fixtures observing their writer lock as FREE; and `GC-04` is discharged by the approved SC-09 extraction-compatible-control-flow wording, enumerated handler differences, and restored 47-site census. None creates a security finding. The `OMP-PORT` numbering and duplicate `INV-37` label are parked operator record anomalies, outside this security review; they are neither resolved nor reclassified here.

```yaml
VERDICT: PASS
DIGEST:
  headline: "All 21 pinned paths were censused; real Git-path, static-audit, writer-path, subprocess, and diagnostic-output boundaries remain mitigated, with no security regression."
  in_scope: true
  scope_reason: "The diff consumes Git-controlled path bytes, audits repository source/argv, derives and executes a checker from canonical writer paths, and forwards child output; cycle-1 narrows a spawn catch and strengthens resource/lock proofs without changing cycle 0's PASS conclusion."
  severity_max: info
  findings: []
  must_fix: []
  threat_model:
    - { boundary: "Git index/worktree path bytes -> --changed invariant selection", stride: T, mitigated: true }
    - { boundary: "repository source/argv -> declared-read consolidation audit", stride: T, mitigated: true }
    - { boundary: "canonical writer destination -> derived checkout/checker executable", stride: "T|E", mitigated: true }
    - { boundary: "checker stdout/stderr -> operator stderr", stride: I, mitigated: true }
    - { boundary: "advisory checker runtime -> writer availability", stride: D, mitigated: true }
  open_questions: []
  files_touched: []
  expertise_update: []
artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-62-check-state-decomposition/.harness/harness/features/FEAT-62-check-state-decomposition/notes/review-harness-security-reviewer-c1.md
```
