# Ship review — BUG-1286-test-tree-enforcement

**Reviewed revision `9adbce6b`. Branch `feat/BUG-1286-test-tree-enforcement`, not merged, worktree intact.**

## The decision you need to make

**The feature works. It is blocked on budget, not on behaviour.**

Four independent reviewer lenses found **zero behavioural defects** in the guard this feature
builds. Seventeen of your nineteen success criteria are met. The blocking gate passed. What stops
it is three things that each need one small edit, and a rework budget that is spent — 10 of 10.

Your options are:

1. **Authorise a budget raise for one cycle.** All three remedies are small, well-understood and
   routable to squads that already own the files. This is my recommendation.
2. **Risk-accept the high finding under DEC-176** and ship with two criteria recorded UNMET. Honest,
   and cheaper, but you would be shipping a complexity finding the factory's own gate raised.
3. **Stop here.** Everything is preserved and re-enterable.

I cannot choose for you: raising the budget is your decision under DEC-157, and accepting a high
finding's risk is yours alone under DEC-176.

## What was built, and what proves it

The suite-layout predicate now refuses every **tracked** test-shaped file outside `tests/`, reading
the Git index, behind a single `is_test_shaped()` and a self-policing exceptions registry. The
runner presents that refusal before any test runs. There is a re-runnable tree-audit instrument, an
audit record, and DEC-213 is amended to the shipped invariant.

All five planned tasks are implemented and committed. I re-ran every task's own `verify:` verbatim
rather than accepting any agent's report:

- unit suite exit 0, **341 PASS / 0 FAIL**, 27 files — 316 before this feature, so +25 real checks
- integration exit 0, **14 PASS / 0 FAIL**
- `--check-layout` exit 0; tree-audit `TOTAL 85 OUTSIDE 9 VIOLATIONS 0`; decision anchors 30/0 failed
- `check-state.sh` exits 0 with no violation and no note for this feature

**The plan phase's stated honest limit is closed.** Every green/red result on record at signature
time was a hand-simulation of the specification against reader-written reimplementations — three
independent reimplementations agreed and none was the artifact that ships. I re-proved case 11's
four red cases and two green controls against the **built** artifact with my own probe, and
confirmed the wiring by reading `tests/unit/test-suite-layout.py:493,528`, where the live config
reaches the assertion. That is the one thing build was told not to skip, and it did not.

**One real defect was caught and fixed mid-build.** The qa gate proved that T-02 case 3's ordering
assertion was tautological — it compared a list built in the order it was already written, so it
held whatever the runner emitted. In a feature whose entire subject is guards that cannot fail,
that was not something to ship. It now derives from the runner's actual output and reddens under
reversal.

## The three things blocking

**B-1 · high · gates ·** `code-grade.py` fails at the reviewed revision. `violations` grades **1**
against a bar of 4 (cyclomatic 23, cognitive 35, ABC 45.7); `_registry_findings` grades **3**
against 4. I re-ran the gate myself at `9adbce6b` — exit 1 — because the panel raised it on a
single run it could not repeat. It is real. It is a **complexity** finding, not a behavioural one:
no lens found anything wrong with what the code does. Remedy: decompose `violations` into one named
helper per responsibility. Owner: `harness-backend-dev`, which the plan's own lanes rows already
assign to that file.

**B-2 · SC-12 UNMET · record defect, and it is my fault ·** the audit note records SHA
`5f76d6b1…`, which is a real commit but **not an ancestor of the reviewed revision**. It became
orphaned when the main session rebased onto `origin/main` at my request, after the note was
written. The note was correct when authored and the measured rows are byte-identical at both SHAs,
so the measurement is sound — only the provenance token is wrong. Remedy: one token.

**B-3 · SC-16 UNMET · unproven, not wrong ·** the criterion's decisive clause is that
`violations()` has exactly one caller. I verified by `git grep` at the reviewed revision that it
does — `run-unit-tests.sh:33`, alone. But no unit assertion pins that repository-wide; the nearest
one counts lines *inside* `run-unit-tests.sh` and would stay green if a second caller appeared
elsewhere. Remedy: one caller-count assertion.

