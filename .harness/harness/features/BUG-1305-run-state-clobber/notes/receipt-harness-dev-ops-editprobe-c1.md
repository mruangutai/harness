# Receipt — harness-dev-ops — editprobe-c1 — BUG-1305 F-04

**BLUF: F-04 is DORMANT on this host, decided by M1.** This host's real `Edit` tool cannot
create a file that does not already exist (`edit_creates_reachable: no`) — it refuses at the
tool boundary before any hook ever sees the call, so the vulnerable guard branch the panel
found is unreachable in practice. Separately, M2 proves the panel's reading of the **pinned**
guard (`dc0e0313`) was correct — that guard really did let an Edit-creates payload through —
but the **current working-copy HEAD** (`2728aa2`, a descendant of `dc0e0313`) already carries a
fix that closes it. Both facts hold at once and neither alone is the full picture.

## M1 — host property: can `Edit` create a nonexistent file?

Fixture: `mkdir -p "$TMPDIR/bug1305-m1"` → resolved
`/private/var/folders/y3/nd_jssrd5dq8lbds73f0fy5m0000gn/T/bug1305-m1`.

Attempt 1 (creating shape, `old_string: ""` equivalent — this host's Edit tool takes a
hashline patch, not old_string/new_string; the creating-insert shape is `PUT <1:`):
```
edit(path=".../bug1305-m1/absent.json#0000", input="PUT <1:\n+{\"hello\":\"world\"}\n")
→ error: File not found: /private/.../bug1305-m1/absent.json. Use the write tool to create new files.
```
The rejection fires on existence, before any tag/shape check — no second shape was needed;
the error text names the reason directly. No second attempt was warranted.

CONTROL (same tool, same invocation shape, existing file — proves the shape itself is valid
and the prior rejection was existence-gated, not shape-rejected):
```
$ printf 'alpha\n' > .../bug1305-m1/present.txt
read(".../bug1305-m1/present.txt") → tag #BCB8, content "alpha"
edit(path=".../bug1305-m1/present.txt#BCB8", input="PUT <1:\n+beta\n")
→ success: [.../present.txt#22C6]
   1:beta
   2:alpha
```

```
edit_creates_reachable: no
```

## M2 — guard behaviour under an Edit-creates payload, pinned tree (`dc0e0313`)

Synthetic project root: `$TMPDIR/bug1305-m2/proj`, with pinned
`.claude/skills/harness/bin/{check-domain.sh,harness_boundary.py,harness_yaml.py,run_identity.py}`
materialised via `git show dc0e0313:<path>` and a minimal `.harness/team-config.yaml`, laid out
at the same 4-levels-up depth `root_from_script` expects.

Absent-target attempt (non-empty, realistic `old_string`, so the empty-string case can't be
blamed for the result):
```
$ PAYLOAD='{"hook_event_name":"PreToolUse","tool_name":"Edit","tool_input":{"file_path":".harness/feat1/features/BUG-9999/runs/run1/.run-identity.json","old_string":"placeholder","new_string":"{\"run_uid\":\"FORGED\"}"}}'
$ (cd "$PROJ" && echo "$PAYLOAD" | HARNESS_PROJECT_DIR="$PROJ" bash "$PROJ/.claude/skills/harness/bin/check-domain.sh")
→ (no output)
EXIT=0
```

CONTROL (same shape, witness file pre-exists with real content, `old_string` matches it):
```
$ printf '{"run_uid":"REAL-UID-1"}' > "$PROJ/.harness/feat1/features/BUG-9999/runs/run1/.run-identity.json"
$ PAYLOAD='{...,"tool_input":{"file_path":"...\/.run-identity.json","old_string":"REAL-UID-1","new_string":"FORGED-UID"}}'
$ (cd "$PROJ" && echo "$PAYLOAD" | HARNESS_PROJECT_DIR="$PROJ" bash "$PROJ/.claude/skills/harness/bin/check-domain.sh")
→ check-domain: BLOCKED — .../.run-identity.json: this path is the run's write-once identity
  witness, recorded at the run's first landed checkpoint. ...
EXIT=2
```

```
guard_refuses_edit_create: no   (pinned tree dc0e0313; exit 0 absent vs exit 2 present)
```

### Working-copy vs pinned tree — the eng-lead's caveat, resolved

