# FEAT-09 — plan-time route check — ship review

**For: Mike Ruangutai. Written at HEAD `3a5a245`, branch `feat/FEAT-09-plan-time-route-check`.**

## The short version

The feature works and is ready to ship. **Eleven of twelve success criteria are met.** The twelfth is
not broken — it is *unproven*, and that is the one thing needing your ruling.

The build phase should never discover routing again. Every PLAN task now either names the agent whose
domain grants write on its paths, or declares itself an explicit main-session step, and a checker
rejects a plan that does neither. Run live against this feature's own PLAN: **0 violations, and one
DEVIATION line naming T-01** — the DEC-174 carve-out disclosed rather than blocked, which is the
behaviour SC-12 asks for.

The sharpest evidence that this was worth building: **three of this feature's own four tasks turned
out to be outside every agent's grant.** The old process would have found that at dispatch, mid-build.

## The decision I need from you

**SC-08 says exactly one path matcher exists. The code genuinely satisfies that** —
`check-plan-routes.py` contains no path comparison at all; every path decision is delegated to
`check-domain.sh`. What fails is the *alarm*: the one fixture written to catch a future contributor
re-introducing a prefix comparison **cannot fail**.

It presupposes a path "granted only through a mid-pattern wildcard." No such path exists in the
manifest — every mid-pattern grant is shadowed by a broader prefix-shaped one. I measured this myself
rather than take it from the report, and it is worse than first stated: a live `--resolve` on the
fixture path returns **two** agents, and a prefix-only implementation would grant it to **six**. The
test asserts only "no VIOLATION for T-01, some OK for T-01", and the `OK` line emits no agent name, so
both implementations look identical to it.

| Option | What you get | What it costs |
|---|---|---|
| **(a)** Make the checker name the resolving agent so the fixture can assert *which* | A fixture that genuinely discriminates | Changing shipped behaviour to satisfy a test |
| **(b)** Amend SC-08 to assert on `check-domain.sh --resolve` directly | The property proven where it actually lives | A BRIEF amendment — approval-gated, re-signature |
| **(c)** Accept SC-08 as unproven and file it | Ships today; the property is already true by construction | The regression guard stays absent until someone re-introduces the bug |

There is no free option. **(c) is the principled one** — a file containing no path comparison anywhere
cannot contain a prefix comparison, so the property is proven by construction and only the *separate
fixture* the wording demands is missing. But it should be your ruling, not an omission: product flagged
that this was its last scheduled run, so unanswered, SC-08 ships unproven by default.

## The finding that matters most

**Three defects this feature surfaced are the same class: the logic was correct and the thing that was
supposed to notice couldn't.**

- **VF-1 (HIGH, fixed).** An inherited environment variable silently disabled the entire write guard —
  the code deciding which of sixteen agents may write which file. Exit 0, nothing logged, so an audit
  afterwards could not distinguish "the guard allowed this" from "the guard was off."
