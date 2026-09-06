# STATE

## Current

- feature: BUG-1304-worktree-relative-path-guard
- run: validate phase COMPLETE, orchestrated by BuildBug1304
- squad: validator (panel c1, c2 + qa gate), product (goal-check c1, c2), eng (SIMPLIFY)
- status: review — every gate passed, ship-ready, awaiting the operator's ship decision

VALIDATE IS CLOSED AND THE FEATURE IS SHIP-READY at `review_sha` **c5869301**. Panel PASS with
`must_fix: []` and `severity_max: med`; goal-check PASS with all TWELVE criteria met; blocking qa
gate PASS; SIMPLIFY PASS and empty; `check-state.sh` exit 0, zero violations; `run-unit-tests.sh
--kind all` exit 0, 0 `^FAIL `, 73 files discovered — the SAME 73 as the pre-build baseline, so the
green is not a discovery collapse. UAT DOES NOT APPLY: BRIEF.md carries ZERO `verify: uat` criteria,
so `gates.uat: blocking_when_uat_criteria_exist` is satisfied vacuously; pm confirmed it explicitly
rather than leaving it inferred. NOT merged, NOT shipped — both are the operator's.

BRIEFING: `notes/ship-review-2026-09-05-validate-final.md` (+ rendered `.html`, never hand-authored).
It carries thirteen proposed backlog rows B-1..B-13; ANYTHING NOT LISTED THERE DIES SILENTLY.

VALIDATE CYCLE 1 — both FAIL, three gating findings, all closed. Every premise verified at source
before it was routed; a finding resting on a false premise buys a cycle for nothing.
- F-01 (HIGH, REQ-06). `bash-write-guard.sh` routed all three claim refusals through `deny()`, which
  appends "File changes go through the Write tool" — advice naming a route that refuses the identical
  destination with identical text, where REQ-06 requires the control-plane expertise destination get
  the sanctioned CLI and nothing else. FOUND BY THE UI REVIEWER, which scoped itself out of
  rendered-UI review and then audited the refusal strings as the operator interface. The code
  reviewer's own lens could not see it. Closed by `deny_bare()` (`bash-write-guard.sh:655`) at all
  three sites; both routes' stderr now byte-identical modulo prefix, verified by fixture execution.
- F-02 (HIGH x4, mechanical). `code-grade.py` FAILed on four high records. Closed by splitting
  `claim_worktrees` and three test mega-functions; re-derived at this tier, exit 0, ZERO high.
- MF-1 (SC-05, test lane). The refusal stderr clause was unasserted on BOTH routes — behaviour was
  already correct at `harness_boundary.py:291,302`; only the proof was missing. Closed by a
  `contains` argument on each malformed-pointer call.
