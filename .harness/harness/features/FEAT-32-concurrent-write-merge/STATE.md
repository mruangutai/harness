# STATE — FEAT-32-concurrent-write-merge

## Current

Phase: **ship mission, build phase.** `status: Building`. Both signatures verified `approved` /
`operator` / `2026-08-22` at `b1281df` (`plan.yaml:4-7`, `BRIEF.md:431-435`). Mirror opened:
milestone **21**, parent **#700** (`parent_origin: created`), sub-issues **#701-717**.

**THE TWO LANES INTERLEAVE, and that is this feature's whole sequencing problem.** Nine tasks are
main-session-direct under DEC-174 (T-01, T-07, T-08, T-09, T-11, T-12, T-14, T-15, T-16); eight are
the team's (T-02, T-03, T-04, T-05, T-06, T-10, T-13, T-17). The `lanes:` block (`plan.yaml:9-80`,
resolved at `c32f332`) is the authority on which surface sits where.

**DONE — four in the main-session lane, verified by their owner, committed by me (DEC-153: I hold the
pen, it does not).** T-01: the hook-payload probe, `DISPATCHED_PERSONA_KEY=tool_input.subagent_type`,
measured live — and a probe installed in a feature worktree captures NOTHING, because the hook
resolves through `CLAUDE_PROJECT_DIR` to the main checkout. T-16: `validate-digest.py`; its plan
premise was STALE, the task's own verify failed before any edit, and the number is re-derived to
**845** at this sha. T-07: `test-dispatch-guard.py`, 12 assertions, red-proved by disarming
`sys.exit(2)` — **under that mutant three of case 1's four assertions still passed, because the guard
still prints to stderr; only the exit-code assertion discriminates, so T-08 must not weaken it.**
Statuses set `done` in `plan.yaml` FIRST, then `gh-sync close-task`: #701, #707, #716 closed.

**T-15 — WORK DONE, VERIFY UNSATISFIABLE, DEFECT IS A ONE-CHARACTER TYPO IN THE APPROVED PLAN.**
`plan.yaml:2033` asserts `g.endswith(" plan.yaml approval:")` with a LEADING SPACE; the grant the task
adds is `.harness/*/features/*/plan.yaml approval:`, where the character before `plan.yaml` is a
**slash**. Measured, not reasoned: against the real `team-config.yaml`, `endswith(" plan.yaml
approval:")` is **False** and `endswith("plan.yaml approval:")` is **True**. Its two siblings at
`:2043-2044` omit the space and pass; every other clause of T-15's verify holds. **Fix by dropping one
space and keeping it an `endswith` — NOT by weakening it to a bare `in` test**, or the grammar check
stops discriminating. pm owns `plan.yaml` (D-03); the main session cannot make it, holding only that
file's `approval:` mapping. **T-14 depends on T-15, so this blocks the main-session lane, not mine.**
Queued rather than dispatched: a product-lead run was in flight, and dispatching one persona twice at
once is the exact collision this feature exists to fix.

**SEGMENT A IN FLIGHT** to `harness-eng-lead` as the `build` team: T-02 (`plan.yaml:440-559`), then
T-03, T-04, T-05, all `harness-backend-dev`. T-02's receipt and `harness_merge.py` are on disk but
**the run has not returned, so nothing of it is committed and nothing recorded** — a member writes its
artifact at the END of its run, and this feature has already produced two false STATE.md entries from
artifacts read before their run finished.

**#551's COUNT IS EIGHT, NOT SEVEN, AND CORRECTING IT NEEDS THE OPERATOR'S SIGNATURE.** pm measured it
(`notes/research-FEAT-32-551-count.md`, run `t13-count-product`, ESCALATE, 0 send-backs). Occurrence 8
sits at `runs/2026-08-21-2-product/digest.md:28` — an author independent of the `STATE.md` under
suspicion — parked as a non-blocking GitHub-comment item, so it never reached `plan.yaml` or
`BRIEF.md`. The plan's seven is **staleness, not a deliberate hold**; nothing argues for seven. It is
**NEW, not covered**: T-13's intent *enumerates* occurrences 5, 6, 7 and pins all three to run dir
`2026-08-21-1-product`, and signed `BRIEF.md:16` reads "seven measured occurrences".

