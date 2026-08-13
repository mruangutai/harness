# Security review — FEAT-17-guard-boundaries S2 — worktree pointer parser attack

**SHA examined:** `c6a28bdee6efabe0f7b2a116defaa819ecd88cbd` (confirmed `git rev-parse HEAD` == `review_sha`, so the working tree was reviewed directly — no `git show` needed).

**`git status --porcelain` at START:**
```
 M .harness/features/FEAT-17-guard-boundaries/feature.json
```
**`git status --porcelain` at END:**
```
 M .harness/features/FEAT-17-guard-boundaries/feature.json
```
Identical — that one line predates this run (not mine; I made no repo-tree writes). All fixtures were built under `/private/tmp/claude-501/.../scratchpad/wtattack/`, outside the repo.

**Files touched (diff `main...c6a28bd`):**
`.claude/skills/harness/bin/{bash-write-guard.sh,check-domain.sh,check-state.sh,harness_boundary.py,test-bash-write-guard.py,test-check-domain.py,test-check-state.py}`,
`.harness/features/FEAT-17-guard-boundaries/{BRIEF.md,STATE.md,feature.json,notes/*,plan.yaml}`,
`.harness/notes/grilling-central-product-config-2026-08-12.md`,
`docs/harness/{DECISIONS-INDEX.md,DECISIONS.md}`.

Every `file:line` anchor below is at `c6a28bd`, taken directly from the checked-out tree (matches HEAD).

---

## VERDICT: FAIL — one HIGH finding, proven with a live before/after exploit, not theory

### F1 [HIGH] — corrupting a `.git` pointer file (an already-unrestricted write) permanently disables the `out_of_place_worktree` guard for every subsequent write into that tree

`harness_boundary.py:378-382`:
```python
try:
    with open(dot, "r", encoding="utf-8", errors="strict") as fh:
        line = fh.read().strip()
except Exception:
    return None
```
`None` means "unknown", and both callers treat unknown as "not a worktree":
`classify()` at `harness_boundary.py:271-276` (`_wt_owner is not None and not _wt_owner[2]` — `None` short-circuits false, falls through to `not_a_domain_question`, i.e. **allow**), `check-domain.sh:420-421`, `bash-write-guard.sh:128-129` (same pattern, root-side).

**Executed, not reasoned — decisive before/after against the real deployment** (`root` = this repo, real `fleet.yaml`, target = `<scratch>/final_demo/src/main.py`, standing in for a plausible sibling worktree e.g. `../harness-wt1`):

| Step | `.git` file content | `classify()` outcome for `src/main.py` inside it |
|---|---|---|
| 1 | absent | `not_a_domain_question` (nothing there yet — correct, expected) |
| 2 | `gitdir: <root>/.git/worktrees/demo-session\n` (well-formed, exactly what `git worktree add` writes) | **`out_of_place_worktree`** — correctly BLOCKED, `checkout` reported correctly |
| 3 | same bytes **+ one trailing `\xff`** (simulated truncation/corruption) | **`not_a_domain_question`** — ALLOWED |

Same repo, same target file, same globs. The only change between step 2 and step 3 is one corrupted byte in the pointer file, and the guard's verdict flips from BLOCKED to ALLOWED. That reinstalls issue #103 — the exact bug this feature exists to close — inside the fix, silently: no stderr, no log line distinguishes "correctly identified as not-a-worktree" from "parser choked and gave up" (aggravates auditability).

