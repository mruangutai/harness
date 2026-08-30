# UAT — FEAT-43 SC-11 (the skill changes what gets written)
status: ready              # draft | ready | passed | failed — ONLY the operator changes this
review_sha: cd8dae476607704fd3d2b874150aae9f814292d2
base_sha: 7ccfae8dd7644bc3aaea612dabf4317c0d804f99
prerequisites: green — cycle-21 panel PASS, must_fix [], severity_max med

**Verdict on the existing probe first: it does NOT discharge SC-11.** The shipped skill and the
draft the probe graded share **no non-blank line** (draft `notes/skill-draft-2026-08-27.md` 48
lines, shipped `.claude/skills/harness-code-risk-grading/SKILL.md` 288 lines at the pin; `comm -12`
over sorted unique lines returns the empty line and nothing else). The shipped skill teaches things
the draft never contained: two bars by surface (grade 4 production / grade 3 test) where the draft
taught one, five before/after worked habit sections where the draft had three prose paragraphs, plus
`## Reference`, `## Review semantics and self-check` and `## Worked examples`. The probe measured a
different teaching payload; SC-11's own text already reserved this, and the measurement confirms it
rather than contradicting it. **A second gap:** the probe's headline statistic (8.5 vs 38.0) is the
arm **mean** of the two variants' worsts, and on that statistic the gap is 29.5 against a control
spread of 38 — it does not satisfy SC-11's second half as written. On arm **maxima** — the reading
this script pins — the same table gives 10 vs 57, gap 47 > spread 38, which does. Do not re-use the
probe; run the script below.

## Setup (once)

The grader refuses any path outside a git repository (`code-grade.py:36-40`) and reads
`<root>/.harness/harness.json` to classify test vs production (`code-grade.py:48`), so the scratch
area is a throwaway git repo in `/tmp` — never the repository.

```
W=/Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-43-code-risk-grading
rm -rf /tmp/sc11-uat && mkdir -p /tmp/sc11-uat/.harness && cd /tmp/sc11-uat && git init -q .
cp "$W/.harness/harness.json" .harness/harness.json
```

Outputs (four separate paths, none in the repository): `/tmp/sc11-uat/arm_a1.py`,
`arm_a2.py`, `arm_b1.py`, `arm_b2.py`. Keep these filenames — they match no `test_kinds` detect
pattern, so all four are graded at the production bar 4 (verified: a smoke file at this path graded
`"bar": 4`). Agents writing to `/tmp` are permitted by the domain hook by design
(`check-domain.sh:825-831`).

## The task — identical for all four, paste verbatim

```
Implement `load_config(path)` in a single new Python module for a deployment tool.

`load_config` reads a JSON file at `path` and returns a settings dictionary.

Schema. Required top-level keys: `service` (str), `image` (str), `replicas` (int),
`port` (int). Optional top-level sections, each a mapping if present: `env`, `health`,
`limits`. `health`, if present, requires `path` (str) and `interval_seconds` (int).
`limits`, if present, may carry `cpu` (float) and `memory_mb` (int).

Validation rules, all nine enforced:
1. `service` is non-empty and matches `^[a-z][a-z0-9-]*$`.
2. `image` is non-empty and carries a `:` tag.
3. `replicas` is an integer in 1..50.
4. `port` is an integer in 1..65535.
5. `env` keys are uppercase identifiers and `env` values are strings.
6. `health.path` starts with `/`.
7. `health.interval_seconds` is an integer in 1..300.
8. `limits.cpu` is greater than 0 and `limits.memory_mb` is an integer greater than 0.
9. Unknown top-level keys are rejected.

Environment overrides: any variable named `DEPLOY_<KEY>` in `os.environ` overrides the
matching top-level key, coerced to that key's declared type. A value that cannot be
coerced is an error like any other.

Error reporting: collect every violation, never stop at the first. Raise `ConfigError`
whose `errors` attribute is the list of messages, ordered by the rule order above and
then by key name within a section. A missing file and malformed JSON are each one error
in the same form.

Write only the module, to <OUTPUT PATH>. No tests, no README, no CLI. Do not read or
write anything inside a git repository.
```

Substitute `<OUTPUT PATH>` per variant. The text mentions no metric, no grade, no nesting, no
function count — keep it that way in both arms.

## The two arms

**Skill arm — A1 and A2.** Two concurrent `harness-backend-dev` dispatches **from the worktree**
`$W`. The skill is already in that tree's `harness-backend-dev` `skills:` list at the pin, so it
preloads; add one line to make it explicit and reproducible:

