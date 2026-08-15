# UAT — FEAT-12 SC-06 — a factory checkout of kaya-ai runs with no dangling hook

status: **ready** — for the operator to run. Nobody but the operator marks it passed.

**SC-06:** *A fresh factory checkout of `kaya-ai` at `master` executes a Bash call, a Write and a Task
spawn with no missing-hook error.* This is the criterion that proves the fleet entry ships **live**
rather than inert. It is blocking (`gates.uat: blocking_when_uat_criteria_exist`) and no runner in the
harness repository can observe another repository — that is why it is yours.

**What you are actually testing.** kaya's `.claude/settings.json` used to register **eight** harness
hooks across **four** events, every one of them pointing at a script inside
`.claude/skills/harness/bin/` — a tree that no longer exists on kaya's `master`. T-03 unwired all
eight. If any registration survived, Claude Code will try to run a script that is not there, and the
session surfaces **an error naming the missing script path**. So the failure signature per step is a
specific path appearing in an error; the pass signature is the tool call completing with no hook
error at all.

The eight, from `plan.yaml` T-03 (line 311, `intent:` enumeration at 344-352):

| Event | Matcher | Command |
|---|---|---|
| PreToolUse | Bash | `.claude/skills/harness/bin/branch-create-gate.sh` |
| PreToolUse | Bash | `.claude/skills/harness/bin/branch-create-gate.sh` (duplicate, spelled `${CLAUDE_PROJECT_DIR}`) |
| PreToolUse | Bash | `.claude/skills/harness/bin/bash-write-guard.sh` |
| PreToolUse | Write \| Edit | `.claude/skills/harness/bin/check-domain.sh` |
| PreToolUse | Task \| Agent | `.claude/skills/harness/bin/dispatch-guard.sh` |
| SubagentStart | `harness-.*` | `.claude/skills/harness/bin/inject-expertise.sh` |
| SubagentStop | `harness-.*` | `.claude/skills/harness/bin/validate-digest.py --hook` |
| PostToolUse | Write \| Edit \| Bash | `.claude/skills/harness/bin/check-domain.sh --post` |

**Four of those are what a Task spawn fires** — the PreToolUse `Task|Agent` entry, `SubagentStart`,
`SubagentStop`, and `PostToolUse` on the tools the subagent itself uses. Which is why step 4 exists,
and why **step 5 is not optional**: `SubagentStart`/`SubagentStop` are matched on `harness-.*`, and a
fresh checkout of kaya's `master` contains **no `harness-*.md` agents** (T-02 deleted the 16 untracked
ones; none were ever tracked). No Task spawn you can perform there will fire those two matchers. Skip
step 5 and two of the four Task-related registrations pass **vacuously**.

---

## Step 0 — get a fresh factory checkout

```
python3 .claude/skills/harness/bin/factory_workspace.py --repo mruangutai/kaya-ai --issue <N>
```
Run from `/Users/molchairuangutai/GitHub/harness`. Signature confirmed at `d543809`:
`--repo owner/name --issue ISSUE [--fleet FLEET]`. It clones
`https://github.com/mruangutai/kaya-ai.git` into `workspace_root`
(`/Users/molchairuangutai/GitHub/harness-factories`) and cuts `factory/issue-<N>` from
`origin/master`. Any issue number will do — the branch is scaffolding for this test, not work.

**Fresh matters.** Your existing `/Users/molchairuangutai/GitHub/kaya-ai` working tree is not the
subject: SC-06 is about what a *clone of the remote* carries. If you would rather not run the
factory tool, `git clone https://github.com/mruangutai/kaya-ai.git` into a scratch directory is an
equivalent subject.

- **Expected:** a checkout exists, on `master` or a `factory/issue-*` branch cut from it.
- **Failure:** the clone has a `.claude/skills/harness*` directory in it. That would mean T-05's
  deletion is not on the remote and SC-04 is wrong too. Stop and report — the rest of the steps
  would be testing the wrong thing.

**Then open a Claude Code session with that checkout as the project root.** Steps 1-4 are things you
do *inside that session*. Hooks only fire in a session; running the commands from a terminal proves
nothing.

## Step 1 — a Bash call

In the session, ask for something that runs one Bash command, e.g. `git status`.

