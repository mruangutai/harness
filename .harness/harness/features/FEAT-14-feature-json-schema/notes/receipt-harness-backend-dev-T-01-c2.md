# Receipt — harness-backend-dev — T-01 — c2 (send-back)

## The defect (as reported)

`validate-feature-json.py` line 16 spelled the literal two-word string `feature.yaml` inside its
own module docstring, inside `.claude` — the exact thing T-08's `verify:` greps for and fails on
once these untracked files are staged. Confirmed the defect was real before fixing it: the old
docstring text read `"no literal feature.yaml under .claude" check at the far end of the build.`

## The fix

Reworded the paragraph to keep the reasoning (why the sweep globs `feature.*` and never
hard-codes a filename) while dropping the literal string. New wording names the *old format*,
not the old *filename*.

**First draft caught a gap on self-review (not a separate cycle):** the first rewording read
"...old per-feature YAML execution-state format...", which still puts the tokens `feature` and
`yaml` adjacent, separated by exactly one space — `feature.yaml` as an unanchored regex matches
`.` against any single character, including a space, so that draft passed the mechanical grep
check *only* because `YAML` was capitalized and the git-grep invocation carries no `-i`. That is
passing on a flag the gate happens not to set, not on the instruction ("rephrase so the two
tokens are not adjacent at all"). Removed the adjacency outright — "per-feature" is dropped and
"YAML" is replaced with "block-scalar", so neither the literal string nor a same-case-insensitive
variant of it appears anywhere in the sentence. Final wording, as shipped:

```
With no arguments, sweeps every execution-state file on disk: globs
`.harness/features/*/feature.*` and keeps only the `.json`, `.yaml` and
`.yml` suffixes — never two literal filenames — because the corpus spans the
migration window from the old per-feature block-scalar execution-state
format to this JSON one (this schema is live before every file is
converted), and hard-coding a second filename naming the old format here
would redden a later corpus-wide sweep at the far end of the build.
```

Confirmed case-insensitively clean too (`grep -in 'feature.yaml\|feature yaml'` on the file
returns nothing), not just against T-08's literal case-sensitive pattern, since the near-miss
above was a case-sensitivity artifact and a second one should not slip through the same way.

No other line in this file, or any of the other four T-01 files, was touched. This is a
comment-only edit inside a module docstring — zero executable lines changed, so `tests_added: 0`
below reflects a scope with nothing to add a test for, not an Iron Law lapse.

## Mechanical verification (observed output, not description)

Ran T-08's own pathspec verbatim, all five roots, not just `.claude` alone:

```
git grep -c 'feature.yaml' -- .claude .github .harness/harness.json .harness/team-config.yaml docs/harness
```

Output (every hit pre-existing, none of the five T-01 files appear):

```
.claude/agents/harness-orchestrator.md:4
.claude/commands/harness.md:2
.claude/skills/harness-spec-driven/SKILL.md:2
.claude/skills/harness-team/SKILL.md:1
.claude/skills/harness/SKILL.md:12
.claude/skills/harness/bin/check-domain.sh:11
.claude/skills/harness/bin/check-plan-routes.py:6
.claude/skills/harness/bin/check-state.sh:22
.claude/skills/harness/bin/factory_claim.py:6
.claude/skills/harness/bin/factory_decompose.py:7
.claude/skills/harness/bin/gh-sync.py:9
.claude/skills/harness/bin/test-check-domain.py:7
.claude/skills/harness/bin/test-check-plan-routes.py:6
.claude/skills/harness/bin/test-check-state.py:31
.claude/skills/harness/bin/test-factory-claim.py:3
.claude/skills/harness/bin/test-factory-decompose.py:28
.claude/skills/harness/bin/test-gh-sync.py:27
.claude/skills/harness/bin/test-harness-yaml-corpus.py:4
.claude/skills/harness/bin/test-validate-digest.py:2
.claude/skills/harness/bin/validate-digest.py:1
.claude/skills/harness/templates/gitignore.snippet:1
.claude/skills/harness/templates/harness.json:1
.claude/skills/harness/templates/team-config.yaml:1
.harness/harness.json:1
.harness/team-config.yaml:1
docs/harness/BUILD.md:8
docs/harness/DECISIONS-INDEX.md:5
docs/harness/DECISIONS.md:50
docs/harness/SPEC.md:14
docs/harness/org.html:2
```

`test-harness-yaml-corpus.py` shows `4` — matches P's pinned count exactly. None of the four
T-01-owned tracked-adjacent files (`feature-schema.json`, `feature_schema.py`,
`test-validate-feature-json.py`, `run-unit-tests.sh`) appear in this list.
`docs/harness/DECISIONS*` hits (`DECISIONS-INDEX.md:5`, `DECISIONS.md:50`) are the BRIEF's other
pinned carve-out, per T-08's own `skips docs/harness/DECISIONS*` clause — not mine to touch.

`grep -n 'feature.yaml'` run directly against each of the five untracked/edited T-01 paths — **all
five return no matches**:

```
--- .claude/skills/harness/bin/feature-schema.json ---
--- .claude/skills/harness/bin/feature_schema.py ---
--- .claude/skills/harness/bin/validate-feature-json.py ---
--- .claude/skills/harness/bin/test-validate-feature-json.py ---
--- .claude/skills/harness/bin/run-unit-tests.sh ---
```

(no lines printed under any of the five headers — confirms the literal is gone from
`validate-feature-json.py`, on the final wording, and was never present in the other four).

**The receipt files themselves** (this file and the c1 receipt) intentionally quote the literal
string `feature.yaml` — required to describe the defect and paste the grep output. Confirmed this
is not a gate risk: `.harness/features/**` is not in T-08's five-path pathspec (verified by
running `git grep -c 'feature.yaml' -- .harness/features` directly — it returns many pre-existing
hits across the corpus, e.g. `.harness/features/FEAT-01/feature.yaml:1`, none of them scoped by
T-08 at all).

## Verify clause, re-run verbatim

```
.claude/skills/harness/bin/run-unit-tests.sh --kind unit
```

Ran twice this cycle: once against the first (adjacency-flawed) rewording, then discarded that
run and re-ran against the final wording after fixing the adjacency gap caught on self-review.
Only the final run is reported as the cycle's result.

**Exit 0** (`echo $?` after the run: `0`). 12/12 unit scripts PASS — `grep -c '^PASS test-'` on
the captured output returns `12`: `test-harness-yaml-corpus.py`, `test-render-brief.py`,
`test-team-catalog.py`, `test-factory-cli.py`, `test-factory-gh.py`, `test-factory-config.py`,
`test-factory-workspace.py`, `test-factory-decompose.py`, `test-factory-claim.py`,
`test-factory-land.py`, `test-no-distribution.py`, `test-validate-feature-json.py`. Total `^PASS `
count across the whole run (`grep -c '^PASS '`): **72** — unchanged from cycle 1. Within
`test-validate-feature-json.py` specifically: **41/41**, counted by isolating the block between
the previous `PASS test-*.py` marker and this one and counting `PASS ` lines inside it — same 41
checks, no test added, removed or restructured, as instructed. The docstring-only edit did not
move the gate.

## Files touched (T-01, both cycles — complete list)

- `.claude/skills/harness/bin/feature-schema.json` (new, c1)
- `.claude/skills/harness/bin/feature_schema.py` (new, c1)
- `.claude/skills/harness/bin/validate-feature-json.py` (new, c1; docstring reworded, c2 — this
  cycle's only edit)
- `.claude/skills/harness/bin/test-validate-feature-json.py` (new, c1)
- `.claude/skills/harness/bin/run-unit-tests.sh` (one-line edit, c1: `test-validate-feature-json.py`
  added to `UNIT_SCRIPTS`)
- `.harness/features/FEAT-14-feature-json-schema/notes/receipt-harness-backend-dev-T-01-c1.md` (new, c1)
- `.harness/features/FEAT-14-feature-json-schema/notes/receipt-harness-backend-dev-T-01-c2.md` (new, this cycle)

Nothing else. As in c1, `.harness/features/FEAT-14-feature-json-schema/feature.yaml` and
`STATE.md` continue to show as modified in `git status` — that is orchestrator dispatch
bookkeeping predating this run, not a T-01 edit, and no file under `.harness/features/*/` was
touched this cycle either.

## Explicitly not revisited this cycle

CLI output stream (Q2, routed up), redirection-message wording (Q1, routed up), no test
added/removed/restructured, no enforcement-layer files touched, no commit made.
