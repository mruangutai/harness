# Security review — FEAT-44 — cycle 1 — `7ebfc9e..21e97ed`

**Verdict: PASS.** No high/critical finding. One `med` gap in the T-01 verify sweep (the fifth
inert check, hunted per dispatch), plus low/info hardening items. Nothing here blocks the ship;
the med item is a recommendation for the *next* fixture recapture, not a defect in what's
committed now — the committed fixtures are independently confirmed clean.

## Surface 1 — the fixtures (irreversible; audited line-by-line, both files, in full)

Read every line of both files (13 + 11 records = 24 total) verbatim, plus a per-key enumeration
across the concatenated JSON (script-generated, not sampled) and supplementary greps beyond the
author's own sweep (emails/IPs/URLs, `/Users`/`/home` paths, bearer/password/secret/token
keywords, 40+ char base64-shaped runs). **Zero hits beyond one false positive** (the literal MCP
tool name `mcp__snowflake_write_semantic_view_query_tool`, not a secret).

### Per-key classification (24 records, both files)

| key | class | verdict |
|---|---|---|
| `content[].text`, `content[].thinking` | scrubbed → `"fixture text"` | clean |
| `toolCall.arguments`, `data.args` | scrubbed → `{"command":"echo fixture"}` | clean |
| `toolResult` content | scrubbed → `"fixture text"` | clean |
| `session.cwd` | scrubbed → `/tmp/fixture` | clean |
| `systemPrompt`, `task` | scrubbed → `"fixture system prompt"` / `"fixture task"` | clean |
| `credential_pin` records | dropped entirely (0 occurrences, confirmed) | clean |
| `message.contextSnapshot.*` | kept intact (the field under test) | correct, synthetic numeric values only |
| `details.data.output`/`.reply`, `details.status` | synthetic (`"alpha"`/`"done"`/`"success"`) | clean |
| `data.reason`, `data.kind` (session_exit) | structural (`"dispose"`/`"normal"`) | clean, non-sensitive |
| `usage.*`, `cost.*`, `duration`, `ttft`, `timeoutSeconds`, `wallTimeMs` | real numeric telemetry from the trivial capture | non-sensitive, no finding |
| `toolCall.id` (`toolu_…`), `responseId` (`msg_…`) | real Anthropic API artifact IDs from the capture | opaque, non-secret, no finding |
| `session.id`, every record `id`/`parentId` | **real UUIDs/hex ids from an actual captured session — not in the provenance scrub table** | see finding SEC-1 (info) |
| `model`, `resolvedModel`, `agent`, `modelRole`, `thinkingLevel`, `tools` (incl. `mcp__dropbox_team_*`, `mcp__snowflake_*`) | **real values, retained verbatim — not in the provenance scrub table** | see finding SEC-1 (info) |
| `title`/`v`/`updatedAt`/`pad`, `type`/`customType`, `version` | structural, host-authored | non-sensitive, no finding |

**Independent conclusion: both fixtures are clean.** No local username, no `/Users`/`/home` path,
no `credential_pin` remnant, no PEM/AWS/GitHub/Slack-shaped secret, no email, IP, or URL, no real
tool output or command string. The scrub as executed matches its own provenance claims for every
field the provenance note names.

**SEC-1 (info, no action required this cycle).** The provenance note's scrub table is not
exhaustive of what's retained: `model`/`resolvedModel`/`agent`/`modelRole`/`thinkingLevel`/`tools`
(including two MCP integration names — Dropbox, Snowflake) and every record `id`/`parentId`
(including the real session UUID) are real, unmodified values from the capture, and the note is
silent on them. Assessed: non-sensitive — opaque ids and role/tool metadata, not credentials or
PII, and low value even for correlation. But the note's own framing ("scrub or drop **all** of the
following field classes") is not the same as "everything not scrubbed is fine," and this is
precisely the residual-class risk the dispatch asked me to hunt: a future recapture with a richer
tool roster (a real internal MCP server name, a non-public model alias) would sail through the same
unstated gap. Alternative: extend the provenance table with an explicit "retained deliberately,
assessed non-sensitive" row for these field classes, so the next recapture is judged against a
complete list instead of re-deriving it.

