# Measuring your own context — the self-id procedure (DEC-198, DEC-201)

Read this when the loop's step 5 sends you here. The rule is in the playbook; this file is only the
mechanism. `context-watch.py` is read-only and decides nothing — the threshold advises and never
refuses, so a check you cannot complete is one you skip.

The mechanism runs in about a second (DEC-201).

## It MUST be two separate Bash calls

A single call that greps for a nonce it emitted in the same command finds nothing, because the
message carrying it is not in the sidecar yet.

```sh
# first Bash call, on its own. INVENT the 8 characters NOW — do not copy them from here,
# and never reuse a nonce another orchestrator may also have used.
echo self-id ORCH-SELF-<8 random characters you invent, e.g. by mashing the keyboard>

# second Bash call, LATER — the SAME nonce you just invented, retyped
grep -l '"agentType":"harness-orchestrator"' ~/.claude/projects/*/*/subagents/*.meta.json 2>/dev/null \
  | sed 's/\.meta\.json$/.jsonl/' | xargs grep -l ORCH-SELF-<the same 8 characters> 2>/dev/null

# then
python3 .agents/skills/harness/bin/context-watch.py <the id>
```

## Four ways to get this wrong

- **The two calls must be separate**, for the reason above.

- **The nonce must be a fixed literal you can retype**, not one generated in the shell — the second
  call needs the same characters and cannot recover a shell-generated value. **But you must INVENT
  it, not copy one.** `<8 random characters>` above is a blank to fill, not a value: a nonce copied
  from this page is shared by every orchestrator that copied it, so the grep returns two-or-more,
  the check is SKIPPED, and it is skipped silently for everyone forever. Copying the example
  verbatim IS the failure mode, and it has been measured happening.

- **The match count decides what happens next, and all three outcomes are written out here.**
  **Exactly one match** — your agent id is that filename with the `agent-` prefix and the `.jsonl`
  suffix removed. Proceed with that id. **Zero matches** — the nonce has not flushed yet, or the
  sidecar layout has changed. **Two or more matches** — the nonce was not unique. This is
  reproduced, not hypothetical. For zero and for two-or-more the outcome is identical: **SKIP the
  context check for this wake**, say so in one line, and continue the loop. **Never guess an id**,
  and **never treat a skipped check as a passed one** — do not report a headroom figure at all when
  the check was skipped. Skipping is legal because the threshold only advises (DEC-198); reporting a
  headroom figure read off the wrong transcript is not.

- **Never narrow the glob by your cwd.** The transcript directory is named for the SESSION's cwd,
  not yours, so a worktree cwd resolves to a directory that does not exist.
