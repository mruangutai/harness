# kaya-ai measurements — taken by harness-orchestrator, 2026-08-10

All commands run in `/Users/molchairuangutai/GitHub/kaya-ai` on branch `master`. These supersede
every kaya claim in `BRIEF.md` and `plan.yaml` that contradicts them.

## M-1 — harness agent files: 0 tracked, 16 on disk untracked

```
git ls-files '.claude/agents/harness*'   ->  0
ls -1 .claude/agents                     ->  16 files, ALL matching harness-*.md, none other
git status --porcelain                   ->  includes `?? .claude/agents/` (the whole dir untracked)
```

Both of the operator's numbers are true of different things. The agent files **do exist on kaya's
disk** and deleting them is real work; but they were never committed, so the deletion produces **no
commit content** and the remote never carried them. Consequence: an agents clause belongs in the
working-tree verify, never in the remote verify, and `git rm` cannot be used on them.

## M-2 — tracked counts on master

```
git ls-files '.claude/skills/harness*'   ->  55
git ls-files '.claude/commands/harness*' ->   8
git ls-files '.harness/'                 -> 117   (KEPT)
```

## M-3 — the 63 dirty entries, decomposed

`git status --porcelain | wc -l` -> 63, made of `39 M`, `2 D`, `22 ??`.

**58 of the 63 sit under `.claude/skills/harness*`, `.claude/commands/harness*` or
`.claude/agents/`.** The 5 that do not are:

```
 M .claude/settings.json                                   (T-03's target)
 M .claude/settings.json.harness-bak                       (see M-5 — addressed by no task)
 M .harness/features/FEAT-03-live-review-loop/feature.yaml (kaya project state, KEPT)
 M pyproject.toml                                          (kaya's own work)
 M uv.lock                                                 (kaya's own work)
```

`BRIEF.md:199` states "The 16 agent files and the 21 uncommitted skill modifications are untracked
and are unaffected either way." **The second half is false.** 34 of the 39 `M` entries are TRACKED
files under `.claude/skills/harness*` or `.claude/commands/harness*`; committing their deletion
discards those local modifications permanently.

## M-4 — nothing unique is at risk in those 34 (probe run, not inferred)

For each of the 34 modified tracked harness files, compared against this repository at `365a8a9`:

- **28 are byte-identical** to this repo's working-tree copy (`cmp -s`).
- **6 differ**, and every one of them is present in this repo's object database — `git hash-object`
  on kaya's copy, then `git cat-file -e <hash>` in `/Users/molchairuangutai/GitHub/harness` returns
  success for all six:
  `.claude/commands/harness.md`, `.claude/skills/harness-handoff/SKILL.md`,
  `.claude/skills/harness-wayfinding/SKILL.md`, `.claude/skills/harness/SKILL.md`,
  `.claude/skills/harness/bin/check-state.sh`, `.claude/skills/harness/bin/check-docs.sh`.

So the drift is reproducible from this repository in full. `check-docs.sh` is additionally a file
this repo deleted under #202, so kaya's copy is a stale copy of a struck script.

The BRIEF's reason ("untracked") is wrong; this measurement is the correct reason for the same
conclusion, and it is the sentence that should replace it.

## M-5 — `.claude/settings.json.harness-bak` is TRACKED ON THE REMOTE and wires harness scripts

```
git ls-tree -r --name-only origin/master | grep settings
  .claude/settings.json
  .claude/settings.json.harness-bak
```

It is `merge-settings.py`'s backup, it is modified in the working tree, and it registers six harness
scripts. **No task, no REQ and no SC in this plan mentions it.** T-05's pathspec
(`git add -- .claude/skills .claude/commands .claude/settings.json`) does not match it, so it
survives on `master` after this feature, naming five scripts that will no longer exist.

## M-6 — `settings.json` wires SEVEN harness registrations across FIVE hook events, not three

Parsed with `json.load`. Every registration whose command points inside the deleted skill tree:

| Event | Matcher | Script |
|---|---|---|
| `PreToolUse` | `Bash` | `branch-create-gate.sh` |
| `PreToolUse` | `Bash` | `branch-create-gate.sh` **(a second, duplicate entry — different `$VAR` spelling)** |
| `PreToolUse` | `Bash` | `bash-write-guard.sh` |
| `PreToolUse` | `Write\|Edit` | `check-domain.sh` |
| `PreToolUse` | `Task\|Agent` | `dispatch-guard.sh` |
| `SubagentStart` | `harness-.*` | `inject-expertise.sh` |
| `SubagentStop` | `harness-.*` | `validate-digest.py --hook` |
| `PostToolUse` | `Write\|Edit\|Bash` | `check-domain.sh --post` |

`D-02` and `T-03` name **three** `PreToolUse` hooks. Four registrations —
`dispatch-guard.sh`, `inject-expertise.sh`, `validate-digest.py`, `check-domain.sh --post` — plus
the duplicate are outside the enumerated list.

T-03's *headline* instruction ("any hook whose command points inside the skill tree") and its verify
(`assert 'skills/harness' not in t`) both cover all eight; only the enumeration is short. A builder
following "remove exactly the hook entries whose command string references any of [three]" leaves
five registrations wired and then **fails its own verify** — a guaranteed send-back at build.

**This is what SC-06 rests on.** The blocking UAT is a factory checkout executing "a Bash call, a
Write and a **Task spawn** with no missing-hook error". A Task spawn fires
`PreToolUse:Task|Agent`, `SubagentStart` and `SubagentStop` — three of the four the enumeration
misses. The operator runs that UAT himself.

Non-harness hooks in the file are unaffected and must survive: `work-tracking-nudge.sh`,
`pre-commit-tests.sh`, `pr-issue-gate.sh`, `branch-issue-gate.sh`, all under `.claude/hooks/`.
Top-level keys are `hooks` and `env`.
