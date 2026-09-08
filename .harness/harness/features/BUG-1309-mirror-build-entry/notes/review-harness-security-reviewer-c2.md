# Security review c2 — BUG-1309-mirror-build-entry — review_sha 358ac56188a04f63f83dbbc3f9bfd4a6fc1c28f2

## BLUF
**PASS.** No new finding. The code diff `d80a7b12..358ac561` is empty for every source/hook file
(only `feature.json`'s `review_sha` bumped and a 4-line `GRADE-2 REASON` comment added above
`_run_merge_and_check` in `tests/integration/test-hooks-install.py` — confirmed by `git diff --stat`:
5 insertions/1 deletion across those two files only). `merge-gate.py`, `merge-gate.sh` and
`feature_schema.py` are byte-identical to the tree cycle-1 already certified (`git diff` empty,
`git hash-object` unchanged). I independently re-ran the specific lazy-import/universal-reachability
probe the dispatch asked for, with fresh executed evidence at 358ac561 rather than citing cycle-1's
note, and it confirms the same conclusion cycle-1 reached: no new permit path.

## What I examined, and what I measured (not assumed)

**1. Byte-identity of the gate at this pin.** `git diff d80a7b12..358ac561 -- merge-gate.py
merge-gate.sh feature_schema.py` → empty; `git hash-object` on both files matches what cycle-1
reviewed. Since the dispatch's specific question is about mechanism, not text, I still executed
independent probes rather than resting on the hash match alone.

**2. Lazy-import gating, real subprocess, `-X importtime` trace (no mocking).** Ran the real
`merge-gate.py` against this worktree's real `.harness/harness.json` (`github.sync: true`,
`github.repo: "mruangutai/harness"`, pinned) and real feature tree:
- `git status` (non-merge): `-X importtime` trace shows **no** `feature_schema` import line, exit 0,
  no output. Confirms the import is unreachable for the overwhelming majority of Bash traffic.
- `git merge feat/BUG-1309-mirror-build-entry` (real merge command, real branch, real feature.json
  for this feature — which is itself era-exempt): trace shows `feature_schema` imported, decision
  correctly reads the real local era-exempt set, prints the allow notice, exit 0.
- `bash -c "git merge feat/BUG-1309-mirror-build-entry"` (one level of shell nesting): same —
  `nested_merge` still finds it, import fires, correct decision. Nesting does not evade detection.

**3. Shadowing of the lazy import.** `merge-gate.py:10` does `sys.path.insert(0,
os.path.dirname(__file__))`, and a fresh `python3 -c "print(sys.path[0:3])"` shows index 0 is
always the running script's own directory (`''`/cwd or the script dir), ahead of the stdlib zip and
lib paths — there is no site-packages or ambient path entry offering a same-named module. A
filesystem-wide `find / -name feature_schema.py` turned up ~300 hits, but every one sits under other
reviewers'/testers' throwaway `/tmp` and `/private/var/folders/.../T/...` scratch directories from
unrelated bug-895/bug-1305/bug-1308 mutation-test runs — none of those directories are on `sys.path`
for this process, and reaching one would require an attacker who already controls `PYTHONPATH` or
the interpreter invocation, i.e. already has code-execution-equivalent control over the hook's own
environment (P-02: that actor already holds the privilege the shadow would grant — not an
escalation). No exploitable shadow path found.

**4. DEC-138 compliance under adversarial GH read outcomes — executed, in-process, real
`local_branch()`/real feature-glob machinery, only `open`/`glob.glob`/the `gh` subprocess call
faked (matching cycle-1's own reconstruction technique; I could not write disk fixtures —
`bash-write-guard.sh` blocks all my writes, verified live).**
  - Local record owes a receipt (not era-exempt, `build_entry` absent) + `gh pr merge 42` with an
    **unresolvable `gh` binary** → correctly **denies**, and the denial reason does **not** leak the
    `gh` failure text (`[Errno 2]...`) — asserted and passed.
  - Same local record + `gh pr merge 42` where the `gh` subprocess is faked to **succeed** and
    resolve an unrelated branch with no matching local `feature.json` → correctly **falls through to
    allow** (no manufactured deny), because `feature_for` finds no local match for that branch. A
    *successful* GitHub read that resolves to a branch nothing local tracks never manufactures a
    decision either way — the decision surface stays keyed on the local document, never on whether
    the `gh` call itself succeeded or failed.
  - Together these two cases are the concrete rebuttal to "a path that reaches a permit because a
    remote read succeeded, failed, or timed out" — neither the failure nor the success of the GH read
    changed the outcome for a branch the local record does or doesn't track.

