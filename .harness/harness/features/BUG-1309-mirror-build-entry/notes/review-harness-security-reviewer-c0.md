# Security review — BUG-1309-mirror-build-entry — review_sha 6f64a21c

## Headline
`merge-gate.py` fails OPEN (silently allows the merge) when its own `gh pr view` subprocess
call throws instead of returning a non-zero exit — demonstrated by direct execution. This
defeats the entire Build-entry enforcement gate this feature ships, under a plainly realistic
precondition (gh unavailable/misconfigured in the hook's own environment), with no malicious
actor required. `severity_max: high` → FAIL.

## What I examined (all four dispatch items)

### 1. `gh-sync.py` shell-out construction — CLEAN
Read the full diff (`.claude/skills/harness/bin/gh-sync.py`, 292/-67) end to end, including every
new function (`skip`, `record_build_entry`, `cmd_recover_terminal` and its four helpers,
`_build_entry_preflight`, `_record_task_building`, `_closed_task_guard`). Grepped every
`subprocess.run(` and `gh(` call site in the file (12 sites): all pass an argv list, `shell=True`
appears nowhere, `os.system`/`os.popen` appear nowhere. No feature id, branch name, milestone
title or issue body is interpolated into a shell string.

One pre-existing, **unchanged-by-this-diff** construct is worth recording: `_open_ensure_milestone`
(line ~1096, untouched by this diff) builds a `gh api -q` **jq filter** with an f-string
embedding `brief['feat']` (`f'[.[] | select(.title == "{brief["feat"]}") | .number] | first'`).
This is an argv element, not a shell string — no shell injection — but an unescaped `"` in the
feature title could break the jq filter (denial of a milestone-recovery lookup, not code
execution). This diff's new `cmd_recover_terminal` → `_recover_terminal_apply` reuses
`_open_ensure_milestone` unchanged, so the pre-existing construct gains a second caller but no
new reachability an attacker didn't already have via `cmd_open`. The value's origin (the
feature's own BRIEF title) is controlled only by whoever already has write access to the feature
directory — the same actor invoking the CLI. No escalation (P-02). Assessed and dismissed,
info-level, pre-existing.

### 2. `merge-gate.py` / `merge-gate.sh` — two findings, see below.

### 3. Data exposure — CLEAN
Grepped the full changed surface (`gh-sync.py`, `merge-gate.py`, `feature_schema.py`,
`check-state.sh`, `post-merge-sweep.sh`, `bash-write-guard.sh`, `check-domain.sh`,
`check-fixture-secrets.sh`) for token/credential/secret-shaped strings. Nothing writes a `gh`
auth token, a PR body, or an issue payload into `feature.json`, a log, a note, or a receipt.
`record_build_entry`/`save_recorded` write only the four literal enum strings
(`opened`/`recovery-required`/`not-applicable`/`recovered-terminal`) into `feature.json`'s
`github.build_entry`. The only "secret"-shaped string found was `check-fixture-secrets.sh`'s own
test fixture literal `ghp_ABCDEFGH12345678`, used to prove the secret-scrub pattern still
matches — not a real credential.

### 4. `feature_schema.py`: `_feature_dir_name` / `recovery_command_for` — CLEAN
`_feature_dir_name` (pre-existing, unchanged) extracts a path *segment* by splitting on `/` and
locating the literal `"features"` token; the result is used only for set-membership comparison
(`RUNS_AGENT_EXEMPT`), never to construct a filesystem path — a crafted `../` segment could not
cause a traversal because the extracted string is never passed to `open()`/`os.path.join()` for
a read/write. `recovery_command_for` (new) calls `os.path.basename(feat_dir.rstrip("/"))` before
its own set-membership check — `os.path.basename` collapses any `../` before comparison — and
its `harness_yaml.load_file(os.path.join(feat_dir, "plan.yaml"))` read uses `feat_dir` exactly as
the CLI caller supplied it on argv; this is a local operator-invoked CLI tool, not a
network-facing service, so `feat_dir` is not a value crossing a trust boundary an attacker
controls independent of shell access. No traversal.

## Findings

### F1 — HIGH — `merge-gate.py` crashes (exit 1) instead of denying (exit 2) when `gh` cannot be
invoked, silently allowing the gated merge
`merge-gate.py:main` wraps only the harness.json read and the stdin JSON parse in
`try/except Exception: return`. Every subsequent call — `merge_ref`, `head_branch`, `gh_head`,
`local_branch`, `feature_for` — is unguarded. `gh_head` calls
`subprocess.run([os.environ.get("GH_BIN", "gh"), "pr", "view", ...])`; if that binary cannot be
found, Python's `subprocess.run` raises `FileNotFoundError` (not a non-zero returncode — no code
path catches this). The exception propagates out of `main()` uncaught.

**Demonstrated** (`GH_BIN=/nonexistent/gh`, a feature.json with `github.build_entry` absent and
not era-exempt, payload `{"tool_input":{"command":"gh pr merge 42"}}`):
```
EXIT: 1
Traceback ... FileNotFoundError: [Errno 2] No such file or directory: '/nonexistent/gh'
```
`merge-gate.sh` `exec`s the python process directly, so this exit code is the hook's own exit
code. Per this repo's own documented hook convention (DECISIONS.md "exit 2 blocks
(DEC-100/DEC-122)"; `.claude/settings.json:48` registers `merge-gate.sh` as the PreToolUse Bash
hook), **only exit 2 denies** — exit 1 is silently non-blocking, identical in effect to a clean
allow, with nothing but an unlabeled Python traceback on stderr (no `merge-gate: ...` line the
operator would recognize as "the gate failed to run").

