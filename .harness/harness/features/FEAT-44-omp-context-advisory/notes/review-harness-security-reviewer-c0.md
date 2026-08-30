# Security review — FEAT-44 plan (T-01..T-04 intents), review_sha b0ea27d

**Verdict: FAIL.** Three of four questions close clean (no meaningful surface); the fourth —
T-01's fixture-scrubbing instruction — is a concrete, evidence-backed gap: the instruction covers
"message text content" but the *real* transcript schema (verified against a live
`~/.omp/agent/sessions/**` file on this machine, not assumed) carries several other classes of
real, unscrubbed data the instruction never names, and nothing in T-01 requires a pre-commit check.
Once committed this is a permanent git object.

## Q1 — path resolution (T-02/T-03): no meaningful surface

`ctx.sessionManager?.getSessionFile?.()` is a host-runtime object method, not hook-payload input —
the same trust class as the existing `sessionId(ctx)` helper at `harness-hooks.ts:324-328`
(`ctx.sessionManager?.getSessionId?.()`), which the codebase already trusts uncanonicalized. No
mechanism in the diff lets an agent or remote content choose what this returns; it is the host's own
bookkeeping of its own transcript file, read by the orchestrator about its own session. Even in the
hypothetical worst case (host returns a foreign path via a bug), the consequence is capped by what
`readContextAnchor` extracts: exactly one field, `message.contextSnapshot.promptTokens`, a number,
gated by `typeof === "number" && Number.isFinite`. No file content is echoed into the advisory —
only a computed ratio of two numbers (T-02 intent, `contextAdvisoryText`). There is no exfiltration
primitive here: a symlink/`..` in the returned path could at most make the reader parse a *different*
JSONL file for a token count, which is not attacker-useful. No canonicalization/containment check is
warranted; this is inert.

T-01 test 2's `tmpdir()` temp file is test-only, ephemeral, and grants no attacker a capability they
didn't already have (worst case is test flakiness under a hostile shared `/tmp`, not a security
defect). Noise, not a finding.

## Q2 — untrusted transcript content parsed as JSON (T-02/T-03)

Verified the real record schema against a live session file (`~/.omp/agent/sessions/-GitHub-harness/
2026-08-08T13-20-28-049Z_*.jsonl`): a `message`-typed record's inner `message` object for an
assistant turn is `{role, content, api, provider, model, usage, stopReason, timestamp, responseId,
duration, ttft, contextSnapshot}` — **`contextSnapshot` is a top-level sibling of `content`,
host-computed from the real API usage response, not nested inside any string the model or a tool
writes.** `content[]` parts (`text`, `toolCall`, `thinking`) are where model/tool-influenced text
lives, and none of those paths can set a sibling key on the *containing* object — JS property access
on `record.message.contextSnapshot` looks at a direct property, not a substring inside
`content[].text`. For attacker-influenced text to forge an acceptance, the host's own JSONL writer
would need a string-escaping bug that lets embedded text break out of its string context onto a new
top-level key — that is a hypothetical defect in OMP itself, outside this plan's control and D-01's
one-mechanism frame; not a gap this feature can or should fix. **(a) closes: no meaningful forgery
path**, given the verified schema.

