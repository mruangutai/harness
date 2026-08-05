# Security review — FEAT-09 (check-domain.sh --resolve) — cycle 0

Diff: `git diff 47ed11f..4918d06` (14 files, verified `git merge-base main HEAD` = `47ed11f`).
In scope: this diff adds `--resolve` to the authorization guard `check-domain.sh` and a
consumer `check-plan-routes.py` that shells out to it. Both are on the write-authorization
trust boundary. Reviewed against the T1–T8 threat model plus the ordinary OWASP lens.

## Finding 1 — env-var mode confusion can disable the whole domain guard (MED)

`check-domain.sh:36-41` (new in this diff — the pre-change script was unconditionally
`payload=$(cat)`):

```bash
if [ "${1:-}" = "--resolve" ]; then
  payload=""
  export HARNESS_RESOLVE_PATH="${2:-}"
else
  payload=$(cat)          # <-- HARNESS_RESOLVE_PATH is never unset here
fi
```

The Python body branches on `os.environ.get("HARNESS_RESOLVE_PATH") is not None` (`:134`),
and that branch sits *before* the agent-identity check (`:208`) and `domain_check()`
(`:357`). The mode switch is therefore not "was `--resolve` passed on argv" — it is "is
this variable present in whatever environment the hook process inherited." Measured
directly (fixture, no source edits):

```
$ echo '{"agent_type":"harness-documentor","tool_name":"Write",
         "tool_input":{"file_path":".claude/skills/harness/bin/check-domain.sh","content":"x"}}' \
  | HARNESS_RESOLVE_PATH=anything ./check-domain.sh
NOBODY
exit=0
```

harness-documentor has no domain grant on `check-domain.sh` (that path is
harness-backend-dev/harness-dev-ops only, `team-config.yaml:155,197`) — without the
stray env var this same payload correctly exits 2 (confirmed via
`test-check-domain.py` case (g), which passes with a clean environment). With the var
present, `domain_check()` never runs at all: every Write, by every agent, to every
path, is silently allowed for the life of that env var.

**Escalation scenario, and why it doesn't clear `high`:** I could not find an
agent-writable route to set this variable on the hook's own process. `.claude/settings.json`
(the only place a `PreToolUse` hook's environment could plausibly be seeded from,
alongside its `env:` block) is covered by no domain in `team-config.yaml` — grepped,
zero hits — so no agent can add an `env` stanza there through the governed Write path.
`check-plan-routes.py`'s own subprocess call (`:52-57`) does not export the variable
for its child either. The only realistic trigger is an operator's shell already having
`HARNESS_RESOLVE_PATH` exported (e.g. left over from manual `--resolve` debugging, or
copy-pasted from this feature's own test/doc snippets) before launching the CLI — an
operator-level precondition, not an agent-level one. That is why this grades `med`
(defence-in-depth gap) rather than `high`: the blast radius if triggered is total
(complete, silent bypass of the authorization guard for every subsequent write in the
session), but no path in this diff or the manifest lets an *agent* reach the trigger.

Fix is one line: `unset HARNESS_RESOLVE_PATH` in the `else` branch, or better, stop
using an env var for this at all and read `argv[2]` directly inside the already-`--resolve`-gated
branch (it is only ever consumed there).

## Finding 2 — cwd-relative vs root-relative normalisation asymmetry (LOW, informational)

T1's mandate was to prove or disprove that `--resolve` and the hook reach `matches()`
with identically-normalised input. They do **not**, in one respect, though it predates
this diff: the hook computes `os.path.abspath(target)` (cwd-relative, unchanged pre-existing
code at `:296`); `--resolve` computes `os.path.join(root, target)` when `target` is not
absolute (root-relative, new at `:162`). Measured: run both from `cwd=/` with a relative
`file_path` of `docs/SPEC.md` — `--resolve` correctly answers `harness-documentor`;
the hook, resolving `docs/SPEC.md` against `/` instead of the repo root, lands the
`abspath` outside the repo, hits the `commonpath` early-return (`:298-307`, "outside the
repo is not a domain question") and **allows the write for any agent, silently, with no
stderr**. That is a real divergence in the T1 sense (resolver says "only
harness-documentor", enforcer would allow anyone) but I did not find a way to make it
live: Claude Code's Write tool contract requires absolute `file_path` (this harness's own
tool docs state so for Read/Write), and the hook's cwd is set by the CLI itself, not by
an agent. Recorded as a named, measured asymmetry per the dispatch, not filed as a
blocking finding — it requires two preconditions (relative `file_path` *and* non-root
cwd) that no agent controls.

## T2 — fail-open on NOBODY: not found

Empirically probed: empty-string path, missing `$2`, `.`, `/`, absolute paths outside
the repo, `..`-traversal that resolves back inside the repo, unreadable manifest —
every case printed either a granting agent or the literal `NOBODY`, never empty stdout.
`test-check-domain.py` cases (c)/(d) cover this and pass.

## T3 — SHARED-only paths: correctly excluded, not a live fail-open

`check-plan-routes.py:64`, `resolve_agents()`: lines equal to `NOBODY` or matching
`^SHARED ` are both skipped when building the granted-agents list. Verified with
`--resolve package.json` (a `shared:` entry, `team-config.yaml:60`): output is
`NOBODY` + `SHARED package.json`, both lines are filtered by the checker, so the path is
correctly treated as *ungranted* (must be `main-session-direct` or it's a VIOLATION).
The BRIEF's specific worry — a shared-only path reading as ROUTED — does not occur.

## T4 — shell-out injection: not found

`check-plan-routes.py:52-57` uses list-argv `subprocess.run([CHECK_DOMAIN, "--resolve",
path], ...)`, no shell. `check-domain.sh` takes `$2` as an opaque literal (no re-parsing,
no `getopt`), so a leading `-`, backticks, `; cmd`, or `$()` in a `files:` entry cannot
inject. Verified directly against the guard: `--resolve '; touch /tmp/PWNED; echo x'` and
`--resolve '`touch /tmp/PWNED2`'` both printed `NOBODY`, exit 0, and created no files.

## T5, T6, T7, T8 — no findings

- T5: `harness_yaml.py` (unchanged this diff) uses `yaml.load(text, Loader=_StrictSafeLoader)`,
  not `yaml.load` with the default loader; duplicate keys raise `DuplicateKeyError`
  before parsing completes — no widen found.
- T6: `--resolve` deliberately exits 2 (not open) on a missing/unparseable manifest,
  correctly stricter than the hook's documented fail-open (DEC-101 carve-out, which this
  diff does not touch or widen).
- T7: full hook regression suite (27 T-12 cases + 8 resolve cases) passes; out-of-domain
  Write still exits 2, in-domain still exits 0, confirmed independently against fixtures
  (not inline-quoted payloads, to avoid the false-pass shape the dispatch warned about).
- T8: the `--resolve` branch is provably unreachable to `payload=$(cat)` — it's a
  mutually-exclusive `if/else` on argv, and `test-check-domain.py` case (e) proves it
  structurally (an open pipe answers within 10s instead of hanging).

## Secrets / data exposure

No credentials, tokens, or PII in the diff's code or feature docs (grepped
BRIEF/PLAN/STATE/notes/observations for password|secret|token|api[_-]?key|credential;
the only hits are the `execution_mode:` vocabulary token, not a credential).

## No-domain-covers-settings.json check (supports Finding 1's grading)

`grep -n "settings.json" .harness/team-config.yaml` → zero hits. No agent may write
`.claude/settings.json` through the governed path.
