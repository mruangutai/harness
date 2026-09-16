# Security review — BUG-1309-mirror-build-entry — ac2bc0bb @ c8b23e03

## BLUF
The orchestrator's flagged regression is **real and confirmed end-to-end** through the actual hook
with a real PreToolUse payload against a real fixture tree, not just via `merge_ref`. `git_merge()`
in the new `merge-gate.py` (lines 47–61) fixes the pre-subcommand global-flag case (`-C`, `-c`,
`--work-tree`, …) correctly, but as a side effect drops the pre-change code's handling of flags
placed **after** `merge`. Any `git merge <flag> <branch>` shape — including the everyday `--no-ff`
and `--squash`, not an exotic evasion — now silently bypasses the gate: exit 0, empty stdout, empty
stderr. **HIGH**, `must_fix`.

## F-01 / F-03 — verified correct, no finding
- F-01 ambiguity-before-era-exempt ordering: confirmed in source — `if len(owners) > 1: deny(...); return`
  fires immediately after the `feature_for` call, strictly before `owners[0]` is even unpacked, so it
  fires regardless of era-exemption. New test `T-05 duplicate valid records claiming the branch deny
  naming both` exercises this. No gap found.
- F-03 `_build_entry_recovery_notice`: `feature_schema.recovery_command_for` returns only one of two
  hardcoded literals (`"open"` / `"recover-terminal"`); the notice is a bare `print()` to stderr, never
  passed to a shell or subprocess. No injection surface.

## F-02 / the flagged regression — CONFIRMED, table below
Fixture: `/tmp/bug1309-fixture` (`github.sync: true`, `github.repo: "acme/widgets"`,
`feat-x/feature.json: {branch: "feat/x", github.build_entry: "recovery-required"}`). Payloads piped
as real PreToolUse JSON into `merge-gate.py <root>`, `env -u HARNESS_AGENT_TYPE`. Pre-change baseline
recovered via `git show de04d841:...merge-gate.py`, same fixture, same payloads.

| Command | Post-change (`ac2bc0bb`) | Pre-change (`de04d841`) | Classification |
|---|---|---|---|
| `git merge feat/x` | deny | deny | baseline, correct both |
| `git merge --no-ff feat/x` | **empty (ALLOW)** | deny | **INTRODUCED regression** |
| `git merge --squash feat/x` | **empty (ALLOW)** | deny | **INTRODUCED regression** |
| `git merge -m 'msg' feat/x` | empty (ALLOW) | empty (ALLOW) | pre-existing (both mis-parse the branch; same net outcome) |
| `git -C /repo merge feat/x` | deny | empty (ALLOW) | **fix** — this delta's own improvement |
| `git -C /repo merge --no-ff feat/x` | empty (ALLOW) | empty (ALLOW) | pre-existing net outcome (old: `merge` undetected at all; new: detected, then mis-grabs `--no-ff`) |
| `git -c core.pager=cat merge feat/x` | deny | (not applicable — old code never special-cased `-c`) | new coverage, correct |
| `git pull origin feat/x` | empty (ALLOW) | empty (ALLOW) | pre-existing (`git_merge` never recognizes `pull`) |
| `git merge FETCH_HEAD` | empty (ALLOW) | empty (ALLOW) | pre-existing / expected (no feature owns literal branch `FETCH_HEAD`) |
| `sh -c "git merge feat/x"`, 3-level nested `bash -c` | deny | deny (unchanged `nested_merge`) | correct, depth ≤ 3 |
| 4-level nested `bash -c "git merge feat/x"` | empty (ALLOW) | empty (ALLOW), same depth cap | pre-existing, `nested_merge`'s `depth >= 3` cutoff untouched by this diff |

Root cause (`merge-gate.py:47-61`): `git_merge` walks tokens, correctly skipping `takes_value`
global flags and other `-`-prefixed tokens **before** `merge`, but the instant it matches `token ==
"merge"` it returns `rest[index + 1]` unconditionally — it never resumes the skip loop for flags
occurring *after* `merge`. The pre-change code filtered `-`-prefixed words out of the *entire* `rest`
list first, so `--no-ff`/`--squash` were removed regardless of position; that whole-list filter is
what's lost.

