# Grilling — code risk grading — 2026-08-27

Source ticket **#910**. The full research, the measured distribution and the band table also live in
the ticket body and in its artifact link. This note is the planning input: what is SETTLED, what is
still fog, what is OUT, and the facts pm must not re-derive.

## Destination

A change cannot merge carrying a function that grades 1. The engineering squad knows the bands
before it writes code, not after review. The code reviewer reports the numbers in every review, and
a failing grade routes back to the engineering lead through the fix loop that already exists.

## Settled

- **The metrics are cyclomatic complexity, cognitive complexity and ABC.** All three, because they
  are not redundant — at the chosen bar 61 of the 120 failing production functions fail all three,
  but 23 fail on cognitive alone and 6 on ABC alone.
- **CRAP is OUT of this feature.** It is not computable here at all; see the facts below.
- **One grade per function, 1 to 5, WORST metric wins.** Not an average — an average lets a clean
  cyclomatic score hide a tangled cognitive one.
- **The band table, with ABC deliberately loosened one notch from the first draft:**

  | grade | cyclomatic | cognitive | ABC |
  | --- | --- | --- | --- |
  | 5 | ≤ 4 | ≤ 3 | ≤ 8 |
  | 4 | ≤ 8 | ≤ 9 | ≤ 20 |
  | 3 | ≤ 10 | ≤ 15 | ≤ 26 |
  | 2 | ≤ 20 | ≤ 30 | ≤ 45 |
  | 1 | > 20 | > 30 | > 45 |

- **The bar is grade 4 for production code and grade 3 for test code.** Tests are allowed to be
  more repetitive; they are not allowed to be unreadable.
- **ABC was loosened on a measurement, not a preference.** At ABC ≤ 15 it bound 79% of all
  production failures, because ABC counts every function call as a branch — so clean delegation to
  small helpers scored badly, which is the opposite of what the bar should reward. At ≤ 20 it binds
  61%.
- **The grade feeds the EXISTING severity ladder. No second vocabulary.** Grade 1 → a `high`
  finding, which the existing rule already turns into FAIL. Grade 2 → `med`, which does not gate and
  needs a written reason. Grade 3 and above → no finding.
- **A failing grade routes back to the engineering lead, and the machinery already exists.** No new
  loop is to be designed.
- **THE KNOWLEDGE GAP IS TOTAL, AND CLOSING IT IS THE POINT OF THE FEATURE.** The engineering team
  does not know these patterns today — not one of them. The five dev specialists load exactly five
  skills: `harness-handoff`, `harness-expertise`, `harness-principles`, `harness-tdd-enforcement`
  and `harness-digest-dev` (dev-ops has no digest-dev). **None mentions complexity.** Only two
  skills in the whole repository mention it at all — `harness-codebase-design` and
  `harness-simplify` — and both use it informally, about module shape rather than per-function
  metrics. **Neither is loaded by any of the five specialists**; both go to `harness-eng-lead` and
  `harness-code-reviewer` only. Verified in every agent's frontmatter at `origin/main`.

  **The consequence pm must build to:** the squad is not writing to a standard it half-knows and
  occasionally forgets. It has never been told the standard exists. So the skill is not a reminder
  or a reinforcement — it is the ONLY delivery, and if it is thin the team writes exactly as it
  writes today. **A reviewer reporting a grade the author was never taught to hit is a trap, not a
  gate.** The skill must land BEFORE the checker gates anything, and it must carry the habits that
  keep a function at grade 4 — early return over nesting, one loop per function, extract the
  condition — not just the band numbers.
- **Delivery is a SKILL, not Expertise.** Expertise is distilled cold after a run; doctrine that
  applies from day one must arrive at spawn. A skill also reaches an agent that has never worked
  here, which Expertise does not.
- **Two defects found during FEAT-37 are IN SCOPE here, by operator ruling** — both are checkers
  that report something they do not enforce:
  1. `check-plan-routes.py` validates task routes against the branch's `team-config.yaml`, not the
     config the write hook will actually consult. It printed `OK` for a route minutes before every
     write on it was denied. Measured 2026-08-27.
  2. **No script reads the `gates` block of `harness.json` at all.** `qa_gate`, `review`, `uat` and
     `merge` are honoured only by agents reading config as prose.

## Not yet specified

- **What counts as a "changed" function for gating.** A body edit is obviously in. A rename, a
  signature change, a reformat, a file move — not settled, and the answer decides how often the gate
  fires. pm sharpens this.
- **The exact ABC counting rules for Python.** Fitzpatrick's spec varies by language, and the
  measurements in the ticket use one defensible reading. The first task must PIN the rules in a test
  with fixtures before anything gates on them.
- **Whether the two folded-in checker defects are one task each or one task together.** They share a
  shape — a checker reporting what it does not enforce — but not a file.

## Out of scope

- **Coverage instrumentation and CRAP.** Its own feature, later. It would add the repository's first
  dependency manifest and rewire the test runner.
- **Fixing the 226 functions that already fail the bar.** Its own cleanup feature. NOT a ratchet:
  the operator explicitly chose a separate feature over a touch-it-fix-it rule.
