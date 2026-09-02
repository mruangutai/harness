# FEAT-51 · goal-check: does the plan deliver the operator's stated intent?

**yes-with-gaps.**

All four `## Settled` clauses are delivered `complete`, no `## Out of scope` exclusion is crossed, and
the plan stays inside the `## Not yet specified` freedom. Three gaps, none of them a missing capability:
one decision (**D-16**) that cannot reach the agent that must implement it, one task (**T-08**) the
stated intent does not require, and one settled behaviour (the host's wake) the plan **asserts in prose
that no task implements and no automated check can falsify**. Authority for this check is
`.harness/notes/grilling-claude-code-lifecycle-safety-2026-09-01.md`; the BRIEF shows no drift *from*
it (its 7 REQ map 1:1 onto the four settled clauses plus `#551` occurrence 1's replacement-writer half,
and it excludes `#628` at `BRIEF.md:83`).

## 1. Clause-by-clause against `## Settled`

**(1) Live children may finish read-only analysis; feature-artifact writes are quarantined until a
resumed parent explicitly adopts — `complete`.** Predicate `orphan_write` (T-02, self-referential per
D-03); `Write`/`Edit` route (T-03) and `Bash` route (T-07, the route `plan.yaml` actually travels —
verified: `.claude/settings.json:19` registers `check-domain.sh` on `Write|Edit` only, `:28`/`:44`
register `plan-sign-gate.sh` on `Bash`, at `ad93d43e`); artifact set fixed by D-05; sandbox by one
shared glob (D-06); adoption CLI by T-04 delegating to `plan-merge.py` (D-07). "Read-only analysis
survives" is explicit: T-03 refuses no `Read`, `Grep` or `Bash`, and `notes/`, `observations/`, `runs/`
stay writable (D-05, graded SC-05).

**(2) A parent ends a normal turn by a nonterminal suspension with no verdict, the host wakes the SAME
parent, and a terminal digest is required only then — `complete`, with one bound (§6).** T-01 splits
today's single answer at `validate-digest.py:1563`/`:1575` into three; `SUSPENDED` is confined to
`hook_mode` and never enters `VERDICTS`, so no member and no written digest can carry it (T-01, D-01).
D-02 keeps the parent claim unreleased, which is what makes "the same parent" legible to the registry.
Terminal-with-live-children stays refused at exit 2 (T-01 branch 2); with no live child the return falls
to the existing schema check, which demands a terminal verdict — that is "only then".

**(3) The parent does not poll at all — `complete`.** T-05 clause 2 states zero, not a budget; T-04
specifies `quarantine.py` with "no scheduler, no timer, no TTL and no implicit action". The substantive
delivery is T-01: once the turn-end is legal, the context-burning hold-the-turn workaround `#551`
records has no motive.

**(4) The work is `#280` and `#551` together, `#628` is not part of it — `complete`.** `plan.yaml:5`
`source_issues: [280, 551]`; T-01/T-05 answer `#551`'s stop-path harm, T-02/T-03/T-04/T-07 answer
`#280`'s "stop concurrent writes, not concurrent thinking" acceptance boundary. No task lists
`plan-merge.py` in `files:`, and D-12 explicitly refuses to put the new rule inside it.

## 2. Against `## Out of scope`

- **OMP lifecycle behaviour** — not crossed. D-04 confines the boundary to `runtime != omp`; T-02
  case 33 and SC-07 assert it, SC-07 with a demonstrated mutant. No `.omp/` path appears in any
  `files:` list.
- **Rebuilding plan merge safety (`#628`/FEAT-32)** — not crossed. D-07 and T-04 delegate union and
  approval carry-forward to `plan-merge.py`; D-12 rejects a check inside it precisely because adoption
  would then need an exemption.
- **Letting an orphan write and repairing afterward** — not crossed. Both routes refuse `PreToolUse`,
  before the write. T-03 guards `not _post`, so the `--post` sweep at `.claude/settings.json:60` is not
  the enforcement point.
- **Polling, sleeps, heartbeats, fabricated work** — not crossed. No task specifies or permits a timer,
  retry loop, periodic sweep or poll-until-ready. **On `CLAIM_TTL_SECONDS` explicitly: it is a
  pre-existing expiry the plan reads and does not drive.** It is `1200` at
  `inflight_registry.py:24` (`ad93d43e`), applied lazily on read at `:216` through `_expire_where`
  (`:222`) — a value compared during a query, with no scheduler behind it. T-02 forbids changing it and
  keeps expiry query-scoped as `live_children` (`:289`) already does. T-06 records the consequence as an
  honest bound rather than acting on it. Verdict: **not the timer the operator rejected.**

## 3. Against `## Not yet specified`

Inside the freedom. Every mechanism choice is the narrowest host-compatible one available and each is
justified by a host fact, not a preference: the suspension lives in the one hook that already fires on
the stop (D-01); the Bash half is a second rule in an already-registered gate rather than a new hook
needing a `settings.json` entry (D-12); the sandbox is one `shared:` glob rather than twelve grants
(D-06); the predicate needs only schema-2 data already recorded (D-03). Nothing the operator delegated
is quietly settled in the other direction — D-04 and D-05 *narrow* the blast radius rather than widen
it. One dead-but-harmless detail: T-03's guard tuple includes `NotebookEdit`, which the `Write|Edit`
matcher never delivers; it mirrors the tuple already at `check-domain.sh:1647`.

## 4. Intent the plan may have EXCEEDED

- **T-08 — NOT required by the stated intent. Explicit verdict.** The grilling artifact says nothing
  about the decision record; T-08 is a test guarding the *prose content* of a `DECISIONS.md` entry, and
  it exists only because the BRIEF wrote SC-09 with `verify: automated` over that prose
  (`BRIEF.md:142-157`). That is a BRIEF-invented requirement generating a plan task. Its cost is real:
  string assertions on an authority entry ossify wording and renumbering, and it puts the live authority
  file inside the integration suite. **It is nonetheless the only thing that enforces D-15** (see the
  next bullet's mechanism), so cutting T-08 alone re-opens the gap. Recommend to the orchestrator: cut
  T-08 *together with* SC-09's two script-naming clauses, or keep T-08 as the cheapest compensating
  control and accept the ossification — not cut it in isolation.
- **D-16 + the discard half of T-07 — WITHIN the stated intent, but undeliverable as written. Explicit
  verdict.** The `## Destination` names the actor for both acts: "a resumed parent explicitly adopts or
  discards the result". An orphan destroying the only copy of its own result is the same
  unsupervised-durable-state harm, so covering `discard` is a *reading* of the intent, not an addition —
  and it is one branch in a rule already being written. The defect is mechanical, not scope: see §6.
- **D-15 is an errata note wearing a decision's clothes.** It fails DEC-149's three-part bar (it is not
  a trade-off; it is a correction to two bullets of T-06's immutable `intent:`). It is the only route
  available given immutability, so leave it — but a reader will mistake it for a product choice.
- Everything else earns its place: T-04's `list` is required by T-05 clause 4; T-06's DEC-209 entry is
  standing harness practice (DEC-205), not scope creep; T-01's six cases and T-03's FEAT-41 ordering
  case are each the discriminator for a criterion.

## 5. What the plan cannot deliver as written

1. **D-16 will not be built.** `intent:` is the literal dispatch prompt and is all the doer receives
   about the task. T-07's `intent:` directs the opposite — `ADOPT_TOOL = "quarantine.py", with the
   single verb adopt. discard is deliberately NOT covered … Say so in a comment` — and T-07's `verify:`
   greps three labels, none of them D-16's `an orphan quarantine.py discard of a quarantine directory is
   refused`. No SC covers it either (SC-11 names `apply`, `set-task-station` and `adopt` only). As
   written, T-07 ships with `discard` uncovered **and a code comment asserting that omission is
   deliberate**, contradicting the plan's own decision. Fix is one of two: strike D-16, or add a task
   whose `intent:` carries the `--dir` branch and whose `verify:` greps that label. (Contrast D-15,
   which has the same immutability problem but *is* enforced — by T-08.)
2. **The wake is asserted, never proven.** T-05 clause 3 writes "the host resumes the SAME parent" into
   both playbooks. No task implements a wake, and none can: Claude Code exposes no durable child-process
   owner. T-01 only makes the turn-end legal. SC-08 grades the sentence by inspection and SC-10 (uat) is
   the sole observation of the behaviour, so if the host does not resume, settled clause 2 fails and it
   is discovered at the operator's hand-test. Honest, but the orchestrator should know the plan's
   riskiest claim is the one clause with no automated evidence.
3. **SC-06's "no code path schedules either act on a timer" has no assertion behind it.** No task's
   `verify:` proves the negative; it rests on T-04's `intent:` prohibition holding at build time.
4. Carried, not mine: the plan can never acquire an `approval:` mapping (`plan.yaml:7-13`, Q1). Already
   with the operator; not a plan defect and not re-opened here.