**I CLOSED pm's QUESTION WITH A MEASUREMENT IT LACKED THE TOOL TO TAKE, and it STRENGTHENS the
entry.** pm asked whether occurrence 8's claim that the mechanism *demands* a false verdict is too
strong — it turns on whether the validator accepts a member `verdict: none`. **It does not.**
`validate-digest.py:705` ranks members against `{PASS, FAIL, ESCALATE, BLOCKED}`; piping four
synthetic lead digests through `validate-digest.py lead` on stdin, `none` and `unknown` are REJECTED
with "member verdict 'none' is not one of … the roll-up cannot rank it", while `PASS` and `BLOCKED`
are rejected only for a missing `branch` field — the control proving the discriminator is the verdict
value, not an invalid fixture. **A lead force-closed with a member in flight cannot record "I do not
know"; the contract forces an assertion about work it cannot see.** The strong claim belongs as
written.

**OCCURRENCE 9 IS RAISED AND DELIBERATELY NOT COUNTED.** `t13-count-product` was itself force-closed
with pm in flight; the lead drafted `verdict: none`, pm completed, and the lead returned an honest
graded digest. The harm did not materialise, and this feature's own round-5 precedent is explicit that
a force-close followed by a successful resume is NOT an occurrence — a mistake made twice here before
being corrected. The operator decides; I record it as raised.

**`--check-kinds` IS RED, EXPECTEDLY, AND T-10 CLOSES IT.** `MISCONFIGURED:
.claude/skills/harness/bin/test-dispatch-guard.py is not in run-unit-tests.sh's explicit script list`
— T-07 created that file and T-10 registers it, which is why T-10 lists T-07 in `depends_on`. Green at
`b1281df`. Committing red here is deliberate and recorded; the final commit does not ship red.

**ONE COMMIT BEHIND MAIN, AND I CANNOT FIX IT.** `12c66b3` (PR #719) fixed `RUNS_AGENT_EXEMPT` —
FEAT-32 exempt at **5**, so `feature.json` writes work again, confirmed by a write landing at index 5
with `agent` present. `merge` is in `HEAD_MOVERS` (`bash-write-guard.sh:144`), refused for every
governed agent, so **the merge is the main session's act**, and it must wait until no run is in flight
because a HEAD move re-points every file under every agent in the tree. Both `feature_schema.py`
importers in the suite **PASS against the stale copy**, so being behind is a correctness problem for
what ships, not a gate failure.

`cycles_used` **0** of 10 — one product run, zero send-backs. Runs **6** of 20.

## Open Questions

- Q1 **BLOCKING, THE OPERATOR'S SIGNATURE — it gates T-13, which gates T-17.** Amend T-13's intent
  from seven occurrences to eight, supplying occurrence 8's sentence with its own run dir
  (`2026-08-21-2-product`) and its stronger "demands a false verdict" claim, now measured, while
  leaving the `2026-08-21-1-product` pin on 5/6/7 only. pm judged this NEW, not covered. Paying it now
  costs one amend; paying it at T-13 time writes seven permanently into an authority with **no
  propagation checker**.
- Q2 **NOT blocking, the operator's call, same trade already declined once.** `BRIEF.md:16` also reads
  "seven measured occurrences". Amending the BRIEF resets its approval for prose — the trade refused
  on SC-14. Defensible middle: amend T-13 only, accepting the BRIEF then understates a number the
  authority states correctly.
- Q3 **NOT blocking, pm's observation.** T-13's `verify:` asserts only token presence, so seven and
  eight both pass. If the intent is amended, consider binding the count into the verify.
- Q4 **NOT blocking, CARRIED — do not re-raise and do not fix.** SC-14 still names **221** as its
  basis while the plan records at `:1448-1464` that the number is not attributable to scripts. pm
  recommended leaving it; the operator did not overturn that. A goal-check tripping on SC-14 must say
  explicitly that this is the known carried question, never report it as fresh.
- Q5 **NOT blocking, the durable half of the defect that just blocked me.** `RUNS_AGENT_EXEMPT` was
  fixed by hand for two features. The suite asserts the map's MECHANISM, never its COVERAGE:
  `test-validate-feature-json.py:361-399` proves lookups work, and `test-check-domain.py:2232` uses
  `feat not in RUNS_AGENT_EXEMPT` as a fixture *precondition*. Nothing asserts the key set matches the
  corpus — which is why two missing features went unnoticed. Backlog row.
- Q6 **NOT blocking, the main session's act; an agent composing a GitHub post is forbidden**
  (DEC-138 am.6). #551's occurrence record needs updating once Q1 settles. Plus a backlog row against
  run-dir minting, data-losing here: a zero-padded seq sorted before an existing `-1-` id and the
  round overwrote a prior round's digest. Dirs are NOT renamed — that would erase the evidence. **This
  round minted `build-eng` and `t13-count-product` correctly, so it did not recur.**
- Q7 **NOT blocking, pre-existing, NOT mine.** `check-state.sh`'s one violation is FEAT-26's
  unapproved BRIEF — a different flow, standing before this change.
