# FEAT-26 — T-07's absence-assertion is now falsifiable (run verifyfix-product)

**Repaired.** T-07's fifth verify clause asserted a stale sentence was gone with a line-oriented
`grep -q`, but the sentence wrapped across two lines — no single line ever carried the string, so
the `&& exit 1` could never fire and the clause was green whether or not the correction was made.
It is now a whole-file, whitespace-normalised check.

## The new clause

In `plan.yaml` T-07's `verify:`, the old line is replaced by two shell comments plus:

    python3 -c "import re,sys; t=re.sub(r'\s+',' ',open('.claude/skills/harness/SKILL.md').read()); sys.exit(1 if 'composes no issue-closing text into any pull request body' in t else 0)" || exit 1

Chosen over `tr -d '\n'` and `grep -z` for durability: it collapses *any* run of whitespace, so it
survives re-wrapping at a different column, re-indentation, and a tab, not just today's line break.
`\s` passes through the YAML literal block unescaped — confirmed by loading the block with
`safe_load` and running it (below).

## Red proof — the clause fails on the pre-fix wording

Reconstructed the wrapped sentence in a scratch file
(`scratchpad/prefix-wording.md`; the write guard correctly refuses any scratch path shaped like
`.claude/skills/harness/SKILL.md`, so the same logic was run against a differently-named file):

    === OLD clause vs pre-fix wording ===
    grep rc=1   (no match, so `&& exit 1` never fires: clause GREEN on the false sentence)
    === NEW clause vs pre-fix wording ===
    new clause rc=1   (RED)

## Green proof — T-07's whole verify, loaded from the plan and run verbatim

Extracted with `yaml.safe_load` and run in the worktree root:

    VERIFY-OK
    exit=0

## The other four clauses do not share the weakness

Two reasons, and the second is the general one.

- Spans: `^source_issues:` (`templates/plan.yaml:28`), `record-pr` and `source_issues` are single
  tokens and cannot wrap. `gh-sync.py closes` is two tokens and *could* be split by a future
  re-wrap (`SKILL.md:200` today).
- Direction: all four are **presence** assertions (`|| exit 1`). A wrap breaks them into a false
  RED — loud, and fixed on sight. Only an **absence** assertion turns a wrap into a false GREEN.
  The grading rule is pattern span versus matcher unit, plus which direction the failure points.

## Open questions

- Q1: `check-state.sh` reports a third violation the dispatch did not name —
  `FEAT-26 status is 'Review' but notes/handoff-build.md is missing` (DEC-159). Pre-existing: the
  status change is in the uncommitted tree and is not this run's.
- Q2: `PostToolUse check-domain.sh` resolves through `CLAUDE_PROJECT_DIR` (the main repo) and so
  validated a **worktree** `feature.json` against **main's stale** `feature-schema.json`, refusing
  `github.source_issues` as undeclared. The worktree's schema declares it
  (`bin/feature-schema.json` `properties.github`). A worktree write can be denied by a schema the
  worktree does not use.
- Q3: `plan-merge.py` is add-only (`bin/plan-merge.py:262-277`: an existing id with a different
  value is exit 7), so it cannot repair a clause inside an existing task. This edit went through
  the Edit tool. `harness-spec-driven` says to write `plan.yaml` through the merge tool — the rule
  has no route for an in-place correction.
