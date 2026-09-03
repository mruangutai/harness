# Security review — FEAT-54 handoff done-when — c0

## Verdict

**FAIL.** The pinned change adds two exploitable local trust-boundary failures: malformed authority paths can crash the blocking write hook into its documented non-blocking exit path, and the credentialled comprehension probe can follow a repository-controlled path or symlink and submit an arbitrary local file to the configured model service. Both are `high` and must be fixed before ship.

Reviewed range: `0ec44965a961d19177de871c3bb1f02b701e646b..e75767df4b75e71f2c9b12766604cee5008d94e1`. A comparison of every named corpus path against `e75767d` was empty, so the inspected working-tree bytes equal the pin. No test, build, formatter, or linter was run, as dispatched.

## Findings

### F-01 — high — authority paths escape the repository and malformed paths fail the write gate open

**OWASP:** A01 Broken Access Control / path traversal; A03 Injection-shaped unsafe path interpretation; A04 insecure fail-open design.  
**STRIDE:** Tampering, Information disclosure, Denial of service.  
**Owner lane:** **Main direct mutation** — remedy touches DEC-174 enforcement surfaces `.claude/skills/harness/bin/handoff_done_when.py`, `.claude/skills/harness/bin/check-domain.sh`, and their gate tests.

**Concrete attacker and gain.** Any governed orchestrator allowed to write its own `notes/handoff-*.md` controls the `Authority:` value passed to the hook. `finding:` and `approval:` accept an unrestricted path (`handoff_done_when.py:14-15`), then join it directly to `root` (`:85`, `:90`) and call `read_text()` (`:56`, `:93`). An absolute path discards `root`; `../` and symlinks are not contained. This gives the author an oracle over readable files outside the repository (whole-token presence for findings and exact Markdown-heading presence for approvals), and permits unbounded reads of special or very large files.

There is also a deterministic validation bypass. A pointer such as `Authority: approval:bad\u0000path#Approval` passes `APPROVAL_RE`; `Path.read_text()` raises `ValueError`, which the `(OSError, UnicodeError)` handler at `:92-95` does not catch. The exception propagates through `problems()` and the unguarded caller at `check-domain.sh:1567`. That script explicitly documents at `:13-14` that only exit 2 blocks and exit 1 lets the write proceed. The same resolver is reached again on the post-write report path, so the invalid pointer is not recovered there. The author therefore lands a handoff that the new contract was specifically added to refuse.

**Required remedy.** Treat both path-bearing grammars as repository-relative paths: reject absolute paths, `..`, NUL/control characters, and any resolved/symlinked target outside `root`; require a bounded regular file before reading. Convert every malformed-path and resolver exception into a returned problem, and put an exception boundary around the write-gate call so unexpected validator failure still produces exit 2. Add gate-level cases for NUL, absolute, traversal, symlink escape, and an unbounded/special-file target. Persisted `resolve=False` should reject unsafe path grammar without opening a target.

### F-02 — high — the credentialled probe can exfiltrate an arbitrary local file through a repository-controlled symlink

**OWASP:** A01 Broken Access Control / path traversal; A04 insecure design; A09 data exposure through an external processing/logging path.  
**STRIDE:** Information disclosure.  
**Owner lane:** **Engineering / harness-dev-ops via harness-eng-lead** — the affected surface is `tests/manual/probe-handoff-comprehension.py`, which the signed plan assigns to the team lane.

**Concrete attacker and gain.** A repository contributor can add a handoff-shaped symlink pointing to a predictable operator file (for example a workspace `.env` or SSH key) and direct the operator to run the registered review probe on that path. Explicit inputs are accepted without containment (`probe-handoff-comprehension.py:41-43`); the no-argument discovery also follows matching symlinks while selecting by target mtime (`:44-45`). `measure_note()` follows the path with `read_text()` (`:109-112`) and `ask()` places the entire bytes in an `omp -p` prompt sent under live model credentials (`:70-75`). A target without any `## Done when` section is still sent in both arms. The model provider receives the local secret; the model response can also echo it to captured review output.

