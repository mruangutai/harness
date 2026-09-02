---
name: harness-code-review
description: Two-stage review protocol — spec compliance must pass before code quality is examined, findings need concrete failure scenarios, and only substantive issues gate. Loaded by harness-code-reviewer.
user-invocable: false
---

# Code Review Protocol

Read-only. You return findings; you never fix them.

Two stages, **in order**. Stage 1 must complete before Stage 2 begins, and the stages do not mix.

## Why this order

Wrong-thing-built-well is the costlier failure, and finding it second wastes the quality pass.

## Stage 1 — spec compliance

Read `.harness/harness/features/<FEAT>/BRIEF.md` and the plan's decisions — `plan.yaml`'s `decisions:` list,
or `PLAN.md ## Decisions` for a feature still on the pre-DEC-182 format — then the diff. Ask four
questions:

1. Does every change serve a documented `REQ-NN` or `D-NN`?
2. Is anything here that **no** requirement asked for? *(scope creep — a finding even when it is an
   improvement)*
3. Is any requirement or decision **missing** a corresponding change? *(omission)*
4. Do the details match the specific values and constraints that were decided — not just the intent?

Also verify any `SC-NN` marked `verify: inspection`. **This is where those are checked**, and each needs
a `file:line` citation.

Report per violation: the path, the `REQ`/`D` it relates to, and which of the three kinds it is.

## Stage 2 — code quality

Only after Stage 1. Judge against the conventions **already in this codebase**, not an abstract ideal.

Look for: correctness bugs · unhandled errors · **silent failure paths** · missing input validation ·
dropped async rejections · boundary and off-by-one conditions · resource leaks · dead code left behind ·
copy-paste divergence · comments that no longer match the code.

**For every absence assertion, ask what presence assertion sits beside it (DEC-169).** A verify
step that only proves the wrong words are gone passes when the right words are deleted too —
demonstrated live: SC-13's grep passed on a variant that removed two load-bearing rows.

**Fail-open is the highest-value pattern to hunt.** Measured in this project's history: a dangling
reference that resolved to "valid" instead of blocking, a filter that returned a fabricated result on a
partial match. Both passed their test suites. Ask of every branch: *when this lookup misses, does it
block or does it sail through?*

**The assertion's subject (issue #979).** Nine real instances shipped past review because each
one looked like verification and verified nothing — an assertion whose subject was not the thing
it claimed to bind: prose about a mechanism, not the mechanism; a design document, not the API; a
stub, not the collaborator; a substring, not the count. None failed loudly. All went green. For
every new or changed assertion, ask two questions and report a finding if either has no answer:

1. **What subject does this actually bind?** Not what it is near, not what it is named after —
   the literal thing the assertion reads or executes. A test named `test_omits_deleted_tool` that
   greps a sentence, not the tool list, binds the sentence.
2. **What would have to break for this to fail?** If you cannot name a concrete change to the
   subject that reddens the assertion, it is decoration that reads like proof, not proof. Naming
   a mutant and confirming it reddens is the strongest form of this answer — the weakest is a
   plausible English sentence, which is not sufficient on its own for a criterion that claims to
   exclude a specific wrong implementation.

**Fixture provenance.** A fixture standing in for a nested or externally-produced artifact (a
captured subagent transcript, a host response, a database snapshot) must say what it was captured
*from* — depth, shape, or mode — not just that it was captured. "A main-session capture" tested
green while never exercising the nested-subagent case the feature existed for; a provenance line
would have said so before the gap shipped.

