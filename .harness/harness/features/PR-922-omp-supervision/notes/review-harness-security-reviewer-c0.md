# Security review — PR #922 (OMP long-running supervision), `7ccfae8..66e9a9d`

**VERDICT: PASS** (no must-fix; med is the highest severity found, and it is a DoS-only
trigger with unverified blast radius, not data/credential/privilege compromise)

## BLUF

In scope. One real, diff-introduced finding at `med`: the new `HARNESS-FEATURE:` flow-identity
marker — which gates single-flight claims and the #551 "children still in flight" refusal — is
captured from arbitrary conversation message content with no role filter, unlike its sibling
`HARNESS_AGENT_ID` marker which only ever reads the host-controlled system prompt. Externally
authored text (a GitHub issue/PR body, a fetched page, a file) that a harness agent reads or
reflects, and that happens to contain a line matching the marker regex, is treated as an
authoritative assertion — either crashing the hook chain via an uncaught throw once the real
feature is already declared, or (narrower window) being silently accepted as the flow's identity
before it is. One `low` finding on the manual claim-release CLI path (surface 1, cross-feature,
same-user). Surfaces 2 (registry-as-shell-input), 3 (digest/mirror exposure), and 4 (secrets) are
each measured clean — see dispositions below.

## Surface-by-surface disposition

**1. Trust boundary between concurrent features (`inflight_registry.py`).**
Measured, not assumed. Read the full pre- and post-diff module
(`.claude/skills/harness/bin/inflight_registry.py`). Findings:
- The **automated** lifecycle (dispatch-guard.sh → `claim_with_receipt` → host-issued
  `claim_id`/`agent_id`/`job_id` → `releaseClaim` in `harness-hooks.ts`) is correctly scoped:
  `claim_id` is a server-side `uuid4`, `agent_id`/`job_id` come from `ctx.agentId` /
  `task:subagent:lifecycle` event data (host-controlled, not model/tool-input controlled).
  `_matches()` requires exact equality on every selector supplied, so one feature's automated
  release can't touch another's claim by accident.
