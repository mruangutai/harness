# Security review c5 — FEAT-54 handoff Done when

## BLUF

**PASS.** At immutable review SHA `4690f724cdbbdf03649f0cbea07efe7be3c03ce0`, SEC-F-10 is closed: the sole real OMP subprocess path supplies exactly one `--no-tools`, supplies no `--auto-approve`, and the focused behavioral test pins both facts. No alternate probe branch constructs another OMP argv. No high/critical or must-fix security defect survives. SEC-F-08 remains a **med advisory** under the configured `gates.review: advisory_unless_high` policy and therefore does not gate or conceal another gate.

Reviewed range: `b7956fc4..4690f724cdbbdf03649f0cbea07efe7be3c03ce0`. A post-inspection `git diff --quiet 4690f724... -- <the exact 16 paths>` exited 0, binding the inspected working bytes to the pin.

## Current findings

### SEC-F-08 — med, advisory — raw terminal-control bytes remain printable

**Actor/access:** a repository contributor who can commit an otherwise admitted handoff filename or a non-empty `Scope:`/`Authority:` fact containing ESC/OSC/BEL bytes; model/provider output is a second untrusted producer. **Action/gain:** when an operator intentionally runs the locally-run comprehension probe, the contributor-controlled filename/facts and provider answer/error reach `print()` without control-byte neutralization (`tests/manual/probe-handoff-comprehension.py:86-98,112-121,163-200`). This can rewrite or clear visible evidence and, on permissive terminals, alter title/state/clipboard. An actual CLI sink run with an ESC/OSC/BEL-bearing requested path emitted 2 raw control bytes. Source tracing independently confirms that an admitted repository note reaches the same path/fact sinks. This remains med because execution is manual and the demonstrated impact is terminal/display integrity, not host command authority.

**Owner lane:** harness-dev-ops via harness-eng-lead. Escape or visibly encode C0/C1 controls before every terminal sink. Under `.harness/harness.json:347` (`advisory_unless_high`), this med item is recorded but non-gating; there is no other surviving gate to conceal.

## SEC-F-10 disposition — closed

`ask()` has the probe's only `subprocess.run` and builds list-form argv as `[omp, "-p", prompt, "--no-extensions", "--no-skills", "--no-rules", "--no-tools", "--model", model]` (`tests/manual/probe-handoff-comprehension.py:133-147`). Installed `omp v18.1.6 --help` states that `--no-tools` disables all built-in tools and `--auto-approve` skips tool approvals. The focused test calls the real `ask()` path with only `subprocess.run` captured, then asserts `argv.count("--no-tools") == 1` and absence of `--auto-approve` (`tests/unit/test-probe-handoff-comprehension.py:97-106`); all 7 focused tests passed.

Alternate-branch audit: both measurement arms call `measure_arm() -> ask()`; requested/default note selection changes only the note input; the missing-OMP branch changes only the executable string before reaching the same `ask()`; and `--dry-run` returns before any call. A full search of the probe and focused test finds one production `subprocess.run`, one production `--no-tools`, and no production `--auto-approve`. Thus repository prompt injection can still influence model text, but it has no built-in read/bash/edit/write/browser/task authority and no auto-approved tool path. SEC-F-10's attacker-to-operator privilege chain is removed.

## Prior finding dispositions, independently re-derived at c5

