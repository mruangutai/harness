# Security review c4 — FEAT-54 handoff Done when

## BLUF

**FAIL.** The repaired pin is green on literal SC-04, and the authority resolver, probe path admission, Edit reconstruction, persisted grammar pass, and hook exception paths fail closed under the focused current-pin checks. A new **high** finding nevertheless gates under the configured `advisory_unless_high` policy: the manual probe places repository-controlled handoff text into an OMP coding-agent prompt while leaving all built-in tools enabled and passing `--auto-approve`. A contributor who can supply a handoff note can therefore prompt-inject the model into reading files or executing commands as the operator when the credentialled probe is run. The prior raw terminal-control finding survives at **med advisory**.

Reviewed immutable range `0ec44965a961d19177de871c3bb1f02b701e646b..f05e1e6cd74c7d91580dd6ef565a00432faac1ad`. `git diff --quiet f05e1e6c -- <the exact 16 paths below>` exited 0 after inspection. The same 16 paths are byte-identical to c3 pin `39602414e1cfe792655b7e68bce367e92790c32a`; conclusions below were re-measured at the new pin rather than inherited.

## Ranked findings

### SEC-F-10 — high, must-fix — an admitted note can prompt-inject an auto-approved, tool-enabled OMP agent

**Actor and access.** A repository contributor who can place crafted text in a valid `.harness/harness/features/<FEAT>/notes/handoff-*.md` file; they need no operator credentials or shell access.

**Exploit and gain.** `prompt()` embeds the note verbatim as instructions/data, then `ask()` launches `omp -p` with `--auto-approve` but without `--no-tools` (`tests/manual/probe-handoff-comprehension.py:115-142`). Current `omp v18.1.5 --help` states that built-in `read`, `bash`, `edit`, `write`, browser, task and other tools are default-enabled, that `--no-tools` disables them, and that `--auto-approve` skips approval prompts. A malicious note can tell the model to ignore the benchmark questions, read local credentials or repository secrets, run a command, modify files, or send data over an enabled network-capable tool. When an operator performs the intended credentialled local run, those tool calls require no approval. The model's compliance is probabilistic, but the dangerous mechanism and reachable privilege are deterministic; no live exploit was attempted.

**Impact.** Arbitrary actions under the operator account, including credential compromise or repository tampering, conditional on the operator running this explicitly registered manual probe against the malicious note. The manual-only precondition prevents remote-zero-click grading, but this remains exploitable by a repository user against the operator/system and is therefore **high**.

**Required repair.** Launch OMP with `--no-tools` and remove `--auto-approve`; pin the argv contract in `tests/unit/test-probe-handoff-comprehension.py` with a captured subprocess call proving tools are disabled. Consider `--no-session` separately to avoid retaining benchmark inputs, but it is not a substitute for tool removal. **Owner lane:** harness-dev-ops via harness-eng-lead (`tests/manual/probe-handoff-comprehension.py` and its focused unit test).

### SEC-F-08 — med, advisory — repository/model control bytes reach the terminal

A repository contributor can put ESC/OSC/BEL bytes in an admitted handoff filename or `Scope:` fact, and the model/provider error is a second untrusted producer. The probe prints rejected/accepted paths, facts, provider errors, missing facts, and answers without neutralization (`tests/manual/probe-handoff-comprehension.py:82-98,156-197`). An operator's terminal can have visible evidence cleared or rewritten and, on permissive terminals, its title/state/clipboard changed.

Current-pin reproduction called the real output functions with an ESC/OSC-bearing path and Scope; captured output contained **2 literal ESC bytes and 2 literal BEL bytes**. This independently reproduces the c3 mechanism. It does not become high because it requires the operator to run the locally-run probe and primarily affects display integrity; SEC-F-10 separately covers host/tool authority. Escape or visibly encode C0/C1 controls before every terminal sink. **Owner lane:** harness-dev-ops via harness-eng-lead. Under `advisory_unless_high`, this item alone would not gate.

## Prior finding disposition at `f05e1e6c`

