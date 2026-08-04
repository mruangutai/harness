# Security review — FEAT-05 PyYAML file parsers — STRIDE audit of the two write gates

Diff `37a8a66..340e18a` (18 commits). All findings below are from reading
`check-domain.sh`, `bash-write-guard.sh`, `harness_yaml.py` at `340e18a` directly, plus live
end-to-end reproductions against the actual hook binaries in this worktree (commands shown
inline, run against disposable `tempfile.mkdtemp()` fixture roots — never against this repo's
own `.harness/team-config.yaml`). Author artifacts (BRIEF/PLAN/handoff/UAT) were treated as
claims to verify, not facts to relay.

## VERDICT: FAIL

`severity_max: high` — F1 (manifest walk fails OPEN on any non-`YAMLError` read/parse failure)
gates this.

---

## 1. The deadlock/recovery question — REFUTED. No deadlock. [read code, not a fresh live probe]

The author's claim — "the main session is exempt at `check-domain.sh`'s no-agent-identity
check, so it is the only party who can repair the rulebook" — **holds for both hooks**, not
just the one the author cited:

- `check-domain.sh:74-75` — `if not agent: sys.exit(0)` (main session's Write/Edit calls carry
  no `agent_type`)
- `bash-write-guard.sh:51-52` — `agent = d.get("agent_type") or ""` / `if not agent: sys.exit(0)`
  — **structurally identical**, same payload field, checked before `require_or_bootstrap` is
  ever called (`:78`).

So the main session's own Bash call to run the printed `python3 -m pip install pyyaml`
command is **never subject to the PyYAML gate at all** — it exits 0 before `require_or_bootstrap`
is reached. There is a second, independent recovery path too: `harness-dev-ops` is
unconditionally exempt from `bash-write-guard.sh` (`:56-57`, `if agent == "harness-dev-ops":
sys.exit(0)`), also *before* the PyYAML gate — so dev-ops can `tee`/`cat >` a fix via Bash
regardless of PyYAML or marker state, without ever touching `require_or_bootstrap`. It is
**not** exempt from `check-domain.sh` (only the main session is, `:74-75`), so its recovery
channel is Bash, not Write/Edit — confirmed by reading, matches the task's framing.

The UAT's U-05 observation ("even `echo hi` was refused with nothing printed") does not
contradict this: that command was issued by a **spawned subagent** (non-empty `agent_type`),
which is correctly governed and correctly blocked once its grant expired — it was never a
main-session recovery attempt. `notes/uat-bootstrap-escape-expiry.md:100-105`.

**Caveat, stated honestly:** I did not fire a fresh, genuine main-session-Bash `PreToolUse`
hook myself to prove `agent_type` is empty in that exact context — that would require a live
Claude Code session, out of reach for a read-only script-level review. The conclusion rests on
(a) the two hooks reading the identical payload field with identical logic, and (b) the
existing DEC-110-grade design note in `check-domain.sh:9-11,70-73` asserting this is measured
behaviour. Treat as high-confidence, not independently re-measured here.

Verified mechanically: `grep -n "team-config" .harness/team-config.yaml` returns **zero**
matches — no agent's domain grants `team-config.yaml`, confirming the author's "zero agents
hold the manifest" claim.

---

## 2. F1 — HIGH — the manifest walk fails OPEN on any non-`YAMLError` read failure, not just malformed YAML

`harness_yaml.load_file` (`:104-108`) reads the manifest **outside any try**:

```python
def load_file(path):
    with open(path, encoding="utf-8") as f:
        text = f.read()          # not inside a try — a read failure here is not a YAMLError
    return load_str(text, path)
```

Both hooks' manifest-domain-walk call sites catch only two exception types
(`check-domain.sh:133-159`, `bash-write-guard.sh:286-306`:
`except harness_yaml.DuplicateKeyError` / `except harness_yaml.YamlParseError`), and
`load_str` itself (`:92-101`) converts only `yaml.YAMLError` subclasses. Anything else —
a bad encoding, the manifest path being a directory — propagates uncaught, crashes the hook's
`python3` subprocess, and since that heredoc is the last command each script runs (`set -uo
pipefail`, no `set -e`), the crash's exit code becomes the hook's own. Per this file's own
header (`check-domain.sh:13-14`, DEC-100): *"Only exit 2 blocks — exit 1 is a NON-blocking
error and the write proceeds."*

**Verified live, two independent triggers, both plausible file states rather than crafted
payloads** — a disposable `tempfile.mkdtemp()` fixture root, `harness-backend-dev` granted only
`allowed/**`, target `forbidden/x.py` (outside its domain, would normally be denied):

- **Invalid UTF-8 byte in the manifest** (a bad merge smudge, a stray latin-1 paste):
  ```
  $ check-domain.sh   (manifest has one 0xFF byte)
  EXIT 1 — UnicodeDecodeError at harness_yaml.py:107 (load_file's f.read())
  $ bash-write-guard.sh  (same manifest, Bash write to the same forbidden path)
  EXIT 1 — identical UnicodeDecodeError, same call site (harness_yaml.py:120 -> :107)
  ```
