# Security review — FEAT-1714-reject-verb — cycle 0

## BLUF

FAIL. The pinned change is security-relevant because it accepts an autonomous rejection judgement, publishes its reason to GitHub, and performs irreversible parent/milestone mutations. The input and command-injection boundaries are constrained, but the confirmed mutation path fails open: several GitHub write failures still produce exit 0, and failures after the parent closes do not prevent the local terminal station from being recorded. That can leave an irreversibly closed ticket with missing provenance or incorrect board/milestone state while the harness records a completed rejection.

## Review identity

- Pinned SHA: `82bdef1a6f7cd89005f661a06296725f5b1ad9b1`
- Exact range: `origin/main...82bdef1a6f7cd89005f661a06296725f5b1ad9b1`
- Scope: all 46 changed paths in that range; no HEAD-derived claims
- Required records read: BRIEF, plan decisions/tasks, feature.json, STATE, both handoffs, signed answers, and all five receipts present at the pin

## Inspected surfaces and disposition

- **Autonomous digest / deserialization boundary (T-01):** `validate-digest.py:388-434` binds `judgement` to `status: rejected`, requires the exact three-key inline mapping, a positive non-boolean integer or `none`, a non-empty one-line reason of at most 240 characters, and integer-zero cycles. `feature-record.py` and `feature-schema.json` extend the closed enum only. Fail-closed for malformed return shapes.
- **Local record invariants (T-03):** `check-state.py` INV-44 separately rejects non-zero cycles, wrong run count/owner, missing reject judgement, signatures, and panels. The shared terminal tuple is consumed by route, domain, lifecycle, handoff, board, and worktree checks. No auth bypass or privilege elevation found.
- **GitHub authorization and mutation boundary (T-02/T-05):** `gh-sync.py reject` requires explicit `--yes`; dry-run performs no GitHub mutation. Repository/parent/milestone identifiers come from validated recorded configuration, not the reason. Calls use list-form argv or fixed API paths, so the reason and issue value are not shell-interpreted. Finding SEC-1714-01 covers failure ordering/exit status.
- **Reason and successor input:** successor accepts only ASCII-digit strings coercing to a positive integer or literal `none`; reason is read from an explicit operator-supplied file and must be exactly one non-empty line. A 0600 temporary body file is passed with `--body-file` and removed in `finally`. GitHub Markdown/mentions remain interpretable, but this is operator-confirmed content and grants no capability beyond the confirming operator.
- **Data exposure / secrets:** full-diff credential-shaped scan found no added secret, token, password, authorization header, API key, or private key. Reject comments intentionally disclose the supplied rejection reason and successor on the already-authorized GitHub parent; no unrelated feature data is added.
- **Path / command injection:** no shell invocation was added. `reason_file` is opened as a path chosen by the invoking operator; it is never joined beneath a less-trusted directory or interpolated into a command string. Temporary-file cleanup is unconditional after creation.
- **TOCTOU:** the dry-run report and confirmed invocation are separate processes and GitHub state can change between them, but execution reloads the recorded parent/milestone and never discovers or mutates sub-issues. The explicit second `--yes` invocation is the authorization boundary; no attacker-controlled expansion of the mutation set was found.
- **Other 45-path census:** terminal-vocabulary consumers (`board_lifecycle.py`, `factory_config.py`, `gh_board.py`, `handoff_done_when.py`, `plan-merge.py`, `check-domain.py`, `check-plan-routes.py`, `worktree_terminal.py`), doctrine/templates/decision docs, and the feature records introduce no additional trust boundary. The 12 test files exercise validation and lifecycle behavior but are non-production. Every remaining feature note/receipt/review is provenance-only and contains no credential or executable payload.

## Finding

### SEC-1714-01 — med — substance — T-02/T-05

**Concrete failure scenario:** an operator confirms `gh-sync.py reject ... --yes`; GitHub successfully closes the parent, then the backlog write, comment, label, or milestone write fails because of a transient API failure or narrower token permission. `gh-sync.py:1875-1893` prints errors but continues, and the numeric-successor path still records `rejected` at line 1894. The `none` path likewise returns 0, so T-05's caller cannot distinguish partial failure before performing its separate station write. Even failure to close at `gh-sync.py:1868-1873` returns normally with exit 0. The operator/harness therefore receives success while GitHub lacks some or all of the promised provenance/disposition; after a successful close the outcome is partly irreversible.

**Attacker/access/gain:** exploitation requires unusual access or conditions: a GitHub collaborator/admin changing label/comment/milestone permissions or state between confirmation and execution, or a transient API failure. They can cause the local record and GitHub disposition to disagree and suppress the durable rejection reason/label, impairing tamper evidence and operator overrule. They do not gain repository privileges.