| Finding | c4 disposition | Current-pin evidence |
|---|---|---|
| F-01 — authority containment and fail-closed target reads | **Closed.** | `handoff_done_when.py:57-101,143-174,224-253` rejects absolute, traversal and control-bearing finding/approval paths, resolves beneath the project root, requires a regular UTF-8 file and caps the read at 1 MiB. The unit validator passed **54/54** assertions and the actual hook group passed **41/41**, including independent finding/approval symlink-escape and FIFO cases plus a forced resolver exception. |
| F-02 — probe local-file admission | **Closed for the reported path-bypass defect.** | `validate_note` admits only contained, correctly named, regular, bounded UTF-8 handoff notes and uses no-follow/nonblocking descriptor reads (`probe-handoff-comprehension.py:54-109`). Its focused suite passed **6/6**: rejected outside/traversal/symlink/directory/wrong-name/oversized inputs made zero model calls and the valid control made two. SEC-F-10 is distinct: it concerns malicious content in a legitimately admitted note. |
| F-03 — invalid or unreadable Edit mutates before refusal | **Closed.** | PreToolUse reconstructs handoff Edit candidates, refuses invalid UTF-8, and runs the same validator before mutation (`check-domain.sh:1819-1882`). The real-hook group proved exit 2 plus byte identity for invalid and invalid-UTF-8 candidates. |
| F-04 — literal SC-04 red on FEAT-51 | **Closed by the external repair.** | Exact repository-root command exited **0**, with **0 `VIOLATION` lines and 0 `Done when` findings**. The formerly missing FEAT-51 validate handoff is no longer reported. |
| F-05 — blank Scope | **Closed.** | Unit, real write hook and fixture state gate all refused blank/whitespace-only Scope in the current-pin focused runs. |
| F-06 — Scope ordering | **Closed.** | Unit, real write hook and fixture state gate all refused Authority-before-Scope. |
| F-07 — changed-function complexity | **Closed / non-security.** | The exact 16 executable/test bytes are unchanged from the c3 pin whose identity-bound grade passed 86 functions. This security dispatch did not rerun the code-quality grader, which is outside its assigned lifecycle; no security conclusion depends on that grade. |
| F-08 — nested/duplicate heading truncation | **Closed.** | Current unit, write-hook and state-gate focused runs reject nested prose without truncating later content and reject duplicate Done-when H2 sections. |
| F-09 — false approval heading | **Closed.** | Current unit and real-hook cases reject `#Approval` and seven-hash lookalikes beside the valid ATX control. |
| SEC-F-08 — raw terminal controls | **Survives, med advisory.** | Current-pin byte reproduction above; independently matched, not inherited. |

## OWASP/STRIDE assessment

- **Prompt/command injection:** SEC-F-10 is the gating path. List-form `subprocess.run` prevents shell interpolation in the launcher, but it does not sandbox a coding agent whose own tools remain enabled; `--auto-approve` makes the distinction load-bearing.
- **Filesystem/path traversal:** finding and approval pointers share one grammar and one contained, bounded reader. Plan and BRIEF targets are derived from the note's feature directory and pass through the same realpath containment. Ordinary absolute/traversal/control, symlink escape, directory/FIFO, oversized and decoding cases fail closed. The probe independently constrains selected notes before any model call.
- **YAML/deserialization:** only `yaml.safe_load` is used for the bounded plan target; parse/type errors become unresolved authorities. Persisted mode (`resolve=False`) does not open authority targets. No unsafe object constructor is used.
- **Hook fail-open:** the write gate catches import/resolver exceptions and turns them into problems; only exit 2 is treated as blocking, and the current real-hook exception fixture observed exit 2 with `REFUSING`. Invalid-UTF-8 Edit reconstruction likewise exited 2 before mutation. The state check reports an unavailable module as a violation and exits 1, appropriate for that non-hook gate (`check-state.sh:53-56,1243-1262`).
- **Auth/authorization/SSRF/redirects/spreadsheet injection:** no route, session, tenant boundary, redirect, CSV/spreadsheet export, SQL/NoSQL, or user-selected URL was added. `--model` is an argv value, not shell text.
- **Secrets/dependencies/data exposure:** a credential-signature scan over the full **93-path** pinned diff found no API-key, GitHub-token, AWS-key, Slack-token, or private-key literal. No dependency was added; PyYAML was already required. Sending a deliberately admitted repository handoff to the selected model provider is disclosed and manual, but SEC-F-10 makes the provider invocation unsafe because the recipient is a tool-capable agent rather than a text-only model call.
- **Availability:** note and authority reads are bounded at 1 MiB and special files are rejected/nonblocking on the exercised paths. No unbounded network loop or recursive parser was introduced.

## Exact 16-path inspection census