- **Manifest path is a directory** (`os.access(manifest, os.R_OK)` at `check-domain.sh:100`
  returns **True** for a directory, so the "no manifest" fail-open guard does not catch this —
  it falls through to the parser):
  ```
  $ check-domain.sh   (.harness/team-config.yaml is a directory, not a file)
  EXIT 1 — IsADirectoryError at harness_yaml.py:106 (open())
  ```

In both cases the forbidden-path write would proceed: **the crash happens inside the manifest
walk itself, before any agent's domain is even consulted, so every agent's every write is
ungoverned** for the life of that broken manifest — not just the one write that triggered it.
This directly contradicts REQ-04 ("the two PreToolUse write hooks refuse the write rather than
allowing it with enforcement silently off") and the code's own stated design goal
(`check-domain.sh:119-121`, *"Allowing by crash is not allowing"* — written for the
`yaml is None` case, not extended to this one). It also contradicts DEC-171 am.1's fail-closed
mandate, cited by name in both call sites' comments (`check-domain.sh:147-150`,
`bash-write-guard.sh:297-299`) as the reason a malformed manifest should block, not pass.

**A second, narrower instance of the same root cause** exists at `check-domain.sh:305-325`,
the DEC-150/154 state.yaml shape gate: a `RecursionError` from PyYAML's composer on a deeply
literally-nested YAML value (verified separately, ~250-300 nested flow collections is enough to
exceed Python's default recursion limit) crashes the same way — but there the blast radius is
narrower (one file the writing agent already owns, and `check-state.sh:332-344`'s independent
regex-based INV-16 sweep still catches the resulting malformed content on its next run, so it
is not a permanent bypass the way the manifest case is).

**Mitigating factor found and worth stating:** the safe pattern already exists in this same
diff — `check-state.sh:111-119` wraps the identical `harness_yaml.load_file` call in a broad
`except Exception as e:` and reports a per-feature violation instead of crashing. It just was
not applied to `harness_yaml.py`'s own `load_str`/`load_file`, nor to the two hook call sites
that most need it.

**Suggested fix (not applied, read-only):** widen `load_str`'s except clause — e.g.
`except Exception as e: raise YamlParseError(where, e) from e` — and move `load_file`'s
`f.read()` inside the same try, mirroring `check-state.sh`'s own pattern, so any read or parse
failure becomes the already-wired fail-closed path at both call sites, not just
`yaml.YAMLError` subclasses.

---

## 3. Elevation during the escape window — MED — reviewers lose their read-only guarantee

`bash-write-guard.sh` hard-codes a `REVIEWERS` carve-out (`:92`, `:274-277`): any detected
write pattern from `harness-code-reviewer`/`harness-security-reviewer`/`harness-ui-reviewer` is
denied outright, unconditionally, "their job is findings, never fixes." **`check-domain.sh` has
no equivalent** — `grep -n "REVIEWERS\|READ-ONLY" check-domain.sh` returns nothing. Reviewers'
write restriction there comes *only* from their narrow domain glob in `team-config.yaml`.

During an active bootstrap escape (PyYAML absent, grant not yet spent this session),
`check-domain.sh` exits at `:122-123` (`if harness_yaml.yaml is None: sys.exit(0)`) **before**
`domain_check()` is ever reached — and `domain_check()` is the only place a reviewer's
restriction is enforced in this hook. So in that window, a spawned `harness-security-reviewer`
(or any agent) can use the **Write/Edit tool** to write to any path in the repo — not just
config — for the remainder of that session. This is the documented, intended trade-off
("GRANTED, and there is no parser. Stop here" — the escape's whole point is letting writes
through), but it removes a *named, load-bearing* invariant (reviewers never fix) for a window
that is exactly the first-run state this feature exists to handle (REQ-05) — not a rare corner.
Self-healing once PyYAML is installed; bounded to one session.

---

## 4. Non-findings, verified rather than assumed

- **`systemMessage` stdout JSON (D-14b), `harness_yaml.py:313`** — built via `json.dumps()`,
  not string interpolation, so embedded `\n`/`#` in the static `INSTALL_COMMAND` constant
  cannot produce malformed JSON. `grep -n "print(" check-domain.sh bash-write-guard.sh` shows
  every other `print()` in both scripts targets `file=sys.stderr`; this is the only stdout
  writer on the codepath (single-process design, T-13/T-15) — no second-writer collision.
- **YAML alias/anchor expansion ("billion laughs")** — tested directly: a 20-level
  self-referencing alias chain parsed in <2ms with no exponential growth (PyYAML resolves
  aliases as shared object references, not deep copies). Not a DoS vector here.
- **YAML 1.1 type coercion (`on:` → `True`)** — `check-domain.sh:332-333` `str()`-coerces every
  key before comparing to `ALLOWED`, with a dedicated explanatory message at `:340-348`. Correct
  and downstream of a successful parse (unaffected by F1).
- **Marker file edge cases** — directory, unreadable, write-failure all route through
  `except OSError` and fail closed with a message (`harness_yaml.py:261-271,282-292`);
  zero-byte/truncated content just fails the identity compare and blocks. A full scan of
  `.harness/team-config.yaml` for a `path:` glob matching the marker returns nothing beyond the
  universal read-only `.` entries — which `check-domain.sh`'s own `matches()` explicitly
  excludes from write grants (`if pat in (".", ""): return False`). Ordinary agents cannot
  Write/Edit or Bash-write the marker; only the main session and `harness-dev-ops` can, matching
  the existing DEC-85 trust boundary rather than widening it.
- **Gitignore chain (D-01)** — `.gitignore:13` and
  `.claude/skills/harness/templates/gitignore.snippet:11` both list
  `.harness/.pyyaml-bootstrap` — verified present in both, so the marker (which carries a
  session id) cannot be committed.
- **Parser choice** — the only `yaml.load()` call anywhere in the six converted scripts is
  `harness_yaml.py:97`, using a `yaml.SafeLoader` subclass (`_StrictSafeLoader`) — never the
  unsafe default `Loader`. All six scripts route through `harness_yaml.load_str`/`load_file`
  (grep-confirmed) — no second parse path anywhere (SC-04).

---

## DIGEST

```yaml
VERDICT: FAIL
DIGEST:
  headline: "check-domain.sh AND bash-write-guard.sh's manifest walk fail OPEN on any non-YAMLError read failure (bad UTF-8, manifest-as-directory — both verified live) — every agent's every write goes ungoverned, not just the write that triggered it. The suspected escape/deadlock is otherwise refuted: main session and harness-dev-ops both have real Bash recovery paths."
  in_scope: true
  scope_reason: "diff changes the write-gating enforcement layer itself (check-domain.sh, bash-write-guard.sh, harness_yaml.py) — every write from every agent in the org passes through this code."
  severity_max: high
  findings: 2
  must_fix:
    - >-
      harness_yaml.load_str/load_file (harness_yaml.py:92-108) only converts yaml.YAMLError to
      the fail-closed YamlParseError, and load_file's own f.read() sits outside any try. A
      non-YAMLError failure -- UnicodeDecodeError on an invalid-UTF-8 byte, or IsADirectoryError
      when the manifest path is a directory (check-domain.sh:100's R_OK guard does not catch
      this) -- propagates uncaught through both hooks' manifest walk (check-domain.sh:133-159,
      bash-write-guard.sh:286-306), crashes the hook's python3 subprocess, exits 1, and per
      DEC-100 exit 1 is non-blocking: every subsequent write from every agent proceeds
      ungoverned until the manifest is fixed. Verified live against both hook binaries with a
      one-bad-byte manifest and a directory-as-manifest fixture, targeting a path outside the
      test agent's domain in both cases -- both writes would have proceeded. Widen the except
      clause (mirror check-state.sh:111-119's own `except Exception as e:` pattern, already
      present elsewhere in this codebase) and move load_file's read inside the try, so any
      read-or-parse failure becomes the already-wired fail-closed YamlParseError path.
  threat_model:
    - { boundary: "PreToolUse Write/Edit hook (check-domain.sh) manifest walk vs. repo state", stride: T, mitigated: false }
    - { boundary: "PreToolUse Bash hook (bash-write-guard.sh) manifest walk vs. repo state", stride: T, mitigated: false }
    - { boundary: "check-domain.sh state.yaml shape gate (DEC-150/154) vs. one owned file", stride: T, mitigated: false }
    - { boundary: "bootstrap-escape marker (.harness/.pyyaml-bootstrap) as a session-identity write permit", stride: S, mitigated: true }
    - { boundary: "PyYAML-absent escape window -- domain enforcement fully off in check-domain.sh, no reviewer carve-out unlike bash-write-guard.sh", stride: E, mitigated: false }
    - { boundary: "PreToolUse hook stdout (systemMessage JSON, D-14b) -- host's allow/block interpretation channel", stride: T, mitigated: true }
  open_questions:
    - { id: Q1, question: "Should harness_yaml.load_str/load_file catch Exception broadly (matching check-state.sh's own pattern) and move the file read inside the try, so a UnicodeDecodeError/IsADirectoryError/RecursionError all become YamlParseError at both hook call sites instead of crashing the hook open?", blocking: true }
    - { id: Q2, question: "Should check-domain.sh gain a REVIEWERS carve-out symmetric to bash-write-guard.sh's, so a reviewer stays read-only even during an active bootstrap-escape window?", blocking: false }
  files_touched: []
  expertise_update: []
artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/fix-harness-tooling-backlog/.harness/features/FEAT-05-pyyaml-file-parsers/notes/review-harness-security-reviewer-c0.md
```
