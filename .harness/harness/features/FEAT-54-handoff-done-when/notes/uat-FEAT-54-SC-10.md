# UAT — FEAT-54 handoff `## Done when` — SC-10
status: ready              # draft | ready | passed | failed — ONLY you set passed/failed
branch: feat/FEAT-54-handoff-done-when
review_sha: dd55b3570c6a20f5ca1da016d6959752bd0ffc74

**About 25 minutes**: ~10 writing the note, ~5 on the two refusals, ~2 measuring, ~5 on the
label comparison, ~3 recording. SC-10 is four SEPARATE judgments (J1–J4). Record all four.

Nothing you do here writes into the feature record. The write gate is a PreToolUse hook: it
inspects proposed bytes and never creates a file. Your note lives in `/tmp`.

## Setup — paste once

```bash
export WT=/Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-54-handoff-done-when
export UATDIR=/tmp/harness-uat-sc10
export CLAIM=$WT/.harness/harness/features/FEAT-54-handoff-done-when/notes/handoff-uat-probe.md
mkdir -p $UATDIR
gate() { python3 -c 'import json,sys;print(json.dumps({"tool_name":"Write","agent_type":"harness-orchestrator","tool_input":{"file_path":sys.argv[1],"content":open(sys.argv[2]).read()}}))' "$CLAIM" "$UATDIR/note.md" | "$WT/.claude/skills/harness/bin/check-domain.sh"; echo "exit=$?"; }
```

`$CLAIM` must stay ABSOLUTE. With a relative claimed path the gate resolves it against your
cwd, matches no governed path, and exits 0 on a note it never looked at — a silent false pass.
Step 3 is your positive control that the gate is actually engaged.

`$UATDIR` may already hold files from the run that verified these commands. They are scratch —
overwrite them freely; step 5's cleanup removes the whole directory.

## Steps

### 1 (J1 — authoring) Write one real handoff note

Read the template: `$WT/.claude/skills/harness/templates/HANDOFF.md`.

Write it for THIS situation, which is real right now: FEAT-54 is at the end of its `validate`
phase; every criterion except SC-10 is met at `dd55b35`
(`.harness/harness/features/FEAT-54-handoff-done-when/notes/research-FEAT-54-goalcheck-validate-c6.md`);
the immediate next action is to dispatch `harness-product-lead` to run this very UAT script.
Authorities that really resolve for this feature: `brief-sc:SC-10` (and `SC-01`…`SC-15`),
`plan-task:T-01.verify` … `plan-task:T-12.verify`.

Write it at `$UATDIR/note.md` — all five sections, your own words. Then:

```bash
gate
```

expect: **exit=0 and no output.** Any output names the line to fix; fix and re-run.
If you mistype an id you will see, e.g. for `brief-sc:SC-99`:
`Authority pointer 'brief-sc:SC-99' is unresolved in .../BRIEF.md: success criterion SC-99 was not found`.

**J1: did the template let you write a real note without guessing?** PASS / FAIL.

### 2 (J2a — refusal text) Blank the `Scope:` value

Edit `$UATDIR/note.md` so the Scope line is exactly `Scope:` (keep the word, delete the value).

```bash
gate
```

expect: exit=2 and
```
check-domain: BLOCKED — .harness/harness/features/FEAT-54-handoff-done-when/notes/handoff-uat-probe.md: handoff shape (DEC-159).
  ## Done when Scope: value must be non-empty; follow templates/HANDOFF.md
```

**If this exits 0, STOP — `$CLAIM` is not absolute; nothing after this is graded.**

Restore your Scope line before step 3.

### 3 (J2b — refusal text) Cite an authority outside the four legal types

Replace your `Authority:` line with a source-code location, exactly:

`Authority: .claude/skills/harness/bin/handoff_done_when.py:187`

```bash
gate
```

expect: exit=2 and
```
  Authority pointer '.claude/skills/harness/bin/handoff_done_when.py:187' is invalid; legal prefixes are plan-task:, brief-sc:, finding:, approval:; follow templates/HANDOFF.md
```

Restore your real `Authority:` line, then `gate` again to confirm exit=0.

**J2: are those two messages ACTIONABLE — did each tell you what to type next, without
opening the validator?** PASS / FAIL.

### 4 (J3 — line cost) Measure what you actually paid

```bash
wc -l < $UATDIR/note.md
sed -n '/^## Done when/,$p' $UATDIR/note.md | wc -l
```

The first is your whole note against the 60-line cap. The second is the `## Done when`
block's own cost — heading, blank line, `Scope:`, and your `Authority:` lines.

Write both numbers in the recording block.

**J3: is the section worth those lines out of 60?** PASS / FAIL.

### 5 (J4 — the `Scope:` label) Which label does the template endorse?

Put these two side by side for YOUR note:

- A — `Scope: dispatch harness-product-lead to run the SC-10 operator UAT`
- B — `Scope: FEAT-54 handoff done-when, validate phase`

The gate accepts BOTH — it checks shape, never meaning. This half is yours alone.

Now read the template's own wording:

```bash
sed -n '9p;39p' $WT/.claude/skills/harness/templates/HANDOFF.md
```

It says the section "describes the ONE immediate action in Next, not the phase or feature",
and `Scope: <concise label for the ONE action in Next>`.

Two answers, both required:
- (a) is the label YOU wrote in step 1 of A's kind — the immediate action in `## Next`?
- (b) does B — naming the phase/feature — read as WRONG against that wording, or merely as
  a different style?

**J4: (a) yes AND (b) reads as wrong → PASS. Anything else → FAIL, and say which half.**

## Cleanup

```bash
rm -rf /tmp/harness-uat-sc10
git -C $WT status --porcelain -- .harness/harness/features/FEAT-54-handoff-done-when/notes/
```

expect: no `handoff-uat-probe.md` in that output. Nothing was written there.

## Recording block — one line per judgment

```
J1  authoring a real note from the template   PASS / FAIL   result:
J2  refusal messages actionable (both)        PASS / FAIL   result:
J3  section worth its lines (of 60)           PASS / FAIL   note lines: ___  Done when lines: ___
J4  Scope: label — (a) immediate action, (b) phase/feature reads wrong
                                              PASS / FAIL   result:

SC-10 overall (all four must PASS):           PASS / FAIL
What I would change:


Run by: ______________   Date: __________
```

Any FAIL is a fix cycle, not a discussion. `status:` above is yours to set, not an agent's.
