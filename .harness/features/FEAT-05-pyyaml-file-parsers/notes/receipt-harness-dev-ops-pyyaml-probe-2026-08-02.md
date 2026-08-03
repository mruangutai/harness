# dev-ops PyYAML probe — FEAT-05 — 2026-08-02

All commands run `--dry-run` / read-only. Nothing installed, nothing mutated outside this file.

## Chosen install command (headline)

No single universal string exists. The gate prints a command for a **human to run**, not a script to
exec — a bare `||` fallback is wrong here: it fires on *any* nonzero exit (network failure, missing
pip, permissions), not specifically on the PEP-668 error, so an unrelated failure would trigger a
confusing second attempt. Print two lines, gated on the named error string:

```
python3 -m pip install pyyaml
# if that fails with "externally-managed-environment" (PEP 668, e.g. Homebrew/Debian):
python3 -m pip install --break-system-packages pyyaml
```

`--break-system-packages` is unknown to pip < 23.0.1 (raises "no such option"), so it cannot be
attempted first unconditionally — plain install must run first and the flag only added on that
specific named failure. **[reasoned, unverified — no pip < 23.0.1 available on this machine to test
against; both interpreters checked here are ≥ 23.0.1: Homebrew pip 26.1.1, `/usr/bin/python3` pip
24.1.1]**. Local (Homebrew) pip version: 26.1.1 [dry-run verified: `python3 -m pip --version`].

## Ask 1 — install command

- pipx structurally disqualified **[reasoned, not empirically tested — pipx is not installed here]**:
  it installs applications into isolated venvs; a library there is not importable by an arbitrary `python3`.
- venv disqualified unless on PATH for the hook subprocess, which the BRIEF forbids abandoning bare
  `python3` for. **[reasoned]**
- `pip --user` does **not** escape PEP 668: `python3 -m pip install --user --dry-run pyyaml` produces
  the *identical* `externally-managed-environment` error as plain install. **[dry-run verified]**
- Must be `python3 -m pip`, not bare `pip`: four `python3`s are on this PATH
  (`/opt/homebrew/bin`, `/Library/Frameworks/.../3.12`, `/usr/local/bin`, `/usr/bin`), each with its
  own pip; bare `pip` can silently target the wrong one. **[dry-run verified via `which -a python3`]**
- `--break-system-packages --dry-run pyyaml` succeeds cleanly on Homebrew's interpreter (pip 26.1.1).
  **[dry-run verified]**

## Ask 2 — interpreter policy

Bare `python3` off PATH stays (BRIEF constraint). Gate check form (a check, not an install):

```
python3 -c 'import yaml' 2>/dev/null && echo OK || echo MISSING
```

Caveat, unresolved: this must run in the **hook subprocess's** PATH, not necessarily the user's
interactive shell's. I could not directly capture the hook's own spawn environment (would require
editing `.claude/settings.json`, out of scope here). Safest form: have the gate literally shell out
through the same invocation shape `check-domain.sh` already uses, or have `check-domain.sh` itself
self-report `MISSING` once at first run rather than trusting a separate init-time check. Flagged as
`open_question`, non-blocking.

## Ask 3 — session-identifying material

- `check-domain.sh` reads only `agent_type` (:38), `tool_name`+`tool_input` (:74,:240) from the
  PreToolUse payload; `bash-write-guard.sh` reads only `agent_type` (:27) and the same via
  `HOOK_PAYLOAD` env (:53). Neither **reads** `session_id`, `transcript_path`, or `cwd` — confirmed
  by grep returning zero payload-key matches for those terms in both files. This says nothing about
  whether the payload *carries* those keys unread — see below.
- Could **not** empirically confirm the full raw PreToolUse payload shape beyond what these two
  scripts read — that would need editing `settings.json` to snoop stdin, which this dry-run scope
  disallows. Not settled. Cheapest path to settle it: `check-domain.sh:240` already reads
  `HOOK_PAYLOAD` from the env — a build-phase task can add one line there
  (`print(sorted(d.keys()), file=sys.stderr)`) and read it off a real invocation, no stdin plumbing
  or settings.json edit needed.
