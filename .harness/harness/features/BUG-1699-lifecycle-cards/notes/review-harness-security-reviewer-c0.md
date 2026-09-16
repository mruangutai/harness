# Security review — BUG-1699-lifecycle-cards

**PASS.** The pinned diff `8ef4731e816f08dbc562206134c100b0c034a812..ed64ea9cc4ef92e3e54adfa0849a0147230b480b` is security-scoped in because local issue/config records cross into outbound GitHub Project writes and command output. No exploitable security regression was found.

## Surface audit

- **Injection / argv:** Changed Python subprocesses remain list-form argv. Recorded issue identifiers are schema-loaded integers before reaching GitHub arguments; station values are closed enums before projection/write. The new command transaction quotes the parsed `RESUME:` value and admits only `ready|building|review` before invoking `gh-sync.py`. No shell evaluation, SQL/template construction, or flag-shaped untrusted positional value was introduced.
- **Path traversal:** Feature paths are local operator arguments and joins remain under the selected feature directory. The new sync-disabled `status` fast path can update that directory's `plan.yaml`, but grants no capability beyond the invoking operator's filesystem authority and still routes through `plan-merge.py` validation.
- **Auth / authorization:** No authentication or authorization control changed. Existing `gh` authentication and configured repository/project authority remain the outbound boundary; card mutations are limited to recorded issue numbers and configured board fields.
- **Secrets / exposure:** Full-diff credential-pattern census found no added credential material. New output contains lifecycle receipts, issue numbers, stations, paths, and existing GitHub error detail—not tokens or new PII. No export/spreadsheet surface exists.
- **Input validation / DoS:** `approval.resume_station`, feature station, board configuration, plan/feature documents, and issue-number shapes are validated or closed before use. Reconciliation reuses one bounded board snapshot and continues per-card failures; no new unbounded attacker-controlled expansion was introduced.
- **SSRF / redirects:** No user-controlled URL or redirect was added. Outbound calls remain through the configured GitHub CLI/adapters.

## Per-file shipped census

| Paths | Security disposition |
|---|---|
| `.claude/skills/harness/bin/{gh_board.py,gh-sync.py}` | In scope: untrusted local records to configured GitHub writes; closed stations, validated board config, integer issue IDs, list argv. |
| `.claude/skills/harness/bin/{board_lifecycle.py,check-state.py}` | In scope: local feature census plus GitHub read/write boundary; bounded snapshot, repository filtering, schema loaders, list argv. |
| `.claude/skills/harness/bin/plan-merge.py` | In scope: local plan input; resume value is derived and allowlisted before receipt emission. |
| `.claude/commands/harness-{plan,patch}.md`, `.omp/commands/harness-{plan,patch}.md` | In scope: executable command text; receipt is quoted and exact-enum checked before argv use. |
| `.claude/skills/harness-spec-driven/SKILL.md`, `.claude/skills/harness/SKILL.md`, `.claude/skills/harness-digest-dev/SKILL.md`, `.claude/skills/harness-handoff/SKILL.md`, `.claude/skills/harness/references/{build-phase.md,github-mirror.md}`, `.claude/skills/harness/teams/plan.yaml` | In scope by command-orchestration reachability; no new credential, shell interpolation, URL, or authority widening found. |
| `.harness/harness/docs/{DECISIONS.md,DECISIONS-INDEX.md}` | Out of direct runtime surface; authority text only, no secret-shaped additions. |
| `tests/integration/{test-board-lifecycle.py,test-check-state-inv26.py,test-gh-sync-record.py,test-gh-sync-start-task.py,test-plan-merge.py,test-station-argument-spelling.py}`, `tests/unit/test-gh-board.py` | Test-only; fixtures contain no credentials and exercise the same closed station/recorded-card boundaries. |

## STRIDE

| Boundary | STRIDE | Result |
|---|---|---|
| `plan.yaml` / `feature.json` → lifecycle projection | T | Mitigated by schema loaders, closed station vocabulary, and integer issue records. |
| Projection → configured GitHub Project | T, I, E | Mitigated by configured repo/board authority, exact recorded issues, and GitHub authentication; no cross-repository selector added. |
| Approval receipt → command transaction | T, E | Mitigated by exact `RESUME:` parsing, shell quoting, and the three-value allowlist. |
| GitHub/local errors → operator logs | I | Mitigated for this delta: no credentials are added to output; new messages expose only operational identifiers already available to the operator. |
| Reconciliation over active features | D | Mitigated by one bounded snapshot and per-card best-effort writes; no new unbounded network enumeration. |

## Result

No findings and no must-fix items. `severity_max: none`; the diff was scoped in and audited rather than declined. Tasks assessed: T-01 through T-05; no scope change is required.
