# UAT — BUG-1309 mirror build entry — SC-10

**You are judging one thing: when the harness refuses your merge, does the message tell you what to
do next, and does the command it names actually exist and actually clear the state it complains
about?** Eight steps, about ten minutes. Everything runs against a throwaway directory under
`/tmp`.

**The failure this exists to prevent.** FEAT-55 was planned, approved, built, reviewed and merged
with GitHub sync on, and never opened its mirror. Ship exited 0 through a skip. Nothing said so.
The only remaining evidence was a leftover worktree you had to reason about by hand.

**Safety.** No step touches GitHub, your project board, any real feature directory, or any branch.
The GitHub calls go to a fake `gh` script inside the scratch directory. Nothing here can move
`HEAD`. Step 8 deletes the scratch directory.

**What this cannot test, and why.** A live `gh pr merge` against real GitHub is not exercised —
doing so would mutate the real board, which is out of bounds for this test. That gap is already
recorded in `BRIEF.md` under `## Verification gaps`.

## Before you start

Set one variable to the checkout whose gate you are testing, and paste it into every step:

```bash
export UAT_CHECKOUT=/Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-1309-mirror-build-entry
export UAT_ROOT=/tmp/bug1309-uat
export UAT_FEAT=$UAT_ROOT/.harness/harness/features/FEAT-9001-uat-scratch
```

---

## Step 1 — Save the fixture builder

Save the block below to `/tmp/bug1309-uat-fixture.py`. Use any editor, or ask your session to write
that exact path.

```python
#!/usr/bin/env python3
"""BUG-1309 UAT fixture builder — creates a THROWAWAY harness root under /tmp.
Touches no repository and no GitHub state.
  python3 /tmp/bug1309-uat-fixture.py <checkout> <recovery-required|absent|merged> [--unpinned]
"""
import json, os, shutil, stat, subprocess, sys

CHECKOUT = os.path.abspath(sys.argv[1])
CASE = sys.argv[2] if len(sys.argv) > 2 else "recovery-required"
UNPINNED = "--unpinned" in sys.argv
ROOT = "/tmp/bug1309-uat"
FEATURE = "FEAT-9001-uat-scratch"

FAKE_GH = """#!/bin/bash
echo "$*" >> "$FAKE_LOG"
case "$*" in
  *"sub_issues -F sub_issue_id="*) echo '{}'; exit 0 ;;
  *"--jq .id"*) echo 90001; exit 0 ;;
esac
case "$1 $2" in
  "auth status") exit 0 ;;
  "api -X")
    case "$*" in
      *milestones\\ -f*) echo '{"number": 7}' ;;
      *) echo '{}' ;;
    esac ;;
  "issue create")
    n=$(( $(grep -c "issue create" "$FAKE_LOG") + 40 ))
    echo "https://github.com/acme/uat-scratch/issues/$n" ;;
esac
exit 0
"""

if os.path.isdir(ROOT):
    shutil.rmtree(ROOT)
feat_dir = os.path.join(ROOT, ".harness", "harness", "features", FEATURE)
os.makedirs(feat_dir)

with open(os.path.join(ROOT, ".harness", "team-config.yaml"), "w") as f:
    f.write("agents: {}\n")
github = {"sync": True, "board": None}
if not UNPINNED:
    github["repo"] = "acme/uat-scratch"
with open(os.path.join(ROOT, ".harness", "harness.json"), "w") as f:
    json.dump({"github": github}, f)

document = {"feature_id": FEATURE, "branch": "feature/uat-scratch", "github": {}}
if CASE == "recovery-required":
    document["github"]["build_entry"] = "recovery-required"
with open(os.path.join(feat_dir, "feature.json"), "w") as f:
    json.dump(document, f)

# "merged" is the FEAT-55 shape: the work is finished, so the safe remedy is
# recover-terminal, never a bare open that would invent historical task issues.
station = "done" if CASE == "merged" else "building"
task = {"id": "T-01", "title": "scratch task", "change_type": "bugfix",
        "execution_mode": "main-session-direct", "files": ["scratch"],
        "verify": "true", "intent": "scratch"}
with open(os.path.join(feat_dir, "plan.yaml"), "w") as f:
    f.write(f"schema: plan/1\nfeature: {FEATURE}\nstatus: {station}\ntasks:\n"
            f"  - {json.dumps(task)}\n")
with open(os.path.join(feat_dir, "BRIEF.md"), "w") as f:
    f.write(f"# BRIEF — {FEATURE} — scratch UAT fixture\n\n## Problem\nnone\n\n"
            "## Goal\nnone\n\n## Requirements\n- REQ-01: none.\n\n"
            "## Success Criteria\n- SC-01: none. verify: automated\n\n## Approval\n"
            "status: approved\n")

gh_path = os.path.join(ROOT, "gh")
with open(gh_path, "w") as f:
    f.write(FAKE_GH)
os.chmod(gh_path, os.stat(gh_path).st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)

for cmd in (["git", "init", "-q", "-b", "feature/uat-scratch"],
            ["git", "config", "user.email", "uat@example.invalid"],
            ["git", "config", "user.name", "UAT"],
            ["git", "commit", "--allow-empty", "-qm", "scratch"]):
    subprocess.run(cmd, cwd=ROOT, check=True, capture_output=True)

print(f"scratch root : {ROOT}")
print(f"feature dir  : {feat_dir}")
print(f"case         : {CASE}{' unpinned' if UNPINNED else ''}")
print("recorded github.build_entry: "
      + repr((document.get('github') or {}).get('build_entry', '<ABSENT>')))
```