- **Did** find session-identifying `CLAUDE_*` env vars visible to a Claude-Code-spawned subprocess:
  `CLAUDE_CODE_SESSION_ID=4194b3b4-3e70-4687-be09-9a6a50e44d13` (uuid) and
  `CLAUDE_CODE_BRIDGE_SESSION_ID=session_014eZMX1bCGRrL71dpHXwYCj` (`session_<id>` string) —
  observed via `env | grep -i claude` in this session's own Bash subprocess. Not verified inside an
  actual hook subprocess specifically, but this is a real candidate mechanism for the one-session
  bootstrap escape (BRIEF's deferred "how do hooks detect same session") that needs **no** payload
  change at all.

## Ask 4 — full governed path, re-measured

- Bare `python3 -c pass`, 100 iters: **17.10ms/iter**.
- `check-domain.sh` driven by a synthetic payload (`agent_type: harness-backend-dev`, `Write`,
  in-domain `file_path`) that reaches all four launches (:35, :74, :97 `domain_check`, :235
  state-shape gate) and exits 0 silently (matched a domain glob, no stderr) — confirming all four
  ran, not an early exit: **80.63ms/iter**, 100 iters. The grilling's 23.7ms was indeed the
  no-`agent_type` one-launch early exit at :48, as suspected.
- Merged-into-one-launch estimate: a simplified single-process proxy (same JSON parse + manifest
  read + content scan, one launch) measured **17.94ms/iter** — matches bare-launch baseline
  **[measured, but the proxy omits the real glob-regex compilation and `yaml.safe_load` cost of a
  true merge, so treat as a lower bound, not the final number]**. A real merged script also pays a
  one-time `import yaml`; expect roughly 25–35ms merged vs 80.6ms today — **[estimated]**.

## Ask 5 — YAML semantics (probe interpreter: `/usr/bin/python3`, PyYAML 6.0.1, nothing installed)

a. Duplicate top-level key: `yaml.safe_load` **silently last-wins**, no raise —
   `{'id': 'second'}`. Converting `check-domain.sh:285-298`'s dup-detection to bare `safe_load`
   *would* turn a working check into fail-open; the checker needs the custom loader in (d), not
   plain `safe_load`.
b. Bare `2026-07-31` scalar: `type() == <class 'datetime.date'>`. Confirms SC-10's date-scalar risk.
c. `SafeLoader` subclass with the `tag:yaml.org,2002:timestamp` implicit resolver stripped
   (`yaml_implicit_resolvers` rebuilt without that tag) returns the scalar as `str`
   (`'2026-07-31'`), and a normal mapping (`{'a': 1, 'b': 'two'}`) still parses correctly.
d. A `SafeLoader` subclass overriding `construct_mapping` to raise `ConstructorError` on a repeated
   key works (raised on `id: first / id: second`) and leaves a normal mapping unaffected
   (`{'a': 1, 'b': 'two'}`). Both subclasses can be combined (one class, both overrides) without
   conflict.

---

VERDICT: PASS
DIGEST:
  headline: "no single universal install string — two-line printed command, gated on the named PEP-668 error string, not exit status; all 5 asks empirically probed, dry-run only, nothing installed"
  change_type: config
  applied: []
  suite: n/a
  test_kinds_written: []
  open_questions:
    - { id: Q1, question: "does the gate's python3 import-check need to run in the hook subprocess's exact PATH context, or is the interactive-shell PATH a safe proxy — settle by instrumenting check-domain.sh once to print its own PATH/python3 resolution", blocking: false }
    - { id: Q2, question: "is CLAUDE_CODE_SESSION_ID actually present inside the PreToolUse hook's own subprocess (only confirmed in a Bash-tool subprocess here) — settle with a one-time debug print from inside check-domain.sh", blocking: false }
    - { id: Q3, question: "raw PreToolUse payload shape beyond agent_type/tool_name/tool_input is unconfirmed — settle by adding one debug print of sorted(d.keys()) at check-domain.sh:240 (HOOK_PAYLOAD is already parsed there) on a real invocation", blocking: false }
  files_touched: [".harness/features/FEAT-05-pyyaml-file-parsers/notes/receipt-harness-dev-ops-pyyaml-probe-2026-08-02.md"]
  expertise_update: []
artifact: .harness/features/FEAT-05-pyyaml-file-parsers/notes/receipt-harness-dev-ops-pyyaml-probe-2026-08-02.md