## The budget, and a doctrine question you should settle

`cycles_used` reached **10 of 10** during the qa gate. The validator lead reported a send-back
inside its run and then argued it should not count. DEC-157 says the counter increments "when a
lead reports send-backs inside a run" and draws no distinction by member type, so I recorded it
against my own interest.

Whether 10 of 10 *stops* a feature is genuinely undefined. The playbook says stop "on crossing";
step 7 scopes exhaustion to the fix loop; and there is **no mechanical check on `max_total_cycles`
anywhere** — `check-state.sh` only enforces INV-7. Per your standing direction I put it to
`fable-advisor` rather than to you. It ruled: the send-back does count, and forward first-pass work
continues while the branch stops at the first genuine rework demand. I followed that, which is why
validation ran at all instead of stopping three segments earlier. **A one-line decision defining
"exhausts" as reached-versus-crossed retires this permanently.**

`runs` is 37 against an informational budget of 20. INV-22 notes it and never gates. My read: the
count is honest but inflated by a long plan phase — 29 of the 37 predate this session. The eight
runs in this session each resolved something and none was wasted.

## How this briefing was assembled

**No report round was spawned.** I read the digests from disk and from the returns I received
directly. The build and validate record is first-hand: `runs/2026-09-05-{01-eng,01-product,
01-validator,03-validator,04-validator,05-eng,02-product,06-validator}/digest.md`, plus
`notes/qa-matrix-gate-c1.md`, `qa-matrix-gate-c2.md`, `qa-tree-audit.md`, the four
`notes/review-harness-*-c1.md` panel notes, `notes/research-BUG-1286-goalcheck-build-c1.md` and the
five task receipts. **The plan phase I did not run**, and I read it through `notes/handoff-plan.md`,
`plan.yaml`'s `panel:` block and `STATE.md` rather than its 29 run digests — so treat the plan-phase
account above as inherited rather than first-hand.

## Proposed backlog

Anything not listed here dies silently, so this is everything that survived collation.

| ID | Nature | Item |
|---|---|---|
| B-1 | bug | `code-grade.py` fails at the reviewed revision: `violations` grade 1, `_registry_findings` grade 3, bar 4. **Gates.** |
| B-2 | bug | `notes/qa-tree-audit.md` records a SHA orphaned by the rebase; measurement sound, provenance token wrong. **SC-12.** |
| B-3 | chore | No assertion pins `violations()`'s single-caller property repository-wide. **SC-16.** |
| B-4 | chore | Tautological conjunct in `_literal_key_present` (`tests/unit/test-suite-layout.py:414`) — can never be False. |
| B-5 | chore | Unreachable `".."` disjunct in `_is_inside_tests` (`tests/unit/test-suite-layout.py:399`). |
| B-6 | chore | Case 11's `INAPPLICABLE` branch (`tests/unit/test-suite-layout.py:524`) — latent, non-gating. |
| B-7 | chore | Three BRIEF line-number pins went stale inside the feature's own lifetime (SC-06, SC-07, SC-19). BRIEF is approval-gated so nobody touched them. |
| B-8 | chore | Integration case 2 asserts only one sentinel absent where case 4 asserts both. |
| B-9 | bug | `validate-digest.py` demands `code_grade` on a code-reviewer digest and rejects every value while `review_sha` is unpinned, so a plan-phase panel reader that did its job settles as `failed`. |
| B-10 | bug | Agents assigned to a worktree edited the **main checkout** by passing bare relative paths to file tools — twice this session, both caught and reverted. A guard refusing a relative path under a worktree dispatch would close it. |
| B-11 | bug | `check-domain.sh` refused a first digest write with "run digest already holds a recorded digest" when none existed; two runs also had their `state.yaml` clobbered by a later run and needed repair. |
| B-12 | enhancement | Define "exhausts" for `max_total_cycles` as reached-versus-crossed, and decide whether it deserves a mechanical check at all. |

## What I did not do

Not merged, not pushed, no PR. The worktree stands and its removal is not mine. No fix was
dispatched for any finding above — with zero cycles that decision is yours, not mine to pre-empt.