Concrete scenario: a feature with `github.build_entry` absent (owed a receipt, not era-exempt)
attempts `gh pr merge 123`. The hook's own process environment cannot resolve `gh` (uninstalled,
PATH not propagated to the hook's environment, or a stray `GH_BIN` value) — a plausible
operational condition requiring no attacker action. The merge proceeds with **zero enforcement**,
defeating the exact control T-05/DEC-174 exists to provide. This is distinct from, and NOT
covered by, D-07's signed accepted risk: D-07 documents catching a *returncode* failure from `gh`
(auth/network) and falling back with an explicit stderr audit line; it does not address the
subprocess call itself throwing before any returncode exists.

Fix shape (not applied — read-only role): wrap the whole of `main()`'s body (or at minimum every
subprocess-calling helper) in the same `try/except: return` used for the config/payload parse, or
catch `OSError` specifically around `gh_head`/`local_branch` and treat it the same as the existing
`failure` path.

### F2 — LOW — `merge-gate.py`'s command detection is text/basename-only and evadable, but adds
no privilege beyond what the same actor already has
`is_bin` matches a token's basename against the literal string `"gh"`/`"git"`. **Demonstrated**
by direct execution of `merge_ref()` against five payloads — a symlinked/copied binary
(`ln -sf "$(command -v gh)" /tmp/ghx && /tmp/ghx pr merge 123`), an `alias`, and a Python
`subprocess.run(['gh', ...])` wrapper — all return `None` (undetected), so `main()`'s
`if not merge_ref(command): return` exits without ever consulting `feature.json`, regardless of
`build_entry` state.

Rated low, not high: DEC-138/D-07 already make the LOCAL `feature.json` record the sole and
trusted source of truth for this gate, by design (never a GitHub read). An actor who can shape a
Bash command precisely enough to construct this evasion already has the same-or-greater ability
to bypass the gate far more directly — editing `feature.json`'s `github.build_entry` to `"opened"`
via a plain `echo`/`python -c` — which the design already accepts as within the local operator's
trust boundary (P-02: an actor who already controls the value already holds the privilege it
grants). This is a second path to an already-accepted trust boundary, not an escalation; recorded
for completeness, not gating.

## Threat model
| boundary | STRIDE | mitigated |
|---|---|---|
| PreToolUse Bash gate deciding merge-vs-deny on local feature.json record | Tampering (of the enforcement decision itself, via subprocess crash) | **false** — see F1 |
| PreToolUse Bash gate command-string recognition | Tampering (evasion of detection) | false, but non-escalating — see F2 |
| gh-sync.py → `gh` CLI argv construction | Injection | true — argv-list throughout, no shell=True |
| feature.json build_entry recording | Information disclosure | true — enum values only, no secrets |
| feature_schema.py path-segment helpers | Tampering (path traversal) | true — basename/segment-only, never joined into a read/write path |

## open_questions
None blocking. F1 is a concrete, demonstrated defect the backend/dev-ops lane should fix before
ship (wrap `main()`'s remaining subprocess calls in the same fail-safe pattern already used for
the config/payload parse, or explicitly catch `OSError` around `gh_head`).