**Measurement mode.** A claim about host or environment behaviour (a resolved package version, a
binary's location, a runtime flag) is only as good as the mode it was measured under. `bun run`
and `bun test` resolved three different copies of the same package in this project's own history.
State the mode next to the claim.

Do **not** report what a linter catches, and do not restyle to personal preference.

### Grade changed Python

Run the grader against the pinned review, never `HEAD`:

```sh
python3 .claude/skills/harness/bin/code-grade.py \
  --base "$(git merge-base origin/main "$review_sha")" \
  --head "$review_sha"
```

For every gated record that blocks the build — below its bar and not grade 2 — record a **high**
finding naming its file, line, qualified name, the three reported numbers, and its driver metric;
report `code_grade: fail` for it. This is not only grade 1: a grade-3 production function below the
grade-4 production bar blocks identically, and the tool marks it the same way — `SEVERITY: high` in
its report (JSON: `"severity": "high"`) and `RESULT: FAIL`. A record that passes its bar carries no
`SEVERITY:` line at all; do not report a finding for it. For every gated grade-2 function, record a
**med** finding naming the function and a written answer to every `REASON REQUIRED` line the tool
emits; grade 2 never blocks the build (`RESULT: FAIL` still prints, but the run exits clean once
reasoned) and is reported as `code_grade: grade_2`, never `fail`.

### The enum is an audit claim, not evidence of itself

**`validate-digest.py` recomputes `code_grade` independently and refuses your digest when it
disagrees.** It grades `merge-base(<default branch>, review_sha)..review_sha` — the range the
repository derives, which the `reviewed:` field you write cannot change — and compares the result
with the value you reported. You still run the grader yourself: that is how you cite blocking
records by file, line and driver metric, and how you write a reasoned answer to every
`REASON REQUIRED` line. What you no longer do is decide the value. A review that skipped the tool,
or whose run crashed, or that reported a blocking result as a clean one, is now rejected at source
rather than accepted on your word.

Three consequences worth knowing before you write the field:

- **No changed Python path in that range means `n_a`** — and nothing else does. A range whose only
  Python change is a DELETION is `pass`, not `n_a`: a Python file changed, there is simply no
  head-side function left to gate.
- **A mismatch refusal names the value the repository expected**, so the repair is to rerun the
  grader over the canonical range and report what it reports — never to guess another enum value.
- **A grading failure refuses the digest and tells you how to repair the checkout.** An unresolvable
  `origin/HEAD`, a `review_sha` that does not resolve, no merge base with the default branch, a
  range that is empty by construction because `review_sha` is already an ancestor of the default
  branch, a missing or malformed `test_kinds` policy, or committed Python that does not parse — each
  refuses, by name. None of them falls back to your `reviewed:` base, because a checkout that cannot
  derive the repository's own range cannot prove any mechanical result. Fix the checkout or the pin
  and rerun; there is nothing to write around it.

The mechanical result is not the review. A clean grade decides nothing on its own: `must_fix`,
severity and the review policy remain yours, and they still fail a mechanically clean change. The
tool informs judgement; it is never the last word. Raise a `must_fix` when review judgement finds
broken behaviour even if every grade improved, and never treat a clean grade report as a passing
review by itself.

## Findings need failure scenarios

Every finding states **specific inputs or state → specific wrong outcome.**

> `filter.ts:31` — if the author-list fetch rejects, the handler swallows it and renders an empty
> control, so a network blip is indistinguishable from "this document has no authors."

"This could be fragile" is not a finding. If you cannot say how it breaks, drop it.

## What gates, and what does not

| Severity | Meaning |
|---|---|
| `critical` | data loss, security hole, or certain breakage |
| `high` | wrong behaviour in a realistic case |
| `med` | wrong behaviour in an unlikely case, or real maintainability cost |
| `low` / `info` | worth knowing, not worth blocking |

- `must_fix` non-empty **or** `severity_max >= high` → **`FAIL`**
- otherwise → **`PASS` with notes** — logged and surfaced, does not block

**Style and opinion never gate.** This exists to prevent the trap where one permanent nit loops to
`max_cycles` and nothing ever ships.

## Review a pinned SHA

Diff `base..review_sha` from `.harness/harness/features/<FEAT>/review_sha` — **never `..HEAD`**. A commit landing
mid-review must not change what you reviewed.

Check for `[harness:human]` commits since the last pin: those are hand edits that **inherit no earlier
review**, and their paths are in scope for you now.

## Red flags

| Thought | Reality |
|---|---|
| "Quality first, I'll check the spec after" | Wrong order. Wrong-thing-built-well is the costlier failure |
| "This is ugly — must_fix" | Style never gates. `must_fix` means broken |
| "I found 30 things" | Rank them. An unread list gates nothing |
| "It probably handles that case" | Read the branch. "Probably" is how fail-open ships |
| "The tests pass, so it's correct" | Tests prove what was tested. Both measured fail-opens passed theirs |
| "I'll fix this small one myself" | You are read-only. Report it |
