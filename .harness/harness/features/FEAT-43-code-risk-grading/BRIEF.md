# BRIEF — FEAT-43 Code risk grading

## Problem

Nobody on the engineering squad has ever been told what "too complicated to merge" means here. The
five dev specialists load five skills between them and not one of them mentions complexity, so a
developer writing a function has no bar to write to and no way to tell when they have crossed it.
The result is measurable: across 443 production and 903 test functions in
`.claude/skills/harness/bin` at `origin/main`, the worst function in the repository carries a
cognitive complexity of 167 and a cyclomatic complexity of 82, and three of the ten worst live in a
single file. Nothing in the review path reports any of this, so the code that is hardest to change
safely arrives, passes, and stays.

The second half of the problem is that two of the checkers meant to catch this class of error report
things they do not enforce. `check-plan-routes.py` printed `OK` for a task route minutes before
every write on that route was denied by the live hook, because it resolved a different configuration
file than the hook consults. And the `gates` block of `.harness/harness.json` — `qa_gate`, `review`,
`uat`, `merge` — is read by no program at all; it is honoured only by agents reading configuration as
prose. A checker that reports without enforcing is worse than no checker, because its green is
believed.

## Goal

An engineer learns the bar before writing the code, and a review reports whether the code met it.
Every Python function gets one risk grade from 1 to 5, computed from cyclomatic complexity, cognitive
complexity and ABC size, worst metric wins. A change that introduces a function at grade 1 cannot
merge; grade 2 passes with a written reason. The grade feeds the severity ladder that already exists
— grade 1 becomes a `high` finding, which the existing review rule already turns into FAIL — so no
second gating vocabulary is created. Pre-existing debt is neither hidden nor inherited: only the
functions a change is responsible for are graded against the bar.

The teaching lands first. A reviewer reporting a grade the author was never taught to hit is a trap,
not a gate.

## Definition of Done

Written for someone who has not read the plan, and about whether the *grading itself* works — not
about whether some piece of code passed.

You can tell this feature worked when all of the following are things a person can go and observe:

- Show the tool a function that any engineer would call straightforward and it says so. Show it one
  that any engineer would call a tangle and it says that too. **Both directions matter.** A tool that
  only ever agrees with the code in front of it is not measuring anything, and this project has
  already struck one check that graded a dataset whose labels and grader were written by the same
  hand. Nothing here may be checked only against itself.
- Take a working function and deliberately make it harder to follow — bury the logic two levels
  deeper, fold two loops into one, add another condition to an `if`. The grade goes down. Undo it and
  the grade comes back up. **The direction of the movement is the evidence**, not the number it lands
  on.
- Run it over the same code twice, from two different folders, on two different machines, and it
  gives the same answer both times, character for character.
- When a change is rejected, the message names the file, the line, the function and the size of the
  problem, and says which of the three ways of being complicated is the one that failed. The author
  should be able to act on it without opening the tool's source or guessing.
- Someone who has read the guidance and never run the tool can look at a function and say roughly
  what it will score. **If they cannot, the teaching failed no matter how good the tool is.**
- The tool is never the last word. A human reviewer can still reject a change on judgement — that
  splitting a function three ways made it worse to read — even when every number improved.
- When the tool cannot read a file, it says so by name. It never counts an unread file as a clean
  one.

## A caution about the numbers this feature was planned from

The measured distribution recorded during planning — the medians, the p90s, the 120 failing
production functions, the 27.1% and 11.7% failure rates — is **directionally right, not
authoritative.** It was produced with one defensible reading of ABC's counting rules, and Fitzpatrick's
specification varies by language; a different reading shifts every ABC figure. The cognitive
complexity figures are a **Sonar-style approximation, not SonarSource's own algorithm**, and must
never be reported as though they were. The first task of the build pins the counting rules in a test
with hand-derived fixtures, and the fixtures — not the planning measurements — are what the tool is
answerable to from that point on.

## Requirements

- REQ-01: An engineer can find out, before writing code, what makes a function too risky to merge and
  what to do instead — not only the thresholds, but the habits that keep code under them.
- REQ-02: Every one of the five engineering specialists receives that guidance automatically, at the
  moment it starts work, without anyone remembering to hand it over.
- REQ-03: Anyone can compute the risk grade of any Python function in the repository from the command
  line, and get the same answer every time, anywhere.
- REQ-04: Grading against the bar is limited to the functions a change is responsible for, so code
  that was already below the bar is neither counted against the author nor quietly hidden.
- REQ-05: A code review reports, for each function the change is responsible for, the grade, the
  three underlying numbers, the location, and which metric produced the grade.
- REQ-06: A change introducing a function at the worst grade cannot merge; one at the second-worst
  proceeds only with a written reason recorded against that function.
- REQ-07: A file the tool cannot read is reported as ungraded by name, and is never counted as
  passing.
- REQ-08: The limits of the grading — the languages it does not cover, the existing code it does not
  fix, the approximation in one of its numbers — are stated where the people relying on it will read
  them.
- REQ-09: The plan-time route check answers about the same configuration the write hook will consult,
  or refuses to answer at all.