**(b) — the cap is on the NOTICE, not the SCAN, and the plan says so explicitly.** T-02: "There is no
persisted state, no byte offset, no accumulated delta and no dedupe: the newest anchor is read fresh
each time." T-03: `inertNoticeEmitted` only gates whether `contextInertText` is appended to content —
it does not gate whether `readContextAnchor` runs. So on a drifted (anchorless) transcript, **every**
`task` tool_result for the orchestrator (order 7-15 per feature, BRIEF) re-runs the full widening
ladder to a whole-file pass, against a transcript that is itself the orchestrator's own
ever-growing session file (BRIEF's own measured worst case: 34.9 MB). This is real and contradicts
the BRIEF's framing ("[caps] the inert path at one notice per session... pays it once instead of
once per wake") — that sentence is true only of the *notice text*, false of the *read cost*. That
said: no attacker benefits from this path — drift is triggered by an upstream OMP schema change, not
by anything reachable from agent-controlled content, and there is no privileged actor gaining
anything by forcing it. This is a **plan-accuracy / availability nit, not a security finding** (no
named attacker gains anything); flagging it because it is concrete and the BRIEF text overstates the
mitigation, but it does not gate this review.

**(c)** `Number.isFinite` admits negative/non-integer values, but nothing exploitable follows:
`(tokens/threshold).toFixed(2)` handles negative/fractional inputs without throwing, and per T-02's
own spec the advisory interpolates only *numbers* (`tokens`, `threshold`, the computed ratio) plus
static text — never a transcript-derived string. No injection surface. Not a finding.

## Q3 — removing the `context-watch-hook.py` registration (T-04): no security function lost

Read `context-watch-hook.py` in full: it is deliberately advisory-only by its own docstring — "IT
NEVER RAISES AND NEVER BLOCKS," fail-silent on every error path, PostToolUse (tool already ran) +
`exit 2` used only to place text on stderr, never to gate. It enforces nothing.

Read `.claude/settings.json` at `7ebfc9e`: the `PostToolUse` block on the `Write|Edit|Bash` matcher
holds **two separate hook objects** — `check-domain.sh --post` (lines 58-61) and
`context-watch-hook.py` (lines 62-65). T-04's intent names the exact line range to remove (62-65)
and explicitly instructs "Keep the check-domain.sh --post entry at 58 to 61 and keep the matcher."
This is the correct, narrowly-scoped edit — removing only the advisory entry, leaving the
security-relevant domain-guard entry and the matcher untouched. Confirmed no security-relevant check
is disabled by this task.

## Q4 — fixture scrubbing (T-01): FINDING, must_fix, severity high

T-01's intent: *"a REAL captured excerpt from an OMP session transcript... truncated to a handful of
records and with **message text content** scrubbed to short placeholders... Do not hand-author the
record shape: capture it."*

I read a live transcript to check what "a handful of records" actually contains (not assumed):
`message`-typed records with `role: assistant` carry `content[]` parts of type `text`, `thinking`,
**and `toolCall` with an `arguments` object** — i.e. real Bash command strings, real Write/Edit file
paths and file content, real tool inputs from whatever the implementer's machine was doing in that
session. The paired `role: toolResult` records carry `content[].text` — real, unredacted tool
**output** (command stdout/stderr, file reads, `gh`/`git` output, anything printed during that
session). The file also contains a `session`-typed record with a top-level `cwd` (absolute path,
reveals the local username/home directory), and, in other captured sessions, `credential_pin`
records shaped `{type, id, parentId, timestamp, provider, hash}` — a provider identifier plus a
credential hash, persisted per-session by the host.

"message text content scrubbed to short placeholders" most naturally covers `content[].text` on
message-type records. It does not name: `toolCall.arguments` (structured, not "text"), `toolResult`
records' content (a different `role`, real tool output), `session.cwd` / any other `cwd` field, or
`credential_pin` records. Given the instruction's own emphasis — "do not hand-author the record
shape: capture it" — the natural implementation is a contiguous slice of real lines from a real file,
which on a coding agent's session will essentially always include real `toolCall`/`toolResult`
payloads (assistant turns without tool calls are atypical), so the omission is not theoretical: the
literal, faithful-to-instruction execution path plausibly commits real command arguments, real file
contents, a real absolute home-directory path, and possibly a real credential hash into a fixture
file, as a permanent git object, with **no pre-commit check specified anywhere in T-01's `verify`
or `intent`** (the `verify` block only asserts the bun suite is red — it never inspects fixture
content). This repo has no prior convention for safely capturing+scrubbing real host transcripts to
point to (`layout_fixtures.py` is entirely hand-authored stub data, a different risk class); FEAT-44
is introducing this pattern for the first time, underspecified.

Cost if this fires: real command arguments/file contents/absolute paths/credential material from the
implementer's actual working session become part of the repository's permanent history — unlike a
source-code bug, an already-pushed git blob cannot be un-shipped by a follow-up commit.

**Concrete alternative** (what T-01's intent should additionally state):
1. Name every field class that must be scrubbed or dropped, not just "message text content":
   `content[].text`, `content[].thinking`, and `toolCall.arguments` on assistant records; `content[]`
   on `toolResult` records; `session.cwd` and any other `cwd`-bearing field (replace with a synthetic
   path); and instruct that `credential_pin` records be **dropped** from the excerpt entirely (they
   carry no field `readContextAnchor` reads and are pure risk with zero test value).
2. Require a verification step before `git add`: a simple secret-pattern sweep over the two fixture
   files (common token prefixes, `-----BEGIN`, high-entropy runs, or any available scanner) plus a
   manual line-by-line diff against the redaction list above, and record that this was done (e.g. a
   one-line note in the sidecar provenance note T-01 already permits).

## Threat model

| boundary | STRIDE | mitigated | note |
|---|---|---|---|
| `getSessionFile()` return → `readContextAnchor` file read | Tampering | true | host-controlled value, capped consequence (single numeric field extracted); precondition-absent for any real attacker |
| transcript content (model/tool output) → `contextSnapshot` acceptance | Tampering | true | verified schema: field is host-authored telemetry, structurally unreachable from message/tool content |
| repeated full-file scan on drifted transcript | Denial of Service | true | precondition-absent — no attacker action makes drift happen; self-inflicted by host schema change only, not exploitable |
| `.claude/settings.json` hook removal (T-04) | Elevation of Privilege | true | removed hook was fail-open/advisory-only by design; enforcement hook (`check-domain.sh --post`) confirmed to survive as a separate JSON object |
| real captured transcript → committed fixture (T-01) | Information disclosure | false | scrub instruction underspecified against verified real schema; no pre-commit check specified |

## Nits (non-gating)

- T-03/BRIEF's "caps the inert path at one notice per session" language overstates what
  `inertNoticeEmitted` actually caps (the notice text, not the underlying scan) — worth a wording
  fix, not a security gate.
