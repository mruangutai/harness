# Goal-check — BUG-124 plan vs operator's stated intent

**YES WITH GAPS.** The plan closes the reported defect at the only site that can see a dispatch
prompt, derives its vocabulary from the manifest, and every REQ has a task behind it. Two gaps:
D-01 narrows the intent's callee-specific clause (judged below, recommend accept with a disclosure),
and the plan's own `verify:` string becomes self-refusing once T-02 lands.

## The intent tension — D-01, judged

The operator's parenthetical says "against the callee's own domain glob"; D-01
(`plan.yaml:29-42`) validates shape against the `/runs/` grant FAMILY with no ownership check.
Measured facts that bear on it:

- The substitution catches the reported case. `eng-t01` matches none of the three `/runs/` grants
  (`.harness/team-config.yaml:306,315,324`), and `harness_boundary.matches` returns `False` for
  `runs/eng-t01/x` vs `*-eng/**`, `True` for `t01-eng`. Re-measured here.
- It refuses nothing that exists. All **309** distinct run dirs under
  `/Users/molchairuangutai/GitHub/harness/.harness/*/features/*/runs/` end in `-product`, `-eng`
  or `-validator`; zero non-conforming. So the false-positive argument for dropping the ownership
  check costs nothing observable today.
- D-01's non-vacuity claim is confirmed: orchestrator holds `.harness/*/features/**`
  (`.harness/team-config.yaml:45`), so a resolve-to-any-agent rule would pass `eng-t01`.
- **The narrowing is real.** Issue #124's first sentence is the general class — "a run-dir path its
  callee provably cannot write" — and a well-formed wrong-squad slug (orchestrator → `harness-eng-lead`
  naming `runs/t01-product/digest.md`) still passes D-01 while remaining unwritable by the callee.
  D-01 closes the inversion family, not the class. No REQ or SC covers the wrong-squad case, and the
  plan nowhere discloses that it is out of scope.
- The site choice is inside the operator's "either … or": the `check-plan-routes.py` alternative is
  ruled out on measured grounds (`BRIEF.md:43-45`, citing
  `.harness/harness/features/FEAT-31-orchestrator-context-watch/notes/probe-hook-payload-identity.md`,
  which exists). Not a narrowing.

**Recommendation, one step: raise D-01 to the operator at signature** — accept the callee-independent
rule (the false-positive reasoning holds and the wrong-squad case has no observed instance), on
condition that the brief carries one disclosure line naming the wrong-squad slug as detected-by-nothing.
Do not amend the rule shape; ownership checking on prose is the failure D-01 correctly avoids.

## Coverage — every clause, both directions

| Intent clause | Lands on |
|---|---|
| refuse before the dispatch proceeds | REQ-01 → T-02 (`plan.yaml:200-218`, check sits before the claim, D-04) |
| mechanical, at dispatch-guard.sh | REQ-01/03 → T-02 |
| against the callee's own domain glob | REQ-01 → T-02 **as shape only** (see above) |
| dispatcher can fix in one step | REQ-02 → T-01 `run_dir_forms`, T-02 refusal message, T-03 prose |
| vocabulary from team-config.yaml | REQ-04 → T-01, T-02 |
| never blocks on its own failure | REQ-05 → T-01, T-02 (fail-open, DEC-100) |

No REQ is unserved; no task lacks a clause. `check-plan-routes.py` on this plan: 0 violations,
exit 0, T-03 correctly declared main-session-direct. T-03 (docs) is the one addition beyond the
literal ask — proportional, since `SKILL.md:272-274` is today the convention's only statement.

## Do the SCs convince the operator, and does the fix fire on the real shape?

Mostly yes. SC-01/02 assert the reported slug `eng-t01` through the real hook stdin seam of the real
`dispatch-guard.sh`, not a mock; SC-06 requires the red proof against `git show 6d969ed3:` of the
guard; SC-07 closes the strand-a-claim failure mode. SC-04 proves derivation with an invented squad,
so the gate is not literal-token green.

Two evidence notes:

- SC-01..05/07 run inside a throwaway checkout with a synthesized manifest. The **live** three-glob
  vocabulary is proven only at unit level (T-01 `verify:`) plus T-02's own `verify:` line, which is
  the only end-to-end run against the real `team-config.yaml`. That line asserts the string but not
  `exit 2` (`plan.yaml:159`) — already flagged advisory in the draft digest; agreed, not blocking.
- **F1, new: the plan's own verify is self-refusing.** `plan.yaml:159` embeds the literal
  `.harness/harness/features/BUG-124-run-dir-squad-suffix/runs/eng-t01/digest.md`, and the lead
  carries `verify:` verbatim into the member's dispatch prompt. Once T-02 lands, the next dispatch
  quoting that string — a T-02 retry, the qa re-run, a reviewer — is itself refused at exit 2 with no
  override. This is D-01's own "prose cannot tell writes from reads" blindness, aimed at a quoted
  example rather than a directive. It is invisible to REQ-03 and to SC-03, which cover compliant
  paths and no-path prompts only.

D-03's premise re-measured independently and holds: `python3 -I -c "import yaml"` →
`ModuleNotFoundError`, plain `python3 -c` succeeds. All orchestrator-supplied facts checked out; none
was wrong.

## Open questions

- Q1 (blocking at signature): accept D-01's callee-independent shape rule, with the wrong-squad slug
  disclosed as uncovered?
- Q2 (non-blocking): F1 — is a prompt that merely QUOTES a bad slug meant to be refused? If not, the
  fix wants either a non-`.harness/`-anchored fixture path in T-02's `verify:`, or a stated escape.