- **VF-2 (filed as issue #132).** The state-file budget gate is reachable by `Write` but not by `Edit`
  or `Bash` — one of three write routes.
- **SC-08 (open, above).** A fixture whose assertion is coarser than the property it names.

VF-1 and VF-2 are wrong *reachability*; SC-08 is an assertion that cannot *discriminate*. **None was
visible to someone reading the gate's own code, and every gate was green throughout.** An all-green
verify is not an absent defect.

SC-08 is the sharpest of the three, because of *how* it was found: not by review, but because the
goal-check was actually re-run against the tree at the end instead of scored from the records. That is
the argument for why this last leg is not paperwork.

## The unreviewed-guard window — it existed

`check-domain.sh` is the write guard for the whole org. Its `--resolve` change landed at `6792331` and
then **sat committed, with zero independent review, across the entire park** — through eight further
commits including the unpark. That window was real, and nothing in the green gates would have told you
it was open.

**What closed it: the panel that finally reviewed it is exactly what found VF-1.** The window and its
closure are the same event.

## The review pin was re-taken three times

`review_sha` names the commit reviewers actually scoped against. It moved three times, each for a
reason worth knowing:

1. **`1185d7f` — dangling.** Killed by the rebase; removed rather than carried.
2. **`4918d06`** — taken once after the build task and the DECISIONS entry, so the four-wide panel
   scoped a complete diff.
3. **`7a1bff8`** — the VF-1 fix made the pin stale the moment it landed, so it was re-pinned before the
   delta review (your ruling: a delta, not a second four-wide — 2 files, 34 lines).
4. **`7354ad0`** — applying that reviewer's own two findings.

**One of these went stale in a way that failed silently, and that is the lesson.** The *base* pin was
`ae2443d`, a pre-FEAT-08 commit that still resolves. `git diff` against it never errored — it just
returned **71 files where the true diff was 14** (reproduced exactly at `3c245c3`). The same stale base
at HEAD today returns 84 against 30. A wrong answer with exit 0 is worse than a crash.

## A collision worth your attention

Two features ran concurrently, and the peer deleted a tool this flow's measurement depended on.

> this collision is exactly the failure FEAT-09 exists to prevent — and the checker this feature builds
> would not have caught it, because the collision is in a tool the plan uses, not a path a task writes.

## The no-pre-emptive-skips ruling was vindicated, not merely obeyed

Your ruling that all four review steps run with no skips is what produced the only HIGH. **No single
reviewer could have produced it.** Security found the mechanism but did not check it against SC-04;
code verified SC-04 correctly, but under a clean environment. Each reviewer was individually correct.
**The defect lived in the union of the scopes**, and collation is what surfaced it. The UI reviewer
declined on *measurement*, not prediction — a reviewer that looked and declined is a reviewed finding.

This is the empirical answer to a question that had been open across features: for defects of this
shape, adding a lens does not help. Reading the lenses against each other does.

## Spend

**The harness no longer meters spend** (DEC-178, FEAT-08). There is no cost line in this document and
no figure, because the mechanism that produced them has been deleted. For context on why the feature
was chartered: `BRIEF.md:5-11` records that the routing wall cost a real escalation and $16 at FEAT-04
run 10 — a historical figure about the problem, not this feature's spend.

## State, verified by running

Unit suite exit 0 (32 PASS, 0 FAIL) · `check-docs` 0 · `check-state` 0 · decisions-index drift 0 ·
`git diff 7354ad0 HEAD` touches only `feature.yaml`, so **no unreviewed source is in the tree**.
All four tasks DONE. Distillation ran across ten agents; every Expertise file passes its checker.

## Residual backlog — nothing here gates the ship

Fourteen items with rationale in `notes/backlog-detail.md`, plus **issue #132** (the VF-2 route gap).
On your ship acceptance the unstruck ones become backlog issues; anything not listed dies silently.

Two deserve flagging now:

- **B-1 — a `shared:` file is falsely REJECTED.** A task naming `package.json` or `pyproject.toml` is
  rejected by the checker. Note the direction: it fails **closed**, not open — safe, but any dependency
  work hits it immediately. **Answering it amends DEC-179.**
- **B-2 — SC-08 is weaker than its clause count suggests.** Three of its four clauses are respellable
  source greps. This is issue #74 mode 3 live in this very feature: four clauses sharing one matching
  technique have one blind spot, not four. It is the same root as the decision above.

Also new, non-blocking: the `harness-team` rule text describes a state-file violation as "top-level
keys holding prose lists", but the guard rejects *any* unrecognised top-level key including a bare
integer counter. The doc is narrower than the enforcement, so a lead reading only the rule keeps
tripping it.

## Actions I could not complete

- **Closing GitHub issue #100 (T-02) was blocked by the permission classifier.** Its recorded condition
  ("close after VF-1 is resolved") is met, so the issue is stale-open. The mirror is never a gate, so
  this is a reported skip, not a failure. `gh-sync.py close-task .harness/features/FEAT-09-plan-time-route-check T-02`
  run with permission will close it.