- **Shell and TypeScript.** 11 shell scripts and 2 TypeScript files get nothing from this. Shell has
  no practical complexity tooling. State the limit; do not fake coverage of it.
- **Refactoring `validate-digest.py`.** It holds three of the ten worst functions and is
  enforcement-layer under DEC-174, so the squad may not touch it.

## Facts I verified (so pm does not re-derive them)

- **There is no coverage instrumentation of any kind.** `coverage.py` is not installed; there is no
  `requirements.txt`, `pyproject.toml`, `Pipfile` or `poetry.lock` anywhere; `run-unit-tests.sh` has
  no coverage invocation; CI measures nothing — checked at `origin/main` `696de63`.
- **There is no linter or complexity tool either** — no `ruff`, `pylint`, `flake8`, `eslint` or
  Sonar config exists.
- **CRAP therefore degenerates to `comp² + comp`.** And separately: at 100% coverage CRAP equals the
  complexity, so `CRAP ≤ 30` is UNREACHABLE at any coverage once cyclomatic passes 30. Ten
  production functions are already above that.
- **Measured distribution, 443 production and 903 test functions across 92 Python files** in
  `.claude/skills/harness/bin` at `origin/main`. Production medians — cyclomatic 4, cognitive 3, ABC
  7.8. p90 — 14, 22, 29.6. Max — 82, 167, 124.7.
- **Under the settled bands: production 323 pass / 120 fail (27.1%); tests 797 pass / 106 fail
  (11.7%).** Deferred cleanup is 226 functions.
- **The worst function in the repository is `validate-digest.py:530 validate`** — cognitive 167,
  cyclomatic 82. Three of the ten worst are in that one file.
- **The five dev specialists load NO skill that mentions complexity.** They load exactly
  `harness-handoff`, `harness-expertise`, `harness-principles`, `harness-tdd-enforcement` and
  `harness-digest-dev` (dev-ops has no digest-dev). Verified in each agent's frontmatter.
- **Only `harness-codebase-design` and `harness-simplify` mention complexity**, informally and about
  module shape rather than per-function metrics — and neither is loaded by any of the five
  specialists. Both go to `harness-eng-lead` and `harness-code-reviewer` only. **So there is no
  overlap to reconcile and no existing name to reuse.**
- **The fix loop already exists and needs no design.** `harness-team/SKILL.md` defines `loop_back` —
  re-dispatch the step whose `files_touched` produced the rejection, with `feed: [self]` injecting
  the failing report's path, because "without it the target repeats itself verbatim and cannot
  converge". Bounded by `max_cycles`, which then escalates or halts.
- **The review gate rule already exists**: `must_fix` non-empty OR `severity_max >= high` → FAIL,
  and `gates.review` is `advisory_unless_high`. A `high` finding gates today.
- **DEC-174 amendment 4 already settles the enforcement-layer question**, at `DECISIONS.md:5011`: "A
  module a gate imports is not itself a gate... a squad may write the library, and the cutover that
  makes a gate use it is main-session-direct." So building the tool is squad work; the cutover that
  turns its output into a `high` finding is main-session-direct, and the script joins the enumerated
  list on that day. **This is not a question for the operator.**
- The codebase is 1420 markdown, 94 Python, 45 JSON, 36 YAML, 36 HTML, 11 shell, 2 TypeScript files.

## ADDED AFTER THE ROUND, 2026-08-27 — the BRIEF owes a Definition of Done

**The operator asked for this explicitly, and it is a BRIEF requirement, not a nice-to-have.**

`BRIEF.md` must carry a section headed **Definition of Done**, written in plain English, that says
how a reader can tell **the grading itself is working correctly** — not that the code passed.

The distinction is the whole point, and this feature has already seen the failure mode it guards
against. FEAT-37 drafted an eval that graded a labelled dataset in which one agent wrote both the
grader and the labels; a failure would have meant only that those two disagreed with each other. The
operator struck it as code that does nothing. **A checker that only agrees with itself is the same
shape.** Do not build one here.

Write it for someone who has not read the plan. No metric names in the first sentence, no grade
numbers as the explanation, no jargon. Each line should be something a person could actually go and
observe. The substance to cover, at minimum:

- Given a function anyone would call simple, the tool says it is simple. Given one anyone would call
  tangled, it says so. **Both directions, because a tool that only ever agrees is not measuring.**
- Make a function worse on purpose and the grade drops. Make it better and the grade rises. The
  direction of change is the evidence, not the absolute number.
- The same code graded twice gives the same answer, on any machine, in any directory.
- When a change fails, the reviewer's finding names the function, the file, the line, the three
  numbers, and **which metric failed** — enough that the author knows what to change without
  guessing.
- A developer who has read the skill and not run the tool can predict roughly what a function will
  grade. **If they cannot, the teaching failed, whatever the tool reports.**
- The tool is never the only thing that can fail the change. A human reviewer can still say a split
  made the code worse even though every number improved.

pm owns the wording and the SC that grades it. Do not restate this list verbatim as the section.