**Required remedy.** Resolve every requested/discovered path before reading; require a non-symlink regular file contained under `ROOT/.harness/harness/features/*/notes/` with a `handoff-*.md` basename, and refuse rather than call the model when containment or type fails. Add a focused test that a symlink and an absolute/outside path cause zero `omp` invocations. Do not rely on the caller choosing a trustworthy path: repository contents are the untrusted side of this boundary.

## Measured security surface and non-findings

- **Inputs:** hook JSON/content and typed authority pointers are untrusted; CLI note paths and repository note entries are untrusted when the credentialled probe runs; `handoff_done_when_baseline` is project configuration. The baseline can weaken only the persisted presence check, not the write-time resolver; a config editor already has authority to change the project gate configuration, so no separate privilege escalation was charged.
- **YAML/parser:** `plan-task:` reads the fixed feature-local `plan.yaml` and uses `yaml.safe_load` (`handoff_done_when.py:66-72`); parse/read failures resolve false. No unsafe object deserialization or second Done-when parser was found. The defect is variable path handling and its exception boundary, not PyYAML.
- **Injection:** no shell string construction was added. The probe uses list-form subprocess argv (`probe-handoff-comprehension.py:72-75`), and finding tokens are regex-escaped (`handoff_done_when.py:59`). No SQL/NoSQL, template, CSV, or spreadsheet export surface exists in the delta.
- **Secrets/auth:** no credential-shaped literal was found in the changed feature corpus. No route, session, authorization, or redirect/SSRF surface changed. The model probe nevertheless creates the F-02 local-file-to-provider disclosure boundary.
- **Outputs/logging:** hook errors use `pointer!r`, but unresolved target paths are printed raw; control-character rejection belongs in F-01. The committed ship-review HTML is static, contains no script, and visibly HTML-escapes authored text. No CSV/export path changed.
- **Dependencies:** no new package was introduced; the new module uses the already-required PyYAML dependency.

## STRIDE boundary summary

| Boundary | STRIDE | Mitigated? | Result |
|---|---|---:|---|
| Governed handoff Write payload → blocking hook → local filesystem | T/I/D | No | F-01 |
| Repository/CLI note path → local read → credentialled model provider and terminal output | I | No | F-02 |
| Feature-local `plan.yaml` → `yaml.safe_load` | T/D | Yes | Fixed target, safe loader, failures unresolved |
| Persisted handoff corpus → INV-17 grammar-only pass | T | Yes | `resolve=False` does not open authority targets |
| Authored Markdown → committed ship-review HTML | I/T | Yes | Static output, escaped text, no script |

## Shared-set and pinned-diff inspection evidence

Every required shared path was opened before scoping: `.claude/skills/harness/SKILL.md`; `bin/check-domain.sh`; `bin/check-state.sh`; `bin/handoff_done_when.py`; `templates/HANDOFF.md`; `.harness/harness.json`; `DECISIONS-INDEX.md`; the applicable complete DEC-159/160/171/174/179/180/182/214 entries in `DECISIONS.md`; both FEAT-54 handoffs; all five named unit/integration/manual tests; and the complete approved `BRIEF.md` and `plan.yaml`. Large pre-existing gate/test files were inspected through the full pinned hunks plus their caller, normalization, exit, and aggregation paths. The rendered HTML output was opened separately. The whole changed feature corpus was scanned for credential signatures and trust-boundary terms.

Per-file diff census below uses: **E** enforcement/runtime, **I** interpreted output, **T** test, **S** signed/spec/decision/config, **H** handoff input, **R** execution/history record. Every path in the 60-file pinned diff is accounted for.

