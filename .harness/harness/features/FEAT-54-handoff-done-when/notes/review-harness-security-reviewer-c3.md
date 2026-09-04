# Security review c3 — FEAT-54 handoff Done when

## BLUF

**FAIL.** The security-sensitive repairs are fail-closed: finding and approval targets are contained and bounded; nested/duplicate headings cannot hide authorities; approval targets require real ATX headings; rejected probe inputs make zero model calls; and invalid/non-UTF-8 Edit candidates are refused before mutation. The prior medium terminal-control injection remains advisory. Shipping is nevertheless blocked because literal SC-04 exits 1 on one FEAT-51 violation, even though no output names `Done when`.

Reviewed immutable range `0ec44965a961d19177de871c3bb1f02b701e646b..39602414e1cfe792655b7e68bce367e92790c32a`. `git diff --name-only 39602414... -- <required 16 paths>` printed nothing, binding the inspected bytes to the pin.

## Findings

### F-04 — high, must-fix — literal SC-04 is false

From the exact repository root, literal `bash .claude/skills/harness/bin/check-state.sh` exited **1**. The complete output contained exactly one tagged violation and **zero** case-sensitive `Done when` matches:

> `FEAT-51-claude-code-lifecycle-safety: status is 'done' but notes/handoff-validate.md is missing — the validate seam was crossed without a handoff; the successor is on the disk-only path (DEC-159).`

The remaining output rows are informational `note` rows, not additional violations. A ship decision cannot truthfully claim BRIEF SC-04's required clean root check. **Owner lane:** harness-orchestrator/Main direct repository-state and review-pin reconciliation; this review must not repair or fixture-substitute FEAT-51.

### SEC-F-08 — med, advisory — repository/model control bytes reach the terminal

A repository contributor can place ESC/OSC bytes in an admitted handoff filename or `Scope:`/`Authority:` fact; a model response is a second untrusted producer. The locally-run probe prints rejected/accepted paths, facts, provider errors, and answers without neutralization (`tests/manual/probe-handoff-comprehension.py:87-98,156-197`). When an operator runs it, crafted bytes can clear or rewrite visible evidence and, on permissive terminals, alter terminal state or clipboard. The c2 byte probe observed literal ESC bytes; the probe is byte-unchanged from c2 to this pin, and the c3 UI review independently matched this mechanism and severity. **Owner lane:** harness-dev-ops via harness-eng-lead. This is non-gating at med.

## Prior F-01–F-09 disposition

| Finding | Disposition | Security evidence at the pin |
|---|---|---|
| F-01 authority containment/fail-closed | **Closed.** | Finding and approval independently reject absolute, traversal and control-bearing paths; canonical resolution must remain under root; only regular UTF-8 files at most 1 MiB are read; resolver exceptions become problems and the write hook exits 2 (`handoff_done_when.py:57-101,143-174,224-253`; unit and real-hook cases cover both types). Directory, FIFO/special, oversize, unreadable/non-UTF-8, and symlink-escape outcomes fail closed by the same bounded reader. |
| F-02 local-file disclosure through probe admission | **Closed.** | Admission precedes `run`/`ask`, canonicalizes to `.harness/harness/features/<FEAT>/notes/handoff-*.md`, rejects final symlinks, opens no-follow/nonblocking, checks descriptor type/size, bounds the read, then UTF-8 decodes. Six focused tests passed; every outside/traversal/symlink/directory/wrong-name/oversize rejection kept the call log empty, while the valid control made exactly two calls. Unreadable/non-UTF-8 inputs are caught before `ValidatedNote` construction. |
| F-03 invalid/unreadable Edit mutates before refusal | **Closed.** | PreToolUse reconstructs handoff Edit candidates and validates before mutation. Invalid shape and non-UTF-8 prior bytes exit 2 with byte-identity assertions (`check-domain.sh:1819-1881`; `test-check-domain.py:4138-4184`). Other `OSError`/ambiguous reconstruction returns to the Edit tool's own match/read refusal; it does not create a writable candidate the hook silently approved. |
| F-04 literal SC-04 | **Survives, high, must-fix.** | Exact violation and owner above. This converges with the c3 QA and UI reviews. |
| F-05 blank Scope | **Closed.** | Whitespace-only values are refused by unit, write-gate and state-gate cases. |
| F-06 Scope order | **Closed.** | The product ruling in `notes/research-FEAT-54-validation-order-c1.md` applies REQ-02; all three layers require the non-empty Scope before every Authority. |
| F-07 complexity grades | **Closed.** | The exact pinned grader recorded by c3 QA exited 0 with **86 passing functions**; production met bar 4, tests/probes bar 3. |
| F-08 nested/duplicate truncation (code-review numbering) | **Closed.** | Exactly one Done-when H2 is required; nested H3 is retained as unexpected prose rather than truncating; duplicate H2 is counted and refused. Direct parser execution passed **54/54** named assertions, including both mutants. |
| F-09 non-Markdown approval heading | **Closed.** | `_atx_heading_text` requires 1–6 hashes, separating whitespace and valid ATX form; `#Approval` and seven hashes fail beside a valid `## Approval` control in unit and real-hook tests. |
| SEC-F-08 terminal output (security-review numbering) | **Survives, med advisory.** | Raw terminal sinks remain as described above. |