**Observe:** the file exists.

```bash
python3 -c "print(open('/tmp/bug1309-uat-fixture.py').read().count(chr(10)), 'lines')"
```

- **PASS** if it prints a line count near 80.
- **FAIL** if the file is missing or empty.

---

## Step 2 — Confirm the gate is actually wired into your session

If this entry is missing, no refusal can ever reach you, and the rest of this test would be
measuring a script nobody calls.

```bash
grep -n "merge-gate.sh" $UAT_CHECKOUT/.claude/settings.json
```

**Observe:** one line naming `merge-gate.sh` as a hook command.

- **PASS** if a line is printed.
- **FAIL** if nothing is printed.

---

## Step 3 — Your normal merge command, refused

```bash
python3 /tmp/bug1309-uat-fixture.py $UAT_CHECKOUT recovery-required

printf '{"tool_input":{"command":"git merge feature/uat-scratch"}}' \
  | HARNESS_PROJECT_DIR=$UAT_ROOT bash $UAT_CHECKOUT/.claude/skills/harness/bin/merge-gate.sh
```

**Observe:** a JSON line with `"permissionDecision": "deny"` and a reason reading roughly:

> merge-gate: FEAT-9001-uat-scratch records github.build_entry=recovery-required, so no Build entry
> receipt exists for it. This merge is denied until `python3
> .claude/skills/harness/bin/gh-sync.py open /tmp/bug1309-uat/.harness/harness/features/FEAT-9001-uat-scratch`
> records one.

On macOS the path in the message reads `/private/tmp/bug1309-uat/...` — that is the same directory
as `/tmp/bug1309-uat`, resolved. Not a defect.

**This is the step you are really judging.** Read that sentence as if you had just been interrupted
mid-merge and knew nothing about this feature. Ask yourself: *which feature is at fault, what is
wrong with it, and what do I type next?*

- **PASS** if the message names the feature, says what is wrong, and gives you a command you could
  run without opening any source file.
- **FAIL** if you would have to go read code to work out what to do — or if no deny appeared at all.

---

## Step 3b — The refusal survives the flags you actually type

Nobody merges with a bare `git merge`. If the gate reads the FIRST option after `merge` as the
branch name, every one of these would find no owner and be silently allowed — a deny you can only
see when you type the command the way you really type it.

```bash
python3 /tmp/bug1309-uat-fixture.py $UAT_CHECKOUT recovery-required

printf '{"tool_input":{"command":"git merge --no-ff feature/uat-scratch"}}' \
  | HARNESS_PROJECT_DIR=$UAT_ROOT bash $UAT_CHECKOUT/.claude/skills/harness/bin/merge-gate.sh

printf '{"tool_input":{"command":"git merge --squash feature/uat-scratch"}}' \
  | HARNESS_PROJECT_DIR=$UAT_ROOT bash $UAT_CHECKOUT/.claude/skills/harness/bin/merge-gate.sh

printf '{"tool_input":{"command":"git merge -m message feature/uat-scratch"}}' \
  | HARNESS_PROJECT_DIR=$UAT_ROOT bash $UAT_CHECKOUT/.claude/skills/harness/bin/merge-gate.sh
```

**Observe:** THREE JSON lines, one per command, each carrying `"permissionDecision": "deny"` and
each naming `FEAT-9001-uat-scratch` and `github.build_entry=recovery-required` — the same message
you read in Step 3, unchanged by the flag.

- **PASS** if all three print a `deny`.
- **FAIL** if any one of them prints nothing. A silent allow here is the whole defect: the flag,
  not the branch, was read as what you were merging.

---

## Step 4 — The remedy it named is a real command

```bash
python3 $UAT_CHECKOUT/.claude/skills/harness/bin/gh-sync.py
```

**Observe:** a usage line listing the subcommands. Both `open` and `recover-terminal` appear in it.

- **PASS** if the command the Step 3 message told you to run (`open`) is in that list.
- **FAIL** if it is absent or misspelled relative to the message.

---

## Step 5 — Running the remedy clears the state

```bash
FAKE_LOG=$UAT_ROOT/calls.log GH_SYNC_GH=$UAT_ROOT/gh \
  python3 $UAT_CHECKOUT/.claude/skills/harness/bin/gh-sync.py open $UAT_FEAT

python3 -c "import json,sys; print(json.load(open(sys.argv[1]))['github'].get('build_entry'))" \
  $UAT_FEAT/feature.json
```

