# Plan fix c6 — the unpinned-repo deny now names a remedy that clears it (BUG-1309)

**Both c3 residuals are closed in plan.yaml; the merge deny's BEHAVIOUR is untouched.** Three items
amended under their existing ids through `plan-merge.py amend` (compare-and-swap on each field's
sha256): `D-09.choice`, `T-05.verify`, `T-05.intent`, `T-07.intent`. `approval.status` stays
`pending`; tasks 9, decisions 9; no new task, no new decision, no BRIEF edit. Worktree HEAD `4e8f5ea1`,
not moved.

## The remedy route — verified at source, c3's suggestion overturned

The c3 grading (R1) proposed naming `/harness-init --upgrade` as the clearing command. **It does not
pin a repo, so it cannot clear the deny either.** What I read, in the worktree at HEAD:

- `.claude/commands/` holds only `harness.md`, `harness-plan.md`, `harness-ship.md`,
  `harness-grilling.md` — `--upgrade` is a MODE of the harness-init skill, whose `## --upgrade`
  section (`.claude/skills/harness-init/SKILL.md:327-336`) runs exactly `upgrade-config.py`,
  `merge-settings.py`, `merge-gitignore.sh`.
- `upgrade-config.py` never touches `github.repo` (grep for `repo` returns only prose/docstring);
  it merges the shipped template, whose block is `"sync": false, "repo": null`
  (`.claude/skills/harness/templates/harness.json:166-169`).
- The repo is pinned only in the fresh-onboarding mirror interview, from
  `gh repo view --json nameWithOwner -q .nameWithOwner`, under the user's eyes
  (`harness-init/SKILL.md:245-248`), or by hand.
- The language that names the actually-clearing fix already exists at `check-state.sh:2351-2353`
  ("github.sync is ON but github.repo is not pinned — … Pin the repo (from `gh repo view`) or turn
  sync off"); `wayfind.py:60-61` and `board-station.py:139-140` agree.

**Conclusion encoded: no command pins `github.repo`.** The unpinned deny reason names the
configuration fix and no command at all.

## What changed, clause by clause

- **R1a — `T-05.intent` step 6** now branches on `github.repo`, applying the SAME unpinned test
  `gh-sync.py:246` applies (null, empty, or no `/`). Two verbatim reason strings: PINNED keeps
  today's `recovery_command_for` route and the spelled-out `gh-sync.py open <feature-dir>`; UNPINNED
  names pinning `github.repo` in `<root>/.harness/harness.json` (or `github.sync: false`) and
  **carries no `open` token in any form** — the same rule the step-5 era line already carries, which
  is what makes the two branches distinguishable by grep. A closing line states the deny itself is
  unchanged in both branches (D-09).
- **R1b — one paired test case.** New case `T-05 unpinned repo absent build_entry denies naming the
  configuration fix`: `FEAT-9001-fixture-non-era`, no `build_entry`, fixture root with
  `github.sync: true` and `github.repo: null`. Declared THE CONFIG PAIR with the existing
  `T-05 non-era absent build_entry denies` — the wording follows THE ERA PAIR's "one without the
  other is a rejected return". **Necessary addition I made and am flagging:** the pair only
  discriminates if every OTHER fixture root PINS `github.repo` (the drafted roots did not say so, so
  every existing deny case would have taken the unpinned branch). That requirement is now in the
  task text. Both case names are in `T-05.verify`, still a literal `|` block.
- **R1c — `D-09.choice`** gained one sentence: the state blocks BOTH halves — Build refused by T-04
  AND every harness-feature merge denied by T-05, whose self-gate keys on `github.sync` alone — and
  the remedy is the configuration fix, never `gh-sync.py open`. `D-09.because` was not amended, so
  the overturnable-at-signature disclosure survives byte-identically.
- **R2 — `T-07.intent` WHY paragraph** gained one sentence: for the era corpus, settled bullet 8 is
  delivered by the PRE-EXISTING gates at `post-merge-sweep.sh:192-195` and `:206-209` (the anchors
  the task already cites), which keep the worktree and return before the new build-entry block; the
  new check is the backstop for a ship that exits cleanly printing neither line.

## Verification

```
$ python3 /Users/molchairuangutai/GitHub/harness/.claude/skills/harness/bin/check-plan-routes.py .harness/harness/features/BUG-1309-mirror-build-entry/plan.yaml
MANIFEST /Users/molchairuangutai/GitHub/harness/.harness/team-config.yaml
OK T-01 granted to harness-backend-dev, harness-dev-ops, harness-qa
OK T-02 granted to harness-backend-dev, harness-dev-ops, harness-qa
OK T-03 granted to harness-backend-dev, harness-dev-ops, harness-qa
DEVIATION T-04 .claude/skills/harness/bin/gh-sync.py, tests/integration/test-gh-sync.py granted to harness-backend-dev, harness-dev-ops, harness-qa but declared main-session-direct
OK T-05: declared main-session-direct (.claude/settings.json, .claude/skills/harness/templates/settings.snippet.json, .omp/extensions/harness-hooks.ts ungranted)
DEVIATION T-06 .claude/skills/harness/bin/check-state.sh, .claude/skills/harness/bin/feature_schema.py, tests/integration/test-check-state.py granted to harness-backend-dev, harness-dev-ops, harness-qa but declared main-session-direct
DEVIATION T-07 .claude/skills/harness/bin/post-merge-sweep.sh, tests/integration/test-post-merge-sweep.py granted to harness-backend-dev, harness-dev-ops, harness-qa but declared main-session-direct
OK T-08: declared main-session-direct (.claude/skills/harness/references/github-mirror.md, .claude/skills/harness/SKILL.md ungranted)
OK T-09 granted to harness-documentor
0 violation(s) across 1 plan(s)
EXIT=0
```

`yaml.safe_load` reloads clean: tasks 9, decisions 9, `approval.status: pending`; every `verify:` is
a literal `|` block; the unpinned reason block contains no `open` token (checked by extracting the
block and searching it).

## Reported, not changed

- **`gh-sync.py:247`** prints "github.repo is not pinned — run /harness-init --upgrade to record
  it". Per the reads above, that route **cannot** pin the repo, so the message sends the operator to
  a no-op. Pre-existing text, outside this pass's three items and outside every task's `files:` —
  T-04 does touch `gh-sync.py`, so a one-line message fix could be absorbed there if the operator
  wants it, but that is a scope decision, not mine.
- No success criterion in `BRIEF.md` contradicts either clause; SC-04's merge-refusal wording is
  about the refusal, which is unchanged.

## Open questions

None blocking. The one judgement call I made without asking: requiring every other T-05 fixture root
to pin `github.repo` (reversible, and the pair is vacuous without it).