Not flagged as a security finding: a broken `parentId` chain exists in both files (`fd3fddaf`'s
`parentId: "64d6a78a"` resolves to no record in either file — a mid-capture record was dropped
during truncation without repairing the chain). This is a fixture-integrity concern, not a
disclosure risk (`64d6a78a` is an opaque id, no content). Noting it for QA rather than gating here.

### SEC-2 (med) — the T-01 secret/username sweep is a real gate on an irreversible step, and it has two concrete blind spots

`plan.yaml`'s T-01 `verify:` block is the automated floor under the one irreversible action in this
feature (a committed secret in fixture content can't be un-shipped). Its intent text claims the two
absence-checks are "each preceded by a positive control… so a grep that errors cannot read as a
clean sweep." Verified against the actual script (`plan.yaml:94-96`) and empirically:

1. **The claimed positive control doesn't control the thing it's guarding.** The only "control" is
   `grep -q '{' "$A" && grep -q '{' "$B"` — it proves the files are non-empty JSON, not that the
   secret-pattern or username regexes are capable of matching a real hit. It never injects a
   known-bad value and asserts the sweep catches it. A regex with a structural blind spot for a
   real secret shape reads exactly like a clean sweep; nothing in the script would tell the two
   apart. This is the fifth inert check the dispatch asked me to hunt for.

2. **The secret-pattern regex misses the single most likely secret shape for this project.**
   `credential_pin|-----BEGIN|AKIA[0-9A-Z]{16}|(sk|ghp|gho|github_pat|xox[abp])[-_][A-Za-z0-9]{8}`
   — empirically tested (`grep -qE` against synthetic secrets of realistic shape, this session):
   real **Anthropic** keys (`sk-ant-api03-…`) are **missed** (the `sk[-_]` branch demands 8
   *consecutive* alnum chars immediately after `sk-`, and `sk-ant-` breaks at 3 before the next
   hyphen); Google API keys (`AIza…`) are **missed**; DB connection strings with embedded
   credentials (`postgres://user:pass@host/db`) are **missed**. Given this feature's whole fixture
   corpus is captured from an Anthropic-model coding agent, an `sk-ant-` key is the most probable
   credential to appear in any future recapture, and the sweep is blind to exactly that shape.

3. **The username check is self-referential to the invoker, not the capturer.** `grep -qF
   "$(whoami)"` passed in this review only because the account running the check happens to be the
   same account (`molchairuangutai`) that captured the fixture. Run this same script from CI, from
   a different reviewer's machine, or after a recapture by a different author, and `$(whoami)`
   reflects the *runner's* identity, not whichever username may be baked into a re-scrubbed
   fixture — the check would pass vacuously regardless of whether a real username leaked.

Current fixtures are clean regardless (confirmed above by independent read), so this is not a
defect in what's shipping. It is a real gap in the mechanism meant to catch the next one.
Alternative: (a) replace the vendor-enumerated key pattern with a shape-based one — e.g. `sk-[a-z]+-[A-Za-z0-9_-]{20,}`
generalizes past `sk-ant-` to whatever comes next, plus a generic high-entropy-token heuristic near
`key|token|secret|password` (case-insensitive) as a backstop; (b) pin the captured username as a
recorded literal (in `fixture-provenance.md` or an env var read by the verify script) instead of
deriving it from the invoking shell, so the check is anchored to the capture, not the CI runner;
(c) add one real positive-control line to the verify script itself — inject a known `sk-ant-…`
shaped string into a scratch copy, assert the regex fires, discard the copy — proving the mechanism,
not just file readability.

## Surface 2 — the reader (`readContextAnchor` / `resolveSessionFile`, `harness-hooks.ts:440-577`)

Audited by reading the implementation and independently fuzzing the exported functions (bun,
this session — see below) rather than resting on the structural argument alone (O-02).

- **Path handling.** `resolveSessionFile` (`:550-570`) takes the path **only** from
  `ctx.sessionManager.getSessionFile()`, a host accessor with no caller-supplied argument. No tool
  call argument, transcript field, or subagent output feeds into path construction anywhere in this
  function or its caller. Traversal/symlink/non-file concerns don't have an attacker on the other
  end here — the trust boundary is the host object itself, which is out of this diff's control
  surface. Assessed and dismissed as a finding under that trust model. (One `..`-shaped adversarial
  string I fed the function was passed through unresolved, confirming there is no validation of the
  accessor's return — but since nothing attacker-reachable can set that return, this is a
  robustness note, not an exploit path.)
- **Resource exhaustion.** `readContextAnchor` scans the file tail with a geometrically-widening
  window (64 KiB → 256 KiB → 1 MiB → …) and only falls back to reading the **whole file
  synchronously** (`readSync`) when no `contextSnapshot` is found anywhere in it — the terminal
  "inert" case, after which `contextNoticeEmitted` permanently suppresses further scans for that
  session (`harness-hooks.ts:796-808`). Measured directly rather than argued: a 40 MB adversarial
  file with **zero** matching records completed a full synchronous scan in **31 ms** (bun, this
  machine) — comfortably inside the BRIEF's cited 34.9 MB worst case, and it happens at most once
  per session. On the steady-state healthy path (an anchor exists, which it does by design since
  it's the newest assistant record) each `tool_result` call only reads the small tail window. Not a
  DoS finding.
- **JSON parse / malformed-record safety.** `anchorFromFragment` wraps `JSON.parse` in try/catch,
  applies a substring prefilter, and walks the fixed path with `typeof`-guards at every hop,
  requiring a finite number at the leaf. Fuzzed directly: nonexistent path, directory-as-path, empty
  file, a torn/malformed JSON line followed by a valid one, `promptTokens` as a string, `null`,
  `contextSnapshot` as an array, and the 40 MB no-match case above — **every case returned a safe
  typed result (`none`/`inert`/`tokens`), zero throws.** `resolveSessionFile` fuzzed the same way
  (missing `sessionManager`, non-function accessor, throwing accessor, non-string/empty return) —
  same result, zero throws.
- **String taint / prompt injection.** Traced explicitly, per the dispatch's ask: the **only**
  transcript-derived value that ever reaches agent-visible text is `anchor.tokens`, and it is
  type-checked (`typeof === "number" && Number.isFinite`) at the point it's read out of the parsed
  JSON, before it ever reaches `contextAdvisoryText`. `contextInertText` and
  `contextAccessorFailureText` interpolate only compile-time constants (`CONTEXT_TOKENS_FIELD`,
  `SESSION_FILE_ACCESSOR`) — never anything read from the transcript. **No attacker-influenced
  string crosses into the orchestrator's context or an exported artifact through this feature.**
  Established at source, not inferred.
- **Fail-open on enforcement.** This is the dispatch's sharpest question: the advisory block
  (`harness-hooks.ts:793-815`) runs **before** `postDomain(...)` — the actual `check-domain.sh`
  post-write enforcement call — inside the same `tool_result` handler. If the advisory path threw
  unhandled, `postDomain()` would never run for that event, silently disabling the enforcement gate
  for that tool result (the same defect class as issue #556, which this file's own top-of-file
  comment names explicitly). Audited every call reachable from the advisory block and confirmed by
  fuzzing (above): every fs call, `JSON.parse`, and accessor invocation is wrapped in try/catch with
  a safe fallback, and no adversarial input tried — including the ones most likely to throw
  (directory path, throwing accessor, malformed/wrong-typed JSON, huge file) — produced an unhandled
  exception. **Enforcement does not fail open through this code today.** One low-severity hardening
  note: the block has no defensive try/catch wrapping it *as a whole* — its safety currently rests
  on every individual call site staying guarded. Given this file's own history (B-1, issue #556) is
  about exactly this class of regression recurring, a belt-and-suspenders `try { …advisory… } catch
  { /* advisory is best-effort; never let it block postDomain */ }` around the whole block would
  make a future edit's new unguarded call fail closed-to-advisory rather than open-to-enforcement,
  instead of relying on every future contributor rediscovering the same discipline. Not blocking —
  no live gap exists in the code as shipped.

## Surface 3 — the retirement (`.claude/settings.json`, seven deleted artifacts)

`git diff` on `.claude/settings.json` shows exactly one hook command removed:
`context-watch-hook.py` from the `PostToolUse` `Write|Edit|Bash` matcher's hook array. Every other
registration is byte-identical pre/post: `SubagentStart` → `inject-expertise.sh`; `PreToolUse`
`Write|Edit` → `check-domain.sh`; `PreToolUse` `Bash` → `branch-create-gate.sh`,
`bash-write-guard.sh`, `gh-close-gate.sh`; `PreToolUse` `Task|Agent` → `dispatch-guard.sh`;
`PostToolUse` `Write|Edit|Bash` → `check-domain.sh --post` (**retained, same array, same
matcher**); `SubagentStop` → `validate-digest.py --hook`. The actual enforcement hook
(`check-domain.sh --post`) that domain-policy enforcement depends on is untouched.

Confirmed the removed hook was advisory-only pre-change: `git show
7ebfc9e:.claude/skills/harness/bin/context-watch-hook.py` contains zero `sys.exit` calls — under
DEC-100 (`exit 2` is the only blocking signal) this script never blocked anything even before
removal. Its retirement, and the six other deleted context-watch artifacts (`context-watch.py`,
three test files, `verify-context-watch-live.py`, `references/context-check.md`), removes an
inert advisory path, not an enforcement capability. No finding.

## Assessed and dismissed

- Session/record UUIDs and Anthropic API artifact IDs (`toolu_…`, `msg_…`) retained in the fixtures
  — opaque, non-secret, no correlatable PII value. (Folded into SEC-1 for completeness rather than
  raised separately.)
- Path traversal / symlink handling on `resolveSessionFile`'s return value — no attacker-reachable
  input feeds that accessor; the trust boundary is the host object itself, outside this diff.
- `readContextAnchor`'s tail-doubling full-file fallback as a DoS vector — measured (31 ms / 40 MB),
  bounded to once per session, not a finding.
- Broken `parentId` chain in the fixtures — fixture-integrity issue, not a disclosure risk; no
  content is exposed by the dangling reference.
- MCP tool-name fingerprint (`mcp__dropbox_team_*`, `mcp__snowflake_*`) in the `tools` array —
  operationally revealing at most (confirms two integrations exist), not a credential or exploit
  path. Folded into SEC-1.

```yaml
VERDICT: PASS
DIGEST:
  headline: "Fixtures independently confirmed clean; the T-01 secret/username sweep has a real (med) blind spot for its own most-likely target, and the reader is fail-safe under fuzzing — nothing here blocks the ship."
  in_scope: true
  scope_reason: "Two real surfaces per dispatch: irreversible fixture content committed to git history, and an in-process untrusted-JSONL reader running inside the same handler that enforces domain policy."
  severity_max: med
  findings: 2
  must_fix: []
  threat_model:
    - { boundary: "fixture JSONL content committed to git history", stride: "I", mitigated: true }
    - { boundary: "T-01 verify sweep as the automated floor for future fixture recaptures", stride: "I", mitigated: false }
    - { boundary: "untrusted-shaped JSONL parsed in-process inside the tool_result enforcement handler", stride: "D", mitigated: true }
    - { boundary: "transcript-derived value crossing into orchestrator agent context", stride: "T", mitigated: true }
    - { boundary: "advisory computation sequenced before postDomain() enforcement in the same handler", stride: "E", mitigated: true }
    - { boundary: "PostToolUse hook registration surface (context-watch-hook.py retirement)", stride: "E", mitigated: true }
  open_questions: []
  files_touched: []
  expertise_update: []
artifact: .harness/harness/features/FEAT-44-omp-context-advisory/notes/review-harness-security-reviewer-c1.md
```
