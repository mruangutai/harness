# Security review — FEAT-31 orchestrator-context-watch — panel-c0

Base `d065b3b`, review sha `fcb8984f2bc2db1277ee6a3fc657fcbb0592826e`. All source cited below was
read with `git show fcb8984...:<path>` (committed content), never the worktree. No file was
edited; two fixture scripts were written under the scratchpad and run against the *committed*
`context-watch.py`, never against real `~/.claude/projects`.

## Verdict

**PASS**, `severity_max: med`, zero `high`/`must_fix`. One med-severity, demonstrated availability
defect (finding 1) and one low-severity, demonstrated-but-unreachable path-join gap (finding 2).
Neither meets the `high` bar this gate uses.

## File census

In scope (touch the real surface: reads someone's transcript, joins ids into paths, or is the
fail-open boundary named in the dispatch):
- `.claude/skills/harness/bin/context-watch.py` (new, 781 lines) — findings 1, 2 below.
- `.claude/skills/harness/bin/context-watch-hook.py` (new, 91 lines) — fail-silent verdict below;
  stderr-channel content checked clean.
- `.claude/skills/harness/bin/verify-context-watch-live.py` (new, 518 lines) — dev-only second
  opinion tool. `subprocess.run([sys.executable, context_watch_path, "--projects-dir", ..., agent_id], ...)`
  is list-argv, `shell` not set (defaults False) — no shell injection. `agent_id`/`projects_dir`
  are argv, same trust level as context-watch.py's own CLI. No finding.
- `.claude/settings.json` — confirms the PostToolUse matcher is exactly `Write|Edit|Bash`, matching
  the hook's own docstring measurement. Correctly wired.
- `.harness/harness.json`, `.claude/skills/harness/templates/harness.json` — adds
  `budgets.orchestrator_context_warn_tokens` and an integration-test allowlist. Data, not code; no
  injection surface.

Scoped OUT, with reason:
- `.claude/skills/harness/bin/check-state.sh` (INV-17 handoff-shape check) — reads/greps files
  under `.harness/*/features/*/notes/handoff-*.md`, which are the harness's own agent-authored
  artifacts, not externally-untrusted input; no shell interpolation of file content, only
  `os.path.basename`/`read()` in an embedded Python heredoc. No path or injection surface.
- `.claude/skills/harness/bin/feature_schema.py`, `feature-schema.json` — the new `agent` field is
  validated as a non-empty string and used only in an f-string error message, never as a path
  component or shell argument. No surface.
- `.claude/skills/harness/bin/run-unit-tests.sh` — CI/dev script; the new kind-cross-check heredoc
  reads `.harness/harness.json` via `HARNESS_JSON` env var passed to Python `os.environ`, not
  shell-interpolated into source; no untrusted input (repo config only).
- All `test-*.py` additions — verified each isolates itself with `tempfile`/fixture dirs; grepped
  and confirmed none of `test-context-watch*.py` touch real `~/.claude/projects`
  ("NOTHING READS ~/.claude/projects" is stated and true of the diff).
- `.harness/harness/docs/DECISIONS.md`, `DECISIONS-INDEX.md`, and all `FEAT-31-.../` `BRIEF.md`,
  `STATE.md`, `feature.json`, `plan.yaml`, `notes/*`, `observations/*` — internal harness
  bookkeeping, no untrusted input, no credential-shaped strings (full-diff grep for
  key/secret/password/token/bearer/PEM/AKIA patterns: zero hits).

## Findings

### 1. MED — a single malformed transcript entry silently discards every other orchestrator's row, with a misleading `exit 0`
`context-watch.py:176-183` (`_three_field_sum`) does arithmetic on `usage.get("input_tokens")` etc.
with no type check beyond `or 0`. If any of the three fields is a non-numeric JSON value (a string,
list, or dict — plausible from a future API-shape change or a truncated/corrupted transcript, not
from attacker-authored prompt text), Python raises `TypeError: can only concatenate str (not
"int") to str`. This is **not** caught inside `_build_row`/`discover_orchestrator_rows`
(`context-watch.py:288-363`) — only `main()`'s outer `try/except Exception` around the
`discover_orchestrator_rows` call (`context-watch.py:745-752`) catches it, and its handler sets
`rows = []`, discarding every row already discovered anywhere else under `projects_root` — not
just the malformed one.