```
$ git -C <worktree> status --porcelain
 M .harness/harness/features/BUG-1305-run-state-clobber/feature.json
 M .harness/harness/features/BUG-1305-run-state-clobber/observations/harness-pm.md
?? .harness/harness/features/BUG-1305-run-state-clobber/notes/research-BUG-1305-goalcheck-build-c1.md
?? .harness/harness/features/BUG-1305-run-state-clobber/notes/review-harness-code-reviewer-c1.md
?? .harness/harness/features/BUG-1305-run-state-clobber/notes/review-harness-qa-c1.md
?? .harness/harness/features/BUG-1305-run-state-clobber/notes/review-harness-security-reviewer-c1.md
?? .harness/harness/features/BUG-1305-run-state-clobber/notes/review-harness-ui-reviewer-c1.md
(check-domain.sh itself: clean — not modified by this measurement)
$ git -C <worktree> rev-parse HEAD
2728aa2072b2e51ef18113720c94bcd59d9160ee
$ git -C <worktree> merge-base --is-ancestor dc0e0313 HEAD; echo $?
0   (dc0e0313 IS an ancestor of HEAD — HEAD has advanced past the pin)
$ git -C <worktree> diff dc0e0313 -- .claude/skills/harness/bin/check-domain.sh | head -80
  @@ -2036,13 +2036,15 @@ ...
  -    # PRE. Write supplies complete content. Edit is reconstructed only for the protected
  -    # artifact identities whose contracts must reject an invalid candidate before mutation:
  -    # run digests, run state, and handoff notes.
  +    # PRE. The identity witness is denied by path alone: an Edit must not bypass the
  +    # write-once rule merely because its target is absent or its old_string is ambiguous.
  +    ...
       if (_tool == "Edit" and target
  +            and RE_RUN_IDENTITY.match(_norm(target))):
  +        targets = [(_norm(target), "", _show(target), _claimed_abs(target))]
  +    elif (_tool == "Edit" and target
               and (RE_RUN_DIGEST.match(_norm(target))
                    or RE_STATE_YAML.match(_norm(target))
  -                 or RE_RUN_IDENTITY.match(_norm(target))
                    or RE_HANDOFF.match(_norm(target)))):
```
The eng-lead's read was correct: HEAD already special-cases `RE_RUN_IDENTITY` by path alone,
ahead of the `_edit_reconstructed_content` branch. Re-ran the SAME absent-target payload against
a fixture built from the CURRENT (`HEAD`) copies of the four scripts instead of the pinned ones:
```
EXIT=2, stderr: check-domain: BLOCKED — ...this path is the run's write-once identity witness...
```
So: **pinned tree (`dc0e0313`) is vulnerable; current tree (`HEAD`) is already fixed.** The
fix landed as a real commit between the pin and HEAD, not as an uncommitted edit — `git status
--porcelain` above shows `check-domain.sh` untouched.

## M3 — blast radius: SKIPPED

M1 returned `edit_creates_reachable: no`. Per the assignment's own branch: M3 is skipped
because Edit-creates is unreachable on this host, so it has no blast radius to measure —
inventing a scenario for an unreachable route was avoided.

```
edit_created_witness_detected: n/a
```

## Cleanup

```
$ rm -rf "$TMPDIR/bug1305-m1" "$TMPDIR/bug1305-m2"
```
Confirmed removed (directory listing after cleanup shows no `bug1305-m1`/`bug1305-m2` entries;
other agents' unrelated `bug1305-*`/`qa-bug1305-*` fixtures under `$TMPDIR` are pre-existing and
not touched).

## Open questions

- { id: Q1, question: "F-04 was found against the pinned review sha (dc0e0313); the fix already
  present at HEAD (2728aa2) means the finding is stale for the CURRENT tree even though it was
  real for the pin. Should the Advisor ruling record F-04 as 'fixed between pin and HEAD, host
  precondition also absent' rather than reopening a guard change against HEAD?", blocking: true }
- { id: Q2, question: "This measurement used this one host/session's Edit tool. If a different
  host or tool version ever permits Edit-creates, the pinned-tree guard hole would have been
  live there — worth a portable regression test on `check-domain.sh` for the Edit-creates path
  independent of any single host's Edit semantics?", blocking: false }
