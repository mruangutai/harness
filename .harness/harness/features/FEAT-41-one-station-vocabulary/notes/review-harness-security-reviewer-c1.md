# Security review — FEAT-41-one-station-vocabulary — c1 (independent re-review)

**Both stages ran.** Stage one (REQ-05/SC-06/SC-07 spec compliance): the intended design is sound
and mostly implemented; one closure claim (F-03) is empirically false and one new gap defeats the
same requirement by a different route. Stage two (ordinary code-security quality): no injection,
TOCTOU, partial-write, or secrets-leak defects found in the named files.

**BLUF: FAIL, severity_max=high.** F-01 and F-02 are genuinely closed — reprobed live, not
trusted on the commit message. F-03 is **not closed**: an ordinary backslash-newline line
continuation defeats `plan-sign-gate.py` end to end, confirmed by executing the real gate
subprocess (exit 0, permits) and the real `plan-merge.py` (actually signs). F-04's case-fold and
six-pattern widening are real and correctly closed for every path-shape probe tried, including the
build's own claimed-safe realpath cases (all reproduced independently as non-reproducing). But a
**second, different, live-confirmed HIGH gap** in the same mechanism was found: a symlink or
hardlink with any basename other than `plan.yaml` bypasses `check-domain.sh`'s route denial
entirely — pre-hoc AND post-hoc — while the actual `Write` tool follows the link and corrupts the
real file's bytes. Reachable by every governed agent type via a path they are already granted.

## F-01 — CLOSED (confirmed)