| Finding | C5 disposition | Evidence |
|---|---|---|
| F-01 — authority containment/fail-closed reads | **Closed.** | `handoff_done_when.py:57-101,123-174,224-253` rejects absolute/traversal/control-bearing pointer paths, canonicalizes beneath root, requires regular bounded UTF-8 targets, uses `yaml.safe_load`, and catches resolver failures. Resolver test passed 54/54; real-hook handoff group passed 41/41, including symlink escape, FIFO and injected resolver exception. |
| F-02 — probe note admission | **Closed.** | `probe-handoff-comprehension.py:49-109` contains notes beneath the feature tree, requires the handoff path shape and a regular bounded UTF-8 no-follow file. Focused probe suite passed 7/7: outside/traversal/symlink/directory/wrong-name/oversized inputs made no model call; valid input made two. |
| F-03 — Edit mutates before refusal | **Closed.** | `check-domain.sh:1819-1874` reconstructs protected Edit candidates and exits 2 on invalid UTF-8 before mutation. Real hook tests observed invalid-candidate and invalid-UTF-8 refusal with byte identity preserved. |
| F-04 — SC-04 Done-when violation | **Closed for SC-04.** | Literal command produced no line naming `Done when`. Its process exit was 1 only because of an unrelated concurrent INV-29 worktree violation, detailed below; no handoff-shape finding survived. |
| F-05 — blank Scope | **Closed.** | `_scope_problems` rejects empty/whitespace-only values; unit, real write hook, and persisted-state fixtures passed. |
| F-06 — Scope ordering | **Closed.** | `_order_problems` requires Scope before the first Authority; all three layers' fixtures passed. |
| F-07 — changed-function complexity | **Closed/non-security.** | No security disposition depends on complexity; the security-relevant behavior was exercised directly. Code-quality grading remains the code-review lane. |
| F-08 — nested/duplicate heading truncation | **Closed.** | H3 content stays in the body and is rejected as unexpected; duplicate Done-when H2s are rejected. Unit, write-hook and state fixtures passed. |
| F-09 — false approval heading | **Closed.** | `_atx_heading_text` accepts only 1–6 hash ATX headings with required whitespace; `#Approval` and seven-hash lookalikes were rejected in unit and real-hook tests. |
| F-10 — SC-15 regression proof watched wrong output | **Closed.** | Both absent-target fixtures now reject **every** line naming `handoff-plan.md` by passing empty needles (`test-check-state.py:2234-2239`). The executable caller mutant changes the sole `resolve=False` call to `resolve=True`; the integration run printed `real=0, mutant=1` and exited green (`test-check-state.py:2299-2340`). |
| SEC-F-08 — raw terminal controls | **Survives, med advisory.** | Reproduced and source-traced above. |
| SEC-F-10 — tool-enabled auto-approved probe | **Closed.** | Exactly-one `--no-tools`, no `--auto-approve`, sole subprocess path and 7/7 focused test above. |

## Literal SC-04 evidence

From the repository root, the literal command `bash .claude/skills/harness/bin/check-state.sh` exited **1** and emitted **0 lines naming `Done when`**. The only `VIOLATION` was unrelated to handoff validation: INV-29 reported the concurrent `BUG-1157-approval-overrule` worktree because its landed `feature.json` was absent. Per SC-04's stated falsifier (a reported handoff/Done-when line) and the assignment's unrelated-path non-goal, SC-04 is clean for FEAT-54; the unrelated live-worktree condition is recorded rather than misreported as exit 0.

## OWASP / STRIDE assessment

- **Prompt/command injection:** list-form subprocess argv prevents shell interpolation. The admitted note remains untrusted prompt data, but `--no-tools`, `--no-extensions`, `--no-skills`, and `--no-rules` remove host-action channels; SEC-F-10 is mitigated.
- **Path traversal/filesystem:** finding/approval paths reject absolute, traversal and control-bearing values and all resolved targets remain beneath root. Plan/BRIEF targets derive from the note's feature directory and use the same contained bounded reader. Symlink escape and special-file fixtures fail closed.
- **Hook bypass/tampering:** write-time validation uses `resolve=True` and exceptions become exit-2 refusals. Persisted validation deliberately uses `resolve=False`; the repaired mutant proves this mode is load-bearing. Edit reconstruction refuses invalid UTF-8 before mutation.
- **Deserialization/availability:** PyYAML uses `safe_load`; reads are capped at 1 MiB and regular-file checks prevent static FIFO/device blocking. No unbounded recursive or network input was added.
- **Auth/authorization/SSRF/export injection:** no route, session, tenant authorization, redirect, user-selected URL, SQL/NoSQL, shell interpolation, CSV or spreadsheet export exists in the 16-path scope.
- **Secrets/dependencies/data exposure:** no dependency was added. A credential-signature scan over the complete 214-path pinned diff found no AWS/GitHub/Slack/private-key-shaped literal. The manual, documented model call intentionally sends the selected repository note to the configured provider; host tools are now disabled.

