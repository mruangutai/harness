# Ship review — BUG-201-depends-on-integrity

**Recommendation: ship — and the merge needs you.** A `depends_on` naming a task that does not exist
in the plan is now refused at the one place both the reader and the writer already share, and the
three consumers that used to swallow the refusal now say what actually went wrong. All nine success
criteria are met, each verified by its own declared method at the reviewed commit. The reviewer
panel raised one gating defect; it was fixed and re-validated. **Nothing about BUG-201's code
blocks the merge — but the pull request cannot merge, for two reasons that are both records and
both outside this feature's authority.** Read "Merge status" next.

**How this briefing was assembled — disclosure (DEC-69).** No report round was spawned. I read the
run digests off disk:
`runs/2026-09-06-01-product`, `runs/2026-09-06-01-validator`, `runs/2026-09-06-02-product`,
`runs/2026-09-07-01-product`, `runs/2026-09-07-01-validator`, `runs/2026-09-07-02-product`,
`runs/2026-09-07-02-validator`, `runs/2026-09-07-03-product`, `runs/2026-09-07-03-validator`,
`runs/2026-09-07-01-eng`, `runs/2026-09-07-04-validator`, `runs/2026-09-07-02-eng`,
`runs/2026-09-07-03-eng`, `runs/2026-09-07-04-product`, `runs/2026-09-07-05-validator`,
`runs/2026-09-07-04-eng`, `runs/2026-09-07-06-validator`, `runs/2026-09-07-05-product`
(each `.../digest.md`). Phases I did not run myself — plan, and the first three build segments —
are summarised from those digests, not from memory.

## Merge status — PR #1476 is open and RED, and neither cause is BUG-201's code

`main` requires the `integration` check and `enforce_admins` is on, so no override exists. The check
reports seven violations, five of them another feature's.

**Cause 1 — this branch is based on a commit that never reached `origin/main`.** Base `af859ee8` is
not an ancestor of `origin/main` (merge-base `41c16c73`). The PR therefore carries **40 commits, of
which 12 are BUG-201's**; the other 28 are BUG-1290-factory-claim-repo-root, merged into the local
`main` and never pushed — its own PR number was never recorded either (INV-28). Five CI violations
are BUG-1290's records: INV-32 for readers `goalcheck`, `scope` and `should-not-exist`, plus its
missing `handoff-build.md` and `handoff-validate.md`. **I did not touch them.** Recording a panel
reader that did not run would falsify the record, and they belong to a feature I was not dispatched
against.

**Cause 2 — BUG-201's own two rows are the harness defect filed below as B-1**, not an omission.
`notes/handoff-plan.md` and `notes/handoff-build.md` cannot be written at all for a feature that
lives only in a worktree: `check-domain.sh:1141-1149` takes the checkout-relative path from
`harness_boundary.checkout_relative` and discards the worktree root, then passes that rel with the
*main* root into `handoff_done_when.problems` (`:1748`), so every `Authority:` pointer is looked for
in a checkout where the unmerged feature directory does not exist. Measured again today: the guard
refused the write and named all three pointers. Bending a pointer to satisfy the gate would leave a
false authority in the record, so it was not done.

**What unblocks it — your call, and none of it is BUG-201 work.** (a) Fix B-1 (one line: carry
`_ck[0]` as the root for the handoff check), which lets BUG-201 — and every future worktree feature —
write its own notes; (b) decide what happens to BUG-1290's five record violations, which will redden
the first PR that pushes local `main`'s backlog whatever else changes; (c) if you would rather land
BUG-201 alone, it needs a base that is on `origin/main`, which is a history decision I have no
authority to make.

## What shipped

Issue #201: a plan could name a dependency that did not exist, and every consumer that tripped over
it reported something else — usually that the plan was missing or unparseable.

- **The rule** — `.claude/skills/harness/bin/harness_yaml.py`, inside `validate_plan_doc`'s call
  tree, so the read route and the `plan-merge.py` write route are both covered with no new wiring.
  One exception names *every* dangling pair, not just the first (D-02). A `depends_on` that is not
  a list is rejected on its own terms rather than iterated character by character.
- **The diagnosis** — the three swallow sites now report the real cause in three deliberately
  different postures (D-05): `factory_claim.py` keeps polling and reports (a poller must not gate),
  `gh-sync.py start-task` refuses at exit 2, `gh-sync.py status ready` leaves its existing refusal
  and exit status untouched and adds one stderr line.
- **Out of scope by the operator's own ruling**: self-dependencies, cycles, and ordering. This is
  referential integrity, not DAG policy.