**5. Gate's own failure modes → permit or refuse?**
  - `merge-gate.py` unreadable/missing `.harness/harness.json` (`ROOT=/nonexistent`): outer
    `try/except Exception: return` in `main()` → silent **permit**, exit 0, no output. Pre-existing,
    unchanged code (outside this diff's two changed files), and it is the same class of "PreToolUse
    hooks fail open on non-exit-2" behavior already accepted project-wide (only `exit 2` blocks,
    G-01) — not new at this pin.
  - `feature_for`'s `except (OSError, json.JSONDecodeError): continue` (a corrupt/unreadable
    `feature.json`): swallows the parse error and treats that path as "no match," same as a branch
    tracked by no feature at all → falls to the existing allow branch. Pre-existing, unmodified by
    any commit in this feature's history (present since merge-gate.py's original commit, untouched
    by 1ad433b4/d80a7b12/358ac561) — not new.
  - **`merge-gate.sh`'s own root-resolution failure is fail-CLOSED, not fail-open**: if
    `harness_boundary.resolve_root` can't be resolved (including a missing/broken `python3`),
    `root` is empty and the wrapper `exit 2`s, refusing *every* Bash call, not just merges. That is
    an availability/DoS-shaped concern (a broken interpreter jams the whole session), never a permit
    bypass, and the file is byte-identical to the certified tip — not this cycle's finding to raise,
    and not new.
  - "Missing interpreter" specifically: covered by the point above — it manifests as the wrapper
    refusing everything, not as `merge-gate.py` permitting something.

**6. Token/PII/repo-identifier exposure on permit or deny paths.** Grepped `merge-gate.py` for every
`os.environ`/`print` site: the only environment read is `GH_BIN` (an operator-set binary path, not a
secret) interpolated into the "could not verify" stderr notice; the only other interpolated values
are the feature id, branch name, `build_entry` value, and `github.repo` (the project's own already-
configured repo slug) — never a token, PR body, or issue payload. No new `print`/log site exists in
this diff (file unchanged). Unchanged from cycle-1's identical finding.

**7. The two cycle-0 highs.** Not re-litigated — restated only to confirm the file that carries their
fix (`merge-gate.py`) has not moved a single byte since cycle-1 verified both closed.

**8. `test-hooks-install.py`'s 4-line comment addition.** Pure `GRADE-2 REASON` documentation above
`_run_merge_and_check`; no executable line changed (confirmed in the diff body). No security surface.

## Threat model
| boundary | STRIDE | mitigated |
|---|---|---|
| lazy `import feature_schema` reachable on non-merge Bash traffic | Elevation of privilege (import-time code running where it shouldn't) | **true** — `-X importtime` trace shows it never fires for a non-merge command |
| `import feature_schema` shadowed by an attacker-controlled module | Tampering | **true** — `sys.path.insert(0,...)` always wins; no reachable ambient shadow found |
| merge decision swayed by GH read success/failure rather than local record (DEC-138) | Tampering | **true** — both a GH failure and a GH success were forced against a local record and neither overrode it |
| gate's own failure modes (missing harness.json, corrupt feature.json) resolving to permit | Tampering | false in the sense that they DO permit, but this is the pre-existing, signed D-07/DEC-138 posture, unchanged by this diff — not a new gap |
| `merge-gate.sh` root-resolution failure | Denial of service | **true** (fails closed, blocks everything — availability concern, not a bypass) |
| token/identifier leakage on permit or deny stderr/stdout | Information disclosure | **true** — only `GH_BIN` (non-secret), feature id, branch, repo slug ever interpolated |

## Assessed and dismissed (not findings)
- Two cycle-0 highs: settled, confirmed closed at d80a7b12, file unmoved since — not re-raised.
- `UnicodeDecodeError`/`local_branch()`-crash gaps from cycle-1: unchanged, still non-escalating
  (P-02), not re-raised.
- `merge-gate.sh` fail-closed-on-broken-interpreter: an availability tradeoff, not a security gap;
  out of this role's gating scope.
- Filesystem-wide `feature_schema.py` hits under other reviewers' `/tmp` scratch dirs: none on
  `sys.path`, no reachable shadow.

## Process note (non-gating)
To reconstruct the DEC-138 adversarial scenarios without disk fixtures (blocked by
`bash-write-guard.sh`, verified live — same restriction cycle-1 hit), I wrote one throwaway probe
script to `/tmp/harness_c2_security_probe.py` via the Write tool and could not `rm` it afterward
(bash-write-guard blocks `rm` for this role too). It is outside the repo/worktree, untracked, and
carries no repo content — flagging for transparency, not as a security finding.

## open_questions
None blocking.
