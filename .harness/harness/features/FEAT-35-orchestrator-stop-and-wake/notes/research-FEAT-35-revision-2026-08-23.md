# FEAT-35 — the one consolidated revision, applied (2026-08-23)

**Verdict: all five items landed. Both artifacts remain `status: pending`, unsigned.
`check-plan-routes.py` exits 0 with 5 OK lines and no DEVIATION** (it carried one before).

## What changed

**Scope amendment (BRIEF, `## Constraints`).** The constraint no longer reads as SKILL.md-exclusive.
It now binds BEHAVIOUR: `.claude/skills/harness/SKILL.md` is the only behaviour changed, travelling
with exactly two sanctioned companions — the decision record (DEC-158 forbids the measurement living
in the playbook) and the regression test. "Nothing else, and no third companion." Leads stay out
(#610, #552).

**FIX 1 — T-02.** The self-id step now writes all three match outcomes, and four of them are
`verify:` greps rather than intent prose: `Exactly one match`, `SKIP the context check for this
wake`, `Never guess an id`, `never treat a skipped check as a passed one`. Zero and two-or-more take
the identical path: skip, one line saying so, continue. The two-or-more case is recorded as
reproduced (a non-unique probe matched three transcripts), and the intent states that skipping is
legal under DEC-198 while reporting a headroom figure off the wrong transcript is not.

**FIX 2 — BRIEF `## Constraints`, "What supplies the mechanism".** The false sentence ("am.4's
enumeration IS the enforcement layer") is gone. The operative test is now
`check-domain.sh --resolve .claude/skills/harness/SKILL.md` → `NOBODY` at `569d417`, stated as
independent of am.4. Am.4 is cited for the category only, with its own heading and ruling
(`DECISIONS.md:4854`, `:4862` — both re-read at this tree).

**FIX 3 — D-08.** T-05 moves to `execution_mode: team`, `execution_agent: harness-dev-ops`; the two
`lanes:` rows move with it; T-04 writes **no** amendment 5.

**Item 5 — T-01 and D-09.** T-01 must add a sentence beginning `The single-flight refusal on your
return is EXPECTED`, greppable in its `verify:`. D-09 records the leads' enforced wait as an accepted
cost of the boundary.

## Evidence D-08 rests on, all re-derived at `569d417` in this worktree

- `run-unit-tests.sh` is already a CI step, twice: `.github/workflows/tests.yml:81` (`--kind unit`)
  and `:87` (`--kind integration`). T-05 neither creates nor promotes it.
- T-05's edit is one basename into `UNIT_SCRIPTS`, so gate status is identical before and after —
  and am.4's rule fires on **the day** a script becomes a gate (`DECISIONS.md:4877-4880`).
- `check-domain.sh --resolve` on both T-05 files returns `harness-backend-dev, harness-dev-ops`.
- **Contrary evidence, engaged not ignored:** that workflow's comment says the required context is
  `integration`, and both suites are steps of that job — so the runner IS reached by a required
  check. It still fails am.4's category ("hooks, validators, gate scripts"): a runner that executes
  assertions refuses nothing. The other reading makes every `bin/test-*.py` enforcement layer, which
  contradicts both the enumeration (each *gate's* test) and the squad grant on
  `.claude/skills/harness/bin/**`. Am.4's circularity worry is also absent: the change only adds
  assertions, and the drift detector exits 2 for the whole suite on any unlisted `test-*.py`, so a
  bad registration is loud.
- `harness-dev-ops` over `harness-backend-dev` because dev-ops's `consult-when` names test-runner
  setup (`team-config.yaml:212-214`); both are granted, so either is legal.

## Independent check on item 5's mechanism

`#551` is real and its bound is in the code, not inferred: `validate-digest.py --hook` returns 2 for
`norm(agent) in ("lead","orchestrator")` with live children, and `stop_hook_active` short-circuits
the next pass — which is why `inflight_registry.children_refusal_lines` prints "this refusal fires
ONCE; a second identical return will ship". So the cost to leads is **one turn**, not an unbounded
wait, and D-09 says exactly that rather than overclaiming.

## Discrimination check

All five new `verify:` literals are absent from `git show 569d417:.claude/skills/harness/SKILL.md`,
so none of them passes vacuously.

## Out of scope, held out

Q9 (fabricated completion) — shapes REQ-03 only; no task added; main session files it.
Q5 (leads' pattern) — recorded as D-09, not planned.

## Open questions

None. The revision is complete and both artifacts await the operator's signature.