## Squad by squad

| Squad | Result | Digest |
|---|---|---|
| Product — plan draft | PASS. BRIEF REQ-01..05 / SC-01..09, plan D-01..05, T-01..06, 0 route violations | `runs/2026-09-06-01-product/digest.md` |
| Validator — plan panel c0 | PASS. Both readers ran, 10 findings, none gating | `runs/2026-09-06-01-validator/digest.md` |
| Product — panel record c0 | PASS. Panel transcribed into `plan.yaml` | `runs/2026-09-06-02-product/digest.md` |
| Product — replan c1 | BLOCKED (contract violation). Artifacts landed; the host lost the member's return, and the run was closed honestly rather than as an inferred PASS. **This is the one cycle counted before review.** | `runs/2026-09-07-01-product/digest.md` |
| Validator — advisor consult | PASS. Three binding rulings, all `artifact_change: none` | `runs/2026-09-07-01-validator/digest.md` |
| Product — goal-check of the plan | PASS. All ten c0 findings disposed | `runs/2026-09-07-02-product/digest.md` |
| Validator — plan panel c1 | PASS. 19 findings, `severity_max: med`, `must_fix: []` | `runs/2026-09-07-02-validator/digest.md` |
| Product — panel repair + record | PASS. V-1 and S-2 repaired in the specification, full record at cycle 1 | `runs/2026-09-07-03-product/digest.md` |
| Validator — advisor, panel currency | PASS. The c1 record is current for signature | `runs/2026-09-07-03-validator/digest.md` |
| Eng — build segment A (T-01..T-04) | ESCALATE. The rule reddened four suites whose *pre-existing* fixtures encoded the very bug it removes, and no signed task owned those files | `runs/2026-09-07-01-eng/digest.md` |
| Validator — advisor, build escalation | PASS. Four binding rulings: execution-time adjustment, no replan; T-03's own cycle repairs the fixtures | `runs/2026-09-07-04-validator/digest.md` |
| Eng — T-03 fix cycle | PASS. Three fixtures made legal, ten suites green, **no assertion weakened, no production code touched** | `runs/2026-09-07-02-eng/digest.md` |
| Eng — build segment B (T-05, T-06) | PASS. Red observed first at T-05; T-06 green on all ten suites | `runs/2026-09-07-03-eng/digest.md` |
| Validator — QA gate + SIMPLIFY | PASS. `matrix_ok: true`; SIMPLIFY folded in `refuse(stream=...)` | `notes/qa-harness-qa-c1.md`, `notes/receipt-harness-backend-dev-simplify-c1.md` |
| Product — panel record repair | PASS. The missing `goalcheck` reader row recorded; 19 findings and the signature untouched | `runs/2026-09-07-04-product/digest.md` |
| Validator — reviewer panel c1 | **FAIL**, one gating finding (below). Spec compliance clean; `matrix_ok: true`; security and UI both audited and returned PASS | `runs/2026-09-07-05-validator/digest.md` |
| Eng — MF-1 fix | PASS. Grade 3 → grade 5, behaviour byte-identical | `runs/2026-09-07-04-eng/digest.md` |
| Validator — re-validation c2 | PASS. MF-1 closed, `must_fix: []`, matrix reproduces with no count collapse | `runs/2026-09-07-06-validator/digest.md` |
| Product — ship goal-check | PASS. **9 of 9 criteria met** | `runs/2026-09-07-05-product/digest.md` |

## The one gating finding, and how it closed

The reviewer panel found that the function this feature exists to add,
`_validate_plan_depends_on`, was itself code-risk **grade 3** in production code (cyclomatic 10,
cognitive 14) — a high finding, and `gates.review: advisory_unless_high` makes a high one gate.
Two private helpers were extracted (`_depends_on_entries`, `_dangling_edges`); the function is now
grade 5 and both helpers grade 4. Ten hostile inputs were run against the old and the new
implementation and every raised message was byte-identical, so nothing observable moved. All nine
feature suites and both standing test pools re-ran green at the new pin.

The fix had one trap worth recording: signed criterion SC-04 requires the tree to hold exactly one
`def _validate_plan_depends_on` and one call site, so a helper named after its parent would have
cleared the complexity bar and reddened the specification in the same edit. The helpers were named
away from it and SC-04 was re-verified by grep at the reviewed commit.

## Goal check — 9 of 9 met