**Test-suite gap that let this ship green**: the new tests added in the same commit
(`tests/integration/test-merge-gate.py`) cover `-C`, `-c`, `--work-tree` (pre-subcommand) and the
duplicate-owner ambiguity case, but add no case with a flag placed *after* `merge`. The pinned suite
passing is consistent with the regression, not evidence against it.

## Fail-open / injection checks (items 3–4 of dispatch) — no new finding
- `main`'s outer `except Exception: return` (unchanged by this diff, predates it) is a pre-existing
  fail-open surface for a malformed `harness.json` or non-JSON stdin. Not touched by `ac2bc0bb`.
- `feature_for`'s `except (OSError, json.JSONDecodeError): continue` is deliberate, documented
  per-record skip (comment updated in this diff to describe the same intent for the new list form);
  a fully-malformed record set still collapses to `owners == []`, same fail-open shape as the
  pre-change `document is None` path — refactor preserved behavior, did not widen it.
- `gh_head`/`GH_BIN`: unchanged by this diff, list-form `subprocess.run` argv (no `shell=True`), no
  injection surface; `GH_BIN` override requires control of the hook's own environment, which already
  implies compromise well beyond this hook.
- Attacker-controlled branch names land only inside `json.dumps(...)`-wrapped deny reasons (properly
  escaped) or `print()` stderr text — no manual JSON string-concatenation, no command-line
  interpolation into a shell.

## Severity and rationale
`--no-ff` is an idiomatic, everyday merge flag (not an adversarial evasion technique) in this
project's own git history. This bypass is reachable by ordinary use, not just a crafted attack, and
is fully silent (exit 0, no stdout, no stderr) — unauditable after the fact. It defeats the exact
control this hook exists to provide for any `recovery-required` feature. Rated **HIGH**: it's an
enforcement-bypass reachable by an ordinary actor of the system (an agent/operator running git),
not remote code execution or credential/data compromise, so not `critical`.

## must_fix
- **SEC-01** (high) `merge-gate.py:47-61` `git_merge` — must also tolerate/skip flags occurring
  *after* the `merge` token when locating the branch positional (not just before it), or must
  otherwise restore whole-list flag filtering. Concrete repro: `git merge --no-ff feat/x` against a
  `recovery-required` feature owning `feat/x` returns empty stdout (ALLOW) instead of a deny. Add
  regression coverage for `--no-ff`, `--squash`, and other post-subcommand-flag shapes alongside the
  existing `-C`/`-c`/`--work-tree` pre-subcommand tests, since the current suite is silent on this
  shape and would not catch a re-regression.

```yaml
VERDICT: FAIL
DIGEST:
  headline: "git_merge only skips flags before 'merge', not after — 'git merge --no-ff feat/x' and '--squash' silently bypass the gate (confirmed end-to-end); F-01/F-03 verified correct"
  severity_max: high
  findings: 1
  must_fix:
    - "SEC-01 (high) merge-gate.py:47-61 git_merge takes rest[index+1] unconditionally once 'merge' is matched, so any flag placed after 'merge' (--no-ff, --squash, ...) is grabbed as the branch instead of skipped, and feature_for() then finds no owner -> silent ALLOW (exit 0, empty stdout/stderr) for a recovery-required feature. Confirmed via real hook + real PreToolUse payload against a fixture tree, and confirmed absent pre-change (de04d841 correctly denied the same two commands). Fix: resume flag-skipping after matching 'merge', not just before it; add regression tests for post-subcommand flags."
  threat_model:
    - { boundary: "PreToolUse tool_input.command string -> merge-gate.py branch/owner resolution", stride: "T", mitigated: false }
    - { boundary: "feature.json ambiguity (two records claiming one branch) -> merge-gate.py main()", stride: "T", mitigated: true }
    - { boundary: "gh-sync.py _build_entry_recovery_notice command derivation", stride: "I", mitigated: true }
    - { boundary: "gh_head subprocess argv / GH_BIN env override", stride: "E", mitigated: true }
  open_questions: []
  files_touched: []
  expertise_update: []
artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-1309-mirror-build-entry/.harness/harness/features/BUG-1309-mirror-build-entry/notes/review-harness-security-reviewer-c14.md
```