```
Read .claude/skills/harness-code-risk-grading/SKILL.md and follow it while you write this.
Then: <THE TASK, verbatim>
```

**Control arm — B1 and B2.** Two concurrent `harness-backend-dev` dispatches **from the owner
checkout `/Users/molchairuangutai/GitHub/harness` on `main`**, where the skill file does not exist
and the agent's `skills:` list does not name it (verified: 0 matches for `harness-code-risk-grading`
in `.claude/agents/harness-backend-dev.md` on main; the file is absent at base `7ccfae8`). **This is
load-bearing** — a control dispatched from the worktree would preload the skill and the experiment
would measure nothing. Dispatch text is `<THE TASK, verbatim>` and nothing else.

The control must NOT be told: the skill's name or existence; the words complexity, cognitive,
cyclomatic, ABC, grade, band or bar; that anything is being measured, compared, or graded; that
another agent has the same task; or any advice to decompose, return early or keep functions small.

## Grading — paste one per variant

```
cd /tmp/sc11-uat
python3 "$W/.agents/skills/harness/bin/code-grade.py" --json arm_a1.py | jq '[.records[].cognitive] | max'
python3 "$W/.agents/skills/harness/bin/code-grade.py" --json arm_a2.py | jq '[.records[].cognitive] | max'
python3 "$W/.agents/skills/harness/bin/code-grade.py" --json arm_b1.py | jq '[.records[].cognitive] | max'
python3 "$W/.agents/skills/harness/bin/code-grade.py" --json arm_b2.py | jq '[.records[].cognitive] | max'
```

Cognitive complexity is `.records[].cognitive` in the `--json` object
(`code-grade.py:68-71`); the per-variant number is the **maximum** over that variant's functions.
Invocation resolved from `code-grade.py --help` and `main()` at `code-grade.py:169-193`, and smoke-run
on one throwaway file — the full suite was not re-run. If any variant reports a non-empty
`"ungraded"`, that file did not parse: record it and treat the run as inconclusive, not as a result.

## The decision — arithmetic on four numbers

Call them `a1 a2 b1 b2` (each a per-variant maximum).

```
worst_A = max(a1, a2)        worst_B = max(b1, b2)
spread_A = |a1 - a2|         spread_B = |b1 - b2|
gap = worst_B - worst_A
```

**SC-11 is met when BOTH hold:** `worst_A < worst_B` **and** `gap > max(spread_A, spread_B)`.
Either one failing is `not_met`. Record all four raw numbers whatever the outcome.

|Outcome|Meaning|What the operator does|
|---|---|---|
|both hold|the shipped skill changes the code|record `passed`|
|`worst_A < worst_B` but `gap <= max(spread_A, spread_B)`|**null** — the arms are indistinguishable from noise|record `failed`. SC-11 is `not_met`. **A finding against the skill, not the developer:** the teaching is not strong enough to show. Do not re-run for a better draw and do not re-run with a different task; raise it as feature work on the skill|
|`worst_A >= worst_B`|**reversed** — the control wrote cleaner code|record `failed`, and treat it as evidence the skill may be actively unhelpful. Raise it against the skill|

Nothing here is a reason to change the tool, and no result changes any other SC.

## Recording

Fill these in and set `status:` at the top of this file. That is the whole record; do not edit
`BRIEF.md`.

- U-01 (SC-11): a1 = ____  a2 = ____  b1 = ____  b2 = ____
  worst_A = ____  worst_B = ____  spread_A = ____  spread_B = ____  gap = ____
  both conditions hold? ____
  result:

Then tell the main session the verdict; `harness-pm` records SC-11 `met`/`not_met` in the goal-check
with this file as the evidence pointer. The UAT was **not** executed here and SC-11 is **not**
judged.

## Open question — SETTLED before the run

The BRIEF's own probe citation reports arm means (8.5 / 38.0). This script pins arm **maxima**,
because SC-11's first half says "the worst cognitive complexity in the arm".

**Ruled by the operator on 2026-08-29, before any number was drawn:
`answers/Q9-sc11-maxima-and-t01-no-exemption.md` — MAXIMA. The arithmetic above is the ruled method,
not a proposal. Nothing here changes after the run.**

## Tree state

`git -C <worktree> status --porcelain`:

```
?? .harness/harness/features/FEAT-43-code-risk-grading/notes/uat-sc11-c21.md
```
