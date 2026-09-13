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

Read `<HARNESS_FEATURE_TREE_ROOT>/.harness/harness/features/<FEAT>/BRIEF.md` and the plan's decisions — `plan.yaml`'s `decisions:` list,
or `PLAN.md ## Decisions` for a feature still on the pre-DEC-182 format — then the diff. Ask four
questions:

1. Does every change serve a documented `SC-NN` or `D-NN`?
2. Is anything here that **no** criterion asked for? *(scope creep — a finding even when it is an
   improvement)*
3. Is any criterion or decision **missing** a corresponding change? *(omission)*
4. Do the details match the specific values and constraints that were decided — not just the intent?

Also verify any `SC-NN` marked `verify: inspection`. **This is where those are checked**, and each needs
a `file:line` citation.

Report per violation: the path, the `SC`/`D` it relates to, and which of the three kinds it is.

## Stage 2 — code quality

Only after Stage 1. Judge against the conventions **already in this codebase**, not an abstract ideal.

Look for: correctness bugs · unhandled errors · **silent failure paths** · missing input validation ·
dropped async rejections · boundary and off-by-one conditions · resource leaks · dead code left behind ·
copy-paste divergence · comments that no longer match the code.

**Fail-open is the highest-value pattern to hunt.** Measured in this project's history: a dangling
reference that resolved to "valid" instead of blocking, a filter that returned a fabricated result on a
partial match. Both passed their test suites. Ask of every branch: *when this lookup misses, does it
block or does it sail through?*

Do **not** report what a linter catches, and do not restyle to personal preference.

### Absence, subject and mutant (DEC-169, issue #979)

The one canonical copy; `harness-verification-rules` and `harness-review` point here. Evidence is
DEC-169.

- **Every absence assertion has a presence assertion beside it** — `sed -d` satisfies an
  absence-grep completely.
- **Every new or changed assertion answers two questions, or it is a finding:** what subject does
  it actually bind (the literal thing it reads or executes, not what it is near or named after),
  and what concrete change to that subject reddens it. No answer to the second means decoration
  that reads like proof.
- **A criterion that claims to exclude a specific wrong implementation names the mutant, and you
  flip it** — swap the operator or threshold and confirm the named test reddens. Ask this of every
  new assertion, not only the risky-looking ones; it is the question in this class with the most
  teeth.
- **A fixture says what it was captured from** (depth, shape, mode), and **a claim about host
  behaviour names the mode it was measured under**; never accept one mode as covering another.

### Grade changed Python

Run the grader against the pinned review, never `HEAD`:

```sh
python3 <HARNESS_CONTROL_PLANE_ROOT>/.claude/skills/harness/bin/code-grade.py \
  --base "$(git merge-base origin/main "$review_sha")" \
  --head "$review_sha"
```

Every record the tool marks `SEVERITY: high` — below its bar and not grade 2, whatever its grade —
is a **high** finding naming file, line, qualified name, the three numbers and the driver metric,
reported as `code_grade: fail`. Every gated grade-2 function is a **med** finding with a written
answer to each `REASON REQUIRED` line, reported as `code_grade: grade_2`; grade 2 never blocks. A
record with no `SEVERITY:` line is not a finding.

**The enum is an audit claim, not evidence of itself.** `validate-digest.py` recomputes
`code_grade` over `merge-base(<default branch>, review_sha)..review_sha` — a range your `reviewed:`
field cannot change — and refuses a digest that disagrees, naming the value it expected; a checkout
it cannot grade refuses by name with its repair, never falling back to your base. You still run the
grader to cite records and reason about grade 2; you no longer decide the value. `n_a` means no
changed Python path in that range and nothing else — a range whose only Python change is a
deletion is `pass`.

The mechanical result is not the review. A clean grade decides nothing on its own: `must_fix`,
severity and the review policy remain yours, and they still fail a mechanically clean change.
Raise a `must_fix` when judgement finds broken behaviour even if every grade improved.

## Findings need failure scenarios — and a kind

Every finding states **specific inputs or state → specific wrong outcome.**

> `filter.ts:31` — if the author-list fetch rejects, the handler swallows it and renders an empty
> control, so a network blip is indistinguishable from "this document has no authors."

"This could be fragile" is not a finding. If you cannot say how it breaks, drop it. **Rank what you
report** — an unread list gates nothing.

**Every finding carries `kind`** (DEC-228; `validate-digest.py` refuses a finding without one, and
`substantive` is a violation, not a synonym): `substance` would change shipped code and re-gates
only the tasks it names; `form` is document, digest or record shape, fixed in the same run and never
re-gating; `proportionality` says the plan exceeds what the change needs and routes to a mission
downgrade, never another panel cycle. The `findings:` shape is in your agent file's output block.
When you genuinely cannot classify one, return one `open_questions` entry with your recommendation
rather than defaulting to `substance` — the heavier route is not the safe one (DEC-230).

## What gates, and what does not

| Severity | Meaning |
|---|---|
| `critical` | data loss, security hole, or certain breakage |
| `high` | wrong behaviour in a realistic case |
| `med` | wrong behaviour in an unlikely case, or real maintainability cost |
| `low` / `info` | worth knowing, not worth blocking |

- `must_fix` non-empty **or** `severity_max >= high` → **`FAIL`**
- otherwise → **`PASS` with notes** — logged and surfaced, does not block

**Style and opinion never gate** — one permanent nit would otherwise loop to `max_cycles` and
nothing ships. **Neither does a `form` finding.** Only `substance` earns `must_fix` or a severity at
or above `high`; a `proportionality` finding is a route, not a gate. **You are read-only**: report
the small one too, never fix it.

## Review a pinned SHA

Diff `base..review_sha` from `<HARNESS_FEATURE_TREE_ROOT>/.harness/harness/features/<FEAT>/review_sha` — **never `..HEAD`**. A commit landing
mid-review must not change what you reviewed. `[harness:human]` commits since the last pin are hand
edits that **inherit no earlier review**; their paths are in scope now.

## Before there is a SHA: plan-phase review

While `approval.status` is pending and `feature.json` has no `review_sha`, the target is the plan
(DEC-207): grade `BRIEF.md` and `plan.yaml` as the specification — never a diff — and write

```yaml
reviewed: plan:<path-to-plan.yaml>
code_grade: n_a
```

`validate-digest.py` accepts this form only under those preconditions. Findings enter the one
batched signature review (DEC-176), never a separate pre-signature fix dispatch.