Both new handoffs have ordered non-empty immediate-action scopes and a contained `approval:.harness/harness/features/FEAT-54-handoff-done-when/BRIEF.md#Approval` target. The target is a real ATX heading, and the BRIEF and plan approval records name Mike Ruangutai with approved status dated 2026-09-02. No new handoff uses a finding authority. Finding and approval resolution have independent negative cases and positive controls; neither relies on the other type's coverage.

## Other OWASP/STRIDE results

- **Auth/secrets/dependencies:** no route, session, tenant authorization or redirect changed. A full 87-path pinned-diff signature sweep found no API-key, GitHub-token, AWS-key, Slack-token or private-key literal. No dependency was added; PyYAML was already required.
- **Injection/requests:** authority paths are not shelled; the probe uses list-form argv. No SQL/NoSQL, template, CSV/spreadsheet, SSRF or user-controlled redirect surface exists. `--model` is an operator-selected argv value, not shell text.
- **Data exposure:** a real probe intentionally sends an admitted repository handoff to the selected model provider, disclosed by its docstring, locally-run registration and DEC-214. Rejected inputs make no model call. This closes arbitrary local-file disclosure but does not promise redaction of admitted repository content.
- **Persisted corpus:** `resolve=False` still validates unsafe path grammar but opens no authority targets, as approved. The corpus reader's ability to follow an on-disk handoff symlink or wait on a special file predates this diff; a local actor able to install either already controls the checkout/state gate, so it is assessed-and-dismissed rather than charged to FEAT-54.
- **Availability:** authority reads are capped at 1 MiB and reject non-regular files before open; probe reads are no-follow/nonblocking and bounded. The 60-line whole-note cap bounds authority-resolution work without adding a forbidden per-section cap.

## Five repaired lead digests

All five carry fenced lead YAML with top/member `PASS`, empty `must_fix`, and no blocking question hidden behind a passing verdict. The two validator digests explicitly carry SC-04 as an unresolved external escalation; the three engineering digests have empty escalations. C3 QA invoked `validate-digest.py lead` separately for each, and every normal validation printed `digest ok` and exited 0—none passed through DEC-127's loud self-exception path:

- `runs/2026-09-03-qa-validation-c2-validator/digest.md`
- `runs/2026-09-03-validation-c1-eng/digest.md`
- `runs/2026-09-03-validation-c2-eng/digest.md`
- `runs/2026-09-03-qa-post-simplify-c2-validator/digest.md`
- `runs/2026-09-02-validation-c1-eng/digest.md`

## Scope census and evidence

The diff has **87 paths**. The 16 required files were inspected individually: five playbook/gate/template files, config plus two decision files, both FEAT-54 handoffs, and six test/probe files. BRIEF and plan were inspected as approval authorities. The other 69 paths are FEAT-54 state/feature records, review/research/QA/receipt evidence, observations, and the grilling record; they add no executable boundary, and all were included in the credential-signature sweep. This review is in scope because the executable subset accepts governed handoff text, resolves author-selected filesystem paths, sends admitted content to a model provider, emits terminal output, and supplies lead digests interpreted by the orchestrator.

Focused execution at the pin: `test-handoff-done-when.py` exit 0 with **54** named PASS assertions; `test-probe-handoff-comprehension.py` exit 0 with **6** tests and a two-call valid control. C3 QA's configured sweeps discovered **25 unit** and **44 integration** files, both exit 0. No credentialled model call, formatter, linter, project-wide build, or SC-10 UAT was run. SC-10 remains pending operator action.

```yaml
VERDICT: FAIL
DIGEST:
  headline: "Security-sensitive authority, probe-admission, Edit, truncation and ATX repairs fail closed; terminal control injection remains medium, and literal SC-04 still fails on one FEAT-51 violation."
  in_scope: true
  scope_reason: "The diff accepts governed handoff input, resolves author-selected filesystem paths, can send admitted content to a model provider, emits repository/model data to a terminal, and carries lead digests interpreted by the orchestrator."
  severity_max: high
  findings: 2
  must_fix:
    - "F-04: obtain a review pin where literal repository-root SC-04 exits 0; current output has the one FEAT-51 missing-handoff violation and zero Done when matches. Owner: harness-orchestrator/Main direct repository-state and review-pin lane."
  threat_model:
    - { boundary: "governed finding authority -> pointer parser -> project filesystem", stride: "TID", mitigated: true }
    - { boundary: "governed approval authority -> pointer parser/strict ATX matcher -> project filesystem", stride: "TID", mitigated: true }
    - { boundary: "PreToolUse Edit payload plus prior bytes -> candidate -> mutation decision", stride: "TE", mitigated: true }
    - { boundary: "repository/CLI note path -> admitted note -> credentialled model provider", stride: "IT", mitigated: true }
    - { boundary: "repository note or model response -> operator terminal", stride: "TR", mitigated: false }
    - { boundary: "lead digest -> validator contract -> orchestrator routing", stride: "TE", mitigated: true }
    - { boundary: "repository corpus -> literal SC-04 state gate", stride: "TR", mitigated: false }
  open_questions: []
  files_touched:
    - .harness/harness/features/FEAT-54-handoff-done-when/notes/review-harness-security-reviewer-c3.md
  expertise_update: []
artifact: .harness/harness/features/FEAT-54-handoff-done-when/notes/review-harness-security-reviewer-c3.md
```