- **E:** `.claude/skills/harness/bin/check-domain.sh`; `.claude/skills/harness/bin/check-state.sh`; `.claude/skills/harness/bin/handoff_done_when.py`; `tests/manual/probe-handoff-comprehension.py`.
- **S:** `.claude/skills/harness/SKILL.md`; `.claude/skills/harness/templates/HANDOFF.md`; `.harness/harness.json`; `.harness/harness/docs/DECISIONS-INDEX.md`; `.harness/harness/docs/DECISIONS.md`; `.harness/harness/features/FEAT-54-handoff-done-when/BRIEF.md`; `.harness/harness/features/FEAT-54-handoff-done-when/plan.yaml`; `.harness/notes/grilling-handoff-done-when-2026-09-02.md`.
- **H:** `.harness/harness/features/FEAT-54-handoff-done-when/notes/handoff-build.md`; `.harness/harness/features/FEAT-54-handoff-done-when/notes/handoff-plan.md`.
- **T:** `tests/integration/test-check-domain.py`; `tests/integration/test-check-state.py`; `tests/integration/test-run-unit-tests-kinds.py`; `tests/unit/test-handoff-done-when.py`.
- **I:** `.harness/harness/features/FEAT-54-handoff-done-when/notes/ship-review-2026-09-02-t05t09-eng.html`; `.harness/harness/features/FEAT-54-handoff-done-when/notes/ship-review-2026-09-02-t05t09-eng.md`.
- **R:** `.harness/harness/features/FEAT-54-handoff-done-when/STATE.md`; `.harness/harness/features/FEAT-54-handoff-done-when/feature.json`; `notes/qa-build-c0.md`; `notes/qa-build-c1.md`; `notes/qa-build-c2.md`; `notes/receipt-harness-backend-dev-simplify-efficiency.md`; `notes/receipt-harness-backend-dev-simplify-reuse.md`; `notes/receipt-harness-dev-ops-T-09-c0.md`; `notes/receipt-harness-dev-ops-simplify-altitude.md`; `notes/receipt-harness-dev-ops-simplify-apply.md`; `notes/receipt-harness-dev-ops-simplify-simplification.md`; `notes/receipt-harness-dev-ops-t05t09-eng-t05.md`; `notes/receipt-harness-dev-ops-t05t09-eng-t09.md`; `notes/receipt-harness-documentor-t10.md`; `notes/research-FEAT-54-c4record.md`; `notes/research-FEAT-54-c4recordfix.md`; `notes/research-FEAT-54-c4recordgoalcheck.md`; `notes/research-FEAT-54-goalcheck-plan-c0.md`; `notes/research-FEAT-54-goalcheck-plan-c1.md`; `notes/research-FEAT-54-goalcheck-plan-c2.md`; `notes/research-FEAT-54-goalcheck-plan-c3.md`; `notes/research-FEAT-54-goalcheck-plan-c4.md`; `notes/research-FEAT-54-planfix-c1.md`; `notes/research-FEAT-54-planfix-c2.md`; `notes/research-FEAT-54-planfix-c2b.md`; `notes/research-FEAT-54-planfix-c2c.md`; `notes/research-FEAT-54-planfix-c3.md`; `notes/research-FEAT-54-planfix-c4.md`; `notes/research-FEAT-54-planrevision-c2.md`; `notes/research-panel-transcription-c0.md`; `notes/research-panel-transcription-c3.md`; `notes/review-harness-code-reviewer-planpanel-c0.md`; `notes/review-harness-code-reviewer-planpanel-c2.md`; `notes/review-harness-code-reviewer-planpanel-c3.md`; `notes/review-harness-code-reviewer-planpanel-c4.md`; `notes/signature-inputs-c3.md`; `notes/tdd-executor-record.md`; `observations/harness-orchestrator.md`; `observations/harness-pm.md`; `observations/harness-product-lead.md` (all paths in this R group are under `.harness/harness/features/FEAT-54-handoff-done-when/` unless already absolute above).

## Success-criterion inspection notes

- **SC-07:** the pinned gates call one implementation: `check-domain.sh:1562-1567` with `resolve=True`, and `check-state.sh:54,1244-1251` with `resolve=False`; neither gate implements a second body parser or target resolver.
- **SC-08:** no current-contract “four sections” claim remains in the named live surfaces. The two matches at `check-state.sh:1199,1218` are the BRIEF's explicitly exempt past-measurement/incident record.
- **SC-11:** `git diff --name-status b7956fc4..e75767d -- '.harness/harness/features/*/notes/handoff-*.md'` reports only the two FEAT-54 handoff additions, so no pre-base handoff is modified and the positive control is non-empty.
- **SC-04:** not executed in this security panel because the dispatch expressly prohibited validation commands; no met claim is made here.
- **SC-10:** **pending operator UAT** and cannot be marked met by this review.
