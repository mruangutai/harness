---
name: harness-code-review
description: Two-stage review protocol — spec compliance must pass before code quality is examined, findings need concrete failure scenarios, and only substantive issues gate. Loaded by harness-code-reviewer.
user-invocable: false
---

# Code Review Protocol

Read-only. You return findings; you never fix them.

Two stages, **in order** (wrong-thing-built-well is the costlier failure, and finding it second
wastes the quality pass). Stage 1 must complete before Stage 2 begins, and the stages do not mix.

## Stage 1 — spec compliance

Read `<HARNESS_FEATURE_TREE_ROOT>/.harness/harness/features/<FEAT>/BRIEF.md` and the plan's
decisions — `plan.yaml`'s `decisions:` list (legacy features: `PLAN.md ## Decisions`) — then the
diff. Ask four questions:

1. Does every change serve a documented `SC-NN` or `D-NN`?
2. Is anything here that **no** criterion asked for? *(scope creep — a finding even when it is an
   improvement)*
3. Is any criterion or decision **missing** a corresponding change? *(omission)*
4. Do the details match the specific values and constraints that were decided — not just the intent?

Also verify any `SC-NN` marked `verify: inspection`. **This is where those are checked**, and each needs
a `file:line` citation.

Report per violation: the path, the `SC`/`D` it relates to, and which of the three kinds it is.

**Amendments are the map of departures, never the anchor (DEC-229/DEC-230).** Read the build
lead's digest `amendments:` list — each entry names a task field (`intent`, `files`, `verify`)
the lead changed on its own authority, with `was`, `now` and a reason. For every entry, compare
the resulting diff against the BRIEF's success criteria and `plan.yaml`'s `decisions:` ONLY: a
departure that serves both passes without comment; one that weakens, contradicts, or escapes a
criterion or a decision is a `substance` finding with a concrete failure scenario, cited to the
`SC`/`D` it fails. Stage 1 never uses a task's `intent`, `files` or `verify` — signed or amended —
as its compliance anchor: the task text is the builder's HOW, and grading the diff against the
HOW the builder just rewrote would make the amendment its own reviewer. The reason on an
amendment is a claim, not evidence; Stage 2 recomputes.

## Stage 2 — code quality

Only after Stage 1. Judge against the conventions **already in this codebase**, not an abstract ideal.
Stage 2 examines the pinned diff and recomputes code quality on its own — `code-grade.py` over
every changed Python path included — and inherits nothing from an amendment's reason: a lead
that amended `verify` "for efficiency" has asserted it, and this stage measures it.

Look for: correctness bugs · unhandled errors · **silent failure paths** · missing input validation ·
dropped async rejections · boundary and off-by-one conditions · resource leaks · dead code left behind ·
copy-paste divergence · comments that no longer match the code · one more branch on an if/else chain
or a second boolean that must stay in sync
(`<HARNESS_CONTROL_PLANE_ROOT>/.agents/skills/harness-craft/references/model-the-domain.md`) · a
compatibility shim beside a migrated caller
(`<HARNESS_CONTROL_PLANE_ROOT>/.agents/skills/harness-craft/references/migrate-callers-then-delete.md`) ·
a one-caller wrapper or pass-through layer (`harness-codebase-design` reader load).

**Fail-open is the highest-value pattern to hunt.** Measured in this project's history: a dangling
reference that resolved to "valid" instead of blocking, a filter that returned a fabricated result on a
partial match. Both passed their test suites. Ask of every branch: *when this lookup misses, does it
block or does it sail through?*

Do **not** report what a linter catches, and do not restyle to personal preference.

### Principles applied

Read `## Principles applied` in each dev receipt under `notes/`. Two claims are checkable; check them:

- **Build the Lever** — the diff contains the script, codemod or generator. None → `form` finding.
- **Test Behavior** — the named kept test fails when every import returns nothing. Passes →
  `substance` finding; the test is decoration.

A cited principle you cannot match to a change in the diff is a `form` finding. An absent or empty
section is not a finding.

### Absence, subject and mutant (DEC-169, issue #979)

The one canonical copy; `harness-verification-rules` points here. Evidence is DEC-169.

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
- **A test that would still pass if every function it imports returned `undefined` observes no
  behaviour** and cannot fail for a defect. Five shapes: weak or no assertion (`toBeDefined`,
  `not.toThrow`), mock-or-absence only (`toHaveBeenCalled`, `toEqual([])`), self-referential
  expected value (`expect(f(a)).toBe(f(a))`), constant pin (restating a hand-maintained default or
  prompt string), fixture-asserts-fixture (the subject never runs in the body). The fix: call the
  subject with one concrete input and assert the literal output; no such assertion exists → delete
  the test.
- **A fixture says what it was captured from** (depth, shape, mode), and **a claim about host
  behaviour names the mode it was measured under**; never accept one mode as covering another.

### Grade changed Python

A changed Python path in the pinned range → run `code-grade.py` per
`<HARNESS_CONTROL_PLANE_ROOT>/.agents/skills/harness/references/code-grade-review.md`. A record
marked `SEVERITY: high` — below its bar and not grade 2 — is a **high** finding, reported as
`code_grade: fail`; a gated grade-2 function is a **med** finding that never blocks, reported as
`code_grade: grade_2`. **You do not set `code_grade`**: `validate-digest.py` recomputes it and
refuses a digest that disagrees (DEC-209).

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
re-gating; `proportionality` says more is planned than the change needs and carries `scope: task` (one
task over-builds — pm trims it) or `scope: mission` (the plan lane exceeds the work — the only
finding that downgrades the mission; never another panel cycle). The `findings:` shape is in your agent file's output block.
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

The pin is `review_sha` in the feature's `feature.json` — the orchestrator writes it (INV-6),
never you — or `HARNESS-REVIEW-PIN: <sha>` in your dispatch when `feature.json` cannot carry it
(#1677); the two must agree when both exist. Diff `base..review_sha` with
`base = git merge-base origin/main "$review_sha"` — **never `..HEAD`**. A commit landing
mid-review must not change what you reviewed. Where an earlier cycle's pin exists, note both: the
range between them is the fix cycle's work.

**Reconcile hand edits before Stage 1** — `validate-digest.py` recomputes both from the checkout
and refuses a verdict that disagrees:

```sh
git log --format='%h %s' --grep='\[harness:human\]' "$base..$review_sha"
git status --porcelain
```

| Found | Action |
|---|---|
| `[harness:human]` commits in the range | Report exactly that set in `human_commits_in_scope`. They **inherit no earlier review**; their paths are in scope now |
| Modified tracked files outside `<HARNESS_CONTROL_PLANE_ROOT>/.harness/**` | **Stop.** A tree matching no commit has no pinnable verdict — return `BLOCKED` and ask for a `[harness:human]` commit or a stash |
| Unattributed commits that look manual | A finding — attribution is what makes review scope derivable |

## Before there is a SHA: plan-phase review

No `review_sha` yet → the plan is the target (DEC-207): grade `BRIEF.md` and `plan.yaml` as the
specification, never a diff, and write

```yaml
reviewed: plan:<path-to-plan.yaml>
code_grade: n_a
```

Preconditions and where the findings go:
`<HARNESS_CONTROL_PLANE_ROOT>/.agents/skills/harness/references/plan-phase-review.md`.