1. `.claude/skills/harness/bin/handoff_done_when.py` — parser, containment, bounded file/YAML reads, fail-closed resolver.
2. `tests/unit/test-handoff-done-when.py` — 54 direct parser and filesystem-security assertions.
3. `tests/unit/test-probe-handoff-comprehension.py` — admission-before-model-call evidence; missing tool-disable assertion is part of SEC-F-10's repair.
4. `tests/integration/test-check-domain.py` — 41 focused real-hook outcomes, including exception and pre-mutation Edit cases.
5. `.claude/skills/harness/bin/check-domain.sh` — PreToolUse trust boundary, Edit reconstruction, exit-2 behavior.
6. `.harness/harness.json` — frozen baseline, locally-run probe registration, and authoritative `review: advisory_unless_high` policy.
7. `tests/integration/test-check-state.py` — 17 focused persisted-mode/baseline/grammar outcomes.
8. `.claude/skills/harness/bin/check-state.sh` — corpus input, baseline use, no target re-resolution, module-failure reporting.
9. `.claude/skills/harness/templates/HANDOFF.md` — author-facing untrusted input contract and typed pointer surface.
10. `.claude/skills/harness/SKILL.md` — five-section author/orchestrator instruction surface.
11. `tests/manual/probe-handoff-comprehension.py` — model, host-tool, repository-input and terminal-output boundaries; source of both findings.
12. `.harness/harness/docs/DECISIONS.md` — DEC-159/214 approved resolution and persisted-check posture.
13. `.harness/harness/docs/DECISIONS-INDEX.md` — indexed DEC-159/174/179/201/212/213/214 authority routing.
14. `.harness/harness/features/FEAT-54-handoff-done-when/notes/handoff-plan.md` — real non-empty ordered Scope and approval pointer input.
15. `.harness/harness/features/FEAT-54-handoff-done-when/notes/handoff-build.md` — real non-empty ordered Scope and approval pointer input.
16. `tests/integration/test-run-unit-tests-kinds.py` — **5/5** current-pin registration, mutation and normal-suite-exclusion checks.

## Measurements and adequacy limits

- Exact SC-04, repository root: `bash .claude/skills/harness/bin/check-state.sh` → **exit 0**, **0 `Done when` findings**, **0 tagged violations**.
- Focused current-pin checks: validator **54/54**; probe admission **6/6**; real write-hook group **41/41**; persisted-state group **17/17**; probe registration/isolation **5/5**.
- No credentialled model call, SC-10 UAT, formatter, linter, build, or unrelated suite ran.
- SEC-F-10 was not exercised with a malicious live model prompt. Its mechanism is bound to the current program argv and the installed runtime's own help: tools default enabled, `--no-tools` disables them, and `--auto-approve` bypasses approval. Model obedience is the only unexecuted precondition.
- Ordinary symlink/special-file behavior is covered; concurrent directory-renaming races were not stress-tested. The resolver's canonical target is reopened by path after metadata checks, so its race resistance is not proven, but the only demonstrated outputs are authority-resolution booleans and no concrete attacker gain above a local filesystem writer's existing privilege was established; no speculative finding is raised.
- The secret scan covers credential-shaped literals, not semantic secrets. SC-10 remains pending operator action and is intentionally not claimed.

```yaml
VERDICT: FAIL
DIGEST:
  headline: "SC-04 is green, but a repository-controlled handoff can prompt-inject the probe's auto-approved, tool-enabled OMP agent; terminal-control output also remains medium advisory."
  in_scope: true
  scope_reason: "The exact 16-path diff accepts governed repository text, resolves author-selected filesystem targets, invokes a credentialled model agent, emits repository/model output to a terminal, and controls write/state gates."
  severity_max: high
  findings: 2
  must_fix:
    - "SEC-F-10: run the comprehension model with built-in tools disabled (`--no-tools`) and without `--auto-approve`, then pin that argv contract in tests/unit/test-probe-handoff-comprehension.py. Owner: harness-dev-ops via harness-eng-lead."
  threat_model:
    - { boundary: "repository contributor-controlled handoff -> prompt -> default-enabled OMP tools auto-approved on operator host", stride: "TIE", mitigated: false }
    - { boundary: "repository/model/provider text -> operator terminal", stride: "TR", mitigated: false }
    - { boundary: "finding/approval pointer -> shared parser -> project filesystem", stride: "TID", mitigated: true }
    - { boundary: "PreToolUse Edit payload plus existing bytes -> reconstructed candidate -> mutation decision", stride: "TE", mitigated: true }
    - { boundary: "persisted note plus frozen baseline -> INV-17 routing", stride: "T", mitigated: true }
    - { boundary: "validator import/resolver exception -> hook decision", stride: "E", mitigated: true }
  open_questions: []
  files_touched:
    - .harness/harness/features/FEAT-54-handoff-done-when/notes/review-harness-security-reviewer-c4.md
  expertise_update: []
artifact: .harness/harness/features/FEAT-54-handoff-done-when/notes/review-harness-security-reviewer-c4.md
```