`gh-sync.py:618,627-628` both `_record_station` failure prints carry `gh-sync: FAILED`;
`_commit_terminal_station` (`:649-694`) failure lines ("station committed nowhere", "station
recorded but NOT committed") carry **neither** `SKIP` nor `FAILED` — read in full, matches the
deliberate-asymmetry design stated in the docstring. `post-merge-sweep.sh` gates worktree removal
on absence of those two literals from ship's combined output. No leaked secrets in the git-command
error paths (`_git_detail`, local `status`/`commit` only, no remote/credential surface).

## F-02 — CLOSED (reprobed with fresh payloads, real subprocess)

Ran `plan-merge.py sign-approval` for real, against fresh fixtures, with two payloads not in the
build's or the prior probe's matrix:

- `--by $'Bob\napproval:\n  status: approved\n  approved_by: Eve'` (an attempt to close the
  mapping and open a sibling `approval:`/`approved_by:` key via embedded newlines) — `_field_lines`
  quotes the whole value as one double-quoted scalar; reload gives back the literal string
  containing `\n`, not a second mapping. **No injection.**
- `--by $'Line\u2028Sep'` (Unicode line separator U+2028) — round-trips byte-for-byte
  (`yaml.safe_load` gives back `'Line\u2028Sep'`, codepoints confirmed); `_verify_signature`'s
  value comparison would have caught any drift and did not need to. **No injection.**

`_field_lines` (`plan-merge.py:245`) and `_verify_signature` (`:271`) hold under this second round
of adversarial probing. No disagreement with the build's or the prior reviewer's F-02 matrices.

## F-03 — **NOT CLOSED.** Backslash-newline continuation bypass, HIGH, blocks ship.

`words()` (`plan-sign-gate.py:97`) tokenizes with `shlex.shlex(..., posix=True)`. Confirmed live:

```
python3 -c "import shlex; s='plan-merge.py \\\nsign-approval --file x.yaml'
lex=shlex.shlex(s, posix=True, punctuation_chars=True); lex.whitespace_split=True
print(list(t for t in lex))"
-> ['plan-merge.py', '\nsign-approval', '--file', 'x.yaml']
```

`shlex` treats `\` immediately before a newline as an escape of the newline itself, so the newline
survives glued onto the following token as `'\nsign-approval'` — not equal to the literal
`'sign-approval'` (`VERB`), so the adjacency test in `denies()` (`:112`, `is_tool`/`toks[j:j+1] ==
[VERB]`) never fires. Real bash does the opposite: `bash -c 'echo plan-merge.py \<newline>sign-approval'`
prints `plan-merge.py sign-approval` — bash deletes both the backslash and the newline and joins
with the surrounding single space, i.e. the **executed** command is byte-identical to the ordinary
adjacent form the gate is built to catch.

Confirmed end to end, not merely in the tokenizer:
- Real `plan-sign-gate.py` subprocess, fed the exact JSON payload Claude Code would deliver
  (`agent_type: harness-backend-dev`, `tool_input.command` containing the literal
  `plan-merge.py \<newline>sign-approval --file ... --by ... --date ...`) — **exit 0, no
  refusal.** The bare-verb form of the identical command through the same subprocess correctly
  exits 2.
- Real `plan-merge.py`, invoked through `bash -c` with the identical continuation text, against a
  disposable fixture: `SIGNED ... APPLIED`, exit 0, `approval:` block written with the requested
  signer and date. The signature actually lands.

Root cause is symmetric with F-03's own fix for `--`: the gate's tokenizer does not model this one
bash-specific joining rule, and the same class ("a habitual, non-attack shell construct forges the
signature") the build's fix commit closed for `--` reopens here for a line continuation, which is
at least as ordinary a habit for wrapping a long CLI invocation. Untested by
`test-plan-sign-gate.py` (grepped: no case names a backslash or a continuation).

**Severity: HIGH, blocks ship.** Same threat class cycle 0 rated HIGH for the `--` variant: a
forged main-session-only approval signature, reachable by any agent with ordinary Bash access.

## F-04 — case-fold CLOSED; realpath half does not reproduce; **new symlink-name-mismatch gap, HIGH, blocks ship**

**Case-fold matrix, independently reproduced:** `Plan.yaml`, `PLAN.YAML` both denied (`IGNORECASE`
on `RE_PLAN_YAML`, `check-domain.sh:1046`); `plan.yaml.bak` and `myplan.yaml` still allowed
(anchored pattern, confirmed).

**Realpath half — DOES NOT REPRODUCE**, matching the build's own claim, verified by tracing
`_norm()` (`:984`) myself rather than trusting the commit message: `_norm` computes
`os.path.relpath(os.path.abspath(path), ...)` — no `realpath`, but that is irrelevant for `./`,
`..`, a doubled slash, an absolute path, or a trailing slash, because `abspath` already collapses
all of those to the identical string `RE_PLAN_YAML` matches on the trailing `plan.yaml` segment.
Tried the same set the build's fix commit names; all still deny.

**The new gap: a differently-named link to the same file.** `RE_PLAN_YAML` matches on the literal
final path segment (`plan\.yaml$`). A symlink or hardlink pointing AT `plan.yaml` but named
something else never matches the regex, at either checkpoint:
- PRE route denial, `check-domain.sh:1466`: `RE_PLAN_YAML.match(_norm(target))` — `target` is the
  Write/Edit tool's own `file_path` argument, unresolved.
- POST route for a named file (Write/Edit/NotebookEdit that already landed), `:1509-1510`:
  `_rel = _norm(target); if not has_shape_rules(_rel): sys.exit(0)` — same unresolved path, so the
  vocabulary-legality check in `shape_problems` is never even reached.
- The filesystem-glob sweep (`SWEEP_GLOBS`, around `:1522+`) that WOULD find the real file by its
  real on-disk name only runs for **Bash** calls with no named file — a Write/Edit call always
  supplies `target`, so it always takes the POST-named-file branch above and never reaches the
  glob sweep at all.

So a Write/Edit call to a link with a mismatched basename is checked by **neither** mechanism, pre
or post — worse than the disclosed Bash residual (SC-06's "post-Bash sweep", which at least catches
an illegal vocabulary word): here even an illegal value sails through silently.

**Confirmed live, with the actual Write tool, not simulated:**
```
ln -s <target>/plan.yaml alias-link.md          # ordinary Bash; `ln` is absent from
                                                 # bash-write-guard.sh's KNOWN_DATA_FEEDERS
                                                 # (checked directly), not intercepted
Write(path=alias-link.md, content=<tampered YAML>)
```
`stat -f %i` before/after: same inode for `plan.yaml` (`184469781`) throughout. The symlink itself
is untouched (still a symlink after the write). The real `plan.yaml`'s task status field reads
`TAMPERED-VIA-SYMLINK` afterward. This is my own tool call against the same Write-tool
infrastructure a governed agent's Write call would use — not inference from POSIX semantics.

**Reachability is universal, not hypothetical**, checked against `team-config.yaml`: every squad
member (pm, frontend/backend/ai/data-engineer dev-ops, qa, all three reviewers) holds an
`upsert: true` grant on some `.harness/*/features/*/notes/<pattern>-*.md` or
`.../observations/<agent>.md` path — a sibling of `plan.yaml` one directory down. A relative
symlink from that already-granted path to `../plan.yaml`, then an ordinary Write to the agent's own
legitimately-granted filename, clears the domain check trivially (it *is* their own granted path)
and clears the shape gate (wrong basename) simultaneously. The write can carry an arbitrary
`approval:` block, defeating REQ-05's core promise — "only the main session can record a
signature" — with a route that touches neither `plan-merge.py` nor `plan-sign-gate.py` at all.

**Severity: HIGH, blocks ship.** Rated at the same bar as F-02/F-03 rather than critical, per this
review's own vocabulary (critical = remote/credential/data-breach shaped; this is an internal
governance-record forgery) — but it is the most complete of the three bypasses found: zero
detection pre- or post-hoc, by any currently-implemented gate.

## Cross-feature `set-feature-station`/`set-task-station` — assessed, NOT a new finding

Traced `cmd_set_task_station` (`plan-merge.py:719`) and `cmd_set_feature_station` (`:797`): neither
checks that `--file` names the calling agent's own feature, only that the resolved path has the
shape of *some* feature's `plan.yaml` (`_resolve_plan` → `require_destination`, tail-regex only).
A Bash call to either verb against another feature's `plan.yaml` writes a **legal** station value
with no cross-feature binding. This reproduces the same mechanism the peer reviewer (Panel2) flagged
as a new HIGH.

**Judged to be the already-disclosed, accepted residual, not a new finding.** BRIEF's own
disclosure: "a shell command that writes a *legal* station value into plan.yaml is still not
attributable to its author... it cannot catch a well-formed forgery. Closing that would need write
attribution the platform does not offer." A Bash-invoked `set-feature-station`/`set-task-station`
call is exactly this shape — a shell command, writing a legal value, through the sanctioned tool,
unattributable — and REQ-05 never promises per-feature scoping, only "no editor tool" and
"signature only by the main session." Recorded here as assessed-and-dismissed per this review's own
practice, so a later reader does not re-open it as new. Distinguished explicitly from the F-04
symlink finding above, which is genuinely outside the disclosure: it evades the Write/Edit-tool
route the disclosure does not cover, defeats even the post-hoc sweep, and can forge the
`approval:` block directly with no `plan-merge.py` involvement at all.

## Ordinary code-security sweep — clean

- No `shell=True`, no `os.system`, in any changed file across the named set; every `subprocess`
  call uses list-form argv (`gh-sync.py`, `board_lifecycle.py`, `worktree_terminal.py`,
  `check-domain.sh`'s git calls).
- `locked_update` (`harness_merge.py:126`): read-transform-write under an exclusive lock, tempfile
  + `os.replace` for atomicity — no TOCTOU between validation and write (validation happens before
  the lock, but the vocabulary it validates against, `harness.json`, is not attacker-influenced
  mid-call), no partial-write path (a raised `MergeRefusal` writes nothing; a failed tempfile write
  is cleaned up and `path` is never touched).
- No secrets, tokens, or operator-identity leakage found in log/error/commit-message paths across
  the named files.
- `check-domain.sh` exiting 0 for a no-`agent_type` payload is confirmed correct: the plan.yaml PRE
  route denial (`:1466`) has no `agent_type` branch at all — it is unconditional on tool+shape, so
  it also binds the main session, matching DEC-180's "independent of domain" claim. SC-07's
  `plan-sign-gate.py` refusal was reprobed directly by subprocess: no-`agent_type` payload exits 0;
  `agent_type` present exits 2 with a message naming both `sign-approval` literally and the
  sanctioned `plan-merge.py sign-approval` route (`REASON`, `plan-sign-gate.py:56-65`).

## Not independently re-verified

Whether Claude Code/OMP's production `Write` tool implementation follows a symlink identically to
the plain local `write` tool I used to test it. I used the actual Write-tool infrastructure of this
same runtime rather than a POSIX-semantics argument, which is the strongest evidence obtainable
under review constraints, but the production agent runtime is a separate process I cannot drive
directly.

## Reconciliation with Panel2's parallel review

Two independent security reviewers were dispatched to this cycle (dispatch collision, flagged to
Main). Panel2's F-03 and F-04-symlink findings match mine independently, from the same live
subprocess methodology, converging on identical root causes (O-08). Panel2's cross-feature
tampering finding was reconciled DOWN here to assessed-and-dismissed on a closer reading of the
BRIEF's own disclosure text — the two reviews should be treated as agreeing on three HIGH findings
(F-03, F-04-symlink, plus F-02/F-01 both closed), not four.

## Verdict

FAIL. Two HIGH must-fix items block ship: F-03 (line-continuation gate bypass) and F-04's symlink
gap (route-denial bypass via basename mismatch). Both are live-confirmed against the real binaries
in this worktree, not theoretical.