- REQ-10: The gate policy recorded in configuration is applied by a program, not inferred from prose
  by whoever happens to read it.
- REQ-11: The vocabulary this feature introduces has one canonical spelling that the tool, the
  guidance and the review all share.

## Success Criteria

- SC-01: A fixture suite pins the exact counting rules. At least twelve fixtures span all five
  grades, and each asserts the exact cyclomatic value, cognitive value, ABC magnitude, per-letter A,
  B and C counts, and the resulting grade. A fixture set that exercises fewer than all five grades
  fails the criterion.
  verify: automated      evidence: unit
- SC-02: Every fixture's expected numbers are derived in writing beside the expectation, and the
  derivation is checkable by hand without running the tool. A reviewer re-derives at least three
  fixtures independently, at the pinned review sha via `git show <review_sha>:<path>`, and cites the
  line of each. A derivation that reads "as produced by the tool" fails the criterion — that is the
  check-only-against-itself shape the Definition of Done forbids.
  verify: inspection
- SC-03: Direction of change is proven, in both directions. At least four before/after pairs assert
  that the deliberately worsened member grades strictly lower than its partner, and at least two
  pairs assert the improved member grades strictly higher. Each pair changes exactly one habit —
  nesting depth, loop count, condition count — so the pair names which metric moved.
  verify: automated      evidence: unit
- SC-04: The same input produces byte-identical output from two different working directories, with
  the repository checked out at two different absolute paths, and with directory entries presented in
  a different order. Paths in the output are repository-relative and the ordering is total.
  verify: automated      evidence: integration
- SC-05: A failing finding carries every field an author needs, each asserted separately: the
  repository-relative file path, the line number of the `def`, the qualified function name, the
  cyclomatic value, the cognitive value, the ABC magnitude, the grade, and the name of the metric
  that produced the grade. A single whole-string match does not satisfy this — one assertion per
  field.
  verify: automated      evidence: integration
- SC-06: A corpus containing one file with a syntax error reports that file by name as ungraded,
  excludes it from every count of graded and passing functions, and exits with a status distinct from
  both the all-clear and the bar-failed statuses. No run over such a corpus exits zero.
  verify: automated      evidence: integration
- SC-07: The set of functions a change is responsible for is exactly right on a seven-way fixture
  repository containing, in one commit: a newly added function, a body edit that worsens an existing
  function, a body edit that improves one, a rename with an unchanged body, a whitespace-only
  reformat, a signature change that adds no branching, and a whole-file move with no body edits. The
  gated set is exactly the new function and the worsened one, asserted by set equality, and each of
  the five excluded cases is asserted absent individually.
  verify: automated      evidence: integration
- SC-08: A function that was already below the bar and that the change does not worsen produces no
  finding. On the same fixture repository, an untouched grade-1 function is asserted absent from the
  findings and present in the informational listing. This is the criterion that keeps the feature
  from becoming a ratchet the operator explicitly refused.
  verify: automated      evidence: integration
- SC-09: The guidance and the tool cannot disagree. A test reads the worked examples out of the skill
  file, runs the tool over each example's source, and asserts the tool's grade equals the grade the
  skill claims, one assertion per example. The test fails if the skill carries fewer than five worked
  examples, so the check cannot pass by the skill containing none.
  verify: automated      evidence: unit
- SC-10: All five engineering specialists load the guidance. The skill name appears in the `skills:`
  list of `harness-frontend-dev`, `harness-backend-dev`, `harness-ai-dev`, `harness-data-engineer`
  and `harness-dev-ops`, in both the canonical agent definitions and the generated Claude adapters,
  read at the review sha — ten assertions, one per agent per tree, never a repository-wide count.
  verify: automated      evidence: unit
- SC-11: A developer who has read the guidance and has not run the tool predicts the grade of five
  unseen functions by eye, and at least four of the five match the tool. This is the only check that
  can fail the teaching rather than the tooling, and a failure here is a finding against the skill,
  not against the developer.
  verify: uat
- SC-12: A clean grade report cannot pass a review on its own. With every graded function at grade 5,
  the gate evaluation still returns FAIL when `must_fix` is non-empty, and returns PASS when
  `must_fix` is empty and the maximum severity is `med`. Both cases asserted.
  verify: automated      evidence: unit
- SC-13: The `gates` block is read by a program. Each of the four keys — `qa_gate`, `review`, `uat`,
  `merge` — is resolved from the configuration file by name, asserted individually; and a
  configuration fixture carrying an unrecognised policy value raises loudly rather than falling back
  to a default. A missing or unreadable configuration is a loud failure, never a skip.
  verify: automated      evidence: unit
- SC-14: A grade-2 function in the gated set emits an explicit demand for a reason, naming that
  function, in the tool's output; and the same run with no grade-2 function emits none. Both
  directions asserted, so the demand cannot be unconditional text.
  verify: automated      evidence: integration
- SC-15: The written reason actually gets written. At the review sha, the code reviewer's finding
  note answers every reason demand the tool emitted for this feature's own change, naming each
  function. If the tool emitted no demand, the criterion is recorded `not_met` with that fact stated
  — not `met` vacuously.
  verify: inspection