**Observe:** `gh-sync` reports a milestone, a parent issue and one task issue created, then the
second command prints exactly `opened`. Two notice lines about the board and about issue types are
expected and harmless — the scratch fixture configures neither. Full second-command output:

```
opened
```

- **PASS** if it prints `opened`.
- **FAIL** if it prints `recovery-required`, `None`, or an error.

---

## Step 6 — The same merge command is now allowed

```bash
printf '{"tool_input":{"command":"git merge feature/uat-scratch"}}' \
  | HARNESS_PROJECT_DIR=$UAT_ROOT bash $UAT_CHECKOUT/.claude/skills/harness/bin/merge-gate.sh
echo "exit=$?"

printf '{"tool_input":{"command":"git merge --no-ff feature/uat-scratch"}}' \
  | HARNESS_PROJECT_DIR=$UAT_ROOT bash $UAT_CHECKOUT/.claude/skills/harness/bin/merge-gate.sh
echo "exit=$?"
```

**Observe:** **no JSON at all** from either command, and `exit=0` twice. Silence is the allow, and
it must hold for the flag form too — a gate that denies `--no-ff` after the receipt is recorded
would be over-refusing.

- **PASS** if nothing is printed except the two `exit=0` lines.
- **FAIL** if a `deny` reappears on either.

---

## Step 7 — The FEAT-55 shape: a different message, a different remedy

Same absence, but the work is already finished. A bare `open` here would invent GitHub task issues
for work that is already done — which is exactly what went wrong on FEAT-55. The gate must send you
somewhere else.

```bash
python3 /tmp/bug1309-uat-fixture.py $UAT_CHECKOUT merged

printf '{"tool_input":{"command":"git merge feature/uat-scratch"}}' \
  | HARNESS_PROJECT_DIR=$UAT_ROOT bash $UAT_CHECKOUT/.claude/skills/harness/bin/merge-gate.sh

FAKE_LOG=$UAT_ROOT/calls.log GH_SYNC_GH=$UAT_ROOT/gh \
  python3 $UAT_CHECKOUT/.claude/skills/harness/bin/gh-sync.py recover-terminal $UAT_FEAT --yes

python3 -c "import json,sys; g=json.load(open(sys.argv[1]))['github']; print('build_entry =', g.get('build_entry'), '| task issues =', g.get('issues'))" \
  $UAT_FEAT/feature.json

printf '{"tool_input":{"command":"git merge feature/uat-scratch"}}' \
  | HARNESS_PROJECT_DIR=$UAT_ROOT bash $UAT_CHECKOUT/.claude/skills/harness/bin/merge-gate.sh
echo "exit=$?"
```

**Observe, in order:**
1. a `deny` naming `recover-terminal … --yes` — **not** `open`;
2. `gh-sync` creating a milestone and a parent issue, and **no task issues**;
3. `build_entry = recovered-terminal | task issues = {}`;
4. nothing, and `exit=0`.

- **PASS** if all four hold — especially that `task issues = {}` is **empty**, and that the second
  message named a different command from Step 3's.
- **FAIL** if it told you to run `open`, or if any task issue was created, or if the merge is still
  denied afterwards.

---

## Step 8 — A refusal with no remedy still tells you what to do

Some states cannot be fixed by a command; the message has to say so instead of naming a command
that would not work.

```bash
python3 /tmp/bug1309-uat-fixture.py $UAT_CHECKOUT recovery-required --unpinned

printf '{"tool_input":{"command":"git merge feature/uat-scratch"}}' \
  | HARNESS_PROJECT_DIR=$UAT_ROOT bash $UAT_CHECKOUT/.claude/skills/harness/bin/merge-gate.sh
```

**Observe:** a `deny` that says **NO COMMAND CLEARS THIS BY ITSELF**, then names the two
configuration fixes — pin `github.repo` in `harness.json`, or set `github.sync` to false — and the
`gh` command that produces the right value.

- **PASS** if the message is honest that no single command fixes it **and** still leaves you with a
  concrete next action.
- **FAIL** if it names a command that would not actually clear this state, or leaves you with
  nothing to do.

---

## Step 9 — Clean up

```bash
rm -rf /tmp/bug1309-uat /tmp/bug1309-uat-fixture.py
echo "removed"
```

- **PASS** if it prints `removed`.

---

## Your verdict

SC-10 is **met** only if Steps 3, 3b, 5, 6 and 7 all PASS — a refusal you can act on without
reading source, a refusal that survives the merge flags you actually type, and the named remedy
both existing and clearing the state. Steps 4 and 8 are supporting;
Steps 1, 2 and 9 are setup and teardown.

Record the result where the ship decision is made. If any step FAILED, quote the message you
actually saw and say what you would have needed it to tell you — the wording is the deliverable
here, and only you can judge it.
