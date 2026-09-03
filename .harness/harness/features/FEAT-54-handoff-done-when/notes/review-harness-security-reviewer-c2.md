# Security review — FEAT-54 handoff done-when — c2

## Verdict

**PASS (security), with one medium advisory.** The two prior high security findings are closed at pinned SHA `53e1745462b75e1c54967b43e2f4fbdfc7037e23`: authority targets are contained and resolver failures block, while the credentialled probe rejects outside, traversal, symlink, wrong-name, non-regular, oversized, and non-UTF-8 inputs before making model calls. One new medium terminal-output injection remains: repository-controlled note paths, facts, and model answers are printed without neutralizing control bytes. The literal SC-04 root check separately remains failed (exit 1, zero `Done when` lines), and SC-10 remains pending operator UAT; neither is waived by this security verdict.

Reviewed range: `0ec44965a961d19177de871c3bb1f02b701e646b..53e1745462b75e1c54967b43e2f4fbdfc7037e23`. `git rev-parse HEAD` returned the exact review SHA. The named-set diff census is 16 files, `+1715/-97`; every named file is classified below.

## Live security finding

### F-08 — med — terminal control bytes from repository/model input are emitted raw

**OWASP:** injection / output neutralization. **STRIDE:** Tampering, Repudiation.  
**Owner lane:** harness-dev-ops via harness-eng-lead (`tests/manual/probe-handoff-comprehension.py`).

A repository contributor can commit or direct the operator to a handoff filename or shape-valid `Scope:` containing ANSI/OSC control bytes. When the operator runs the registered manual probe, `validate_note()` prints a rejected path directly (`tests/manual/probe-handoff-comprehension.py:86-98`), `print_plan()` and `print_note_header()` print accepted paths/facts directly (`:155-177`), and `measure_arm()` prints the model's untrusted response directly (`:180-197`). The contributor can therefore clear/rewrite visible review evidence or, on terminals supporting dangerous OSC operations, manipulate terminal state/clipboard. The model response is a second untrusted producer because the handoff is prompt content. A focused byte measurement of a rejected path containing `ESC [31m` showed literal `1b 5b 33 31 6d ... 1b 5b 30 6d` in stdout. The prerequisite is an operator invoking this review-only probe in a control-sequence-interpreting terminal, so this is medium rather than high.

Recommended repair: neutralize C0/C1/DEL and ANSI/OSC sequences in every terminal-bound path, fact, error detail, and model answer while retaining the raw note only in the provider-bound prompt. Add a byte-level output test. This is advisory under the high-or-above security gate.

## Prior F-01..F-07 reassessment