- MF-2 (SC-07, record lane). plan.yaml D-02 lacked the ambiguous-claim treatment; D-08 lacked the
  identical-refusal-semantics clause (the product lead's own reservation, taken). Both landed at
  `e9dbc91d` under an Advisor ruling that required NO fresh signature and NO re-run panel.

THE SPLITS WERE THE REAL CYCLE-2 RISK and were checked twice, because a split that drops an
assertion produces a GREENER suite and the suite passing is therefore not evidence. (1) byte-level
`git show af5ddd7a:` vs `git show c5869301:` diff of all four functions — every prior assertion
intact, two strictly tightened; (2) RUNTIME pre-change assertion counts measured at BOTH pins,
unchanged at 10 and 12. THE TEXTUAL CALL-SITE COUNT IS A FALSIFIED PROXY: it moved 10->8 and 12->9
because the split hoisted calls into shared helpers, so T-03's and T-05's `-ge 10`/`-ge 12` greps
now read red with correct delivery behind them (backlog B-6). The panel records honestly that
nobody deleted an assertion and watched it go red — the one form of evidence not obtained.

MY RULING ON F-03, recorded with the dissent it overrode. The security reviewer rated the
Bash-reachable claim-registry mutation (`inflight_registry release`/`release-all`) HIGH and
must_fix; the validator lead rated it HIGH but non-gating. I ruled NON-GATING on a ground neither
cited: BRIEF REQ-03 already records and the operator already APPROVED that
`.harness/.inflight-claims.json` is mutated by a `python3` CLI call and that no such mutation is a
governed write on either route. It is also not a regression — before BUG-1304 the same agent could
write the main checkout with no guard at all, so self-unbinding restores the status quo ante.
Backlog B-1 carries it WITH the security reviewer's dissent; the operator may overrule.

CYCLE BUDGET — 14 of 16 under `RuleBug1304FinalBudget` (hard ceiling 20, never a target; first-pass
gate and panel runs cost ZERO; only a send-back charges; past 16 needs a FRESH ruling). Cycle 14 was
the single cycle-1 send-back covering F-01, F-02 and MF-1; MF-2 was charged ZERO as a record repair.
`len(runs)` is 21 against `max_total_runs` 20 — INFORMATIONAL, and surfaced rather than buried.
THIRTEEN of the fourteen cycles were spent in PLANNING: three adversarial panel cycles and four
binding rulings on a change whose difficulty was deciding WHAT to bind, not how. The build passed
every task first time.

THE THREE REQUIRED FOLLOW-UPS ARE FILED AND OPEN, and are NOT backlog rows. None was implemented
inside BUG-1304 — doing so would expand an approved scope.
- #1341 — `dispatch-guard.sh:122` `_root_for` basename equality should be `worktree_for_feature`
  prefix alignment. Struck T-08's defect; the strike is legitimate only because #1341 owns it.
- #1342 — `linked_worktrees` fail-OPEN on OSError and on an unreadable pointer. NARROWER than when
  filed: `RuleBug1304UnreadableConflict` settled the registry half, so only `linked_worktrees`
  remains open, and the issue text still describes the wider scope.
- #1343 — `validate-digest.py:1755` `live_children` cannot see a compatibility child past 1200s.

BINDING RULING `RuleBug1304UnreadableConflict`, recorded WITH the reading that LOST. T-04's binding
made FEAT-51's directory-at-the-registry-path case refuse where FEAT-51 pinned fail-open. I argued
no conflict existed — REQ-05 enumerates three fail-closed causes, a directory is an OSError and none
of them, and every `UnreadableRegistry` assertion in the tree uses a parse payload, so narrowing
`live_claims:298` would have cost zero assertions. THE ADVISOR RULED OTHERWISE and it binds. DEC-218
carries all three consequences, including that quarantine machinery's own failures stay fail-open.

DEAD ENDS, do not re-open: the binding key (DEC-208 ruling 2 rejected a payload key); building S
from which registry FILE a claim sits in; filtering the binding enumerator with `_expire` or
`CLAIM_TTL_SECONDS`; the `CHECK_DOMAIN_BIN`/`BASH_WRITE_GUARD_BIN` override for SC-06; narrowing
`live_claims`'s OSError catch; and the simplify reader's call-local prefix helper.

## Open Questions

- HARNESS DEFECT — INV-26 and the mirror contract contradict each other. `gh_board.project` places a
  sub-issue at its own station "VERBATIM AND WITH NO EXCEPTION", so a done task wants the done
  column, but NO subcommand writes that column before `ship` (`gh-sync.py cmd_status` writes `ready`
  and `review` only). D-24's widening applies solely while the feature station is `review`, so every
  feature is red between its last task landing and its review transition, and no command can clear
  it. Cost here: T-10's `verify:` could not pass until after the station write. Backlog B-8.
- HARNESS DEFECT — INV-32 reports a wrongly-KEYED but otherwise complete panel reader entry as
  "reader <x> never ran or was not recorded", which reads as a missing panel record. Backlog B-9.
- HARNESS DEFECT — `plan-merge.py apply` cannot amend an existing top-level `panel`: it is not in
  `UNION_KEYS` (`:104`), so the step-8 guard (`:764-774`) exits 7 CONFLICT and writes nothing. The
  working verb is `set-panel --value-file` (`:1040`), which the playbook never names. Backlog B-10.
- HARNESS DEFECT — a handoff note cannot be written from a worktree. `check-domain.sh:1614` passes
  `rel` worktree-STRIPPED with `root` the MAIN checkout while `FEATURE_RE` is `^`-anchored. Measured
  both ways. This is BUG-1304's own defect class one layer up. Backlog B-11.
- HARNESS DEFECT — subagents returned complete, well-formed VERDICT/DIGEST blocks while the host
  reported `failed (exit 1)` with "yield called with null data". Observed FOUR times in this feature,
  including the cycle-2 panel lead itself. A caller routing on that status alone re-spends the
  spawn. Backlog B-12.
- HARNESS DEFECT — `runs/*/state.yaml` is clobbered by a later run reusing a run id; `digest.md` is
  guarded against replacement and `state.yaml` is not. BUG-1305 owns this class. Backlog B-13.