- **Finding (low), Tampering.** `release()`/`reconcile()`'s CLI selectors (`--agent`,
  `--feature`) carry no binding to the calling process's own identity — no PID check, no
  claim ownership token. `release_cmd()` (the string printed to an operator on refusal) uses
  only `--agent`/`--feature`, both of which are trivially discoverable (`inflight_registry.py
  list`, or reading `.harness/.inflight-claims.json` directly, or worktree directory names).
  **Threat actor:** a Bash-capable harness agent already running under the operator's own
  account (worst case: one steered by prompt injection from content it is processing) that
  targets a *different, concurrently running* feature. **Sequence:** it runs
  `python3 .agents/skills/harness/bin/inflight_registry.py release --agent harness-pm --feature
  <sibling-feature>`, which defeats that sibling's single-flight protection — precisely the
  #628/#551 hazard this PR otherwise strengthens. Rated `low`, not higher: this requires an
  already-trusted local process, a second feature genuinely running concurrently, and correctly
  guessing both names; it is same-user/same-machine (no privilege gain), and the worst outcome
  (two concurrent PM writers) is caught by ordinary `plan.yaml` diff review before merge, same as
  before this PR. `bash-write-guard.sh` does not block it (it only intercepts *write* patterns —
  `perl -pi`, `sed -i`, redirections — not an ordinary command invocation, and this is the exact
  command the tool's own refusal message tells an operator to run).
- **PID-reuse liveness (explicitly asked about).** `_pid_alive()` (`os.kill(pid, 0)`) is the
  sole OMP-liveness check. PID reuse after the true supervisor dies produces a **false "still
  alive,"** which delays crash reconciliation (self-heals once the reused PID exits) — an
  availability nuisance, not an authorization bypass: `_matches()` still requires the *feature*
  and *agent* strings to equal the true stored values, so a reused PID cannot be leveraged to
  seize or misattribute a claim it doesn't already match. No escalation path found here.

**2. Registry file as untrusted input → shell/subprocess/log injection.**
No finding — measured. `harness-hooks.ts`'s `runPolicy()` calls `spawnSync(gatePath(script),
args, {...})` with **no `shell: true`** and `args` as an array, so Node never tokenizes through a
shell regardless of claim content. `dispatch-guard.sh` pipes the JSON payload to python **only
via stdin** (`printf '%s' "$payload" | python3 -I -c '...'`); no payload field is ever
string-interpolated into a shell command. `release_cmd()` shell-quotes every argument with
`shlex.quote()` before composing the printed remedy string. `feature_root()`/`_root_for()`
resolve a feature to a worktree by `os.path.basename(worktree) == feature` equality against
real, already-enumerated `git worktree` paths — never by joining the untrusted feature string
into a filesystem path — so no path-traversal vector either. Clean.

**3. Data exposure in digest/mirror paths.**
No finding — measured. `validate-digest.py`'s diff only threads a `feature` parameter through
already-local release/children-lookup calls (no new network call, no new log field). The mirror
doc (`github-mirror.md`) changes are prose-only. `gh-close-gate.sh`'s one code change
(`python3 -P` → `python3 -I`) is a *stronger* interpreter-isolation flag, consistent with the
same hardening applied elsewhere in this diff (T-08/T-15 comments), not a regression. No new path
from local content (transcripts, paths, tokens) to GitHub or logs was found in this diff.

**4. Secrets.**
No finding — measured, not inferred. Grepped the full diff (all 48 files, not only the four
named) for credential-shaped strings (`api[_-]?key|secret|token|password|bearer|authorization|
ghp_|gho_|github_pat_|BEGIN …KEY`). The only hits are unrelated: a config field literally named
`orchestrator_context_warn_tokens`, and prose describing an "unguessable token" used as a
*test canary* in the live-run verification narrative (DEC-204) — not a credential. No new
provider keys, no logged secrets, in `.omp/config.yml`, `harness-hooks.ts`, or the 15 agent
frontmatter `blocking: true` additions (a control-flow property, not an access-control change —
confirmed against `check-omp-port.py`'s new drift check, which enforces it symmetrically).

## The headline finding, in full

`.omp/extensions/harness-hooks.ts`: `detectHarnessFeature()` is applied to
`messageText(candidate)` inside **both** `message_update` and `message_end` handlers, with **no
role filter** — contrast `detectHarnessAgent()`, which only ever scans the host-controlled
`event.systemPrompt` array, and `lastAssistantText()` in the same file, which explicitly checks
`message?.role !== "assistant"` before using content. `setFeature()` runs unconditionally on
every message for the life of the agent's turn:

```
if (currentFeature && currentFeature !== feature) throw new Error(...);
currentFeature = feature;
```

**DEC-204 states the intended boundary** ("The extension captures that message before the first
tool call") but the shipped code has no such cutoff (no `capturedOnce` guard, unlike the
`expertiseInjected` boolean used for the analogous one-shot injection nearby) — it rescans every
subsequent message of any role for the whole conversation. This is new in this diff (the base
`harness-hooks.ts` had no feature concept at all).

**Threat actor:** anyone whose text a harness agent reads or reflects — a GitHub issue/PR
author, a web page fetched during research, a file under review. No access to Harness or the
operator's account is required.

**Sequence:** once an agent's real `HARNESS-FEATURE: FEAT-NN-slug` is legitimately captured
(the normal case, from its own dispatch's first line), any later message — including the
agent's own output when it quotes or summarizes external content — that contains a line
matching `^HARNESS-FEATURE: (?:FEAT|BUG)-[0-9]+(?:-[a-z0-9]+)+$` throws an uncaught `Error` from
inside an async `pi.on(...)` handler. This is exactly the failure mode this PR is built to
survive (a multi-hour unattended run), triggered by ordinary content a harness agent's job is to
process — e.g. this very PR's own body, or any diff/issue an agent is asked to review, could
carry such a line. `omp-hooks.test.ts`'s "OMP task lifecycle adapter" fixture only exercises the
golden path (one clean assignment message); no case exercises a conflicting or role-other-than-
declaration occurrence.

**Severity: med.** I cannot verify from this repo how the OMP host runtime handles an uncaught
exception thrown from a `pi.on(...)` async handler — whether it aborts only that hook invocation
or kills the whole supervised session (`open_questions`, Q1). I am not inflating to `high`
against that unverified worst case, but the finding stands regardless of blast radius: an
external, unauthenticated party can, with no interaction with Harness or the operator, plant a
control-plane value that a security-critical extension currently trusts on parity with its own
system prompt. `must_fix`: scope `detectHarnessFeature()`'s message-content path to the exact
mechanism DEC-204 describes (the first non-tool-result message of the conversation, captured
once) rather than every subsequent message of any role.

## threat_model

- boundary: cross-feature claim release/reconcile via `inflight_registry.py` CLI (same-user,
  same-machine) — stride: T — mitigated: false (automated paths ARE mitigated via host-issued
  claim_id/agent_id/job_id; only the manual/CLI selector path is open)
- boundary: PID-based OMP claim liveness (`_pid_alive`, PID reuse) — stride: D — mitigated:
  true (self-healing false-negative only; no ownership/authorization bypass demonstrated)
- boundary: registry file / hook payload → shell or subprocess argv — stride: T/I — mitigated:
  true (array-argv `spawnSync`, stdin-only payload transport, `shlex.quote` on the one printed
  remedy, basename-equality worktree lookup)
- boundary: external content → `HARNESS-FEATURE` flow-identity marker (`detectHarnessFeature`
  over unfiltered message content) — stride: T/D — mitigated: false

## Open questions

- Q1 (non-blocking, informs severity only): does an uncaught exception thrown from a
  `pi.on("message_update"/"message_end", ...)` async handler abort only that hook invocation, or
  terminate the supervised OMP session? Not answerable from this repo; would reclassify the
  headline finding toward `high` if it kills a multi-hour run outright, or toward `low` if it is
  swallowed per-event.

```yaml
VERDICT: PASS
DIGEST:
  headline: "Feature-scoped claims are sound on their automated paths; the new HARNESS-FEATURE marker trusts unfiltered message content (any role, whole conversation) on par with the system prompt, letting external content crash or spoof flow identity — med, not must-fix, pending host-crash-blast-radius confirmation."
  in_scope: true
  scope_reason: "Diff adds a new cross-feature trust boundary (feature-scoped claims sharing one registry file), a new externally-influenceable control marker (HARNESS-FEATURE parsed from live conversation content), and touches process supervision (PID liveness, wall-clock removal) — all genuine security surface, confirmed against the pre-diff versions of inflight_registry.py and harness-hooks.ts to isolate what this PR actually introduces."
  severity_max: med
  findings: 2
  must_fix: []
  threat_model:
    - { boundary: "cross-feature claim release/reconcile via inflight_registry.py CLI", stride: "T", mitigated: false }
    - { boundary: "PID-based OMP claim liveness (PID reuse)", stride: "D", mitigated: true }
    - { boundary: "registry file / hook payload -> shell or subprocess argv", stride: "T", mitigated: true }
    - { boundary: "external content -> HARNESS-FEATURE flow-identity marker", stride: "T", mitigated: false }
  open_questions:
    - { id: Q1, question: "Does an uncaught exception from a pi.on message_update/message_end async handler abort only that hook call, or the whole OMP-supervised session? Determines whether the HARNESS-FEATURE finding is med or high.", blocking: false }
  files_touched: []
  expertise_update: []
artifact: .harness/harness/features/PR-922-omp-supervision/notes/review-harness-security-reviewer-c0.md
```