**Evidence:** `.claude/skills/harness/bin/gh-sync.py:1868-1894`; BRIEF SC-03 requires the confirmed path to comment, label when numeric, reseat, close the milestone, and record the station last; T-05 permits the station write only after `gh-sync.py reject` succeeds. Errors are logged but never converted to a non-zero/refused result, and `_record_station` is not gated on all prior writes succeeding.

**Required remediation:** make every required reject mutation contribute to an explicit failure result; do not record `rejected` (and return non-zero so the `none` caller cannot record it) unless every required GitHub action succeeds. Preserve close-before-reseat ordering and report which irreversible writes already occurred so retry/recovery is auditable.

## STRIDE / OWASP disposition

| Boundary | STRIDE | OWASP area | Disposition |
|---|---|---|---|
| Orchestrator digest → validator | T | injection / input validation | Mitigated by exact keys, strict types, line/length bound, status binding, zero-cycle check. |
| CLI reason/successor → GitHub | T, I | command injection / input validation / data exposure | Shell injection mitigated by list argv and body-file; intended comment exposure confirmed by `--yes`. |
| Local feature record → GitHub lifecycle | T, R | integrity / repudiation / fail-open | **Unmitigated: SEC-1714-01.** Partial writes and even close failure return success; station may certify an incomplete lifecycle. |
| GitHub parent/milestone mutation | E, S | authorization | Uses the operator's configured `gh` authority and explicit `--yes`; no client-side privilege grant or user-selected repository added. |
| Terminal station consumers | T, D | schema/state validation / availability | Shared closed vocabulary; malformed/unknown stations remain refused. No new unbounded work. |

## Dismissed candidates

1. **Reason-file path traversal:** dismissed. The path is explicitly supplied by the trusted operator running the command, not derived from an issue or judgement; reading another local file grants no new capability to that same OS principal. Contents are passed as a body file, not executable syntax.
2. **Shell/flag injection through reason or successor:** dismissed. GitHub calls are list-form argv; reason bytes never become argv tokens, and successor must be positive digits before appearing only in comment content.
3. **GitHub Markdown / mention injection:** dismissed as a vulnerability. The confirming operator is shown the intended comment action and already has authority to post equivalent content. There is no privilege delta; mention notifications are an inherent, visible property of the chosen GitHub comment sink.
4. **Unbounded reason denial of service:** dismissed as security finding. The digest boundary caps the autonomous reason at 240 characters. `gh-sync.py` lacks the same cap, but only the local operator can choose that file; GitHub rejection then falls under SEC-1714-01's incorrect-success mechanism rather than a separate attacker-controlled DoS.
5. **Nonexistent/self-referential successor:** dismissed. The value is provenance supplied by the autonomous judgement and confirmed by the operator; the command does not grant the referenced issue authority or mutate it.
6. **Dry-run/confirmation TOCTOU:** dismissed. Execution reloads the same recorded parent-only mutation set and cannot expand to sub-issues; `--yes` is a fresh operator authorization. State drift can cause write failure, which is covered by SEC-1714-01.
7. **Secrets in changed docs/fixtures:** dismissed after full 46-path diff scan; credential-shaped additions were only `tokens: null`, prose mentioning operator authorization, and test variable names.

```yaml
VERDICT: FAIL
DIGEST:
  headline: "Reject lifecycle fails open on GitHub write errors and can certify incomplete irreversible mutations."
  in_scope: true
  scope_reason: "The diff validates untrusted autonomous judgement/reason input and adds operator-authorized GitHub issue, board, comment, label, milestone, and terminal-record mutations."
  severity_max: med
  findings:
    - { id: SEC-1714-01, kind: substance, scope: task, severity: med, reader: security-reviewer, owner: T-02/T-05, summary: "gh-sync reject returns success on required GitHub write failures and may record rejected after partial mutation.", why: "A close, comment, label, backlog, or milestone failure can leave GitHub and the terminal local record inconsistent, with missing rejection provenance after an irreversible close." }
  must_fix:
    - "SEC-1714-01: fail non-zero and withhold the rejected station until every required GitHub mutation succeeds; report partial irreversible progress for recovery."
  threat_model:
    - { boundary: "orchestrator reject digest to validator", stride: T, mitigated: true }
    - { boundary: "operator reason and successor to GitHub comment", stride: T, mitigated: true }
    - { boundary: "local feature record to GitHub lifecycle", stride: R, mitigated: false }
    - { boundary: "GitHub mutation authority", stride: E, mitigated: true }
  open_questions: []
  files_touched:
    - .harness/harness/features/FEAT-1714-reject-verb/notes/review-harness-security-reviewer-c0.md
  expertise_update: []
artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-1714-reject-verb/.harness/harness/features/FEAT-1714-reject-verb/notes/review-harness-security-reviewer-c0.md
```