- **Expected:** the command runs and returns its output. No hook error before or after it.
- **Failure looks like:** an error naming `.claude/skills/harness/bin/branch-create-gate.sh` or
  `.claude/skills/harness/bin/bash-write-guard.sh` (PreToolUse), or
  `.claude/skills/harness/bin/check-domain.sh` with `--post` (PostToolUse, fires after the Bash
  call). `branch-create-gate.sh` may appear twice — there were two registrations, spelled
  differently. Any of those paths in an error message = a surviving registration = **SC-06 not met**.

## Step 2 — a Write

Ask the session to create a throwaway file in the checkout, e.g. `scratch-uat.txt` with one line.

- **Expected:** the file is written. No hook error.
- **Failure looks like:** an error naming `.claude/skills/harness/bin/check-domain.sh` (PreToolUse on
  `Write|Edit`), or the same path with `--post` afterwards.
- Delete the file when you are done; it is not part of the evidence.

## Step 3 — an Edit

Ask the session to change one word in a file that already exists (`README.md` is fine; revert after).

- **Expected:** the edit applies, no hook error.
- **Failure looks like:** the same `check-domain.sh` paths as step 2. This step exists because
  `Write` and `Edit` share a matcher — if step 2 passed, this should too, and a disagreement between
  them is itself a finding worth reporting.

## Step 4 — a Task spawn

Ask the session to spawn a subagent for a trivial job — "use a general-purpose subagent to count the
files under `.claude/`" is enough. The job does not matter; the spawn does.

- **Expected:** the subagent spawns, does the job, and returns. No hook error at spawn, none while it
  works, none when it finishes.
- **Failure looks like:** an error naming `.claude/skills/harness/bin/dispatch-guard.sh` at the moment
  of the spawn (PreToolUse on `Task|Agent`). If the subagent's own Bash or Write calls error, the
  paths are step 1's and step 2's.
- **What this step cannot see:** `inject-expertise.sh` and `validate-digest.py --hook`. Their matcher
  is `harness-.*` and there is no such agent in this checkout. Step 5 covers them.

## Step 5 — read `settings.json` directly (covers the two matchers no spawn can reach)

From a terminal, in the fresh checkout:

```
python3 -c "
import json
t = open('.claude/settings.json').read()
d = json.loads(t)
assert 'skills/harness' not in t, 'a harness skill path survives in settings.json'
assert set(d) >= {'hooks', 'env'}, 'a top-level key was lost: %s' % sorted(d)
cmds = [h['command'] for ev in d['hooks'].values() for m in ev for h in m['hooks'] if 'command' in h]
for s in ('work-tracking-nudge.sh', 'pre-commit-tests.sh', 'pr-issue-gate.sh', 'branch-issue-gate.sh'):
    assert any(s in c for c in cmds), 'a non-harness hook was lost: ' + s
assert all('.claude/hooks/' in c for c in cmds), 'a hook outside .claude/hooks/ survives: %s' % cmds
print('ok', len(cmds), 'hooks remain')
"
```

This is T-03's own `verify:` string, verbatim (`plan.yaml` line 320) — deliberately reused rather than
reinvented, so a pass here means the same thing the build claimed.

- **Expected:** `ok 4 hooks remain`, exit 0.
- **Failure looks like:** `AssertionError: a harness skill path survives in settings.json` — that is a
  surviving `inject-expertise.sh` or `validate-digest.py --hook` (or any of the other six), and it is
  the *only* way you will see those two. Or
  `AssertionError: a non-harness hook was lost: <name>` — the unwiring over-reached and took one of
  kaya's own four hooks with it, which is a different failure and equally a not-met.

## Step 6 — clean up

Delete `scratch-uat.txt`, revert the step-3 edit, and remove the scratch checkout if you made one
outside `workspace_root`. Nothing in this script is meant to be committed to kaya.

---

## Recording the result

SC-06 is met only if **every one of steps 1-5 shows its expected observation**. A single hook error
naming a `.claude/skills/harness/bin/` path is a not-met, no matter how many other steps passed —
that path is exactly the thing this feature deleted.

Write the outcome where you sign: pass/fail per step, and for any failure the **verbatim error line**
including the path. The path is what identifies which of the eight registrations survived, and
without it the fix is guesswork.

I do not mark this passed. Neither does any agent.