**Reachability, proven empirically against the live `fleet.yaml`** (not assumed):
```python
hb.classify("/Users/.../GitHub/harness-wt1-DEMO/.git", root, ["src/**"], [], "probe")
# -> "not_a_domain_question"
```
This deployment's `workspace_root` (`.harness/factory/fleet.yaml`) is `/Users/molchairuangutai/GitHub/harness-factories` — disjoint from `/Users/molchairuangutai/GitHub/harness-wt1` or any other sibling of the harness checkout. A write to `<sibling>/.git` is therefore **already fully permitted, unconditionally**, by `classify()` itself, for any `harness-*` agent with ordinary Bash or Write access (which is nearly every governed agent — this is not a privileged action). So the corrupting write requires no bypass, no evasion, no elevated access: it is the same class of action the guard already grants freely. It doesn't even need to be malicious — a crashed process, a disk-full truncation, an editor autosave mid-write, or a stray `tee`/append into the wrong file produces the identical byte pattern (confirmed separately: appending any second line to an otherwise-valid pointer also returns `None` — same fail-open, via the regex's non-`MULTILINE` `$` never reaching end-of-string across an embedded `\n`).

**This gates the review** (`severity_max: high`, `must_fix` non-empty).

### F2 [MED] — the `worktrees`/`.git` basename shape assumption (`harness_boundary.py:393-396`) fails open for real, non-default git layouts

Confirmed by execution: a submodule-style pointer (`gitdir: ../.git/modules/sub`) and a bare-repo-style worktree pointer (`gitdir: /path/repo.git/worktrees/id`, where the git-dir is named `repo.git` not `.git`) both return `None` → same fail-open as F1.
Reachability for *this* deployment is low — the harness repo is a plain top-level checkout, not a submodule or bare repo, so I cannot name a live trigger today. Recording as defense-in-depth, not blocking, because the trigger requires a git topology this repo does not use.

### F3 [MED, latent/inert today] — `.git` as a symlink to an arbitrary directory is misread as "legitimate main checkout"

`os.path.isdir(dot)` at `harness_boundary.py:375` follows symlinks. Confirmed by execution: a directory whose `.git` entry is a symlink to *any other directory* (not necessarily a real git-dir) returns `(cur, cur, True)` — "legitimate main checkout" — rather than `None` or `False`.
In `classify()`'s current target-side call site this happens to produce the *same* net outcome as `None` (both fall through to `not_a_domain_question`), so it is not independently exploitable there today. The two ROOT-SIDE call sites (`check-domain.sh:420`, `bash-write-guard.sh:128`) test `worktree_owner(root)` directly and would treat a symlinked `root/.git` as fully legitimate, waving the session through with no refusal. **Open question, not asserted as exploitable**: I did not verify whether `.git` itself is excluded from every governed agent's writable globs in `team-config.yaml` — if it is (as I'd expect, since `.git` is not a source path any agent is normally granted), this is inert; if some domain grants a glob broad enough to reach `root/.git` (e.g. a bare `**` or a misconfigured shared path), this becomes live. Flagged rather than closed.

---

## Attacks tried and found NOT exploitable (recorded so a future reviewer does not re-raise them)

- **Relative `gitdir:` pointer resolved against `cur`** (`harness_boundary.py:387-391`): matches real git semantics (a worktree's relative pointer is relative to the worktree directory, not process cwd). Confirmed correct via execution.
- **Relative pointer escaping upward** (`../../.git/worktrees/x`): resolves and is correctly judged illegitimate for an out-of-place location — not a fail-open. Confirmed via execution.
- **Trailing newline / CRLF / trailing spaces / no trailing newline**: all parse correctly (`.strip()` absorbs them). Confirmed via execution.
- **Symlinking `<sibling>/.git` to a legitimate worktree's real pointer *file***: does not launder — legitimacy is keyed off `cur` (the checkout location), not the pointer target, so this is correctly judged illegitimate. Confirmed via execution.
- **Reaching the checkout directory itself through a symlink**: `real()` resolves it correctly to the underlying legitimate checkout, as its own docstring intends. Confirmed via execution.
- **Unreadable ancestor directory** (`chmod 000`): does **not** raise inside `worktree_owner`. `os.path.isdir`/`isfile` and `os.path.realpath` swallow `OSError`/`PermissionError` internally (CPython's `genericpath`/`posixpath` implementation) and degrade gracefully — walks past the unreadable node, no crash, no exit 1. This specific dispatch concern is **falsified**, not merely unconfirmed.
- **Self-referential symlink cycle**: no hang, no exception — `os.path.realpath`'s built-in cycle guard short-circuits. Confirmed via execution.
- **`os.path.commonpath` `ValueError`**: every call site found (`select_base`'s `inside()`, `worktree_owner`'s legitimacy check, and the new worktree-creation scan at `bash-write-guard.sh:463`) wraps the call in `try/except ValueError`. No uncaught site found.
- **The fleet-bricking DoS concern (D-06)**: tested, not just accepted. `check-domain.sh:271` (`_governed = bool(agent) and agent.startswith("harness-")`) and `bash-write-guard.sh:50-58` (`sys.exit(0)` for empty/non-`harness-` `agent_type`, and for `harness-dev-ops`) both confirm the **main session bypasses `resolve_fleet`'s `sys.exit(2)` entirely**, on both routes. A malformed `fleet.yaml` blocks every governed subagent's writes (by design — fail-closed) but never locks out the one tier that can repair it. D-06 holds.
- **Worktree-creation scan** (`bash-write-guard.sh:377-431`, new in this diff): `_worktree_destination` returns `None` (refuse) for any unparsed form — correctly conservative, fails closed on the parser's own uncertainty. I did **not** deep-test the classic scanner-bypass class (`sh -c "git worktree add ..."`, `command git`, aliases, `xargs`) — out of primary scope for "the worktree pointer parser" and not enough budget left to do it justice; flagging as an open question rather than a finding either way.

---

## open_questions

- `{ id: Q1, question: "Is '.git' itself excluded from every governed agent's writable globs in team-config.yaml, at every base (harness root and every product base)? F3 is inert only if so.", blocking: false }`
- `{ id: Q2, question: "Does the new worktree-creation scan (bash-write-guard.sh:365-431) resist invocation via 'sh -c', 'command git', a shell alias, or xargs? Not tested here.", blocking: false }`

## Nothing I could not falsify

I was able to execute every fixture named in the dispatch directly against `harness_boundary.py` with no git binary and no governed write (per the dispatch's own guidance) — issue #284 did not block me this run. Nothing to report under "if you cannot falsify something."

```yaml
VERDICT: FAIL
DIGEST:
  headline: "worktree_owner() fails open on a corrupted .git pointer file, and creating that corruption is itself an already-unrestricted write — proven with a live before/after exploit (BLOCKED -> ALLOWED on the identical target) against this deployment's real fleet.yaml, reinstalling issue #103 inside its own fix"
  in_scope: true
  scope_reason: "New shared parser (harness_boundary.py) is the sole trust boundary for two write guards; it reads untrusted/attacker-reachable filesystem state (.git pointer files) with no git subprocess as its ground truth, and fails open by design on any parse failure"
  severity_max: high
  findings: 3
  must_fix:
    - "harness_boundary.py:378-382 worktree_owner(): a .git pointer file that fails to parse (non-UTF-8, multi-line, or an unrecognised shape) must not be indistinguishable from 'not a worktree.' The two states (parsed-and-legitimate vs. parse-failed) currently collapse to the same None return and the same allow-outcome in every caller; at minimum this needs a distinguishable failure mode that does not silently permit writes into a checkout git itself already produced, and ideally a loud refusal (matching this module's own fail-closed pattern elsewhere) rather than a quiet fall-through to not_a_domain_question."
  threat_model:
    - { boundary: "filesystem: .git pointer file content, read with NO git subprocess as the sole ground truth for the out-of-place-worktree refusal", stride: T, mitigated: false }
    - { boundary: "filesystem: .git as a directory-symlink, read via os.path.isdir at the root-side worktree_owner(root) call", stride: S, mitigated: "partial — inert at the target-side call site today, unverified at the root-side call sites (Q1)" }
    - { boundary: "hook process: uncaught exception inside the hook heredoc after a successful harness_boundary import", stride: D, mitigated: true }
    - { boundary: "resolve_fleet/select_base sys.exit(2) as a shared-module DoS against repair", stride: D, mitigated: true }
  open_questions:
    - { id: Q1, question: "Is '.git' itself excluded from every governed agent's writable globs in team-config.yaml, at every base? F3 is inert only if so.", blocking: false }
    - { id: Q2, question: "Does the new worktree-creation scan resist sh -c / command git / alias / xargs invocation? Not tested.", blocking: false }
  files_touched: []
  expertise_update: []
artifact: .harness/features/FEAT-17-guard-boundaries/notes/review-harness-security-reviewer-2026-08-12-panel.md
```