Demonstrated (scratchpad `badtype_demo.py`, run against the committed module via
`importlib`): one orchestrator with a well-typed transcript at 250,000 tokens (25% over the
200,000 default threshold) sits alongside a second orchestrator whose transcript has
`input_tokens: "1000"` (a string). Calling `discover_orchestrator_rows` directly raises the
uncaught `TypeError`; calling `main(["--projects-dir", root])` — the real CLI entrypoint —
prints `context-watch: error scanning ...: TypeError...` to stderr, then prints
**`no orchestrators found under <root>`** and returns **exit 0**, even though a real
over-threshold orchestrator exists in the same tree. This contradicts the tool's own documented
contract ("Exit status: 0 when every discovered orchestrator row was measured and no row
warned") and REQ-07's stated invariant ("unmeasured rows are rows, never omissions") — here the
row isn't even reported as unmeasured, it's erased along with everyone else's.

This is the tool's own advisory instrument failing in exactly the way its hook counterpart
(`context-watch-hook.py`) says it must not: the hook's fail-silent design is justified by
pointing at "the operator's own reading of `context-watch.py`" as the backstop — and this finding
shows that backstop can itself report a false all-clear under a data-corruption precondition, not
just go silent.

Not attacker-reachable in the classic sense (no plausible untrusted actor shapes
`message.usage.input_tokens`'s type via prompt content — it's written by the Claude Code CLI
itself from API response metadata), so this is a robustness/availability gap rather than an
exploitable vulnerability, rated `med` (unusual precondition, defense-in-depth gap on a
monitoring instrument) rather than `high`.

**Minimal remedy:** treat a non-numeric usage sub-field the same as an absent one in
`_three_field_sum` (skip/contribute nothing rather than raising), and/or wrap the per-file work
inside `discover_orchestrator_rows`'s loop so one bad sidecar becomes an `_unmeasured_row` for
*that* agent only, never an exception that erases the whole run.

### 2. LOW — unsanitized path join of `session_id`/`agent_id` in `warn_for_agent`, reachability-closed
`context-watch.py:514-515`:
```
subagents_dir = os.path.join(projects_root, slug_of_path(cwd), session_id, "subagents")
jsonl_path = os.path.join(subagents_dir, "agent-%s.jsonl" % agent_id)
```
`session_id` is joined as a raw path component with no traversal check. Demonstrated (scratchpad
`traversal_demo.py`, run against the committed module): `session_id = "../../../../../../../../etc"`
resolves `jsonl_path` to `/etc/subagents/agent-passwd.jsonl` — fully outside `projects_root`.
(`agent_id` alone cannot achieve the same because it is always prefixed with the literal string
`"agent-"` before being used as a path segment, so its own first segment can never equal `..`; the
traversal requires control of `session_id`.)

This is the mirror image of the dispatch's item-1 concern about ids *harvested from disk*
(`discover_orchestrator_rows`/`_orchestrator_jsonl_paths`, `context-watch.py:331-604`) — those ARE
safe, structurally, because every id there comes from `os.listdir()` output sliced from a real
filename: POSIX filenames can never contain `/`, and `os.listdir` never yields `.` or `..`, so no
join built from those values can escape its parent directory. No fixture needed for that half; it
is a language/OS invariant, not a project-specific check.

`warn_for_agent`'s `session_id`/`agent_id`/`cwd`, by contrast, come from a different provenance:
either (a) the PostToolUse hook payload that Claude Code itself generates for the *currently
running* tool call (`context-watch-hook.py:38-42`, `payload.get("session_id")` /
`payload.get("agent_id")` / `payload.get("cwd")`) — framework-generated session metadata, not
attacker-authored text reachable via a prompt; or (b) CLI flags (`--session-id`, `--warn-for`,
`--cwd`) on `context-watch.py` itself, supplied by whoever already has shell access to invoke the
tool directly. In both cases the actor who could shape these values already holds at least the
access the traversal would grant (reading a file elsewhere on the *same machine, same user*) — no
privilege is gained. I therefore close this as **reachability-closed**, not `n/a`: the mechanism is
real and demonstrated, only the provenance argument keeps it from being exploitable today.

**Minimal remedy (defense in depth, not blocking):** after building `subagents_dir`, check
`os.path.commonpath([projects_root, os.path.realpath(subagents_dir)]) == os.path.realpath(projects_root)`
before opening anything, so a future caller that feeds `warn_for_agent` a genuinely
less-trusted identifier doesn't silently inherit this gap.

### 3. Assessed and dismissed — env var overrides of config/projects root
`HARNESS_CONFIG_PATH` and `HARNESS_PROJECTS_ROOT` (`context-watch-hook.py:57-58`) let whichever
process environment the hook subprocess inherits redirect where it reads config and transcripts
from. This could, in principle, suppress every warning (point `HARNESS_PROJECTS_ROOT` at an empty
directory) or spoof the threshold. Closed as precondition-absent: setting these for the hook's own
subprocess requires control over the environment Claude Code's own hook-invocation process runs
in, which is operator-level access already — not a channel a prompt or transcript content can
reach. Recorded here (P-12) so a later reviewer doesn't have to re-derive this if a future feature
adds any less-trusted way to influence that environment.

## Item 4 — fail-silent verdict on `context-watch-hook.py`

**Verdict: fail-silent is the right trade for every error class this hook actually swallows.**
Reasoning: (a) the matcher is measured, not assumed, and covers ~95% of an orchestrator's tool
calls (2949/3359 Bash alone at 87.8%, per the docstring's own count against 25 real transcripts —
confirmed against the actual `.claude/settings.json` matcher `Write|Edit|Bash`), so a crashing
warning path takes down nearly every tool call an orchestrator makes; (b) the instrument is purely
advisory — it decides nothing, blocks nothing, holds no security-relevant state — so a missed
warning is a UX regression, not a control bypass; (c) `warn_for_agent` itself is already
self-guarding (`context-watch.py:513-545`, its own bare `try/except Exception: return None`), so
the hook's outer catch (`context-watch-hook.py`, bottom) only ever needs to absorb payload-parsing,
import, or argument-extraction failures — all cheap, all benign to swallow silently.

The one place silence is compounded rather than merely accepted: the hook's own justification
leans on "the operator's own reading of `context-watch.py` is the backstop" — and finding 1 shows
that backstop can itself misreport "no orchestrators found" under a corrupted-transcript
precondition. That doesn't change the verdict on the hook's *own* fail-silent design (still
correct), but it means fixing finding 1 is what actually keeps the stated backstop honest — I'm
flagging the dependency rather than treating the two as unrelated.

## Findings from the dispatch's already-filed list

Not re-proposed: #663–#669. `_safe_listdir`'s `OSError` swallow (#665) and the blind-spot footer's
`except Exception` at what is now line ~695-699 (weaker, does announce on stderr) were re-read and
match the prior assessment exactly — the footer's catch is a *third*, distinct site from the one in
finding 1 above (finding 1 is `main()`'s catch around `discover_orchestrator_rows`, not the footer).
Q-WARNVERB not reopened.

```yaml
VERDICT: PASS
DIGEST:
  headline: "One demonstrated med-severity availability gap (a malformed transcript entry erases every other orchestrator's row under a misleading exit 0); one demonstrated but reachability-closed low-severity path-join gap; the hook's fail-silent design is judged correct on its own terms."
  in_scope: true
  scope_reason: "New code reads someone else's session/transcript content off disk, joins ids into filesystem paths, and ships a hook whose stderr is confirmed to land inside a live agent's context -- squarely path-handling, data-exposure, and fail-open/fail-silent surface per the dispatch."
  severity_max: med
  findings: 3
  must_fix: []
  threat_model:
    - { boundary: "hook payload (session_id/agent_id/cwd) -> os.path.join in warn_for_agent (context-watch.py:514-515)", stride: T, mitigated: false }
    - { boundary: "on-disk directory/file names (os.listdir) -> os.path.join in discover_orchestrator_rows/_orchestrator_jsonl_paths", stride: T, mitigated: true }
    - { boundary: "malformed/wrong-typed transcript JSON -> arithmetic in _three_field_sum, uncaught past _build_row into main()'s outer catch", stride: D, mitigated: false }
    - { boundary: "hook stderr channel -> lands inside the calling orchestrator's own tool-result/context (settled-Q-HOOKCTX.md)", stride: I, mitigated: true }
    - { boundary: "HARNESS_CONFIG_PATH/HARNESS_PROJECTS_ROOT env vars -> config and projects-root resolution", stride: T, mitigated: true }
  open_questions: []
  files_touched: []
  expertise_update: []
artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-31/.harness/harness/features/FEAT-31-orchestrator-context-watch/notes/review-harness-security-reviewer-panel-c0.md
```