Every criterion was executed by its own declared method at `review_sha 626bb599`, not inferred from
a passing suite: SC-01, SC-03, SC-06, SC-08 automated/unit; SC-02, SC-07, SC-09
automated/integration; SC-04 and SC-05 by inspection. Where a criterion enumerated N clauses, all N
were counted (SC-07's six named suites each run individually, SC-09's nine clause lines, SC-08's
five named cases). No criterion declares `verify: uat`, so no user acceptance test applies.
Evidence: `notes/research-BUG-201-depends-on-integrity-goalcheck-ship-c1.md`.

## Open questions

**One, and it is yours to decide: the merge, above.** Four wording findings (L-1, S-1, S-3, S-4)
rode into your batched signature review on 2026-09-07 and signing accepted them; they are not
re-opened here. Everything else that survived collation is in the backlog table below.

## Budget

`cycles_used: 3 / 10`. The three: the lost-host replan re-dispatch, the T-03 fixture escalation, and
the MF-1 review fix. `runs: 18 / 20` — under the informational bound, and each run resolved
something: no run in the list repeats another's work.

## Proposed backlog

Unstruck rows become issues on ship acceptance. **Anything not listed dies silently.**

| ID | Nature | What |
|---|---|---|
| B-1 | bug | `check-domain.sh` resolves a handoff note's checkout-relative path against the **main** checkout root, so no `notes/handoff-*.md` can be written for a feature that lives only in a worktree — every Authority pointer is unresolvable. Measured three times, most recently today with the live refusal. Fix: carry the worktree root from `harness_boundary.checkout_relative` and pass it as the root for the handoff check. **This is half of why PR #1476 cannot merge.** |
| B-2 | chore | `plan-merge.py` has no write route to the top-level `lanes` key (`AMENDABLE_KEYS == ("tasks","decisions")`), so `factory_claim.py` and `gh-sync.py` could not be listed in `lanes.rows` even though T-06 edits them. Advisor-settled for this plan; the gap is still there. |
| B-3 | bug | `code-grade.py`'s pre-image lookup appears line-based rather than by qualname or body: `tests/unit/test-factory-claim.py:432 run_main` was graded as changed although its body is byte-identical at base and only its line offset moved. Raised independently at c1 and c2. |
| B-4 | enhancement | The "one actionable line" diagnostic contract is not guaranteed: `str(exc)` can carry newlines for a generic parse error, and a crafted `depends_on` entry can carry control or ANSI bytes into the same stderr line. Advisory remedy: `repr()`-quote the entry in the join. Non-gating — same-trust actor, no sink parses it. |
| B-5 | chore | The two new diagnostics repeat the plan path twice and inherit "failed to parse YAML in `<path>`" framing for a file that *did* parse. SIMPLIFY deferred this under its one-fix ceiling; the shape matches three pre-existing sites, so it is a tree-wide convention question. |
| B-6 | chore | The new refusal lines state a cause without a consequence clause, unlike the sibling refusal at `gh-sync.py:1160-1168`. Style only. |
| B-7 | chore | `require_or_bootstrap` in `harness_yaml.py` is grade 3 (high) and pre-existing at base — the same bar MF-1 was held to, on a function this feature did not touch. |
| B-8 | bug | An `Edit` with a **relative** path resolves against the process cwd (the main checkout) rather than the assigned worktree; one edit leaked into the main checkout and was caught and reverted by hand. Twice in this feature, and nothing mechanically prevents it. |
| B-9 | bug | A member emitted its fenced digest as a final assistant turn instead of through the terminal yield; the host recorded `failed (exit 1)` while the work had landed correctly. A correct run recorded as a failure. |
| B-10 | enhancement | Nothing pins the new rule against a *future* regression: the 12 cases reach every new line, but no mutation run confirms the suite reddens when the rule is broken. `test-factory-claim-mutation.py` covers the claim cache, not this. |
| B-11 | chore | SC-03's `>= 67` corpus floor is a point-in-time property of the ambient corpus, not of this code; an unrelated archival would redden a structurally correct implementation. Recorded as a signed panel finding; the criterion is spent, the pattern is not. |
| B-12 | chore | The now-unreachable skip branch in the decompose path: a dangling blocker is refused at load, so the branch that used to skip such an edge can no longer be reached. Ruled BACKLOG by the build-escalation advisor consult (Q-ADV-7). |
| B-13 | bug | BUG-1290-factory-claim-repo-root is `done` on the local `main` but was never pushed and never had a PR recorded (INV-28), and its record carries five violations — three INV-32 readers plus two missing handoff notes. Any PR raised from a branch based on local `main` inherits them into the required CI check. **This is the other half of why PR #1476 cannot merge.** |