| ID | Disposition at `53e1745` | Evidence |
|---|---|---|
| F-01 high, authority traversal/fail-open | **CLOSED.** Finding and approval paths share `_pointer_path`, `_unsafe_rel_path`, and `_read_target`: control bytes, absolute paths and `..` are rejected; `resolve(strict=True)` plus `relative_to(root)` contains canonical targets; only regular files of at most 1 MiB are opened (`handoff_done_when.py:45-95,133-160,220-235`). Both `_resolve_finding` and `_resolve_approval` route through that reader. Unexpected resolver exceptions become a problem, and the hook's outer exception boundary appends `REFUSING` before exit 2 (`check-domain.sh:1561-1567`). | Resolver unit command exited 0: absolute/traversal/control under both `resolve` modes, symlink escape, FIFO, finding/approval good/bad, and AND semantics all printed PASS. The real-hook integration command exited 0: unsafe absolute/traversal/NUL, symlink escape, special target, and injected validator exception cases all printed `ok`. Approval uses the identical contained reader; its control-byte and resolving/unresolving branches were independently exercised. |
| F-02 high, local-file-to-provider disclosure | **CLOSED.** Admission canonicalizes beneath `.harness/harness/features/<FEAT>/notes/handoff-*.md`, rejects a final symlink, opens with `O_NOFOLLOW|O_NONBLOCK`, checks the opened descriptor is regular and at most 1 MiB, bounds the read, and UTF-8 decodes before constructing `ValidatedNote` (`probe-handoff-comprehension.py:51-108`). Only validated notes reach `run()`/`ask()` (`:223-252`). | `python3 tests/unit/test-probe-handoff-comprehension.py` exited 0, `Ran 6 tests`, `OK`: repository-outside, absolute-outside, traversal, explicit/default symlink, directory, wrong basename, and oversized inputs all kept `self.calls == []`; a valid handoff made exactly two calls. No live credentialled call was made. Provider exposure is now limited to the validated repository handoff the signed benchmark intentionally measures. |
| F-03 high, invalid Edit lands before report | **CLOSED.** PreToolUse reconstructs the Edit result for handoffs and sends it through the same shape validator before the tool mutates; invalid UTF-8 existing bytes return a sentinel that exits 2 (`check-domain.sh:1822-1875`). Ambiguous/no-op edits remain the Edit tool's own refusal responsibility; an OS-unreadable file cannot be matched by that same Edit route. | Real-hook integration printed `ok` for invalid candidate exit 2, byte-identical non-mutation, and invalid-UTF-8 fail-closed/non-mutation (`test-check-domain.py:4114-4166`). |
| F-04 high, literal SC-04 root check | **LIVE, outside the security lane.** The exact command exits 1, so the approved criterion is false even though its Done-when subject is clean. Concrete failure: a ship decision claiming SC-04 would certify a gate that actually refuses the repository. **Owner:** main direct corpus/state reconciliation; do not repair or waive in this review. | Exact c2 execution recorded below: six `VIOLATION` lines (FEAT-51 missing `handoff-validate.md`, plus five current run-digest contract violations), zero output lines containing `Done when`; exit 1. |
| F-05 high, blank Scope | **CLOSED.** `_scope_problems` rejects whitespace-only values (`handoff_done_when.py:170-176`). | Unit, write-hook, and persisted-state tests all printed PASS/`ok` for blank Scope; valid controls remained green. |
| F-06 med, Scope order/spec conflict | **CLOSED.** Product ruling `notes/research-FEAT-54-validation-order-c1.md` applies BRIEF REQ-02; `_order_problems` requires Scope before the first/every Authority (`handoff_done_when.py:193-208`). | Unit, write-hook, and persisted-state reversed-order cases all printed PASS/`ok`. No extra Authority ordering was introduced. |
| F-07 high/med, changed-function risk grade | **CLOSED by exact current-pin QA evidence.** | `notes/qa-validation-post-simplify-c2.md:19-37` records an identity-bound 62-pair census: 20 production functions at grade 4+ and 42 tests at grade 3+, assertion exit 0. Current `measure_note` is grade 4 (cyclomatic 3, cognitive 0, ABC 12.7); the former `_handoff_pre_edit_cases` grade-2 failure is absent (grade 5, with its two helpers grade 4 per `notes/qa-validation-c2.md:21-48`). |

## OWASP/STRIDE assessment and non-findings

- **Auth/authorization:** no route, session, identity, privilege, redirect, or tenant-data API changed. The hook remains a local write gate; the untrusted side is the governed handoff payload and repository filesystem.
- **Path/injection/input:** F-01's absolute, traversal, control-byte, symlink-escape, special-file, size, decoding, and exception paths are contained/fail-closed. List-form subprocess argv prevents shell injection. `--model` is operator input and does not cross an authorization boundary. F-08 is the remaining interpreted-output injection.
- **Secrets:** a credential-literal sweep of all 16 named files found zero key/token/private-key signatures. No dependency was added; runtime additions are stdlib plus the pre-existing PyYAML requirement.
- **Data exposure:** the manual real run intentionally sends the complete validated repository handoff to the selected model provider (`prompt()`/`ask()`, `probe-handoff-comprehension.py:123-151`), as disclosed by `.harness/harness.json:284-289` and DEC-214. It has no tools/extensions/skills/rules and is locally-run only. Rejected paths make zero calls. No redaction claim is made; operators must treat repository handoff text as provider-visible. Model and note terminal output remains F-08.
- **Persisted corpus:** INV-17 calls the shared module with `resolve=False` and therefore checks unsafe path grammar without opening authority targets (`check-state.sh:1244-1251`). Its reader's pre-existing treatment of filesystem symlinks/special files was assessed: a FIFO can block and a symlink can be followed before shape checking, but both behaviors exist in the base check-state corpus reader and a local actor able to create such entries can already make the state gate fail or stall; neither is introduced/widened by this diff. Recorded as assessed-and-dismissed, not silently omitted.
- **Availability:** authority reads are bounded to 1 MiB and special files are rejected before open. Probe reads use nonblocking/no-follow flags and an opened-descriptor size/type check. No SQL/NoSQL, template, CSV/spreadsheet, SSRF, or package-supply-chain surface exists in the named delta.

## Threat model