## Exact 16-path census

1. `.claude/skills/harness/bin/handoff_done_when.py` — untrusted block grammar, contained bounded target resolution, safe YAML, fail-closed resolver.
2. `tests/unit/test-handoff-done-when.py` — 54 direct parser/path/symlink/special-file assertions.
3. `tests/unit/test-probe-handoff-comprehension.py` — admission and exact OMP argv contract; 7/7 passed.
4. `tests/integration/test-check-domain.py` — real PreToolUse/shape/Edit/exception boundary; handoff group 41/41 passed.
5. `.claude/skills/harness/bin/check-domain.sh` — hook payload, path matching, Edit reconstruction, `resolve=True`, exit-2 refusal.
6. `.harness/harness.json` — frozen baseline, locally-run probe registration, `advisory_unless_high` policy.
7. `tests/integration/test-check-state.py` — persisted grammar, all-line absent-target assertions, and real=0/mutant=1 proof; FEAT-54 group 18/18 passed.
8. `.claude/skills/harness/bin/check-state.sh` — corpus/baseline boundary, `resolve=False`, module failure reporting.
9. `.claude/skills/harness/templates/HANDOFF.md` — author-facing untrusted-input and authority contract.
10. `.claude/skills/harness/SKILL.md` — five-section orchestration instruction; no command construction added.
11. `tests/manual/probe-handoff-comprehension.py` — admitted file, model prompt/argv, provider output and terminal boundaries; SEC-F-08 survivor and SEC-F-10 closure site.
12. `.harness/harness/docs/DECISIONS.md` — DEC-159/214 authority and write-time resolution record.
13. `.harness/harness/docs/DECISIONS-INDEX.md` — indexed DEC-159/174/179/201/212/213/214 routing; no executable surface.
14. `.harness/harness/features/FEAT-54-handoff-done-when/notes/handoff-plan.md` — real admitted note/pointer input.
15. `.harness/harness/features/FEAT-54-handoff-done-when/notes/handoff-build.md` — real admitted note/pointer input.
16. `tests/integration/test-run-unit-tests-kinds.py` — list-form fixture subprocesses and probe exclusion/registration mutants; 5/5 passed.

## Verification and limits

- `python3 tests/unit/test-handoff-done-when.py` — exit 0, **54/54** assertions.
- `python3 tests/unit/test-probe-handoff-comprehension.py` — exit 0, **7/7** tests.
- `python3 tests/integration/test-check-domain.py` — exit 0; handoff group **41/41** and the full selected file passed.
- `python3 tests/integration/test-check-state.py` — exit 0; FEAT-54 group **18/18**, including `real=0, mutant=1`, and the full selected file passed.
- `python3 tests/integration/test-run-unit-tests-kinds.py` — exit 0, **5/5** checks.
- `omp --help` — v18.1.6 confirms `--no-tools` disables all built-in tools and `--auto-approve` skips approval prompts.
- No credentialled model call, formatter, linter, project-wide build, unselected suite, SC-10 UAT, or PM goal-check ran.

## Threat model

| Boundary | STRIDE | Mitigated |
|---|---|---|
| Repository handoff text → OMP prompt → operator host tools | T/I/E | **Yes** — no tools/extensions/skills/rules and no auto-approval |
| Repository/model/provider text → operator terminal | T/R | **No** — SEC-F-08, med advisory |
| Typed authority pointer → repository filesystem | T/I/D | **Yes** — grammar, containment, regular/bounded UTF-8 reads |
| PreToolUse Edit payload + prior bytes → candidate → mutation decision | T/E | **Yes** — reconstruction and exit-2 refusal |
| Persisted handoff + frozen baseline → INV-17 routing | T | **Yes** — shape/grammar only; caller mutant pins no re-resolution |

No open questions.