- SC-16: The route check now answers about the configuration the hook consults. On a fixture pairing
  an owner checkout whose manifest grants nothing with a linked worktree whose branch manifest grants
  everything, the checker reports a violation. The previous revision of the checker is run against
  the same fixture and shown to report OK, so the assertion is proven able to fail.
  verify: automated      evidence: integration
- SC-17: The two bars are applied per surface, from the classification the configuration already
  carries rather than a second list: a production function at grade 4 passes and at grade 3 fails; a
  test function at grade 3 passes and at grade 2 fails. Four assertions, and one asserting the
  classification is derived from the existing `test_kinds` detection rather than a hardcoded path
  list.
  verify: automated      evidence: unit
- SC-18: The stated limits are present where a reader meets them. The guidance says, in plain
  English, that shell and TypeScript files are not graded, that grading does not fix the code already
  below the bar, and that the cognitive number is an approximation of the Sonar method and not that
  method. Read at the review sha and each of the three cited by line.
  verify: inspection
- SC-19: The reviewer cannot report without stating the grading result. A code-reviewer return that
  omits the grading field is rejected by the digest validator, and a return stating a failing grade
  is not accepted as a pass. Both asserted; the rejection message names the missing field.
  verify: automated      evidence: integration
- SC-20: The recorded gate policy changes a gating outcome, not only a library return. The digest
  validator imports the policy module and resolves the `review` key from the configuration file: a
  code-reviewer return carrying a non-empty `must_fix` alongside `VERDICT: PASS` is rejected against
  a fixture configuration whose `review` key is `advisory_unless_high`, and the same return is
  accepted against a fixture whose `review` key is `advisory`. That pair is the criterion — a single
  rejection is satisfiable by a hardcoded rule and proves nothing about the configuration being
  read. A fixture with no `gates` block makes the validator exit non-zero naming the gate, never
  accept. The previous revision of the validator is run against the first return and shown to accept
  it, so the assertion is proven able to fail.
  verify: automated      evidence: integration

## Verification gaps

- `eval` has no runner (`cmd: null` in `.harness/harness.json`). The central claim that guidance
  changes how an agent writes code is therefore **not proven by any automated gate**. SC-11, a UAT
  step, is the only thing carrying it, and it depends on a human sitting down with the skill.
- `component`, `ui` and `typecheck` have no runners. This feature touches no surface they would
  cover, so nothing is lost here.
- `functional` is excluded by DEC-187 and is not routed around.
- There is **no coverage instrumentation of any kind** in this repository — no `coverage.py`, no
  dependency manifest, no coverage step in CI. Nothing in this feature reports how much of the graded
  code is exercised, and CRAP is not computable here at all.

## Constraints

**Supplies the mechanism — these are what the feature is built on, not obstacles:**

- DEC-31 supplies the gating rule: `must_fix` non-empty or `severity_max` at `high` or above fails.
  Grade 1 becoming a `high` finding is all that is needed to gate; no new loop is designed.
- The fix loop already exists in `harness-team`'s `loop_back`, bounded by `max_cycles`. A failing
  grade routes back to the engineering lead through it unchanged.
- DEC-174 amendment 4 supplies the routing rule for a library a gate calls: a squad may write the
  library, and the cutover that makes a gate use it is main-session-direct.
- DEC-63 supplies the delivery mechanism: a rule reaches an agent by being named in its `skills:`
  frontmatter, injected in full before the agent's first action. This is why the delivery is a skill
  and not Expertise, which is distilled cold after a run and never reaches an agent that has not
  worked here.
- DEC-11 amendment 1 supplies the rule that `skills:` is capability and lives in agent frontmatter,
  not in the team manifest.

**Blocks or bounds the solution:**

- DEC-174 amendment 4 names `check-plan-routes.py`, `check-domain.sh`, `bash-write-guard.sh`,
  `validate-digest.py`, `check-state.sh`, `dispatch-guard.sh` **and the test file of each** as the
  enforcement layer. The squad may not execute changes to any of them. `validate-digest.py` holds
  three of the ten worst functions in the repository and is therefore untouchable here.
- `.omp/agents/**` and `.claude/agents/**` are owned by nobody, by ruling in the team manifest. So is
  every `.claude/skills/harness-*/` skill file — measured with `check-domain.sh --resolve`, which
  returns `NOBODY`. Those surfaces are main-session-direct.
- DEC-182 governs the plan format; DEC-120 reserves the approval signature to the main session.
- DEC-190's precedent applies to a missing dependency: a loud error, never a quieter mode.

**Out of scope, by operator ruling:**

- Coverage instrumentation and CRAP. Its own feature; it would add the repository's first dependency
  manifest and rewire the test runner.
- Fixing the 226 functions that already fall below the bar. Its own cleanup feature, and explicitly
  **not** a touch-it-fix-it ratchet.
- Shell (11 files) and TypeScript (2 files). Shell has no practical complexity tooling. The limit is
  stated in the guidance; coverage of it is not faked.
- Refactoring `validate-digest.py`.

## Approval

status: pending