| Boundary | STRIDE | Mitigated? | Result |
|---|---|---:|---|
| Governed handoff payload → pointer parser → project filesystem | T/I/D | Yes | F-01 closed: grammar, canonical containment, type/size bound, two exception boundaries |
| PreToolUse Edit payload + existing bytes → reconstructed candidate → write decision | T/E | Yes | F-03 closed: invalid and non-UTF-8 candidates exit 2 before mutation |
| Repository/CLI note path → credentialled model provider | I/T | Yes | F-02 closed for local-file disclosure; only validated repository handoffs admitted, rejected inputs make zero calls |
| Repository note/model response → operator terminal | T/R | No | F-08 medium; raw terminal controls survive |
| Persisted handoff → INV-17 grammar-only pass | T | Yes | `resolve=False` opens no authority target and retains unsafe-path grammar checks |
| Repository corpus → exact SC-04 state gate | T/R | No | F-04 live outside security: command exit 1; zero Done-when lines |

## Complete named-set census

- `.claude/skills/harness/SKILL.md` — interpreted author guidance; five-section/write-time resolution wording inspected, no executable secret/auth surface.
- `.claude/skills/harness/bin/check-domain.sh` — **in scope**: untrusted hook JSON, PreToolUse Edit reconstruction, fail-closed exception and exit-2 boundary.
- `.claude/skills/harness/bin/check-state.sh` — **in scope**: repository corpus/config input, baseline trust and grammar-only persisted check; exact root invocation executed.
- `.claude/skills/harness/bin/handoff_done_when.py` — **in scope**: pointer grammar, path canonicalization, filesystem reads, PyYAML parsing, resolver failures.
- `.claude/skills/harness/templates/HANDOFF.md` — interpreted author output; fixed shape/AND/provider-neutral pointers inspected, no code execution.
- `.harness/harness.json` — **in scope**: frozen-baseline configuration and credentialled locally-run probe registration; no secret literal.
- `.harness/harness/docs/DECISIONS-INDEX.md` — decision locator inspected for DEC-32/48/100/159/160/163/174/179/214; no runtime input.
- `.harness/harness/docs/DECISIONS.md` — interpreted authority; applicable indexed entries inspected, including exit-2, gate ownership, write-time resolution, and locally-run probe risk.
- `notes/handoff-plan.md` — repository/model input; contained approval pointer and ordered non-empty Scope inspected.
- `notes/handoff-build.md` — repository/model input; contained approval pointer and ordered non-empty Scope inspected.
- `tests/integration/test-check-domain.py` — **in scope proof**: real-hook unsafe path, symlink/special, injected-exception, pre-mutation and non-UTF-8 cases inspected and executed.
- `tests/integration/test-check-state.py` — **in scope proof**: resolve-false, unsafe grammar, Scope order/label and non-mutation cases inspected and executed.
- `tests/integration/test-run-unit-tests-kinds.py` — probe registration/isolation test inspected; no credentialled execution path in normal suites.
- `tests/manual/probe-handoff-comprehension.py` — **in scope**: filesystem admission, provider disclosure, subprocess argv and terminal output; F-08 lives here.
- `tests/unit/test-handoff-done-when.py` — resolver branch proof inspected and executed.
- `tests/unit/test-probe-handoff-comprehension.py` — zero-call admission proof and positive call control inspected and executed.

## Commands and review-time evidence

- `git rev-parse HEAD` → exact pinned SHA.
- Named-set `git diff --stat base..review_sha` → 16 files, `+1715/-97`.
- `python3 tests/unit/test-handoff-done-when.py` → exit 0; 44 named PASS lines.
- `python3 tests/unit/test-probe-handoff-comprehension.py` → exit 0; 6 tests, `OK`; no real model call.
- `python3 tests/integration/test-check-domain.py` → exit 0; all focused FEAT-54 hook cases printed `ok`, including containment, special/symlink, exception, Edit non-mutation and invalid UTF-8.
- `python3 tests/integration/test-check-state.py` → exit 0; all 14 FEAT-54 cases printed `ok`, including unsafe grammar, Scope constraints and clean-corpus non-mutation.
- Literal SC-04 command, from repository root: `bash .claude/skills/harness/bin/check-state.sh` → **exit 1**. Output census: **6 `VIOLATION` lines**, **0 lines containing `Done when`**. The six are FEAT-51's missing `notes/handoff-validate.md` and digest-contract failures for `2026-09-03-qa-validation-c2-validator`, `2026-09-03-validation-c1-eng`, `2026-09-03-validation-c2-eng`, `2026-09-03-qa-post-simplify-c2-validator`, and `2026-09-02-validation-c1-eng`. No waiver or fixture substitution was applied.
- Focused terminal-output measurement: dry-run with an ESC-bearing rejected path piped to `od -An -tx1` → literal `1b 5b 33 31 6d` and reset `1b 5b 30 6d` in stdout, establishing F-08 without a model call.
- Credential signature grep across all 16 named files → no matches.

SC-10 is **pending operator UAT**. It was not executed, inferred, or claimed by this review.
