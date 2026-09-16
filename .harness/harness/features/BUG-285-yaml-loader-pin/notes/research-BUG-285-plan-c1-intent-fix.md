# cycle-1 patch: T-01 step f now requires the probe note to be COMMITTED

**Done, and the plan is otherwise byte-identical.** `tasks[T-01].intent` step f carries the commit
requirement; every other field of T-01, all four decisions, `approval.status: pending`, the single
task and the absent `panel:` key are unchanged. Verified by two independent parsers
(`harness_yaml.load_file` and `yaml.safe_load`, which agree) and by a field-by-field comparison of
T-01 against its pre-amend values.

## The new step f (plan.yaml:116-120, on disk)

```
f. Record both transcripts verbatim, plus the exact commands you ran, in your own notes file
   under this feature's notes/ directory, and COMMIT that note with the test change - SC-03
   is graded with "git show <review_sha>:<that path>", so an uncommitted note grades
   not_met however good the proof. Then delete the throwaway script and its tempdir.
   Nothing under tests/ or .claude/ may be left changed by the probe.
```

The tempdir/no-trace half of step f is intact. `intent:` is still a `|` literal block
(`    intent: |` present in the raw bytes) and so is `verify:`, whose value is exactly
`env -u HARNESS_AGENT_TYPE python3 tests/integration/test-gh-sync.py\n`.

**One deliberate deviation from the report's wording, recorded rather than silent:** the report
renders the command in markdown backticks. Backticks are decoration in a data value
(`harness-spec-driven`: no markdown in any value), and the existing `intent` block uses double
quotes for every literal it names — `"does not parse"`, `"doc = json.loads(text)"`. So the command
is quoted, not backticked. Substance, subject and grading procedure are the report's. `intent`
now contains zero backticks, one `COMMIT that note`, one `git show <review_sha>:<that path>`.

## The write route: `apply` cannot do this, and said so

The dispatch mandated `plan-merge.py apply`. Run with a proposal carrying the corrected `intent`,
it refused, correctly:

```
CONFLICT: id='T-01' in 'tasks' carries two different values.
EXIT=7
```

`apply` is **add-only** — exit 7 on any changed value (`plan-merge.py:1217-1218`, exit table
line 50). Its own BUG-1128 comment names the successor verb: `amend`, a compare-and-swap that
replaces ONE field of ONE named id under the same lock and the same text splice. That is the
route taken, and it is a plan verb — not an editor, not a `Write`:

```
AMENDED tasks:T-01.intent
APPLIED .../features/BUG-285-yaml-loader-pin/plan.yaml
EXIT=0
```

The `--expect-sha256` was `1f68a422…c09c48`, read from `amend --show` in the same worktree.

## What else changed: nothing

`git status --porcelain` in the worktree shows only `?? .harness/harness/features/BUG-285-yaml-loader-pin/`
— the still-untracked feature directory. No test file, no production file, no BRIEF, no decision, no
commit. `check-plan-routes.py <this plan>` → `OK T-01 granted to harness-backend-dev,
harness-dev-ops, harness-qa`, `0 violation(s) across 1 plan(s)`, exit 0.

No new line in the intent block exceeds 93 characters; the block's pre-existing widest line is 96,
so nothing about its shape moved either.

## Open question, non-blocking

`plan-merge.py`'s docstring header lists six verbs (lines 11-16) and omits `amend`, which the
BUG-1128 section 1200 lines lower adds. A dispatch or skill written from that header mandates
`apply` for a revision it cannot perform. `harness-spec-driven`'s write-route paragraph has the same
gap. Worth a harness chore; it cost one refused apply here.
